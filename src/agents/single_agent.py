from __future__ import annotations

from src.contracts import ProcurementDecision, RunTelemetry
from src.decision import merge_decision
from src.intake import intake_request
from src.llm import LLMClient
from src.policy_engine import apply_policy
from src.prompts import SYSTEM_PROMPT, make_context
from src.tools import BudgetTool, PolicyTool, SoftwareTool, VendorTool


TOOLS = [BudgetTool(), SoftwareTool(), VendorTool(), PolicyTool()]


def run_single(request_id: str) -> ProcurementDecision:
    request, injection = intake_request(request_id)
    telemetry = RunTelemetry(llm_calls=0, tool_calls=0, tool_names=[])
    results = {}
    for tool in TOOLS:
        result = tool.run(request)
        telemetry.tool_calls += 1
        telemetry.tool_names.append(tool.name)
        results[tool.name] = result

    policy = apply_policy(
        request,
        results["budget_tool"].data,
        results["software_tool"].data,
        {**results["vendor_tool"].data, "ok": results["vendor_tool"].ok, "error": results["vendor_tool"].error},
        injection,
    )

    llm = LLMClient()
    llm_json = {}
    if llm.available:
        try:
            llm_json = llm.generate(SYSTEM_PROMPT, make_context(request, policy))
            telemetry.llm_calls += 1
        except Exception:
            llm_json = {}
    return merge_decision(request_id, policy, llm_json, telemetry)

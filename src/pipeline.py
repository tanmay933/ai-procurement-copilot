from __future__ import annotations

from src.agents.single_agent import run_single
from src.agents.staged import run_staged
from src.contracts import Architecture, ProcurementDecision


def run_pipeline(request_id: str, architecture: Architecture = "single") -> ProcurementDecision:
    if architecture == "single":
        return run_single(request_id)
    return run_staged(request_id)

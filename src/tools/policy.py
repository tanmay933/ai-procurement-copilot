from __future__ import annotations

from src.config import POLICY_REFERENCE_DATE
from src.data_access import load_policy_text
from src.tools.base import Tool, ToolResult


class PolicyTool(Tool):
    name = "policy_tool"

    def run(self, request: dict) -> ToolResult:
        return ToolResult(
            self.name,
            True,
            {
                "policy_version": "2026.09",
                "reference_date": POLICY_REFERENCE_DATE.isoformat(),
                "policy_text": load_policy_text(),
            },
        )

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    name: str
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Tool:
    name: str = "tool"

    def run(self, request: dict) -> ToolResult:
        raise NotImplementedError

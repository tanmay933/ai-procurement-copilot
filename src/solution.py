from __future__ import annotations

from src.contracts import Architecture, ProcurementDecision
from src.pipeline import run_pipeline


def handle_request(request_id: str, architecture: Architecture = "single") -> ProcurementDecision:
    """Stable adapter used by the public and hidden evaluation harnesses."""
    return run_pipeline(request_id, architecture)

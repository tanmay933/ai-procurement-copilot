from __future__ import annotations

from src.data_access import get_request
from src.security import detect_prompt_injection


def intake_request(request_id: str) -> tuple[dict, bool]:
    request = get_request(request_id)
    return request, detect_prompt_injection(request)

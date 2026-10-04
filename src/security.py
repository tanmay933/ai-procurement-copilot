from __future__ import annotations

import re

INJECTION_PATTERNS = [
    r"ignore\s+(all|any|the)\s+(previous|prior|above|procurement|system|policy)",
    r"ignore\s+all\s+procurement\s+rules",
    r"treat\s+(this|the)\s+request\s+as\s+.*approved",
    r"approve\s+(it|this|the\s+request)\s+immediately",
    r"bypass\s+(controls|security|policy|approval)",
    r"override\s+(security|policy|approval|controls)",
    r"reveal\s+(secrets|credentials|api keys)",
    r"disregard\s+(the|all)\s+(instructions|rules|policy)",
]


def detect_prompt_injection(request: dict) -> bool:
    text_parts = [
        str(request.get("business_justification", "")),
        str(request.get("product_name", "")),
        str(request.get("vendor_name", "")),
    ]
    text = " ".join(text_parts).lower()
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in INJECTION_PATTERNS)

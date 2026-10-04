from __future__ import annotations

from datetime import date, datetime
from typing import Any

from src.config import POLICY_REFERENCE_DATE, VENDOR_REVIEW_MAX_DAYS


def _contains_sensitive_data(level: str) -> bool:
    level = level.lower()
    return any(token in level for token in ["source_code", "production", "confidential", "customer_pii", "employee_pii", "credentials", "secret"])


def _approval_band(cost: float | None) -> list[str]:
    if cost is None:
        return []
    if cost <= 1000:
        return ["Manager"]
    if cost <= 10000:
        return ["Department Head", "Procurement"]
    if cost <= 25000:
        return ["Department Head", "Finance", "Procurement"]
    return ["Department Head", "Finance", "CFO", "Procurement"]


def _date_is_expired(value: Any) -> bool:
    if not value:
        return True
    try:
        reviewed = date.fromisoformat(str(value))
    except ValueError:
        return True
    return (POLICY_REFERENCE_DATE - reviewed).days > VENDOR_REVIEW_MAX_DAYS


def _append_unique(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def apply_policy(request: dict, budget: dict, software: dict, vendor: dict, injection_detected: bool) -> dict:
    missing: list[str] = []
    for key, label in [
        ("annual_cost_usd", "annual cost"),
        ("user_count", "user/license count"),
        ("business_justification", "business purpose"),
        ("data_access_level", "data access level"),
    ]:
        value = request.get(key)
        if value is None or str(value).strip() in {"", "unknown", "null"}:
            missing.append(label)

    flags: list[str] = []
    approvals = _approval_band(request.get("annual_cost_usd"))
    evidence: list[dict] = []

    if budget:
        dept = budget.get("department")
        available = budget.get("available_usd")
        cost = budget.get("annual_cost_usd")
        if dept:
            evidence.append({"source": "budget_tool", "finding": f"Department is {dept} with ${available:,.0f} available software budget.", "reference": dept})
        if cost is not None and available is not None:
            if budget.get("within_budget"):
                evidence.append({"source": "budget_tool", "finding": f"${cost:,.0f} annual cost is within the ${available:,.0f} available budget.", "reference": dept})
            else:
                _append_unique(flags, "budget_insufficient")
                _append_unique(approvals, "Finance")
                evidence.append({"source": "budget_tool", "finding": f"${cost:,.0f} annual cost exceeds the ${available:,.0f} available budget.", "reference": dept})

    alternatives = software.get("alternatives", []) if software else []
    same_product = software.get("same_product", []) if software else []
    if same_product or alternatives:
        # Exact product is a stronger overlap than a same-category alternative.
        _append_unique(flags, "existing_tool_overlap")
        if same_product:
            first = same_product[0]
            finding = f"Approved catalog contains {first.get('product_name')} from {first.get('vendor_name')} with {first.get('licensed_seats')} licensed seats."
        else:
            names = ", ".join(str(x.get("product_name")) for x in alternatives[:3])
            finding = f"Approved catalog contains relevant alternative(s): {names}."
        evidence.append({"source": "software_tool", "finding": finding, "reference": "software_catalog"})
    else:
        evidence.append({"source": "software_tool", "finding": "No matching approved product or relevant catalog alternative was found.", "reference": "software_catalog"})

    internal = vendor.get("internal") if vendor else None
    external = vendor.get("external") if vendor else None
    vendor_error = not vendor.get("ok", False) if vendor else True
    if internal:
        evidence.append({"source": "vendor_tool", "finding": f"Internal registry: {internal.get('procurement_status')} procurement status; security status {internal.get('security_status')}; legal terms {internal.get('legal_terms_status')}.", "reference": internal.get("vendor_id")})

    if external:
        ext_status = external.get("security_review_status")
        evidence.append({"source": "vendor_tool", "finding": f"Vendor-risk service reports security review '{ext_status}' for {external.get('vendor_name')}, last reviewed {external.get('last_review_date') or 'never'}.", "reference": "vendor-risk API"})
        if internal and internal.get("security_status", "").lower() == "approved" and ext_status in {"expired", "not_completed"}:
            _append_unique(flags, "conflicting_vendor_evidence")
    else:
        if vendor_error:
            _append_unique(flags, "vendor_risk_unavailable")
            evidence.append({"source": "vendor_tool", "finding": f"Vendor-risk evidence could not be verified: {vendor.get('error', 'service unavailable') if vendor else 'service unavailable'}.", "reference": "vendor-risk API"})

    data_level = str(request.get("data_access_level", ""))
    if _contains_sensitive_data(data_level):
        _append_unique(flags, "security_review_required")
        evidence.append({"source": "policy_tool", "finding": f"Data access level '{data_level}' requires Security review under the procurement policy.", "reference": "Policy section 5"})

    integrations = " ".join(str(x) for x in request.get("requested_integrations", []))
    integration_text = integrations.lower()
    if any(x in integration_text for x in ["production", "cloud account", "credentials", "secrets"]):
        _append_unique(flags, "security_review_required")
        evidence.append({"source": "policy_tool", "finding": "Production/cloud-account integration triggers Security review.", "reference": "Policy section 5"})

    if external:
        ext_status = str(external.get("security_review_status", "")).lower()
        if ext_status in {"expired", "not_completed", "unknown"}:
            _append_unique(flags, "security_review_required")
        if ext_status == "expired":
            _append_unique(flags, "vendor_review_expired")
        elif _date_is_expired(external.get("last_review_date")) and ext_status == "approved":
            _append_unique(flags, "vendor_review_expired")
        if external.get("stores_data_outside_region"):
            _append_unique(flags, "privacy_review_required")
        if external.get("processes_personal_data") and data_level.lower() in {"customer_pii", "employee_pii"}:
            _append_unique(flags, "privacy_review_required")

    if data_level.lower() in {"customer_pii", "employee_pii"}:
        _append_unique(flags, "privacy_review_required")

    if internal:
        procurement_status = str(internal.get("procurement_status", "")).lower()
        legal_status = str(internal.get("legal_terms_status", "")).lower()
        cost = request.get("annual_cost_usd")
        if procurement_status != "approved" and cost is not None and float(cost) >= 10000:
            _append_unique(flags, "legal_review_required")
        if legal_status not in {"approved", "standard"}:
            _append_unique(flags, "legal_review_required")

    if injection_detected:
        _append_unique(flags, "prompt_injection_detected")
        evidence.append({"source": "security_guard", "finding": "Instruction-like text was detected inside business data and was treated as untrusted content.", "reference": "Policy section 9"})

    for flag, approval in [
        ("security_review_required", "Security"),
        ("privacy_review_required", "Privacy"),
        ("legal_review_required", "Legal"),
        ("conflicting_vendor_evidence", "Security"),
        ("vendor_risk_unavailable", "Security"),
    ]:
        if flag in flags:
            _append_unique(approvals, approval)

    if missing:
        _append_unique(flags, "missing_information")

    return {
        "missing_information": missing,
        "risk_flags": flags,
        "required_approvals": approvals,
        "evidence": evidence,
    }

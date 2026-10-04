from __future__ import annotations

from src.contracts import EvidenceItem, ProcurementDecision, RunTelemetry


def fallback_text(policy: dict) -> tuple[str, str]:
    missing = policy["missing_information"]
    flags = policy["risk_flags"]
    if missing:
        return "Request clarification before approval", "Obtain the missing request information, then rerun procurement review."
    if "budget_insufficient" in flags:
        return "Route for budget exception and required reviews", "Send the evidence package to Finance and the other required human reviewers."
    if "vendor_risk_unavailable" in flags or "conflicting_vendor_evidence" in flags:
        return "Route for manual vendor/security review", "Resolve the vendor evidence gap or conflict before any approval decision."
    if "existing_tool_overlap" in flags:
        return "Review existing approved software before new purchase", "Confirm why the existing catalog option does not satisfy the stated use case, then continue required approvals."
    if any(flag in flags for flag in ["security_review_required", "privacy_review_required", "legal_review_required", "vendor_review_expired"]):
        return "Route for required reviews before approval", "Send the evidence package to the listed human reviewers; do not approve autonomously."
    return "Proceed to required business approval", "Send the evidence package to the required business approver(s) for human approval."


def merge_decision(request_id: str, policy: dict, llm_json: dict, telemetry: RunTelemetry) -> ProcurementDecision:
    fallback_recommendation, fallback_next = fallback_text(policy)
    recommendation = str(llm_json.get("recommendation") or fallback_recommendation)
    next_step = str(llm_json.get("next_step") or fallback_next)

    # Code owns the safety floor. A model cannot turn a risky/unfinished request into approval.
    if policy["missing_information"]:
        recommendation = fallback_recommendation
        next_step = fallback_next
    elif policy["risk_flags"] and any(
        flag in policy["risk_flags"]
        for flag in ["budget_insufficient", "security_review_required", "privacy_review_required", "legal_review_required", "vendor_risk_unavailable", "conflicting_vendor_evidence", "prompt_injection_detected"]
    ):
        if recommendation.lower().startswith(("approve", "purchase", "proceed with purchase")):
            recommendation = fallback_recommendation
            next_step = fallback_next

    evidence = [EvidenceItem.model_validate(item) for item in policy["evidence"]]
    return ProcurementDecision(
        request_id=request_id,
        recommendation=recommendation,
        evidence=evidence,
        required_approvals=policy["required_approvals"],
        missing_information=policy["missing_information"],
        risk_flags=policy["risk_flags"],
        next_step=next_step,
        human_review_required=True,
        telemetry=telemetry,
    )

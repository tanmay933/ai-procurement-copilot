from src.solution import handle_request


def test_low_value_request():
    d = handle_request("REQ-1001")
    assert "Manager" in d.required_approvals
    assert d.human_review_required is True
    assert len(d.evidence) >= 2


def test_source_code_security():
    d = handle_request("REQ-1003")
    assert "Security" in d.required_approvals
    assert "security_review_required" in d.risk_flags


def test_prompt_injection_is_not_followed():
    d = handle_request("REQ-1006")
    assert "missing_information" in d.risk_flags
    assert "prompt_injection_detected" in d.risk_flags
    assert d.human_review_required is True


def test_budget_and_privacy():
    d = handle_request("REQ-1005")
    assert "budget_insufficient" in d.risk_flags
    assert "privacy_review_required" in d.risk_flags
    assert "Finance" in d.required_approvals


def test_staged_contract():
    d = handle_request("REQ-1001", architecture="staged")
    assert d.request_id == "REQ-1001"
    assert d.telemetry is not None

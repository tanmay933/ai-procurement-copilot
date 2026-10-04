from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.config import LLM_PROVIDER
from src.solution import handle_request

ROOT = Path(__file__).resolve().parent
REQUESTS = json.loads((ROOT / "data" / "requests.json").read_text(encoding="utf-8"))
BY_ID = {r["request_id"]: r for r in REQUESTS}

st.set_page_config(page_title="Procurement Copilot", page_icon="🧾", layout="wide")
st.title("AI Procurement Request Copilot")
st.caption("Evidence-first recommendations. Human approval remains mandatory.")

with st.sidebar:
    st.header("Analysis")
    request_id = st.selectbox(
        "Purchase request",
        list(BY_ID.keys()),
        format_func=lambda rid: f"{rid} · {BY_ID[rid]['product_name']}",
    )
    architecture = st.radio("Architecture", ["single", "staged"], format_func=lambda x: "Single-agent baseline" if x == "single" else "Staged / 2-agent")
    st.divider()
    st.caption(f"LLM provider: **{LLM_PROVIDER}**")
    st.caption("The policy engine owns approvals, risk flags and missing information.")

req = BY_ID[request_id]

left, right = st.columns([0.95, 1.25], gap="large")
with left:
    st.subheader("Purchase request")
    c1, c2 = st.columns(2)
    c1.metric("Annual cost", "Missing" if req.get("annual_cost_usd") is None else f"${req['annual_cost_usd']:,.0f}")
    c2.metric("Users", "Missing" if req.get("user_count") is None else str(req["user_count"]))
    st.write(f"**Product:** {req['product_name']}")
    st.write(f"**Vendor:** {req['vendor_name']}")
    st.write(f"**Category:** {req['category']}")
    st.write(f"**Data access:** {req['data_access_level']}")
    st.write(f"**Business purpose:** {req['business_justification']}")
    if req.get("requested_integrations"):
        st.write("**Integrations:** " + ", ".join(req["requested_integrations"]))

with right:
    if st.button("Run procurement analysis", type="primary", use_container_width=True):
        try:
            result = handle_request(request_id, architecture=architecture)
            st.session_state["result"] = result
            st.session_state["result_architecture"] = architecture
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

result = st.session_state.get("result")
if result is None:
    st.info("Run the analysis to gather evidence and generate a recommendation.")
else:
    st.divider()
    st.subheader("Recommendation")
    st.success(result.recommendation)
    st.write(f"**Next step:** {result.next_step}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Human review", "Required" if result.human_review_required else "Not required")
    c2.metric("Tools called", result.telemetry.tool_calls if result.telemetry else 0)
    c3.metric("LLM calls", result.telemetry.llm_calls if result.telemetry else 0)

    tab1, tab2, tab3 = st.tabs(["Evidence", "Controls", "Raw output"])
    with tab1:
        for item in result.evidence:
            with st.container(border=True):
                st.markdown(f"**{item.source}** — {item.finding}")
                if item.reference:
                    st.caption(item.reference)
    with tab2:
        if result.required_approvals:
            st.write("**Required approvals / reviews**")
            for item in result.required_approvals:
                st.write(f"- {item}")
        if result.missing_information:
            st.warning("**Missing information:** " + ", ".join(result.missing_information))
        if result.risk_flags:
            st.write("**Risk flags**")
            for item in result.risk_flags:
                st.write(f"- `{item}`")
        else:
            st.success("No additional risk flags detected.")
    with tab3:
        st.json(result.model_dump())

st.divider()
st.caption("AI interprets context; deterministic code applies policy; humans retain approval authority.")

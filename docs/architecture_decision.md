# Architecture Decision Memo

Decision record for the final MVP architecture of the AI Procurement Request Copilot.

![Decision](https://img.shields.io/badge/decision-single%20agent-6A5ACD?style=flat-square)
![Baseline](https://img.shields.io/badge/baseline-staged%20%2F%20two--agent-orange?style=flat-square)
![Evaluation](https://img.shields.io/badge/evaluation-6%2F6%20both-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/status-shipped-blue?style=flat-square)

> Decision record for the final MVP architecture of the AI Procurement Request Copilot.

---

## Decision

Ship the **single-agent architecture** for the final MVP.

---

## Context

The assessment requires comparison of a single-agent baseline and a staged/two-agent architecture using the same evaluation set. Both implementations use the same evidence tools, deterministic policy controls, structured decision contract, and human-review safeguards.

---

## Evaluation

Both architectures achieved:

- Single agent: **6/6 public cases**
- Staged agent: **6/6 public cases**

With Gemini enabled, both architectures maintained **6/6** correctness.

The single-agent implementation showed lower and more predictable latency across the evaluated cases. The staged implementation introduced additional reasoning orchestration without demonstrating an accuracy improvement on the shared evaluation set.

---

## Decision Rationale

The single-agent architecture is therefore preferred because it provides the same measured correctness with:

- fewer reasoning stages
- lower complexity
- smaller failure surface
- simpler debugging and observability
- lower and more predictable measured latency

The staged architecture remains implemented as a comparison baseline rather than being removed.

---

## Safety Boundary

The architecture deliberately separates responsibilities:

- **AI:** interpret evidence and formulate recommendations.
- **Code:** gather evidence, enforce thresholds, apply policy, generate safety-critical flags and approvals.
- **Human:** approve sensitive purchases and handle exceptions.

LLM output cannot reduce deterministic policy requirements.

---

## Final Decision

Ship the **single-agent architecture with deterministic policy enforcement and human approval gates**.

The staged architecture would become preferable only if future evaluation demonstrated a meaningful improvement in decision quality that justified its additional latency and complexity.

---

## Notes

- Code fences, tables, and headings have been checked for valid GitHub Markdown rendering.

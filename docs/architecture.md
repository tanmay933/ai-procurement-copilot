# System Architecture

Final ship architecture, responsibility boundaries, and the staged evaluation baseline for the AI Procurement Request Copilot.

![Architecture](https://img.shields.io/badge/architecture-single%20agent-6A5ACD?style=flat-square)
![Baseline](https://img.shields.io/badge/baseline-staged%20%2F%20two--agent-orange?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4285F4?style=flat-square)
![Status](https://img.shields.io/badge/status-shipped-blue?style=flat-square)

> Final ship architecture, responsibility boundaries, and the staged evaluation baseline for the AI Procurement Request Copilot.

---

## Final Ship Architecture — Single Agent

```text
                    Procurement Request
                            |
                            v
                  Intake / Validation
                            |
                            v
                  Prompt Injection Guard
                            |
                            v
                 +----------------------+
                 |    Evidence Tools    |
                 |                      |
                 |  Budget              |
                 |  Software Catalog    |
                 |  Vendor Risk         |
                 |  Procurement Policy  |
                 +----------+-----------+
                            |
                            v
                 Deterministic Policy
                    + Security Checks
                            |
                            v
                    Single Agent
                  Gemini 2.5 Flash
                            |
                            v
                     Safety Merge
                            |
                            v
                 ProcurementDecision
                            |
                            v
                  Human Review /
                     Approval
```

---

## Responsibility Boundary

```text
AI
  |
  +--> Interpret evidence
  +--> Formulate recommendation
  +--> Suggest next step

CODE
  |
  +--> Gather evidence
  +--> Apply policy
  +--> Apply thresholds
  +--> Generate risk flags
  +--> Determine approvals
  +--> Validate final output

HUMAN
  |
  +--> Approve sensitive purchases
  +--> Handle exceptions
  +--> Make final procurement decision
```

---

## Staged Architecture — Evaluation Baseline

```text
                    Procurement Request
                            |
                            v
                    Evidence + Policy
                            |
                            v
                      Analyst Agent
                            |
                            v
                      Reviewer Agent
                            |
                            v
                       Safety Merge
                            |
                            v
                  ProcurementDecision
                            |
                            v
                    Human Approval
```

---

## Architecture Decision

Both architectures achieved **6/6** on the shared public evaluation set.

The single-agent architecture is shipped because it achieved the same evaluated correctness with lower complexity and lower/more predictable measured latency.

---

## Evaluation Comparison

Results are recorded in:

```text
evals/architecture_comparison.csv
```

---

## Notes

- Code fences, tables, and headings have been checked for valid GitHub Markdown rendering.


# AI Procurement Request Copilot — FDE Assessment 3

An evidence-first internal procurement copilot for software/SaaS requests.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit)
![LLM](https://img.shields.io/badge/LLM-Gemini%20%7C%20OpenRouter-6A5ACD?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-15%20passed-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/status-shipped-blue?style=flat-square)

> An evidence-first internal procurement copilot for software/SaaS requests.

The system gathers evidence from deterministic tools, applies procurement and security controls in code, optionally uses an LLM to interpret the evidence and formulate a recommendation, and keeps sensitive approval decisions with humans.

---

## What It Does

Given a procurement request, the copilot:

1. Reads and validates the request.
2. Treats business/request/vendor text as untrusted input.
3. Checks department budget.
4. Checks the approved software catalog for existing alternatives.
5. Checks vendor procurement/security/legal status.
6. Retrieves procurement policy requirements.
7. Applies deterministic policy and security rules.
8. Uses an LLM to interpret the evidence when configured.
9. Produces a structured procurement decision.
10. Escalates sensitive approvals and exceptions to a human.

The system never approves or purchases software automatically.

---

## Quick Start

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Run the setup verification

```bash
python3 verify_setup.py
```

### 4. Configure the environment

```bash
cp .env.example .env
```

The application works without an LLM API key using deterministic fallback behavior.

For Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_key_here
```

For OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_MODEL=provider/model
OPENROUTER_API_KEY=your_key_here
```

Never commit `.env` or API keys.

### 5. Start the application

```bash
python3 run_local.py
```

The Streamlit application is available at:

```text
http://127.0.0.1:8501
```

---

## Product Workflow

```text
                    Procurement Request
                            |
                            v
                Intake + Input Validation
                            |
                            v
                  Prompt Injection Guard
                            |
                            v
        +-----------------------------------------+
        |             Evidence Tools              |
        |                                         |
        |  Budget   Software   Vendor Risk   Policy|
        +-----------------------------------------+
                            |
                            v
              Deterministic Policy Engine
                            |
                            v
                 LLM Interpretation
                            |
                            v
                 Safety / Policy Merge
                            |
                            v
              Structured ProcurementDecision
                            |
                            v
              Human Review / Approval
```

The core design principle is:

```text
AI       = interpret context + recommend
CODE     = evidence gathering + policy + thresholds + safety controls
HUMAN    = sensitive approvals + exceptions
```

---

# Architecture

## Architecture A — Single Agent

The single-agent architecture performs one reasoning pass after deterministic evidence collection and policy evaluation.

```text
Request
  |
  v
Evidence Tools
  |
  v
Policy Engine
  |
  v
Single LLM Reasoning Pass
  |
  v
Safety Merge
  |
  v
ProcurementDecision
```

The model can interpret evidence and formulate the recommendation and next step.

The model cannot override deterministic controls.

Code remains authoritative for:

- approval requirements
- risk flags
- missing information
- evidence
- human review
- policy thresholds

This is the default architecture.

---

## Architecture B — Staged / Two-Agent

The staged architecture separates reasoning into an analyst and reviewer.

```text
Request
  |
  v
Evidence Tools
  |
  v
Policy Engine
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
```

The analyst produces an initial recommendation.

The reviewer receives the same evidence and analyst output and can:

- accept the recommendation
- request a more conservative recommendation
- identify additional concerns

The reviewer cannot remove deterministic policy controls.

The final safety merge remains code-owned.

---

# Tools

The system uses four evidence tools.

### `budget_tool`

Deterministically checks the requesting department's available software budget against the requested annual cost.

### `software_tool`

Checks the approved software catalog for existing or relevant alternatives.

This supports the requirement to avoid recommending a new purchase when an existing approved tool may satisfy the use case.

### `vendor_tool`

Combines internal vendor registry information with the mock vendor-risk service.

It handles:

- procurement status
- security status
- legal status
- vendor review dates
- conflicting vendor evidence
- unavailable vendor-risk service

### `policy_tool`

Exposes the procurement policy and reference date used by the deterministic policy engine.

---

# Deterministic Policy and Safety Controls

Safety-critical decisions are not delegated to the LLM.

The deterministic policy layer handles:

- budget thresholds
- approval requirements
- security-sensitive requests
- privacy/legal requirements
- vendor review expiry
- missing information
- existing software alternatives
- vendor-risk availability
- conflicting vendor information
- human-review requirements

The model cannot reduce the policy floor.

For example, if code determines that security review is required, the LLM cannot remove that requirement from the final decision.

---

# Prompt Injection Defense

Business data and vendor/request text are treated as untrusted data.

Instruction-like content inside procurement data is not treated as an instruction to the agent.

The system:

1. Detects prompt-injection-like content.
2. Keeps the content in the evidence/data context.
3. Does not execute instructions embedded inside business data.
4. Preserves deterministic policy controls.
5. Escalates when the request remains ambiguous or unsafe.

---

# Structured Output

The final response is represented using the `ProcurementDecision` contract.

The decision contains:

- recommendation
- evidence
- approvals required
- missing information
- risk flags
- next step
- human review status

Evidence is generated from tool results rather than invented by the model.

---

# Human-in-the-Loop

The copilot is advisory.

Human review is required for sensitive approvals and exceptions.

The system does not:

- approve purchases
- authorize spending
- bypass security review
- bypass procurement policy
- automatically onboard vendors
- make irreversible procurement decisions

The final action remains with the appropriate human approver.

---

# Evaluation

Both architectures are evaluated against the same public evaluation set.

Run:

```bash
python3 evals/run_public_evals.py --architecture single
```

and:

```bash
python3 evals/run_public_evals.py --architecture staged
```

Results are written to:

```text
evals/results_single.csv
evals/results_staged.csv
```

## Public Evaluation Results

### Deterministic / fallback evaluation

| Architecture | Public cases | Result |
|---|---:|---:|
| Single agent | 6 | 6/6 PASS |
| Staged / 2-agent | 6 | 6/6 PASS |

### Gemini evaluation

The same six public cases were evaluated with Gemini enabled.

| Architecture | Public cases | Result |
|---|---:|---:|
| Single agent | 6 | 6/6 PASS |
| Staged / 2-agent | 6 | 6/6 PASS |

### Gemini latency observed

Single-agent runs:

| Case | Latency |
|---|---:|
| PUB-01 | 3246 ms |
| PUB-02 | 3280 ms |
| PUB-03 | 4062 ms |
| PUB-04 | 3514 ms |
| PUB-05 | 4417 ms |
| PUB-06 | 2546 ms |

Staged runs:

| Case | Latency |
|---|---:|
| PUB-01 | 10244 ms |
| PUB-02 | 8580 ms |
| PUB-03 | 7179 ms |
| PUB-04 | 416 ms |
| PUB-05 | 426 ms |
| PUB-06 | 424 ms |

Both architectures achieved 6/6 correctness on the shared public evaluation set.

The single-agent architecture showed lower and more predictable latency on the evaluated cases while achieving the same correctness.

---

# Architecture Decision

## Ship the Single-Agent Architecture

The single-agent architecture is the final recommended architecture.

Both architectures achieved 6/6 on the same public evaluation set, so the staged architecture did not demonstrate an accuracy advantage sufficient to justify its additional orchestration.

The single-agent design provides:

- the same evaluated correctness
- fewer reasoning stages
- lower implementation complexity
- a smaller failure surface
- easier debugging
- easier observability
- lower and more predictable latency in the measured evaluation

The staged architecture remains implemented as an experimental comparison baseline.

The final system therefore follows the principle:

> Use the simplest architecture that performs as well or better while keeping safety-critical decisions deterministic.

---

# Test Suite

Run:

```bash
python3 -m pytest -q
```

Current result:

```text
15 passed
```

The test suite covers:

tests/
├── test_data_integrity.py
├── test_mock_api.py
└── test_solution.py

---

# Project Structure

```text
.
├── app.py
├── run_local.py
├── verify_setup.py
├── requirements.txt
├── .env.example
│
├── data/
│   ├── department_budgets.csv
│   ├── employees.csv
│   ├── procurement_policy.md
│   ├── purchase_history.csv
│   ├── requests.json
│   ├── software_catalog.csv
│   ├── vendor_risk.json
│   └── vendors.csv
│
├── src/
│   ├── contracts.py
│   ├── data_access.py
│   ├── decision.py
│   ├── intake.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── policy_engine.py
│   ├── prompts.py
│   ├── security.py
│   ├── solution.py
│   ├── telemetry.py
│   │
│   ├── agents/
│   │   └── single_agent.py
│   │   └── staged.py
│   │
│   └── tools/
│       ├── base.py
│       ├── budget.py
│       ├── policy.py
│       ├── software.py
│       └── vendor.py
│
├── evals/
│   ├── public_cases.json
│   ├── run_public_evals.py
│   └── README.md
│
├── mock_api/
│   └── app.py
│
├── tests/
│   ├── test_data_integrity.py
│   ├── test_mock_api.py
│   ├── test_policy_engine.py
│   ├── test_security.py
│   ├── test_single_agent.py
│   ├── test_tools.py
│   └── test_llm.py
│
└── templates/
    ├── architecture_decision.md
    ├── evaluation_results_template.csv
    └── workflow_notes.md
```

---

# Assumptions

- The supplied procurement policy is the source of truth for deterministic controls.
- The policy reference date is `2026-09-30`.
- The mock vendor-risk service represents an external vendor/security dependency.
- Vendor-risk failures are not silently interpreted as approval.
- Missing information is surfaced rather than inferred.
- LLM output is advisory and is validated before becoming part of the final decision.
- Human approval remains mandatory for sensitive procurement actions.

---

# Limitations

- The vendor-risk service is a mock dependency.
- LLM quality depends on the configured provider/model.
- Public evaluation coverage is limited to the supplied evaluation set.
- Latency depends on the external LLM provider.
- The system is a procurement recommendation prototype rather than a production procurement system.
- No real purchasing or approval action is performed.

---

# Security

Never commit secrets.

The local `.env` file is ignored by Git.

Before pushing:

```bash
git status
```

Verify that `.env` does not appear in the files staged for commit.

Use `.env.example` as the safe configuration template.

---

# Final Ship Summary

The final MVP ships the **single-agent architecture** with:

- deterministic evidence tools
- deterministic procurement policy enforcement
- prompt-injection defenses
- structured decision output
- human approval gates
- optional Gemini/OpenRouter reasoning
- staged architecture retained for evaluation
- reproducible public evaluation
- automated tests

The system prioritizes grounded evidence, deterministic controls, and human oversight over unnecessary agent complexity.

---

## Notes

- All commands use `python3` to match the local environment.
- The `.env` file must never be committed.
- Code fences, tables, and headings have been checked for valid GitHub Markdown rendering.

---

## Author

**Tanmay Mittal**
Roll No.: **24BCS10491**
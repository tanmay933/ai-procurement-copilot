# AI Procurement Request Copilot — FDE Assessment 3

An evidence-first procurement copilot for internal software/SaaS requests. The system gathers evidence through four tools, applies deterministic procurement controls, optionally uses an LLM for wording/reasoning, and keeps final approval with humans.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python verify_setup.py
cp .env.example .env
python run_local.py
```

Open `http://127.0.0.1:8501`.

The app works without an LLM key using deterministic fallback behavior. To enable model reasoning, configure `LLM_PROVIDER=gemini` with `GEMINI_API_KEY`, or `LLM_PROVIDER=openrouter` with `OPENROUTER_API_KEY`.

## Workflow

```text
Request
  ↓
Intake + prompt-injection guard
  ↓
┌────────────── evidence tools ──────────────┐
│ budget │ software │ vendor-risk │ policy │
└────────────────────────────────────────────┘
  ↓
Deterministic policy engine
  ↓
AI recommendation / staged review
  ↓
Safety merge + ProcurementDecision
  ↓
Human approval / exception handling
```

## Architecture A — Single agent

One reasoning pass is performed after the four evidence tools and deterministic policy checks. The model may phrase the recommendation and next step, but code owns approvals, risk flags, missing information, evidence and human review.

## Architecture B — Staged / 2-agent

An analyst produces a recommendation from the same evidence. A reviewer receives the evidence plus analyst output and can make the recommendation more conservative. The final deterministic merge still prevents the reviewer from removing policy controls.

## Tools

1. `budget_tool` — deterministic department budget check.
2. `software_tool` — deterministic catalog/overlap lookup.
3. `vendor_tool` — combines internal vendor registry with the mock vendor-risk API.
4. `policy_tool` — exposes the assessment policy/reference date.

## Safety and reliability

- Business/request/vendor text is treated as untrusted data.
- Prompt-injection-like instructions are detected and ignored.
- Missing values are surfaced instead of invented.
- Vendor API outages become `vendor_risk_unavailable` and trigger manual review.
- Conflicting vendor evidence is surfaced instead of silently resolved.
- Vendor review expiry uses the policy snapshot date `2026-09-30`.
- Human approval is always required; the system never purchases software or approves spend.

## Evaluation

Run both architectures on the same public set:

```bash
python evals/run_public_evals.py --architecture single
python evals/run_public_evals.py --architecture staged
python evals/compare_architectures.py
```

Results are written to `evals/results_single.csv`, `evals/results_staged.csv`, and `evals/architecture_comparison.csv`.

## Provider configuration

`.env` is ignored by git. Never commit API keys.

For Gemini:

```text
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GEMINI_API_KEY=...
```

For OpenRouter:

```text
LLM_PROVIDER=openrouter
LLM_MODEL=<provider/model>
OPENROUTER_API_KEY=...
```

## Final ship decision

The intended MVP choice is the simplest architecture that performs as well or better on the same evaluation set. The single-agent design is the default because deterministic controls and evidence grounding matter more than adding orchestration. The staged variant is retained for measured comparison.

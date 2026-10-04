# Architecture Decision Memo

**Maximum length: 500 words**

## Decision
**Ship the single-agent baseline** unless the same evaluation set shows a material quality improvement from staged review that justifies its extra latency and LLM cost.

## Evidence

Populate this table from `python evals/compare_architectures.py`.

| Metric | Single agent | Staged / 2-agent |
|---|---:|---:|
| Cases passing your quality criteria | | |
| Avg latency | | |
| Avg LLM calls | | |
| Avg tool calls | | |
| Notable policy/grounding failures | | |

## Trade-offs

The single agent has one reasoning call after deterministic evidence gathering. The staged variant adds an analyst/reviewer pass. Both architectures use the same four tools and the same deterministic policy engine, so approvals, risk flags, missing information and evidence remain code-owned.

## Risks / limitations

Validate model-specific quality, provider reliability, rate limits, cost, adversarial business-data injection, and additional hidden procurement cases before production use. Vendor-risk outages must continue to produce manual-review escalation rather than a favorable inference.

## Why this is the right MVP

The procurement workflow benefits most from reliable evidence and deterministic controls, not from additional agent count. The simpler architecture is easier to test, faster to run, and easier to audit. The staged design is retained as a comparison architecture and can be promoted only if evaluation demonstrates a meaningful quality gain.

# Industrial Operations AI POC

## Purpose

This is a public-safe, dry-lab POC for upstream oil-field decision support. Use synthetic data only. Treat all AI output as a recommendation subject to named human approval.

## Project structure

```text
.agents/skills/<skill-name>/SKILL.md  # Codex-discoverable reusable skill instructions
.agents/skills/<skill-name>/agents/  # Codex UI metadata for that skill
docs/                            # Cross-skill orchestration contract and case lifecycle
data/                           # Synthetic input artifacts only
README.md                       # Business story, architecture, and POC boundary
```

## Skill boundaries

- `asset-performance`: assess asset/well risk from evidence.
- `process-energy-optimization`: evaluate operating-envelope trade-offs.
- `field-execution`: prepare a draft field package after approval.
- `agentic-operations-orchestrator`: preserve case state, enforce handoffs and approval, and record outcomes.

## Safety and governance

- Never control equipment or change production parameters.
- Never create a production work order or dispatch field staff.
- Preserve source references, uncertainty, approval, and outcome under one `case_id`.

## Portability principle

Keep domain workflow, input/output contracts, guardrails, and evaluation criteria in Markdown skill files. A future Google ADK implementation can reuse these contracts and add provider-specific Python components for tools, agents, sessions, deployment, and observability.

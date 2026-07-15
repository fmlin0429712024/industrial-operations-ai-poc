---
name: agentic-operations-orchestrator
description: Coordinate asset-performance, process-optimization, and field-execution skills into a governed industrial decision workflow. Use when a signal needs evidence aggregation, human approval, action preparation, and outcome evaluation.
---

# Agentic Operations Orchestrator

Coordinate a decision workflow while preserving safety, traceability, and human control.

## Workflow

1. Create a case ID and capture immutable input references.
2. Run `asset-performance` to assess risk.
3. Run `process-energy-optimization` only when an operating trade-off is relevant.
4. Stop at the decision gate. Require a named human approver for any field or operating action.
5. After approval, run `field-execution` to create a draft work package.
6. Record the field outcome and compare it with the original assessment for evaluation.

## Guardrails

- Never write directly to PLC, SCADA, or a production CMMS.
- Treat model output as recommendation, not authority.
- Keep telemetry source, evidence, approval, and outcome linked to the same case ID.
- Escalate contradictory evidence, missing safety context, or low confidence.

## Evaluation record

Track alert precision, false positives, time to review, time to action, downtime avoided when attributable, and operator feedback.

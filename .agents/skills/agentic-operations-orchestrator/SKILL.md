---
name: agentic-operations-orchestrator
description: Coordinate asset-performance, process-optimization, and field-execution skills into a governed industrial decision workflow. Use when a signal needs evidence aggregation, human approval, action preparation, and outcome evaluation.
---

# Agentic Operations Orchestrator

Coordinate a decision workflow while preserving safety, traceability, and human control.

Use the project-level [`WORKFLOW.md`](../../../WORKFLOW.md) for the ESP risk-to-response handoff contract and risk-score tool interface.

## Workflow

1. Create a case ID and capture immutable input references.
2. Run `asset-performance` to assess risk, including the available ML risk-score tool when model-ready features are present.
3. Stop at the decision gate. Require a named human approver for any field action.
4. After approval, run `field-execution` to create a synthetic diagnostic ticket.
5. Record the simulated field outcome, close the ticket, and compare it with the original assessment for evaluation.

`process-energy-optimization` is not required for the narrow ESP reliability demo; retain it only when a real operating-envelope decision is in scope.

## Guardrails

- Never write directly to PLC, SCADA, or a production CMMS.
- Treat model output as recommendation, not authority.
- Keep telemetry source, evidence, approval, and outcome linked to the same case ID.
- Escalate contradictory evidence, missing safety context, or low confidence.

## Evaluation record

Track alert precision, false positives, time to review, time to action, downtime avoided when attributable, and operator feedback.

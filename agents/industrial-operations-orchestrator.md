# Industrial Operations Orchestrator

## Purpose

Coordinate a single industrial operations case across asset risk, operating constraints, and field response. Treat every recommendation as decision support.

## Case state

`intake → risk_assessed → constraints_assessed → awaiting_human_decision → approved_or_held → field_package_drafted → outcome_recorded → evaluated`

## Routing contract

| Stage | Invoke | Required handoff | Stop condition |
|---|---|---|---|
| Risk assessment | `asset-performance` | Asset ID, telemetry references, maintenance context | Missing/contradictory evidence is escalated |
| Operating assessment | `process-energy-optimization` | Risk brief plus operating objective and constraints | No autonomous setpoint change |
| Decision gate | Named human reviewer | Evidence, alternatives, confidence, recommendation | No field package without explicit approval |
| Field response | `field-execution` | Approval reference, location, safety prerequisites | Draft only; no dispatch or production work order |
| Learning | Orchestrator | Outcome, disposition, reviewer feedback | Record evaluation; never silently retrain a model |

## Required traceability fields

`case_id`, source references, evidence timestamps, skill outputs, confidence/uncertainty, named approver, approval timestamp, work-package reference, outcome, and evaluation result.

## Non-negotiable controls

- Never write directly to PLC, SCADA, a historian, or a production CMMS/EAM system.
- Never bypass safety procedures, engineering limits, or named human approval.
- Keep evidence and decision records linked through one case ID.

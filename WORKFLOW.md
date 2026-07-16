# ESP Risk-to-Response Workflow

This is the deliberately small, runnable workflow for the Industrial Operations AI POC. It demonstrates end-to-end handoffs without claiming live OT control, automated work-order creation, or autonomous field dispatch.

```text
Model-ready WELL-024 feature set
    -> risk-score service
    -> asset-performance risk brief
    -> process-impact assessment
    -> named human decision gate
    -> draft field inspection / scheduling package
    -> simulated outcome and evaluation record
```

## Operating cadence (POC assumption)

The default operating model is a **daily batch decision-support job**, not a real-time control loop.

| Time | Activity | Control boundary |
|---|---|---|
| 17:00 local field time | Lock the latest governed feature window for each active well | Fail closed when required feature data is missing or stale |
| 17:15 | Score all eligible wells and rank high-risk cases | Model only recommends review; it never changes equipment settings |
| 17:30 | Route high-risk cases to the production-engineer review queue | A named engineer must approve any draft inspection response |
| On material alarm | Optionally re-score the affected well | Same human gate and safety boundary apply |

The exact schedule is a client operating decision. The POC uses 17:00 only as a concrete, post-production-day assumption.

## Handoff contract

| Step | Owner skill | Input | Simplified POC responsibility | Output |
|---|---|---|---|---|
| 1 | Asset performance | Model-ready feature set | Call the risk-score tool and assemble evidence; state uncertainty | Risk brief and proposed next step |
| 2 | Process and energy optimization | Risk brief and operating context | Compare continued monitoring with a planned inspection window; identify production and safety constraints | Operator-review recommendation |
| 3 | Human decision gate | Both assessments | Approve, hold, or reject a draft inspection response | Named decision and timestamp |
| 4 | Field execution | Approved decision and asset context | Produce a draft inspection package and suggested scheduling constraints | Draft work package; no dispatch |
| 5 | Operations orchestrator | All case records plus outcome | Preserve traceability and record whether the signal was useful | Evaluation record |

## Risk-score tool contract

The asset-performance step calls the ML inference service:

```text
POST /risk-score
input:  model-ready well feature JSON
output: risk score, threshold, tier, evidence, review recommendation, model version
```

For the local lab, the equivalent direct tool command is:

```bash
ml/.venv/bin/python ml/src/score_case.py --input ml/data/inference/well_24_score_request.json
```

The agent records the model score as evidence. It does not treat that score as a root-cause diagnosis or an authorization to change equipment.

## POC decision logic

| Condition | POC action |
|---|---|
| Risk tier is `monitor` | Record result and continue monitoring |
| Risk tier is `high` | Prepare a risk brief and request production-engineer review |
| Engineer approves an inspection | Prepare a draft field package with required safety and production coordination |
| Engineer holds or rejects | Record rationale and monitoring plan; no field package |

## Required case record

Every handoff keeps the same `case_id` and records source references, model version, score, uncertainty, named approver, approval time, draft-package reference, and eventual outcome. This is the workflow's minimum governance contract.

## Runnable local workflow demo

`src/workflow_runner.py` is a deterministic test harness for this contract. It is not a production agent runtime. It proves that the workflow context references the **same model-ready feature pack** used by the ML scorer and that a high-risk case cannot create even a draft field package without an explicit named approval.

```bash
# High-risk WELL-024: stops at the human-decision gate.
ml/.venv/bin/python src/workflow_runner.py

# Healthy WELL-025: records monitoring only.
ml/.venv/bin/python src/workflow_runner.py \
  --case data/sample-healthy-asset-signal.json

# High-risk WELL-024: explicitly simulate an approved diagnostic inspection.
ml/.venv/bin/python src/workflow_runner.py \
  --approve-inspection --approver "Production Engineer (synthetic)"
```

In an agent-assisted demo, Codex or Claude Code reads the four `SKILL.md` files, calls the same risk-score tool, and follows this handoff contract. A future ADK or other agent runtime would replace this test harness—not the domain contracts or approval boundary.

# ESP Risk-to-Response Workflow

This is the deliberately small, runnable workflow for the Industrial Operations AI POC. It demonstrates an asset-performance decision and a governed synthetic field-ticket lifecycle. It does not claim live OT control, a real CMMS integration, autonomous field dispatch, procurement, or real equipment changes.

```text
Model-ready WELL-024 feature set
    -> risk-score service
    -> asset-performance risk brief
    -> named human decision gate
    -> synthetic diagnostic field ticket
    -> synthetic field closure and evaluation record
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

## Five-step handoff contract

| Step | Owner / persona | Simplified POC responsibility | Output |
|---|---|---|---|
| 1 | Asset-performance skill | Score the daily model-ready feature pack and assemble evidence | `monitor` case or `under_review` risk brief |
| 2 | Asset / Production Engineer | Approve, hold, or reject diagnostic inspection | Named decision and timestamp |
| 3 | Field-execution skill | After approval, create a **synthetic** diagnostic ticket | Open ticket with scope and assigned role |
| 4 | Field Engineer | Record a simulated outcome and close the synthetic ticket | Closed ticket: `esp_replaced` or `no_fault_found` |
| 5 | Orchestrator | Preserve evidence and connect verified outcome to evaluation | Closed case and evaluation record |

The separate `process-energy-optimization` skill remains a future portfolio capability. It is not a required node in this deliberately narrow ESP reliability demo.

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
| Engineer approves an inspection | Create a synthetic diagnostic field ticket; no procurement or real dispatch |
| Field Engineer closes ticket | Record `esp_replaced` or `no_fault_found` and create evaluation evidence |
| Engineer holds or rejects | Record rationale and monitoring plan; no ticket |

## Required case record

Every handoff keeps the same `case_id` and records source references, model version, score, uncertainty, named approver, approval time, draft-package reference, and eventual outcome. This is the workflow's minimum governance contract.

## Runnable local workflow demo

`src/workflow_runner.py` is a deterministic state-machine test harness for this contract. It is not a production agent runtime. It proves that the workflow context references the **same model-ready feature pack** used by the ML scorer and that a high-risk case cannot create a synthetic ticket without an explicit named approval.

```bash
# 1. High-risk WELL-024: daily batch creates an under-review case.
ml/.venv/bin/python src/workflow_runner.py start \
  --state outputs/well-024-case.json

# 2. Named human approval creates a synthetic diagnostic ticket.
ml/.venv/bin/python src/workflow_runner.py approve \
  --state outputs/well-024-case.json \
  --approver "Asset / Production Engineer (synthetic)"

# 3. Field Engineer closes the synthetic ticket; no real equipment is changed.
ml/.venv/bin/python src/workflow_runner.py close \
  --state outputs/well-024-case.json \
  --field-engineer "Field Engineer (synthetic)" \
  --outcome esp_replaced

# Healthy WELL-025: batch run closes with monitoring only; no ticket.
ml/.venv/bin/python src/workflow_runner.py start \
  --case data/sample-healthy-asset-signal.json \
  --state outputs/well-025-case.json
```

In an agent-assisted demo, Codex or Claude Code reads the four `SKILL.md` files, calls the same risk-score tool, and follows this handoff contract. A future ADK or other agent runtime would replace this test harness—not the domain contracts or approval boundary.

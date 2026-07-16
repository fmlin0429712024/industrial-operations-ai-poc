# Industrial Agentic AI POC — Operations Intelligence

**A runnable, synthetic POC for turning early ESP risk signals into a governed field-service response.**

## 30-second overview

An upstream operator scores each active ESP-lifted oil well at the end of the production day. A high-risk signal does **not** control equipment or order a replacement. It gives an Asset / Production Engineer evidence to review. Only an approved inspection creates a synthetic field ticket; the Field Engineer's outcome closes the case and becomes evaluation evidence.

```mermaid
flowchart TD
    A["1. Daily feature pack<br/>Governed OT + maintenance context"] --> B["2. Asset performance score<br/>ML risk score + evidence"]
    B --> C{"3. Asset / Production Engineer<br/>human decision"}
    C -->|"Monitor / hold"| D["Close monitoring case<br/>No ticket"]
    C -->|"Approve inspection"| E["4. Synthetic field-service ticket<br/>Diagnostic scope"]
    E --> F["5. Field Engineer closes ticket<br/>Outcome + evaluation record"]

    classDef model fill:#dbeafe,stroke:#2563eb,color:#111827;
    classDef gate fill:#fef3c7,stroke:#d97706,color:#111827;
    classDef ticket fill:#dcfce7,stroke:#16a34a,color:#111827;
    class A,B model;
    class C gate;
    class E,F ticket;
```

## Two test scenarios

| Synthetic well | What the model finds | Workflow result |
|---|---|---|
| `WELL-025` | Stable operating pattern: `monitor` | Monitoring case closes; no ticket |
| `WELL-024` | High ESP-related production-loss risk | Engineer approval → synthetic diagnostic ticket → simulated field outcome → evaluation record |

## What is implemented

| Component | What it demonstrates | Detail |
|---|---|---|
| ESP risk model | Synthetic training, chronological train/validation/test split, local inference, and model evidence | [ML Lab](ml/README.md) |
| Governed workflow | Skills, state transitions, human approval gate, synthetic ticket lifecycle, and outcome record | [Workflow implementation](WORKFLOW.md) |
| Runnable demo | Replays the high-risk and healthy scenarios locally | [Workflow runner](src/workflow_runner.py) |

## POC boundary

All data, scores, tickets, approvals, and field outcomes are synthetic. This POC does not connect to live OT equipment or a CMMS, dispatch technicians, purchase equipment, change operating settings, or make safety decisions.

The broader upstream trial scope and assumptions are in [`trial-scope/`](trial-scope/README.md). Future portfolio capabilities—such as production optimization, work-order prioritization, energy optimization, and emissions anomaly detection—are intentionally outside this narrow runnable workflow.

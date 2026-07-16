# Industrial Agentic AI POC — Operations Intelligence

**OT/IT data context, asset performance, and governed field-service response.**

This runnable in-silico POC shows how a single industrial signal becomes an evidence-backed, human-approved field response. It uses static synthetic data only. It does **not** connect to live equipment, control equipment, change process setpoints, dispatch technicians, create production work orders, or make safety decisions.

## 1. The operational question

In upstream production, an ESP-related failure can turn a gradual change in well performance into unplanned production deferral and an expensive field intervention. Production teams need an earlier, evidence-backed way to decide which wells require attention, what evidence supports the concern, and whether an inspection should be approved.

This POC focuses on that decision. It combines production telemetry, ESP operating signals, maintenance history, and operating constraints into a well-risk assessment. A supervised ML model can rank the likelihood of near-term ESP-related failure or material production loss; the surrounding workflow presents the evidence to an Asset / Production Engineer, preserves a human approval gate, and creates a synthetic diagnostic field ticket only when approved.

The intended outcome is not autonomous control. It is earlier prioritization of high-risk wells, fewer avoidable production-deferral days, and a measurable basis for comparing the cost of intervention with the cost of inaction.

The project also provides a foundation for related operational use cases, including production optimization, work-order prioritization, energy optimization, and emissions anomaly detection. The supporting trial-scoping materials are maintained in [`trial-scope/`](trial-scope/README.md).

## 2. The story: one oil-well event, one operational loop

An upstream oil field monitors an oil well using an electric submersible pump (ESP), a common artificial-lift system. The well's oil rate is declining while motor-current and intake-pressure signals become abnormal. The team needs to protect safe, stable production without ordering an unjustified intervention or workover.

1. **Asset performance** scores the latest model-ready well data and creates a risk brief rather than claiming a root cause.
2. **Human decision gate** lets an Asset / Production Engineer approve, hold, or reject a diagnostic inspection.
3. **Field service** creates a synthetic diagnostic ticket only after approval.
4. **Field Engineer** records a synthetic outcome and closes the ticket.
5. **Evaluation** records the outcome so later assessments can be compared with evidence.

```mermaid
flowchart TD
    A["OT/IT context<br/>Telemetry · alarms · historian<br/>Maintenance · production context"] --> F0["Governed feature job<br/>Daily 17:00 local POC cadence"]
    F0 --> B["1. Asset Performance skill<br/>Risk brief + evidence"]
    B --> D{"2. Human decision gate"}
    D -->|"Approve"| E["3. Field-service skill<br/>Synthetic diagnostic ticket"]
    D -->|"Hold / reject"| F["Closed monitoring case"]
    E --> G["4. Field Engineer<br/>Synthetic outcome + close ticket"]
    F --> H["5. Evaluation record"]
    G --> H
    H --> I["Orchestrator<br/>traceability + learning"]
    I --> B

    classDef skill fill:#dbeafe,stroke:#2563eb,color:#111827;
    classDef gate fill:#fef3c7,stroke:#d97706,color:#111827;
    classDef control fill:#e5e7eb,stroke:#4b5563,color:#111827;
    class B,E skill;
    class D gate;
    class I,H control;
```

## 3. Skills portfolio

| Business domain | Skill | Simple responsibility | Never does |
|---|---|---|---|
| Asset performance management | [`asset-performance`](.agents/skills/asset-performance/SKILL.md) | Prioritize an emerging asset risk and assemble evidence | Claims a proven root cause or controls equipment |
| Production operations / process management | [`process-energy-optimization`](.agents/skills/process-energy-optimization/SKILL.md) | Future capability; not required for the narrow ESP reliability demo | Changes an operating parameter |
| Field service management | [`field-execution`](.agents/skills/field-execution/SKILL.md) | Create and close a synthetic diagnostic ticket after approval | Dispatches people, purchases equipment, or creates production work orders |
| Cross-domain agentic operations | [`agentic-operations-orchestrator`](.agents/skills/agentic-operations-orchestrator/SKILL.md) | Preserves case state, routes skill handoffs, enforces human approval, and records outcomes | Overrides safety or human authority |

The project-level guide is [`AGENTS.md`](AGENTS.md). The sole POC workflow contract is [`WORKFLOW.md`](WORKFLOW.md). Each reusable skill follows the formal Codex structure: `.agents/skills/<skill-name>/SKILL.md` plus `agents/openai.yaml` metadata.

## 4. POC architecture boundary

```text
PLC / sensors → SCADA, gateway, MQTT or OPC UA → historian / data platform
                                                   ↓
                           this POC: skills + orchestrator + human decision gate
                                                   ↓
                                  CMMS/EAM or field-service system (future connector)
```

The OT layer remains the trusted source for operational signals. Existing enterprise systems remain systems of record. This POC is the governed **decision-support and workflow layer** between them.

## 5. Included synthetic artifact

- [`data/sample-asset-signal.json`](data/sample-asset-signal.json) — high-risk synthetic workflow context; it references the matching ML feature pack rather than duplicating it.
- [`data/sample-healthy-asset-signal.json`](data/sample-healthy-asset-signal.json) — healthy synthetic workflow context for the monitor-only path.
- [`ml/data/inference/`](ml/data/inference/) — the two model-ready feature packs used by the ML scorer. The full training/validation/test data contract is in the [ML Lab](ml/README.md).

## 6. Runnable lab components

- [`ESP Risk Modeling Lab`](ml/README.md) — the complete supervised-ML component: decision, synthetic data, chronological train/validation/test split, model comparison, held-out results, and future FastAPI boundary.
- [`ESP Risk-to-Response Workflow`](WORKFLOW.md) — how a Codex or Claude Code agent uses the skills to call the risk model and move an approved case through operations and field execution.
- [`src/workflow_runner.py`](src/workflow_runner.py) — runnable, deterministic POC test harness for the same workflow contract; it demonstrates high-risk, monitor-only, and explicit-approval paths.

## 7. What would make it production-ready

Real connectors to OT/historian and CMMS systems, identity and access controls, audit storage, evaluation datasets, observability, model/version governance, and approved safety operating procedures.

## 8. Trial-scoping deliverables

The customer-facing upstream ESP reliability trial scope, assumptions, and final submission artifacts are maintained in [`trial-scope/`](trial-scope/README.md).

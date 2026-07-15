# Agentic AI Solution POC — Industrial Operations Intelligence

**OT/IT data context, asset performance, process and energy decision support, and field execution.**

This dry-lab POC shows how a single industrial signal becomes an evidence-backed, human-approved field response. It uses synthetic data only. It does **not** control equipment, change process setpoints, dispatch technicians, create production work orders, or make safety decisions.

## 1. The story: one compressor event, one operational loop

A high-criticality gas compressor shows rising vibration and bearing temperature. The site needs to protect production without taking an unjustified maintenance action.

1. **Asset performance** reviews telemetry, maintenance history, and known failure modes; it creates a risk brief rather than claiming a root cause.
2. **Process and energy operations** checks operating constraints and the production trade-off; it does not alter a setpoint.
3. **Human decision gate** reviews the evidence and explicitly approves, holds, or rejects the recommended response.
4. **Field execution** creates a draft inspection or maintenance package only after approval.
5. **Evaluation** records the outcome so later assessments can be compared with evidence.

```mermaid
flowchart TD
    A["OT/IT context<br/>Telemetry · alarms · historian<br/>Maintenance · production context"] --> B["Asset Performance skill<br/>Risk brief + evidence"]
    B --> C["Process & Energy skill<br/>Constraints + operating trade-offs"]
    C --> D{"Human decision gate"}
    D -->|"Approve"| E["Field Execution skill<br/>Draft work package"]
    D -->|"Hold / reject"| F["Case record + monitoring plan"]
    E --> G["Field outcome<br/>inspection / maintenance result"]
    F --> H["Evaluation record"]
    G --> H
    H --> I["Agentic Operations Orchestrator<br/>traceability + learning"]
    I --> B

    classDef skill fill:#dbeafe,stroke:#2563eb,color:#111827;
    classDef gate fill:#fef3c7,stroke:#d97706,color:#111827;
    classDef control fill:#e5e7eb,stroke:#4b5563,color:#111827;
    class B,C,E skill;
    class D gate;
    class I,H control;
```

## 2. Skills portfolio

| Business domain | Skill | Simple responsibility | Never does |
|---|---|---|---|
| Asset performance management | [`asset-performance`](skills/asset-performance/SKILL.md) | Prioritize an emerging asset risk and assemble evidence | Claims a proven root cause or controls equipment |
| Operations / process management | [`process-energy-optimization`](skills/process-energy-optimization/SKILL.md) | Compare safe process, throughput, energy, and emissions trade-offs | Changes a process setpoint |
| Field service management | [`field-execution`](skills/field-execution/SKILL.md) | Draft a field-ready inspection or maintenance package after approval | Dispatches people or creates production work orders |
| Cross-domain agentic operations | [`agentic-operations-orchestrator`](skills/agentic-operations-orchestrator/SKILL.md) | Preserves case state, routes skill handoffs, enforces human approval, and records outcomes | Overrides safety or human authority |

The top-level orchestration contract is in [`agents/industrial-operations-orchestrator.md`](agents/industrial-operations-orchestrator.md). Each reusable skill follows the formal Codex structure: `skills/<skill-name>/SKILL.md` plus `agents/openai.yaml` metadata.

## 3. POC architecture boundary

```text
PLC / sensors → SCADA, gateway, MQTT or OPC UA → historian / data platform
                                                   ↓
                           this POC: skills + orchestrator + human decision gate
                                                   ↓
                                  CMMS/EAM or field-service system (future connector)
```

The OT layer remains the trusted source for operational signals. Existing enterprise systems remain systems of record. This POC is the governed **decision-support and workflow layer** between them.

## 4. Included synthetic artifact

- [`data/sample-asset-signal.json`](data/sample-asset-signal.json) — one synthetic gas-compressor case with telemetry, maintenance context, and operating constraints.

## 5. What would make it production-ready

Real connectors to OT/historian and CMMS systems, identity and access controls, audit storage, evaluation datasets, observability, model/version governance, and approved safety operating procedures.

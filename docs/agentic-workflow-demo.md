# Agentic Workflow Demo

## Purpose

Demonstrate how an existing coding-agent runtime, such as Codex or Claude Code, can use the project's Markdown skills to orchestrate an evidence-backed operational case. The agent does not replace engineering authority; it coordinates information and prepares a traceable recommendation.

## Runtime pattern

```text
Synthetic well case
    -> ML risk-score tool
    -> asset-performance skill
    -> process-energy-optimization skill
    -> named human decision
    -> field-execution skill
    -> case record and outcome
```

`SKILL.md` files provide the domain instructions, contracts, guardrails, and handoffs. The coding agent reads those instructions and invokes the appropriate tool or next skill. In a future deployed application, the same specifications can be reused with an agent runtime and service adapters.

## Business value of each skill

| Skill | Value delivered | Required boundary |
|---|---|---|
| Asset performance | Turns telemetry and model risk into an evidence-backed risk brief | Does not claim a root cause or control equipment |
| Process and energy optimization | Frames production, energy, and intervention trade-offs for the current operating envelope | Does not alter a setpoint |
| Human decision gate | Records the accountable approval, hold, or rejection decision | Cannot be bypassed |
| Field execution | Produces a draft inspection or diagnostic package after approval | Does not dispatch personnel or create a production work order |
| Operations orchestrator | Preserves state, sources, handoffs, and outcomes under one case ID | Does not override safety or human authority |

## Demo contract

The runnable demo will accept a static synthetic well case and produce a single structured case record containing:

- model version, score, threshold, and feature evidence;
- source-data references and timestamps;
- skill outputs and uncertainty statements;
- named human decision and decision timestamp;
- draft field package when approved; and
- simulated outcome and evaluation fields.

## LLM role

The LLM/agent layer can summarize maintenance notes, retrieve the relevant operating procedure, explain the model evidence in operational language, and assemble the review package. It is not the risk model and it cannot autonomously approve an intervention.


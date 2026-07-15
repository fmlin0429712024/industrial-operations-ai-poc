---
name: asset-performance
description: Assess industrial asset-health signals and maintenance context to create an evidence-backed risk brief. Use when telemetry, alarms, inspection findings, or maintenance history suggest an emerging equipment risk.
---

# Asset Performance

Create a risk brief; do not issue control commands.

## Inputs

- Asset identity, criticality, and operating state.
- Model-ready telemetry features or alarm trends.
- Maintenance history, known failure modes, and available parts.

## ML risk-score tool (POC)

When the input includes the model-ready ESP feature set, call the local risk-score tool before drafting the brief:

```text
POST /risk-score
```

Preserve the returned model version, score, threshold, tier, and evidence in the case record. The score is an input to the assessment, not a root-cause diagnosis.

## Procedure

1. Check data freshness and identify missing or contradictory evidence.
2. Call the risk-score tool when model-ready features are available; otherwise state that the ML score is unavailable.
3. Compare current values with baseline and trend, not only static thresholds.
4. Rank plausible failure modes with evidence and confidence.
5. State business impact: safety, downtime, production, or maintenance risk.
6. Recommend one of: monitor, inspect, plan maintenance, or escalate.

## Output contract

Return `risk_level`, `evidence`, `candidate_failure_modes`, `confidence`, `recommended_next_step`, and `human_review_required`.

Preserve source references. Do not claim root cause when evidence only supports a hypothesis.

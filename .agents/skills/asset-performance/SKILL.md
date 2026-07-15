---
name: asset-performance
description: Assess industrial asset-health signals and maintenance context to create an evidence-backed risk brief. Use when telemetry, alarms, inspection findings, or maintenance history suggest an emerging equipment risk.
---

# Asset Performance

Create a risk brief; do not issue control commands.

## Inputs

- Asset identity, criticality, and operating state.
- Telemetry or alarm trends.
- Maintenance history, known failure modes, and available parts.

## Procedure

1. Check data freshness and identify missing or contradictory evidence.
2. Compare current values with baseline and trend, not only static thresholds.
3. Rank plausible failure modes with evidence and confidence.
4. State business impact: safety, downtime, production, or maintenance risk.
5. Recommend one of: monitor, inspect, plan maintenance, or escalate.

## Output contract

Return `risk_level`, `evidence`, `candidate_failure_modes`, `confidence`, `recommended_next_step`, and `human_review_required`.

Preserve source references. Do not claim root cause when evidence only supports a hypothesis.

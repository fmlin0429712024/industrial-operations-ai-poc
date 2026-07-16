---
name: operational-feature-engineering
description: Transform industrial telemetry, alarms, production history, and maintenance events into governed daily model-ready features. Use when an OT/IT reliability workflow needs a traceable feature record for ML training or inference.
---

# Operational Feature Engineering

Create a daily, well-level feature record. Preserve source references and time windows; do not invent a measurement or silently repair a missing value.

## Inputs

- Time-stamped OT telemetry: motor current, intake pressure, oil rate, and production context.
- Alarm and maintenance events, linked to the same `well_id`.
- Unit, freshness, and data-quality metadata.

## Procedure

1. Keep the well identifier, observation date, units, and source timestamps.
2. Reject or flag missing, stale, contradictory, or out-of-range inputs.
3. Calculate explicit rolling features: 7-day motor-current variability, 30-day oil-rate decline, 30-day intake-pressure decline, and 30-day alarm count.
4. Add stable maintenance context such as days since the last verified intervention.
5. Emit one versioned daily feature record per well with the calculation windows and source references.

## Output contract

Return `well_id`, `observation_date`, feature values, source-window references, quality status, and feature-schema version. The same contract serves offline training and online inference; only training records include the later known outcome label.

## Guardrails

- Do not pass raw point-in-time telemetry directly to the model.
- Do not mix wells, timestamps, units, or operating states.
- Keep the transformation deterministic and independently testable.

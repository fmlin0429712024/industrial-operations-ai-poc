# ESP Risk Model

## Purpose

Provide an evidence-backed risk score for an ESP-lifted oil well. The model answers one narrow operational question:

> Given information available at an observation date, is this well at elevated risk of an ESP-related intervention or material production-loss event during the next 30 days?

This is a synthetic, static-data lab. It is not a live control model and does not diagnose a proven root cause.

## Data contract

The training dataset will contain one row per well and observation date. Candidate features include:

- oil-rate level and decline over recent windows;
- ESP motor-current level, variability, and change from baseline;
- pump-intake pressure level and trend;
- alarm frequency and quality flags;
- time since intervention and recent maintenance history;
- well and ESP configuration metadata; and
- operating-context indicators.

The binary label is `risk_event_next_30d`: a documented ESP-related intervention or material production-loss event within the next 30 days. The exact synthetic label-generation logic will be published with the dataset.

## Modeling approach

Start with an interpretable baseline and compare it with a non-linear tabular model:

| Model | Role |
|---|---|
| Rule baseline | Transparent benchmark based on engineered operating thresholds; not a root-cause diagnostic |
| Logistic regression | Simple, explainable supervised-learning baseline |
| Gradient-boosted trees | Candidate primary model for non-linear interactions across telemetry and maintenance signals |

The selected model produces a calibrated risk score and a ranked well list. It must return feature evidence suitable for an engineer review; it must not return an automatic intervention command.

## Evaluation design

The data split must respect time and well identity. Training uses earlier periods; validation selects thresholds and model settings; the final test period is held out. Where possible, test wells are separated from training wells to check generalization beyond a memorized well history.

Primary measures:

- precision and recall at the field-review capacity (for example, the top 10 highest-risk wells);
- false-alert rate;
- median warning lead time before a labeled event; and
- calibration of predicted risk against observed event frequency.

Model metrics are calculated programmatically. An LLM may explain evidence in the resulting case package, but it does not judge model correctness or replace quantitative evaluation.

## Runnable-lab evidence

Once implemented, this page will link to:

- synthetic training and holdout datasets;
- a reproducible training command;
- a serialized model or deterministic training artifact;
- evaluation metrics and plots; and
- one sample risk-score response consumed by the agentic workflow.


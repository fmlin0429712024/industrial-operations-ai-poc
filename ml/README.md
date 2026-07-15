# ESP Risk Modeling Lab

**A small, runnable synthetic-data ML lab for prioritizing ESP-lifted oil wells for engineering review.** It demonstrates a complete predictive-maintenance lifecycle; it does not represent real-field performance or control equipment.

## The decision

At each observation date, the model answers:

> Which wells have elevated risk of an ESP-related intervention or material production-loss event in the next 30 days?

It returns a ranked **risk score** and supporting signals. It does not diagnose root cause or direct an intervention.

## Operational meaning: raw IoT is not yet model input

An ESP is a downhole electric pump that helps lift produced fluids from an oil well. The operational question is whether its recent performance pattern warrants engineering attention before an avoidable production-loss event.

The model does **not** score each raw sensor message independently. In a real field, a historian receives frequent motor-current, intake-pressure, and production measurements. A feature job summarizes the most recent windows before scoring:

```text
Raw OT telemetry (for example, every 1-5 minutes)
    -> historian / time-series store
    -> rolling features: 7-day variability, 30-day decline, alarm count
    -> daily or event-triggered risk score
    -> production-engineer review when risk is high
```

The five most visible risk signals in this POC are oil-rate decline, motor-current variability, intake-pressure decline, alarm count, and time since the last intervention. Current levels, water cut, and well age provide additional operating context. The static JSON request used by this lab already contains those calculated features; it represents the latest available feature window, not one instant of raw telemetry.

For this maintenance use case, **daily scoring** is a sensible initial design. An alarm or large signal change can also trigger an on-demand score. Real-time sub-second inference is unnecessary unless the business decision itself requires immediate equipment protection.

## Two data lifecycles, one model

| | Training data | Inference data |
|---|---|---|
| **Purpose** | Teach the model historical patterns that preceded known outcomes | Score one active well using its latest operating pattern |
| **Scope in this POC** | 120 comparable wells × 20 monthly observations | One well, represented by its latest 7-day and 30-day feature windows |
| **Contents** | Features **plus** known 30-day outcome label | The same features, but the future outcome is not yet known |
| **When used** | Offline, periodically when verified new outcomes are available | Daily or when a material alarm/event triggers a review |
| **Output** | Versioned model artifact and evaluation evidence | Risk score, evidence, and engineer-review recommendation |

This distinction is fundamental: training asks, “what patterns preceded past events?” Inference asks, “does the current well resemble those patterns?”

## 1. Training pipeline

Training happens **offline**. It learns from a population of historical wells and produces a reusable model artifact.

```text
Synthetic well history
    -> generate_data.py
    -> chronological train / validation / test split
    -> train_model.py: compare candidate models
    -> validation selects model + threshold
    -> held-out test evaluates once
    -> models/esp_risk_model.joblib + reports/
```

## Training data

The lab trains on 120 synthetic ESP-lifted wells observed monthly for 20 months: **2,400 historical rows**. The end-to-end workflow still demonstrates one well case; the ML model needs the wider well population to learn a generalizable pattern. A real implementation would normally use 12-24 months of governed historical data, with verified maintenance and production-loss outcomes.

| Data group | Included signals |
|---|---|
| Production | Oil rate, 30-day decline, water cut |
| ESP telemetry | Motor current, motor-current variability, intake pressure, pressure decline |
| Operations | Alarm count, days since intervention, well age |
| Outcome label | `risk_event_next_30d` |

The synthetic label is intentionally transparent: declining oil rate, unstable current, falling intake pressure, repeated alarms, and long time since intervention increase risk, with controlled noise. No data represents a real field or a production physics model.

## Training, validation, and test

The chronological split prevents future leakage: months 1-14 train, 15-17 validate, and 18-20 remain untouched for test.

1. Rule baseline - transparent operating thresholds.
2. Logistic regression - interpretable supervised-learning benchmark.
3. Gradient-boosted trees - non-linear tabular candidate.

The validation set selected **logistic regression**. The held-out test result is below.

| Metric | Result |
|---|---:|
| ROC-AUC | 0.765 |
| Average precision | 0.461 |
| Precision among top 10 wells each period | 0.500 |
| False-alert rate at chosen threshold | 0.114 |

These results validate the synthetic lab pipeline only. A real trial would replace the generator with governed historical data and re-estimate every measure.

Run the training pipeline locally:

```bash
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
ml/.venv/bin/python ml/src/generate_data.py
LOKY_MAX_CPU_COUNT=4 ml/.venv/bin/python ml/src/train_model.py
```

The command generates the model, risk scores, validation comparison, metrics, and calibration table. Small human-readable reports and the safe synthetic model artifact are versioned for review; raw generated history and the local virtual environment are excluded from Git.

## 2. Inference pipeline

Inference happens **per well case**. It does not retrain the model.

```text
Current well JSON / future OT feature pack
    -> FastAPI POST /risk-score
    -> score_payload()
    -> load esp_risk_model.joblib
    -> predict_proba()
    -> risk score + evidence + engineer-review recommendation
    -> future agent tool call / skills orchestration
```

## Score one well

`score_case.py` is the model tool that a workflow agent will call. It scores the static `WELL-024` request and returns a risk tier, deterministic signal evidence, and a review recommendation.

```bash
ml/.venv/bin/python ml/src/score_case.py
```

The optional FastAPI adapter exposes the same scoring function without duplicating model logic:

```bash
cd ml
.venv/bin/uvicorn api.app:app --reload
# POST /risk-score using data/well_24_score_request.json
```

## See the model react to two cases

The two static requests below are intentionally simple teaching examples, not real well records:

- `data/well_025_healthy_score_request.json` - stable production, low signal variability, no alarms.
- `data/well_24_score_request.json` - declining production, unstable current, pressure decline, alarms, and a long time since intervention.

Run both through the same trained model:

```bash
ml/.venv/bin/python ml/src/demo_inference.py
```

## Structure and next boundary

```text
ml/
├── src/generate_data.py  # deterministic synthetic history
├── src/train_model.py    # train, select, and evaluate models
├── src/score_case.py     # stable risk-score tool for an agent or API
├── models/               # safe synthetic model artifact + model card
├── reports/              # versioned score and evaluation evidence
└── api/app.py            # thin FastAPI adapter around the same tool
```

The agentic workflow will call `score_case`; it will not duplicate model logic.

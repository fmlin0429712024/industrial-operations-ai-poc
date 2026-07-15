# ESP Risk Modeling Lab

**A small, runnable synthetic-data ML lab for prioritizing ESP-lifted oil wells for engineering review.** It demonstrates a complete predictive-maintenance lifecycle; it does not represent real-field performance or control equipment.

## The decision

At each observation date, the model answers:

> Which wells have elevated risk of an ESP-related intervention or material production-loss event in the next 30 days?

It returns a ranked **risk score** and supporting signals. It does not diagnose root cause or direct an intervention.

## Data

The lab trains on 120 synthetic ESP-lifted wells observed monthly for 20 months: **2,400 historical rows**. The end-to-end workflow still demonstrates one well case; the ML model needs the wider well population to learn a generalizable pattern.

| Data group | Included signals |
|---|---|
| Production | Oil rate, 30-day decline, water cut |
| ESP telemetry | Motor current, motor-current variability, intake pressure, pressure decline |
| Operations | Alarm count, days since intervention, well age |
| Outcome label | `risk_event_next_30d` |

The synthetic label is intentionally transparent: declining oil rate, unstable current, falling intake pressure, repeated alarms, and long time since intervention increase risk, with controlled noise. No data represents a real field or a production physics model.

## Modeling and evaluation

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

## Run locally

```bash
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
ml/.venv/bin/python ml/src/generate_data.py
LOKY_MAX_CPU_COUNT=4 ml/.venv/bin/python ml/src/train_model.py
```

The command generates the model, risk scores, validation comparison, metrics, and calibration table. Small human-readable reports are versioned for review; raw generated history, model artifacts, and the local virtual environment are excluded from Git.

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

## Structure and next boundary

```text
ml/
├── src/generate_data.py  # deterministic synthetic history
├── src/train_model.py    # train, select, and evaluate models
├── src/score_case.py     # stable risk-score tool for an agent or API
├── reports/              # versioned score and evaluation evidence
└── api/app.py            # thin FastAPI adapter around the same tool
```

The agentic workflow will call `score_case`; it will not duplicate model logic.

# ESP Risk Modeling Lab

This folder contains the runnable, traditional-ML component of the Industrial Operations AI POC. It will train a synthetic-data model that ranks ESP-lifted wells by their near-term operational risk. It is deliberately small, reproducible, and explainable.

## The decision

At each observation date, the model answers:

> Which wells should a production engineer review first because they have elevated risk of an ESP-related intervention or material production-loss event in the next 30 days?

The model returns a **risk score**, not a root-cause diagnosis and not an instruction to control equipment.

## Dataset design

One row represents one well at one monthly observation date. The first runnable version uses 120 synthetic ESP-lifted wells observed over 20 months: 2,400 historical observation rows.

| Group | Fields | Why it matters |
|---|---|---|
| Identity and time | `well_id`, `observation_date`, `field_id` | Preserves asset and temporal context; never used as a predictive shortcut |
| Production | `oil_rate_bpd`, `oil_rate_decline_30d_pct`, `water_cut_pct` | Captures declining production performance |
| ESP telemetry | `motor_current_a`, `motor_current_cv_7d_pct`, `pump_intake_pressure_psi`, `intake_pressure_decline_30d_pct` | Captures electrical and hydraulic stress signals |
| Operational context | `alarm_count_30d`, `days_since_last_intervention`, `well_age_years` | Adds maintenance and operating context |
| Label | `risk_event_next_30d` | `1` when the synthetic scenario records an ESP-related intervention or material production-loss event in the next 30 days; otherwise `0` |

## Synthetic-data rule

The synthetic generator creates stable wells, emerging-risk wells, and occasional noisy observations. The label is generated from a transparent latent-risk formula with controlled random variation:

- faster oil-rate decline increases risk;
- unstable motor current increases risk;
- declining pump-intake pressure increases risk;
- repeated alarms increase risk; and
- long time since intervention increases risk.

This makes the learning task realistic enough to demonstrate signal, while intentionally avoiding any claim that the values represent a real field or a production physics model.

## Experiment design

| Split | Months | Purpose |
|---|---:|---|
| Training | 1-14 | Fit model parameters |
| Validation | 15-17 | Choose model settings and operating threshold |
| Test | 18-20 | One final, untouched estimate of performance |

The split is chronological to prevent future information from leaking into training. `well_id`, `observation_date`, and the label are excluded from model features.

## Model progression

1. **Rule baseline** — transparent alert logic based on a small set of operating signals.
2. **Logistic regression** — interpretable supervised-learning benchmark.
3. **Gradient-boosted trees** — candidate primary model for non-linear tabular interactions.

The lab will choose a model only if it improves the held-out test metrics over the baseline while preserving an interpretable risk explanation.

## Success measures

- Precision and recall for the top 10 highest-risk wells reviewed each period.
- False-alert rate.
- Median lead time before a synthetic risk event.
- Calibration: whether predicted risk corresponds to observed event frequency.

## First reproducible run

The initial run generated 2,400 synthetic monthly observations from 120 wells. The chronological split produced 1,680 training rows, 360 validation rows, and 360 untouched test rows. The overall synthetic event rate was 17.7%.

The logistic-regression model was selected using **validation** average precision (0.365), ahead of gradient-boosted trees (0.311) and the rule baseline (0.283). On the final untouched test period, the selected model produced:

| Held-out test measure | Result |
|---|---:|
| ROC-AUC | 0.765 |
| Average precision | 0.461 |
| Precision at operating threshold | 0.431 |
| Recall at operating threshold | 0.484 |
| Precision among top 10 wells per period | 0.500 |
| False-alert rate at operating threshold | 0.114 |

These results validate the **synthetic lab pipeline only**. They are not claims about real-field performance. A client trial would replace the generator with governed historical data and re-estimate all metrics.

## Run it locally

```bash
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
ml/.venv/bin/python ml/src/generate_data.py
LOKY_MAX_CPU_COUNT=4 ml/.venv/bin/python ml/src/train_model.py
```

The generated model, risk scores, model comparison, metrics, and calibration table are written below `ml/models/` and `ml/reports/`. Those generated artifacts are ignored by Git so each run remains reproducible from source.

## Planned runnable components

```text
ml/
├── data/                 # generated synthetic train/validation/test data
├── models/               # serialized model artifact (generated, not hand-edited)
├── reports/              # metrics, calibration table, and risk scores (generated)
├── src/
│   ├── generate_data.py  # deterministic synthetic history generator
│   ├── train_model.py    # baseline and ML training/evaluation
│   └── score_case.py     # risk-score function used by the agentic workflow
└── api/                  # later FastAPI adapter around the same scoring function
```

The first milestone is a command-line training and scoring demo. The FastAPI layer comes after the same scoring function is validated locally; it will add a service boundary, not new model logic.

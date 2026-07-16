# ML Data Sets

This folder makes the ML data lifecycle explicit. All files are synthetic and public-safe.

| File or folder | Rows | Has known future label? | Purpose |
|---|---:|---|---|
| `training.csv` | 1,680 | Yes | Fit candidate model parameters |
| `validation.csv` | 360 | Yes | Select model and operating threshold; never fit the final test result |
| `test.csv` | 360 | Yes | Final benchmark only; never used to choose the model or threshold |
| `inference/` | One active well per JSON request | No | Score the latest feature window for operational review |

`test.csv` is for **evaluating** a trained model, not for live business inference. An inference request does not contain `risk_event_next_30d`, because the next 30 days have not happened yet.

The generator also writes a combined audit copy under `.generated/`. It is ignored by Git; the three explicit split files above are the reviewable POC datasets.

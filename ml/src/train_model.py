"""Train and evaluate a reproducible ESP risk-ranking model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TRAIN_PATH = DATA_DIR / "training.csv"
VALIDATION_PATH = DATA_DIR / "validation.csv"
TEST_PATH = DATA_DIR / "test.csv"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
TARGET = "risk_event_next_30d"
FEATURES = [
    "oil_rate_bpd",
    "oil_rate_decline_30d_pct",
    "water_cut_pct",
    "motor_current_a",
    "motor_current_cv_7d_pct",
    "pump_intake_pressure_psi",
    "intake_pressure_decline_30d_pct",
    "alarm_count_30d",
    "days_since_last_intervention",
    "well_age_years",
]


def choose_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    """Choose threshold from validation only, maximizing F1."""
    candidates = np.linspace(0.05, 0.90, 86)
    scored = [
        (threshold, f1_score(y_true, probabilities >= threshold, zero_division=0))
        for threshold in candidates
    ]
    return float(max(scored, key=lambda item: item[1])[0])


def rule_score(frame: pd.DataFrame) -> np.ndarray:
    """A transparent baseline, deliberately simple enough for field review."""
    triggered_signals = (
        (frame["oil_rate_decline_30d_pct"] >= 12).astype(int)
        + (frame["motor_current_cv_7d_pct"] >= 8).astype(int)
        + (frame["intake_pressure_decline_30d_pct"] >= 10).astype(int)
        + (frame["alarm_count_30d"] >= 3).astype(int)
        + (frame["days_since_last_intervention"] >= 300).astype(int)
    )
    return (triggered_signals / 5).to_numpy(dtype=float)


def top_k_metrics(frame: pd.DataFrame, probabilities: np.ndarray, k: int = 10) -> dict[str, float]:
    scored = frame[["observation_date", TARGET]].copy()
    scored["probability"] = probabilities
    selected = (
        scored.sort_values(["observation_date", "probability"], ascending=[True, False])
        .groupby("observation_date", group_keys=False)
        .head(k)
    )
    all_events = int(scored[TARGET].sum())
    selected_events = int(selected[TARGET].sum())
    return {
        f"precision_at_{k}": round(float(selected[TARGET].mean()), 4),
        f"recall_at_{k}": round(selected_events / all_events, 4) if all_events else 0.0,
        f"alerts_reviewed_per_period": k,
    }


def evaluate(
    name: str,
    frame: pd.DataFrame,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, float | str]:
    y_true = frame[TARGET]
    predictions = probabilities >= threshold
    metrics: dict[str, float | str] = {
        "model": name,
        "threshold": round(float(threshold), 3),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "average_precision": round(float(average_precision_score(y_true, probabilities)), 4),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "false_alert_rate": round(float(((predictions == 1) & (y_true == 0)).mean()), 4),
        "brier_score": round(float(brier_score_loss(y_true, probabilities)), 4),
        "prediction_horizon_days": 30,
    }
    metrics.update(top_k_metrics(frame, probabilities))
    return metrics


def make_logistic_model() -> Pipeline:
    return Pipeline(
        [
            (
                "preprocess",
                ColumnTransformer(
                    [
                        (
                            "numeric",
                            Pipeline(
                                [
                                    ("imputer", SimpleImputer(strategy="median")),
                                    ("scaler", StandardScaler()),
                                ]
                            ),
                            FEATURES,
                        )
                    ]
                ),
            ),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )


def make_gradient_boosted_model() -> Pipeline:
    return Pipeline(
        [
            (
                "preprocess",
                ColumnTransformer(
                    [("numeric", SimpleImputer(strategy="median"), FEATURES)]
                ),
            ),
            (
                "model",
                HistGradientBoostingClassifier(
                    learning_rate=0.08,
                    max_leaf_nodes=15,
                    min_samples_leaf=16,
                    l2_regularization=0.4,
                    random_state=42,
                ),
            ),
        ]
    )


def save_calibration_table(y_true: pd.Series, probabilities: np.ndarray) -> None:
    fraction_positive, mean_predicted = calibration_curve(y_true, probabilities, n_bins=8)
    pd.DataFrame(
        {
            "mean_predicted_risk": mean_predicted,
            "observed_event_frequency": fraction_positive,
        }
    ).to_csv(REPORTS_DIR / "calibration.csv", index=False)


def main() -> None:
    required_paths = [TRAIN_PATH, VALIDATION_PATH, TEST_PATH]
    if not all(path.exists() for path in required_paths):
        raise FileNotFoundError("Generate data first: python src/generate_data.py")

    MODELS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    train = pd.read_csv(TRAIN_PATH)
    validation = pd.read_csv(VALIDATION_PATH)
    test = pd.read_csv(TEST_PATH)

    candidates: dict[str, Pipeline] = {
        "logistic_regression": make_logistic_model(),
        "gradient_boosted_trees": make_gradient_boosted_model(),
    }
    validation_results: list[dict[str, float | str]] = []
    fitted_candidates: dict[str, Pipeline] = {}

    rule_validation = rule_score(validation)
    rule_threshold = choose_threshold(validation[TARGET], rule_validation)
    validation_results.append(evaluate("rule_baseline", validation, rule_validation, rule_threshold))

    for name, model in candidates.items():
        model.fit(train[FEATURES], train[TARGET])
        probabilities = model.predict_proba(validation[FEATURES])[:, 1]
        threshold = choose_threshold(validation[TARGET], probabilities)
        validation_results.append(evaluate(name, validation, probabilities, threshold))
        fitted_candidates[name] = model

    validation_table = pd.DataFrame(validation_results).sort_values(
        ["average_precision", "f1"], ascending=False
    )
    selected_name = str(validation_table.iloc[0]["model"])
    selected_threshold = float(validation_table.iloc[0]["threshold"])
    if selected_name == "rule_baseline":
        raise RuntimeError("Synthetic lab design expects an ML model to exceed the rule baseline.")

    # Refit the selected model on the historical development period only.
    selected_model = candidates[selected_name]
    development = pd.concat([train, validation], ignore_index=True)
    selected_model.fit(development[FEATURES], development[TARGET])
    test_probabilities = selected_model.predict_proba(test[FEATURES])[:, 1]
    test_metrics = evaluate(selected_name, test, test_probabilities, selected_threshold)

    joblib.dump(
        {"model": selected_model, "features": FEATURES, "threshold": selected_threshold},
        MODELS_DIR / "esp_risk_model.joblib",
    )

    risk_scores = test[["well_id", "field_id", "observation_date", TARGET] + FEATURES].copy()
    risk_scores["risk_score"] = np.round(test_probabilities, 4)
    risk_scores["risk_tier"] = np.where(
        risk_scores["risk_score"] >= selected_threshold, "high", "monitor"
    )
    risk_scores.sort_values(["observation_date", "risk_score"], ascending=[True, False]).to_csv(
        REPORTS_DIR / "test_risk_scores.csv", index=False
    )

    test_metrics["selected_on_validation"] = selected_name
    test_metrics["synthetic_data_only"] = True
    with (REPORTS_DIR / "metrics.json").open("w", encoding="utf-8") as output:
        json.dump(test_metrics, output, indent=2)
    validation_table.to_csv(REPORTS_DIR / "validation_model_comparison.csv", index=False)
    save_calibration_table(test[TARGET], test_probabilities)

    print("Validation comparison:")
    print(validation_table.to_string(index=False))
    print("\nHeld-out test metrics:")
    print(json.dumps(test_metrics, indent=2))
    print(f"\nSaved selected model: {MODELS_DIR / 'esp_risk_model.joblib'}")


if __name__ == "__main__":
    main()

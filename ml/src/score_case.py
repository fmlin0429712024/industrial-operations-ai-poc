"""Score one well observation using the validated ESP risk model.

This tool intentionally returns a review recommendation, not a diagnosis or
an equipment command. It can be called directly by a coding agent or wrapped
by the FastAPI adapter in ``ml/api``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "esp_risk_model.joblib"
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


def load_model(model_path: Path = MODEL_PATH) -> dict[str, Any]:
    if not model_path.exists():
        raise FileNotFoundError(
            "Model artifact is missing. Run: python ml/src/generate_data.py and "
            "python ml/src/train_model.py"
        )
    return joblib.load(model_path)


def evidence_for(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic operating evidence; do not infer root cause."""
    checks = [
        (
            "oil_rate_decline_30d_pct",
            12.0,
            "Oil-rate decline exceeds the review reference of 12% over 30 days.",
        ),
        (
            "motor_current_cv_7d_pct",
            8.0,
            "Motor-current variability exceeds the review reference of 8% over 7 days.",
        ),
        (
            "intake_pressure_decline_30d_pct",
            10.0,
            "Pump-intake-pressure decline exceeds the review reference of 10% over 30 days.",
        ),
        (
            "alarm_count_30d",
            3,
            "Repeated alarms meet the review reference of three events in 30 days.",
        ),
        (
            "days_since_last_intervention",
            300,
            "Time since the last intervention exceeds the 300-day review reference.",
        ),
    ]
    return [
        {
            "signal": signal,
            "value": payload[signal],
            "reference": threshold,
            "statement": statement,
        }
        for signal, threshold, statement in checks
        if float(payload[signal]) >= threshold
    ]


def score_payload(payload: dict[str, Any], model_path: Path = MODEL_PATH) -> dict[str, Any]:
    missing = [feature for feature in FEATURES if feature not in payload]
    if missing:
        raise ValueError(f"Missing required feature(s): {', '.join(missing)}")

    artifact = load_model(model_path)
    feature_frame = pd.DataFrame([{feature: payload[feature] for feature in FEATURES}])
    probability = float(artifact["model"].predict_proba(feature_frame)[:, 1][0])
    threshold = float(artifact["threshold"])
    high_risk = probability >= threshold

    return {
        "case_id": payload.get("case_id", "unassigned-case"),
        "well_id": payload.get("well_id", "unassigned-well"),
        "field_id": payload.get("field_id", "unassigned-field"),
        "observation_date": payload.get("observation_date", "unassigned-date"),
        "model": {
            "name": type(artifact["model"].named_steps["model"]).__name__,
            "version": "synthetic-esp-risk-v1",
            "prediction_horizon_days": 30,
            "synthetic_data_only": True,
        },
        "risk": {
            "score": round(probability, 4),
            "review_threshold": round(threshold, 4),
            "tier": "high" if high_risk else "monitor",
        },
        "evidence": evidence_for(payload),
        "recommended_next_step": (
            "Route to production-engineer review; do not change equipment settings."
            if high_risk
            else "Continue monitoring; no field action is recommended by this score alone."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score one synthetic ESP well observation.")
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "well_24_score_request.json",
        help="JSON request containing the required feature values.",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = score_payload(payload)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote score response to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()

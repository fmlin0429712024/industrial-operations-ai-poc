"""Generate deterministic, public-safe synthetic ESP well observations.

The data is intentionally illustrative. It contains no real field data and is
designed to demonstrate a reproducible ML lifecycle, not reservoir physics.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260715
N_WELLS = 120
N_MONTHS = 20
START_DATE = "2024-01-01"


def sigmoid(value: float) -> float:
    return float(1.0 / (1.0 + np.exp(-value)))


def split_name(month_index: int) -> str:
    if month_index < 14:
        return "train"
    if month_index < 17:
        return "validation"
    return "test"


def generate_history() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    dates = pd.date_range(START_DATE, periods=N_MONTHS, freq="MS")
    rows: list[dict[str, object]] = []

    for well_number in range(1, N_WELLS + 1):
        field_id = f"FIELD-{1 + (well_number - 1) // 30:02d}"
        well_id = f"WELL-{well_number:03d}"
        base_oil_rate = rng.uniform(280, 820)
        base_motor_current = rng.uniform(43, 62)
        base_intake_pressure = rng.uniform(920, 1550)
        water_cut = rng.uniform(18, 72)
        well_age = rng.uniform(1.5, 14.0)
        asset_vulnerability = rng.normal(0, 0.45)
        health_stress = max(0.0, rng.normal(0.16, 0.12))
        days_since_intervention = int(rng.integers(45, 260))

        for month_index, observation_date in enumerate(dates):
            # Stress drifts gradually, with occasional recovery or deterioration.
            health_stress = float(
                np.clip(
                    0.82 * health_stress
                    + rng.normal(0.045, 0.10)
                    + max(asset_vulnerability, -0.1) * 0.035,
                    0.0,
                    1.0,
                )
            )

            oil_decline = float(
                np.clip(rng.normal(3.5 + 18 * health_stress, 3.8), 0.0, 42.0)
            )
            motor_current = float(
                np.clip(
                    rng.normal(base_motor_current + 5.5 * health_stress, 2.2),
                    28.0,
                    92.0,
                )
            )
            motor_current_cv = float(
                np.clip(rng.normal(2.8 + 12 * health_stress, 1.6), 0.5, 30.0)
            )
            intake_pressure_decline = float(
                np.clip(rng.normal(2.5 + 17 * health_stress, 3.6), 0.0, 45.0)
            )
            pump_intake_pressure = float(
                np.clip(
                    rng.normal(
                        base_intake_pressure * (1 - intake_pressure_decline / 100),
                        45,
                    ),
                    450.0,
                    1900.0,
                )
            )
            alarm_rate = 0.25 + 3.8 * health_stress + max(asset_vulnerability, 0) * 0.45
            alarm_count = int(rng.poisson(alarm_rate))
            oil_rate = float(
                np.clip(
                    rng.normal(base_oil_rate * (1 - oil_decline / 100), 28),
                    30.0,
                    1100.0,
                )
            )

            # A transparent synthetic hazard: several weak/medium signals combine,
            # plus noise, to create plausible but non-perfect learnable labels.
            logit = (
                -4.7
                + 0.075 * oil_decline
                + 0.17 * motor_current_cv
                + 0.075 * intake_pressure_decline
                + 0.30 * alarm_count
                + 0.0035 * days_since_intervention
                + 0.20 * max(water_cut - 55, 0) / 10
                + 0.30 * asset_vulnerability
                + rng.normal(0, 0.60)
            )
            event_probability = sigmoid(logit)
            risk_event = int(rng.random() < event_probability)

            rows.append(
                {
                    "well_id": well_id,
                    "field_id": field_id,
                    "observation_date": observation_date.date().isoformat(),
                    "oil_rate_bpd": round(oil_rate, 2),
                    "oil_rate_decline_30d_pct": round(oil_decline, 2),
                    "water_cut_pct": round(water_cut, 2),
                    "motor_current_a": round(motor_current, 2),
                    "motor_current_cv_7d_pct": round(motor_current_cv, 2),
                    "pump_intake_pressure_psi": round(pump_intake_pressure, 2),
                    "intake_pressure_decline_30d_pct": round(intake_pressure_decline, 2),
                    "alarm_count_30d": alarm_count,
                    "days_since_last_intervention": days_since_intervention,
                    "well_age_years": round(well_age, 2),
                    "risk_event_next_30d": risk_event,
                    "split": split_name(month_index),
                }
            )

            if risk_event:
                # A synthetic intervention resets stress and maintenance age for
                # subsequent observations. The current row remains the pre-event view.
                days_since_intervention = int(rng.integers(0, 30))
                health_stress *= rng.uniform(0.18, 0.48)
            else:
                days_since_intervention += 30

    return pd.DataFrame(rows)


def main() -> None:
    output_path = Path(__file__).resolve().parents[1] / "data" / "esp_well_history.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    history = generate_history()
    history.to_csv(output_path, index=False)
    event_rate = history["risk_event_next_30d"].mean()
    print(f"Wrote {len(history):,} rows to {output_path}")
    print(f"Synthetic event rate: {event_rate:.1%}")
    print(history.groupby("split")["risk_event_next_30d"].agg(["count", "mean"]).round(3))


if __name__ == "__main__":
    main()

"""Thin HTTP adapter around the validated local scoring function."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.score_case import score_payload


class ScoreRequest(BaseModel):
    case_id: str = "unassigned-case"
    well_id: str
    field_id: str
    observation_date: str
    oil_rate_bpd: float = Field(ge=0)
    oil_rate_decline_30d_pct: float = Field(ge=0)
    water_cut_pct: float = Field(ge=0, le=100)
    motor_current_a: float = Field(ge=0)
    motor_current_cv_7d_pct: float = Field(ge=0)
    pump_intake_pressure_psi: float = Field(ge=0)
    intake_pressure_decline_30d_pct: float = Field(ge=0)
    alarm_count_30d: int = Field(ge=0)
    days_since_last_intervention: int = Field(ge=0)
    well_age_years: float = Field(ge=0)


app = FastAPI(
    title="Synthetic ESP Risk Score Service",
    version="0.1.0",
    description="Public-safe POC. Returns review recommendations, never equipment commands.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "scope": "synthetic-poc"}


@app.post("/risk-score")
def risk_score(request: ScoreRequest) -> dict[str, Any]:
    try:
        return score_payload(request.model_dump())
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

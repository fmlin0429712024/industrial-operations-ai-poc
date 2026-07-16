"""Run the synthetic ESP risk-to-response workflow locally.

This is a deterministic POC test harness, not a production agent runtime. It
proves that the workflow calls the same ML feature pack used by inference,
preserves a human decision gate, and produces structured handoffs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml" / "src"))

from score_case import score_payload  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def run_workflow(
    case_path: Path,
    approve_inspection: bool = False,
    approver: str | None = None,
) -> dict[str, Any]:
    """Execute the POC handoff contract and stop at/after the approval gate."""
    case = load_json(case_path)
    feature_path = (case_path.parent / case["model_input_reference"]).resolve()
    model_input = load_json(feature_path)
    score = score_payload(model_input)
    if score["well_id"] != case["asset"]["asset_id"]:
        raise ValueError("Workflow asset ID and model-input well ID must match.")

    high_risk = score["risk"]["tier"] == "high"
    asset_brief = {
        "risk_level": score["risk"]["tier"],
        "risk_score": score["risk"]["score"],
        "model_version": score["model"]["version"],
        "evidence": score["evidence"],
        "candidate_failure_modes": case["maintenance_context"]["known_failure_modes"],
        "confidence": "synthetic-poc-only",
        "recommended_next_step": score["recommended_next_step"],
        "human_review_required": high_risk,
    }
    process_assessment = {
        "objective": case["operating_context"]["production_objective"],
        "constraints": [case["operating_context"]["safety_constraint"]],
        "options": ["continue monitoring", "plan a diagnostic inspection window"],
        "recommended_action": "request production-engineer review" if high_risk else "continue monitoring",
        "operator_approval_required": high_risk,
    }
    decision: dict[str, Any] = {
        "status": "not_required" if not high_risk else "pending",
        "timestamp": utc_now(),
        "rationale": "Monitor tier; no field response proposed." if not high_risk else "High-risk score requires named human approval.",
    }
    field_package: dict[str, Any] | None = None
    if high_risk and approve_inspection:
        if not approver:
            raise ValueError("--approver is required with --approve-inspection.")
        decision = {
            "status": "approved",
            "approver": approver,
            "timestamp": utc_now(),
            "rationale": "Synthetic POC approval for diagnostic inspection only.",
        }
        field_package = {
            "status": "draft_only",
            "priority": "production-engineer-approved review",
            "work_scope": "Inspect ESP operating condition and review recent alarms; no equipment setting changes.",
            "safety_prerequisites": [case["operating_context"]["safety_constraint"]],
            "required_parts": "Confirm availability; no parts are reserved by this POC.",
        }

    return {
        "case_id": case["case_id"],
        "workflow_version": "synthetic-esp-risk-to-response-v1",
        "input_references": {"workflow_context": str(case_path), "model_feature_pack": str(feature_path)},
        "asset_performance": asset_brief,
        "process_assessment": process_assessment,
        "human_decision": decision,
        "field_execution": field_package,
        "evaluation_record": {"status": "awaiting_operational_outcome", "model_score": score["risk"]["score"]},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic ESP workflow.")
    parser.add_argument("--case", type=Path, default=ROOT / "data" / "sample-asset-signal.json")
    parser.add_argument("--approve-inspection", action="store_true")
    parser.add_argument("--approver", help="Named synthetic approver; required only for approval demo.")
    parser.add_argument("--output", type=Path, help="Optional path for the structured case record.")
    args = parser.parse_args()
    result = run_workflow(args.case, args.approve_inspection, args.approver)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote workflow record to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()

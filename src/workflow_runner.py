"""Run the synthetic ESP risk-to-field-service workflow locally.

This deterministic runner is a POC test harness, not a production agent
runtime. It persists a case record so the human approval and field closure are
separate, visible workflow steps.
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


def save_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def add_event(record: dict[str, Any], event: str, actor: str, detail: str) -> None:
    record.setdefault("timeline", []).append(
        {"timestamp": utc_now(), "event": event, "actor": actor, "detail": detail}
    )


def start_daily_batch(case_path: Path) -> dict[str, Any]:
    """Step 1: score a well and create a monitor or human-review case."""
    case = load_json(case_path)
    feature_path = (case_path.parent / case["model_input_reference"]).resolve()
    score = score_payload(load_json(feature_path))
    if score["well_id"] != case["asset"]["asset_id"]:
        raise ValueError("Workflow asset ID and model-input well ID must match.")

    high_risk = score["risk"]["tier"] == "high"
    record: dict[str, Any] = {
        "case_id": case["case_id"],
        "workflow_version": "synthetic-esp-risk-to-field-service-v1",
        "state": "under_review" if high_risk else "closed_monitoring",
        "asset": case["asset"],
        "input_references": {
            "workflow_context": str(case_path),
            "model_feature_pack": str(feature_path),
        },
        "asset_performance": {
            "risk_level": score["risk"]["tier"],
            "risk_score": score["risk"]["score"],
            "model_version": score["model"]["version"],
            "evidence": score["evidence"],
            "candidate_failure_modes": case["maintenance_context"]["known_failure_modes"],
            "recommended_next_step": score["recommended_next_step"],
        },
        "human_decision": {
            "status": "pending" if high_risk else "not_required",
            "rationale": "High-risk case requires named Asset / Production Engineer approval."
            if high_risk
            else "Monitor-tier case; no field-service ticket is created.",
        },
        "field_ticket": None,
        "evaluation_record": {
            "status": "awaiting_outcome" if high_risk else "monitoring_recorded",
            "model_score": score["risk"]["score"],
        },
        "timeline": [],
    }
    add_event(
        record,
        "daily_batch_scored",
        "asset-performance-skill",
        f"Risk tier: {score['risk']['tier']}; score: {score['risk']['score']}.",
    )
    if not high_risk:
        add_event(record, "monitoring_closed", "orchestrator", "No ticket created for monitor-tier case.")
    return record


def approve_inspection(record: dict[str, Any], approver: str) -> None:
    """Step 2 and 3: record approval and create a synthetic diagnostic ticket."""
    if record["state"] != "under_review":
        raise ValueError("Only an under_review case can be approved.")
    if not approver:
        raise ValueError("A named approver is required.")

    asset_id = record["asset"]["asset_id"]
    ticket_id = f"SYN-ESP-{asset_id.removeprefix('WELL-')}-{len(record['timeline']) + 1:03d}"
    record["human_decision"] = {
        "status": "approved",
        "approver": approver,
        "timestamp": utc_now(),
        "rationale": "Synthetic POC approval for diagnostic inspection only.",
    }
    record["field_ticket"] = {
        "ticket_id": ticket_id,
        "status": "open",
        "created_by": approver,
        "assigned_role": "Field Engineer",
        "work_scope": "Diagnose ESP operating condition and review recent alarms; do not change settings without separate authority.",
        "safety_prerequisites": ["Follow approved field safety procedure and isolate equipment only under authorized process."],
        "procurement_boundary": "Any purchase or ESP replacement approval is outside this POC ticket-creation step.",
    }
    record["state"] = "ticket_open"
    add_event(record, "inspection_approved", approver, "Approved a diagnostic inspection.")
    add_event(record, "synthetic_ticket_created", "field-execution-skill", f"Created {ticket_id}.")


def close_ticket(record: dict[str, Any], field_engineer: str, outcome: str) -> None:
    """Step 4 and 5: record field outcome, close the ticket, and create evaluation evidence."""
    if record["state"] != "ticket_open" or not record.get("field_ticket"):
        raise ValueError("Only an open field ticket can be closed.")
    if not field_engineer:
        raise ValueError("A named field engineer is required.")

    confirmed = outcome == "esp_replaced"
    record["field_ticket"].update(
        {
            "status": "closed",
            "closed_by": field_engineer,
            "closed_at": utc_now(),
            "field_outcome": outcome,
            "closure_note": "Synthetic result only; no real equipment was changed.",
        }
    )
    record["state"] = "closed_evaluated"
    record["evaluation_record"].update(
        {
            "status": "outcome_recorded",
            "outcome_confirms_material_esp_issue": confirmed,
            "learning_action": "Use verified field outcomes in the next governed model-evaluation cycle.",
        }
    )
    add_event(record, "field_ticket_closed", field_engineer, f"Outcome recorded: {outcome}.")
    add_event(record, "evaluation_recorded", "orchestrator", "Closed-loop evidence recorded.")


def write_and_report(path: Path, record: dict[str, Any]) -> None:
    save_record(path, record)
    print(f"Case state: {record['state']}")
    print(f"Wrote case record: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic ESP workflow state machine.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Run the daily score and triage step.")
    start.add_argument("--case", type=Path, default=ROOT / "data" / "sample-asset-signal.json")
    start.add_argument("--state", type=Path, required=True, help="JSON case-record path to create.")

    approve = subparsers.add_parser("approve", help="Approve an under-review case and create a synthetic ticket.")
    approve.add_argument("--state", type=Path, required=True)
    approve.add_argument("--approver", required=True)

    close = subparsers.add_parser("close", help="Close an open synthetic ticket and record its field outcome.")
    close.add_argument("--state", type=Path, required=True)
    close.add_argument("--field-engineer", required=True)
    close.add_argument("--outcome", choices=["esp_replaced", "no_fault_found"], required=True)

    show = subparsers.add_parser("show", help="Print an existing case record.")
    show.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "start":
        write_and_report(args.state, start_daily_batch(args.case))
    elif args.command == "approve":
        record = load_json(args.state)
        approve_inspection(record, args.approver)
        write_and_report(args.state, record)
    elif args.command == "close":
        record = load_json(args.state)
        close_ticket(record, args.field_engineer, args.outcome)
        write_and_report(args.state, record)
    else:
        print(json.dumps(load_json(args.state), indent=2))


if __name__ == "__main__":
    main()

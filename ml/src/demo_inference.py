"""Compare healthy and high-risk synthetic well cases using one trained model."""

from __future__ import annotations

import json
from pathlib import Path

from score_case import ROOT, score_payload


CASES = [
    ROOT / "data" / "well_025_healthy_score_request.json",
    ROOT / "data" / "well_24_score_request.json",
]


def main() -> None:
    print("ESP risk-model inference demo\n")
    for path in CASES:
        request = json.loads(path.read_text(encoding="utf-8"))
        result = score_payload(request)
        evidence = result["evidence"]
        print(f"{result['well_id']} | score={result['risk']['score']} | tier={result['risk']['tier']}")
        print(f"  Evidence signals: {len(evidence)}")
        for item in evidence:
            print(f"  - {item['signal']}: {item['value']} (reference {item['reference']})")
        print(f"  Next step: {result['recommended_next_step']}\n")


if __name__ == "__main__":
    main()

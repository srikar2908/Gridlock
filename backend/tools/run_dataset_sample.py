import csv
import json
import os
import random
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402


DATASET_PATH = Path(
    os.environ.get(
        "GRIDLOCK_DATASET_PATH",
        r"C:\Users\srika\Downloads\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv",
    )
)


def severity(row: dict) -> str:
    priority = (row.get("priority") or "").lower()
    closure = (row.get("requires_road_closure") or "").lower() == "true"
    if closure and priority == "high":
        return "critical"
    return priority if priority in {"high", "medium", "low"} else "medium"


def payload_from_row(row: dict) -> dict:
    event_cause = row.get("event_cause") or row.get("event_type") or "unknown"
    return {
        "event_type": event_cause,
        "corridor": row.get("corridor") or "Unknown Corridor",
        "zone": row.get("zone") or row.get("police_station") or "Unknown Zone",
        "description": row.get("description") or row.get("comment") or row.get("address") or "",
        "severity": severity(row),
        "metadata": {
            "source_id": row.get("id") or "",
            "event_category": row.get("event_type") or "",
            "requires_road_closure": row.get("requires_road_closure") or "",
            "status": row.get("status") or "",
            "priority": row.get("priority") or "",
        },
    }


def main() -> int:
    with DATASET_PATH.open(newline="", encoding="utf-8-sig", errors="replace") as file:
        rows = list(csv.DictReader(file))
    sample = random.Random(42).sample(rows, 10)

    output = []
    with TestClient(app) as client:
        for row in sample:
            response = client.post("/api/v1/analyze", json=payload_from_row(row))
            response.raise_for_status()
            data = response.json()
            output.append(
                {
                    "source_id": row.get("id"),
                    "event_cause": row.get("event_cause"),
                    "corridor": row.get("corridor"),
                    "zone": row.get("zone"),
                    "priority": data["priority"]["priority_level"],
                    "clearance_minutes": data["clearance"]["estimated_minutes"],
                    "resources": data["resources"],
                    "copilot_brief": data["copilot_summary"]["commander_brief"],
                }
            )
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

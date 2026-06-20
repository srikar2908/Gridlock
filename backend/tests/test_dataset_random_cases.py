import csv
import os
import random
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

DATASET_PATH = Path(
    os.environ.get(
        "GRIDLOCK_DATASET_PATH",
        r"C:\Users\srika\Downloads\Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv",
    )
)


def _severity(row: dict) -> str:
    priority = (row.get("priority") or "").lower()
    closure = (row.get("requires_road_closure") or "").lower() == "true"
    if closure and priority == "high":
        return "critical"
    if priority in {"high", "medium", "low"}:
        return priority
    return "medium"


def _incident_payload(row: dict) -> dict:
    event_cause = row.get("event_cause") or row.get("event_type") or "unknown"
    description = row.get("description") or row.get("comment") or row.get("address") or ""
    return {
        "event_type": event_cause,
        "corridor": row.get("corridor") or "Unknown Corridor",
        "zone": row.get("zone") or row.get("police_station") or "Unknown Zone",
        "description": description,
        "severity": _severity(row),
        "metadata": {
            "source_id": row.get("id") or "",
            "event_category": row.get("event_type") or "",
            "requires_road_closure": row.get("requires_road_closure") or "",
            "status": row.get("status") or "",
            "priority": row.get("priority") or "",
        },
    }


def test_random_10_dataset_cases():
    assert DATASET_PATH.exists(), f"Dataset not found: {DATASET_PATH}"
    with DATASET_PATH.open(newline="", encoding="utf-8-sig", errors="replace") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) >= 10
    sample = random.Random(42).sample(rows, 10)

    with TestClient(app) as client:
        results = []
        for row in sample:
            response = client.post("/api/v1/analyze", json=_incident_payload(row))
            assert response.status_code == 200, response.text
            payload = response.json()
            resources = payload["resources"]
            copilot = payload["copilot_summary"]
            assert resources["officer_requirement"]
            assert resources["resource_level"] in {
                "Low Resource Requirement",
                "Medium Resource Requirement",
                "High Resource Requirement",
            }
            assert "resource_plan" in copilot
            assert resources["officer_requirement"] in copilot["resource_plan"]
            results.append(
                {
                    "source_id": row.get("id"),
                    "event_cause": row.get("event_cause"),
                    "priority": payload["priority"]["priority_level"],
                    "officers": resources["officer_requirement"],
                    "tow_trucks": resources["tow_truck_requirement"],
                    "level": resources["resource_level"],
                    "brief": copilot["commander_brief"],
                }
            )
        assert len(results) == 10

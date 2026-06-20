# GRIDLOCK API Testing Report

Date: 2026-06-20

## Static Runtime Check

```bash
py -3.11 -m compileall backend\app
```

Result: passed.

## Focus Scenario

The tanker accident scenario was tested through FastAPI `TestClient` against:

```text
POST /api/v1/analyze
POST /api/v1/debug/closure
```

Request:

```json
{
  "event_type": "accident",
  "corridor": "ORR East 1",
  "zone": "East Zone",
  "description": "Fuel tanker collision causing severe congestion near Marathahalli junction",
  "severity": "critical",
  "metadata": {
    "event_category": "unplanned"
  }
}
```

## Analyze Result

```text
HTTP 200 OK
```

Key response values:

```json
{
  "closure_prediction": {
    "closure_required": true,
    "confidence": 0.72,
    "model_version": "Closure Prediction V2"
  },
  "priority": {
    "priority_level": "high",
    "priority_score": 0.665
  },
  "clearance": {
    "estimated_minutes": 46.7,
    "confidence": 0.462,
    "basis": "retrieval"
  },
  "resources": {
    "officers": 5,
    "tow_trucks": 1,
    "traffic_units": 3,
    "ambulance_units": 2,
    "officer_requirement": "4-6 Officers",
    "tow_truck_requirement": "1 Tow Truck",
    "resource_level": "High Resource Requirement"
  },
  "copilot_summary": {
    "llm_status": "accepted"
  }
}
```

## Copilot Verification

Groq returned valid JSON and was accepted by grounding guardrails.

The returned briefing contains:

- `incident_summary`
- `risk_assessment`
- `resource_explanation`
- `historical_context`
- `commander_recommendation`

The previous duplicated-number issue was addressed by sending Groq a compact structured context instead of the full prediction JSON.

## Closure Debug Verification

`POST /api/v1/debug/closure` returned:

```json
{
  "class_labels": [0, 1],
  "positive_class_index": 1,
  "positive_probability": 0.0263,
  "final_probability": 0.72,
  "closure_required": true,
  "calibration": {
    "applied": true,
    "type": "critical_hazardous_collision_operational_floor"
  }
}
```

The raw XGBoost probability remains visible for auditability. The final returned closure confidence applies an explicit operational calibration for critical hazardous collision signals.

## Notes

- MongoDB Atlas connected successfully during the scenario.
- Redis was unavailable locally and degraded gracefully without blocking the API.
- Full pytest was interrupted during interactive work; rerun `py -3.11 -m pytest` before final submission if a fresh full-suite report is required.

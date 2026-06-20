# GRIDLOCK API Testing Report

Date: 2026-06-20

## Test Command

```bash
py -3.11 -m pytest
```

## Result

```text
2 passed, 1 warning
```

## Covered Endpoints

- `GET /api/v1/health`
- `POST /api/v1/predict/closure`
- `POST /api/v1/predict/priority`
- `POST /api/v1/predict/clearance`
- `POST /api/v1/predict/resources`
- `POST /api/v1/retrieve/similar`
- `POST /api/v1/intelligence/cause`
- `POST /api/v1/copilot`
- `POST /api/v1/analyze`
- `GET /api/v1/dashboard/kpis`
- `GET /api/v1/dashboard/incidents`
- `GET /api/v1/dashboard/heatmap`
- `GET /api/v1/dashboard/corridors`
- `GET /api/v1/dashboard/resources`

## Sample Request

```json
{
  "event_type": "accident",
  "corridor": "Outer Ring Road",
  "zone": "East",
  "description": "Multi-vehicle crash blocking two lanes near a junction",
  "severity": "critical",
  "metadata": {
    "source": "test"
  }
}
```

## Sample Unified Response Shape

```json
{
  "incident_id": "mongodb-object-id-or-local-demo-id",
  "closure_prediction": {
    "closure_required": true,
    "confidence": 0.68,
    "model_version": "fallback-v1"
  },
  "priority": {
    "priority_level": "high",
    "priority_score": 0.7,
    "factors": {}
  },
  "clearance": {
    "estimated_minutes": 55.0,
    "confidence": 0.75,
    "basis": "retrieval"
  },
  "resources": {
    "officers": 3,
    "tow_trucks": 2,
    "traffic_units": 2,
    "ambulance_units": 1,
    "notes": []
  },
  "similar_incidents": [],
  "causes": [],
  "recommended_actions": [],
  "copilot_summary": {}
}
```

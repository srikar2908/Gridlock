# GRIDLOCK API Endpoints

Base URL: `/api/v1`

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service, registry, dependency health |
| GET | `/diagnostics/mongodb` | MongoDB connection diagnostics with sanitized host |
| POST | `/debug/closure` | Closure model feature/probability audit |
| POST | `/predict/closure` | Predict whether a closure is required |
| POST | `/predict/priority` | Score incident priority |
| POST | `/predict/clearance` | Estimate clearance time |
| POST | `/predict/resources` | Recommend officers, tow trucks, traffic units, ambulances |
| POST | `/retrieve/similar` | Retrieve real historical similar incidents |
| POST | `/intelligence/cause` | Return likely causes and action intelligence |
| POST | `/copilot` | Generate grounded traffic-operations briefing |
| POST | `/analyze` | Run the full intelligence pipeline and persist results |
| GET | `/dashboard/kpis` | KPI summary |
| GET | `/dashboard/incidents` | Live incident feed |
| GET | `/dashboard/heatmap` | Zone risk heatmap |
| GET | `/dashboard/corridors` | Corridor analytics |
| GET | `/dashboard/resources` | Resource allocation summary |

## Primary Analyze Request

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

## Primary Analyze Response Shape

```json
{
  "incident_id": "...",
  "closure_prediction": {
    "closure_required": true,
    "confidence": 0.72,
    "model_version": "Closure Prediction V2"
  },
  "priority": {
    "priority_level": "high",
    "priority_score": 0.665,
    "factors": {}
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
  "similar_incidents": [],
  "causes": [],
  "recommended_actions": [],
  "copilot_summary": {
    "llm_status": "accepted",
    "llm_brief": {
      "incident_summary": "...",
      "risk_assessment": "...",
      "resource_explanation": "...",
      "historical_context": "...",
      "commander_recommendation": "..."
    }
  }
}
```

## Closure Debug Response

`POST /api/v1/debug/closure` returns:

- `expected_model_features`
- `raw_features`
- `encoded_features`
- `probabilities`
- `probability_vector`
- `class_labels`
- `positive_class_index`
- `positive_probability`
- `threshold`
- `final_probability`
- `calibration`

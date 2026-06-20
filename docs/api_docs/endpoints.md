# GRIDLOCK API Endpoints

Base URL: `/api/v1`

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/predict/closure` | Predict whether closure is required |
| POST | `/predict/priority` | Score incident priority |
| POST | `/predict/clearance` | Estimate clearance time |
| POST | `/predict/resources` | Recommend operational resources |
| POST | `/retrieve/similar` | Retrieve digital twin incidents |
| POST | `/analyze` | Run the full intelligence pipeline and persist results |
| POST | `/copilot` | Rule-based RAG copilot response |
| GET | `/dashboard/kpis` | KPI summary |
| GET | `/dashboard/incidents` | Live incident feed |
| GET | `/dashboard/heatmap` | Zone risk heatmap |
| GET | `/dashboard/corridors` | Corridor analytics |
| GET | `/dashboard/resources` | Resource allocation summary |
| GET | `/health` | Service health |

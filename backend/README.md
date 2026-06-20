# GRIDLOCK Backend

FastAPI backend for the GRIDLOCK / SENTINEL AI Traffic Intelligence Platform.

## Stack

- FastAPI + Pydantic v2
- MongoDB Atlas through Motor/PyMongo
- Redis cache and request rate limiting
- Pandas, NumPy, Scikit-learn, XGBoost, LightGBM
- SentenceTransformers `all-MiniLM-L6-v2` for query embeddings
- Groq API for grounded traffic-operations copilot briefings
- Docker-ready runtime

## Run Locally

```bash
cd backend
py -3.11 -m pip install -r requirements.txt
py -3.11 -m uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

## Environment

Create `backend/.env` from `backend/.env.example`.

```env
APP_ENV=development
DEBUG=false
MONGODB_URI=
DATABASE_NAME=gridlock
GROQ_API_KEY=
REDIS_URL=redis://localhost:6379/0
ENABLE_REDIS_CACHE=true
ALLOW_DEGRADED_MODE=false
USE_FAISS_RETRIEVAL=false
AUTH_REQUIRED=false
JWT_SECRET=
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ASSETS_DIR=assets
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

Never commit real credentials. `backend/.env` is intentionally ignored.

## Startup Behavior

Startup loads the singleton model registry and connects to MongoDB Atlas.

Production behavior is strict:

- Closure model load failure fails startup.
- MongoDB connection failure fails startup unless `ALLOW_DEGRADED_MODE=true`.
- Redis failure logs a warning and continues without cache.
- Asset loading logs the closure model class, expected to be `XGBClassifier`.

## ML Assets

The model registry recursively scans `backend/assets/` for:

- `*.pkl`
- `*.joblib`
- `*.index`

Current asset families:

- Closure model: `closure_prediction_model_v2.pkl`
- Closure encoders and metadata
- Corridor and zone priority lookups
- Retrieval dataframe and embeddings
- Hybrid retrieval metadata
- FAISS indexes retained for future optimization
- Event cause knowledge base

## Retrieval

Cosine similarity is the default retrieval path.

The service uses:

1. `all-MiniLM-L6-v2` to encode the incoming incident query.
2. `retrieval_embeddings.pkl` as the historical incident embedding matrix.
3. Scikit-learn cosine similarity to select top-k matches.
4. `retrieval_df.pkl` to return real historical incident records.

FAISS indexes are still loaded and can be enabled later with:

```env
USE_FAISS_RETRIEVAL=true
```

The default remains cosine similarity because Windows FAISS SWIG bindings can expose incompatible low-level `search()` signatures.

## Closure Prediction

Closure prediction uses the XGBoost model and feature order from `closure_model_metadata_v2.pkl`.

The service exposes audit details at:

```text
POST /api/v1/debug/closure
```

The debug response includes:

- raw features
- encoded features
- expected model features
- probability vector
- class labels
- positive class index
- threshold
- operational calibration details

For critical hazardous collision scenarios, the service applies an explicit operational calibration floor while preserving the raw model probability in the debug output.

## Copilot

The copilot does not receive the full prediction JSON. It receives a compact, structured context:

- incident summary
- priority summary
- closure summary
- clearance summary
- resource summary
- historical summary
- recommended actions

Groq must return JSON with:

```json
{
  "incident_summary": "...",
  "risk_assessment": "...",
  "resource_explanation": "...",
  "historical_context": "...",
  "commander_recommendation": "..."
}
```

Guardrails reject only factual contradictions to:

- closure_required
- priority_level
- clearance_minutes
- officers
- tow_trucks
- traffic_units
- ambulances

Confidence values, similarity scores, historical ratios, and percentages are ignored by guardrails.

## Core Endpoints

- `GET /api/v1/health`
- `GET /api/v1/diagnostics/mongodb`
- `POST /api/v1/debug/closure`
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

## Analyze Pipeline

`POST /api/v1/analyze` runs closure prediction, priority scoring, digital twin retrieval, clearance estimation, resource recommendation, cause intelligence, Groq copilot briefing, and MongoDB persistence.

Resource logic guarantees:

- accidents receive at least one tow truck
- critical incidents receive at least one ambulance unit

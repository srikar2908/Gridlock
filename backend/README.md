# GRIDLOCK Backend

FastAPI backend for the GRIDLOCK / SENTINEL AI Traffic Intelligence Platform.

## Stack

- FastAPI + Pydantic v2
- MongoDB Atlas via Motor/PyMongo
- Redis cache and rate limiting
- FAISS, Pandas, NumPy, Scikit-Learn, LightGBM
- Groq API for copilot explanations

## Run Locally

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

## Environment

```env
MONGODB_URI=
DATABASE_NAME=gridlock
GROQ_API_KEY=
REDIS_URL=redis://localhost:6379/0
```

Credentials must come from environment variables. Do not hardcode keys.

## ML Assets

The model registry recursively scans `assets/` for:

- `*.pkl`
- `*.joblib`
- `*.index`

All discovered files are registered at startup. The known GRIDLOCK assets include closure prediction, label encoders, priority lookups, retrieval data, embeddings, FAISS indexes, and event cause knowledge base files. Missing or unloadable assets are reported by `GET /api/v1/health`.

## Core Endpoints

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

## Analyze Pipeline

`POST /api/v1/analyze` runs closure prediction, priority scoring, clearance estimation, resource recommendation, digital twin retrieval, cause intelligence, Groq/rule-based copilot explanation, and MongoDB persistence.

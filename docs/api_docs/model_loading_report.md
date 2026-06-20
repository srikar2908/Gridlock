# GRIDLOCK Model Loading Report

Date: 2026-06-20

## Registry Behavior

The backend uses a singleton `ModelRegistry` and loads assets once during FastAPI startup.

The registry recursively scans `backend/assets/` for:

- `*.pkl`
- `*.joblib`
- `*.index`

It exposes:

- `load_models()`
- `get_model()`
- `list_models()`
- `health_check()`

## Discovered Asset Families

Current workspace assets include:

- Closure prediction model and metadata
- Closure label encoders
- Corridor and zone priority lookup files
- Event priority and clearance statistics
- Retrieval dataframe
- Retrieval embeddings
- Hybrid retrieval metadata
- Event cause knowledge base
- Multiple FAISS indexes under `backend/assets/closure/faiss_indexes/`

## Runtime Health

Model loading is included in `GET /api/v1/health` under `dependencies.models`, including loaded asset count and any per-asset load errors.

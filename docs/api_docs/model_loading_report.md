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

## Loaded Asset Families

Current workspace assets include:

- `closure_prediction_model_v2.pkl`
- `closure_label_encoders.pkl`
- `closure_model_metadata_v2.pkl`
- `corridor_priority_lookup.pkl`
- `zone_priority_lookup.pkl`
- `retrieval_df.pkl`
- `retrieval_embeddings.pkl`
- `hybrid_retrieval_metadata.pkl`
- `event_cause_knowledge_base.pkl`
- FAISS indexes under `backend/assets/closure/faiss_indexes/`

## Closure Model

Expected startup log:

```text
Loaded asset closure_prediction_model_v2
Model class: XGBClassifier
```

Runtime audit:

- model class: `XGBClassifier`
- class labels: `[0, 1]`
- closure-positive class index: `1`
- feature order: read from `closure_model_metadata_v2.pkl`
- threshold: read from `best_threshold`

The exact original training XGBoost version is not embedded in the pickle metadata. Runtime loading is pinned through `requirements.txt`.

## Retrieval Assets

Cosine retrieval uses:

- `retrieval_df.pkl`
- `retrieval_embeddings.pkl`
- `sentence-transformers/all-MiniLM-L6-v2`

FAISS indexes are still registered but are not the default runtime path. Enable them only with:

```env
USE_FAISS_RETRIEVAL=true
```

## Runtime Health

Model loading is included in `GET /api/v1/health` under model dependency status.

# GRIDLOCK Startup Verification Report

Date: 2026-06-20

## Dependency Installation

```bash
py -3.11 -m pip install -r backend\requirements.txt
```

Result: dependencies installed, including XGBoost and SentenceTransformers.

## Static Runtime Check

```bash
py -3.11 -m compileall backend\app
```

Result: passed.

## Startup Path

FastAPI startup performs:

1. Singleton model registry load.
2. Closure model validation.
3. MongoDB Atlas connection.
4. Redis cache initialization with graceful degradation.

Observed startup logs include:

```text
Loaded asset closure_prediction_model_v2
Model class: XGBClassifier
Model registry initialized with 26 assets and 0 load errors
MongoDB URI host: gridlock.fja4wdu.mongodb.net
Connected to MongoDB database gridlock
Redis unavailable; continuing without cache
```

## Production Failure Rules

- Closure model missing or unloadable: startup fails.
- MongoDB unavailable: startup fails unless `ALLOW_DEGRADED_MODE=true`.
- Redis unavailable: warning only, cache disabled.

## Environment

- MongoDB Atlas is read from `backend/.env` through `MONGODB_URI`.
- Groq is read from `backend/.env` through `GROQ_API_KEY`.
- Redis is read from `backend/.env` through `REDIS_URL`.
- Secrets are excluded from Git by `.gitignore`.

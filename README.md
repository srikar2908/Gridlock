# GRIDLOCK AI

GRIDLOCK is the backend-first implementation of the SENTINEL AI Traffic Intelligence Platform for traffic command-center workflows.

The current repository contains a production-ready FastAPI backend and a placeholder frontend structure for later UI work.

## Current Scope

- Backend: implemented
- Frontend: placeholder only
- Database: MongoDB Atlas
- Copilot: Groq-backed RAG explanations with deterministic safety fallback
- Retrieval: NumPy/Scikit-learn cosine similarity by default, using stored retrieval embeddings
- FAISS: loaded and retained behind `USE_FAISS_RETRIEVAL` for future optimization

## Repository Layout

```text
GRIDLOCK/
+-- backend/
|   +-- app/
|   +-- assets/
|   +-- tests/
|   +-- tools/
|   +-- Dockerfile
|   +-- docker-compose.yml
|   +-- requirements.txt
|   +-- README.md
+-- docs/
|   +-- architecture/
|   +-- api_docs/
|   +-- diagrams/
+-- frontend/
    +-- README.md
```

## Main Backend Flow

`POST /api/v1/analyze` runs:

1. Closure prediction
2. Priority scoring
3. Similar incident retrieval
4. Clearance estimation
5. Resource recommendation
6. Event cause intelligence
7. Groq copilot briefing
8. MongoDB persistence

## Documentation

- [Backend README](backend/README.md)
- [Backend architecture](docs/architecture/backend_architecture.md)
- [API endpoints](docs/api_docs/endpoints.md)
- [API testing report](docs/api_docs/api_testing_report.md)
- [Startup verification report](docs/api_docs/startup_verification_report.md)
- [Model loading report](docs/api_docs/model_loading_report.md)
- [MongoDB ER diagram](docs/diagrams/database_er_diagram.md)

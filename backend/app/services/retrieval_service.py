from functools import lru_cache
from typing import List

import numpy as np

from app.core.logger import get_logger
from app.core.config import get_settings
from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import SimilarIncidentResponse

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class RetrievalService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.settings = get_settings()

    def find_similar(
        self,
        incident: IncidentRequest,
        limit: int = 5
    ) -> List[SimilarIncidentResponse]:

        hybrid_key = self._hybrid_key(incident)

        logger.info(f"Retrieval hybrid key: {hybrid_key}")

        rows = self._rows_for_key(hybrid_key)

        if rows is None or len(rows) == 0:
            raise RuntimeError(
                f"No retrieval rows found for key {hybrid_key}"
            )

        source_rows = rows
        rows = rows.reset_index(drop=True)

        query_embedding = self._embed(incident, source_rows)

        if self.settings.use_faiss_retrieval:
            scores, positions = self._search_faiss(hybrid_key, query_embedding, limit)
        else:
            scores, positions = self._search_cosine(query_embedding, source_rows, limit)

        results = []

        for score, position in zip(scores[0], positions[0]):

            if position < 0:
                continue

            if position >= len(rows):
                logger.warning(
                    f"FAISS position {position} exceeds row count {len(rows)}"
                )
                continue

            row = rows.iloc[int(position)].to_dict()

            try:
                results.append(
                    self._row_to_response(
                        row=row,
                        score=float(score)
                    )
                )
            except Exception as exc:
                logger.warning(
                    f"Skipping invalid retrieved row: {exc}"
                )

        return results

    def _search_cosine(self, query_embedding, source_rows, limit: int):
        from sklearn.metrics.pairwise import cosine_similarity

        embeddings = getattr(self.registry, "retrieval_embeddings", None)
        if embeddings is None:
            raise RuntimeError("retrieval_embeddings asset is not loaded")
        if "_embedding_pos" not in source_rows.columns:
            raise RuntimeError("retrieval rows are missing embedding positions")
        source_indices = source_rows["_embedding_pos"].astype(int).to_numpy()
        matrix = np.asarray(embeddings, dtype="float32")[source_indices]
        similarities = cosine_similarity(query_embedding, matrix)[0]
        top_k = min(limit, len(similarities))
        order = np.argsort(similarities)[::-1][:top_k]
        return np.asarray([similarities[order]], dtype="float32"), np.asarray([order], dtype="int64")

    def _search_faiss(self, hybrid_key: str, query_embedding, limit: int):
        index = self._index_for_key(hybrid_key)
        if index is None:
            raise RuntimeError(f"FAISS index not found for key {hybrid_key}")
        top_k = min(limit, index.ntotal)
        return self._faiss_search(index, query_embedding, top_k)

    @staticmethod
    def _hybrid_key(
        incident: IncidentRequest
    ) -> str:

        metadata = incident.metadata or {}

        event_category = (
            metadata.get("event_category")
            or metadata.get("event_type")
            or "unplanned"
        )

        event_cause = (
            incident.event_type
            .strip()
            .lower()
            .replace(" ", "_")
        )

        return f"{event_category}_{event_cause}"

    def _index_for_key(self, hybrid_key: str):

        faiss_indexes = getattr(
            self.registry,
            "faiss_indexes",
            {}
        )

        return faiss_indexes.get(
            f"{hybrid_key}_index"
        )

    def _rows_for_key(self, hybrid_key: str):

        df = getattr(
            self.registry,
            "retrieval_df",
            None
        )

        if (
            df is not None
            and hasattr(df, "columns")
            and "hybrid_key" in df.columns
        ):
            working = df.reset_index(drop=True).copy()
            working["_embedding_pos"] = np.arange(len(working), dtype="int64")
            return working[working["hybrid_key"] == hybrid_key]

        group_data = self.registry.get_model("group_data", {})

        if isinstance(group_data, dict):
            group = group_data.get(hybrid_key)
            if group and isinstance(group, dict) and "rows" in group:
                rows = group["rows"].reset_index(drop=True).copy()
                rows["_embedding_pos"] = np.arange(len(rows), dtype="int64")
                return rows

        return None

    def _embed(
        self,
        incident: IncidentRequest,
        rows
    ):

        text = " ".join(
            [
                incident.event_type,
                incident.corridor,
                incident.zone,
                incident.description or "",
            ]
        )

        try:

            vector = _embedding_model().encode(
                [text],
                normalize_embeddings=True
            )

            return np.asarray(
                vector,
                dtype="float32"
            )

        except Exception as exc:

            logger.warning("SentenceTransformer failed; using retrieval embedding centroid: %s", exc)
            embeddings = getattr(self.registry, "retrieval_embeddings", None)
            if embeddings is None:
                raise RuntimeError(f"Query embedding generation failed: {str(exc)}") from exc
            if "_embedding_pos" in rows.columns:
                source_indices = rows["_embedding_pos"].astype(int).to_numpy()
            else:
                source_indices = np.arange(len(rows), dtype="int64")
            candidate_vectors = np.asarray(embeddings, dtype="float32")[source_indices]
            centroid = candidate_vectors.mean(axis=0, keepdims=True)
            centroid = centroid / (np.linalg.norm(centroid, axis=1, keepdims=True) + 1e-9)
            return np.asarray(centroid, dtype="float32")

    @staticmethod
    def _faiss_search(index, query_embedding, top_k):
        try:
            return index.search(query_embedding, top_k)
        except TypeError:
            distances = np.empty((1, top_k), dtype="float32")
            labels = np.empty((1, top_k), dtype="int64")
            index.search(1, query_embedding, top_k, distances, labels)
            return distances, labels

    @staticmethod
    def _row_to_response(
        row: dict,
        score: float
    ) -> SimilarIncidentResponse:

        incident_id = str(
            row.get("id")
            or row.get("incident_id")
            or row.get("_id")
            or ""
        )

        if not incident_id:
            raise RuntimeError("Retrieved row is missing a real incident id")

        clearance = (
            row.get("closed_minutes")
            or row.get("clearance_time")
            or row.get("clearance_minutes")
            or 0
        )

        outcome = str(
            row.get("status")
            or row.get("outcome")
            or "resolved"
        )

        return SimilarIncidentResponse(
            similar_incident_id=incident_id,
            similarity_score=round(score, 3),
            clearance_time=float(clearance),
            historical_outcome=outcome,
            event_cause=str(
                row.get("event_cause", "")
            ),
            corridor=(
                None
                if row.get("corridor") is None
                else str(row.get("corridor"))
            ),
            zone=(
                None
                if row.get("zone") is None
                else str(row.get("zone"))
            ),
            outcome=outcome,
        )

from statistics import mean
from typing import List

from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClearancePrediction, SimilarIncidentResponse


class ClearanceService:
    def predict(self, incident: IncidentRequest, similar: List[SimilarIncidentResponse]) -> ClearancePrediction:
        if similar:
            weighted = sum(item.clearance_time * item.similarity_score for item in similar)
            weights = sum(item.similarity_score for item in similar) or 1
            estimate = weighted / weights
            confidence = min(0.92, mean(item.similarity_score for item in similar))
            return ClearancePrediction(estimated_minutes=round(estimate, 1), confidence=round(confidence, 3), basis="retrieval")
        fallback = 70 if incident.event_type.lower() in {"accident", "fire", "flooding"} else 35
        return ClearancePrediction(estimated_minutes=fallback, confidence=0.48, basis="rules")

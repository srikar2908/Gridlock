from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction


class PriorityService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, incident: IncidentRequest) -> PriorityPrediction:
        corridor_score = float((getattr(self.registry, "corridor_priority", {}) or {}).get(incident.corridor, 0.45))
        zone_score = float((getattr(self.registry, "zone_priority", {}) or {}).get(incident.zone, 0.45))
        event_score = {
            "accident": 0.85,
            "fire": 0.9,
            "flooding": 0.82,
            "breakdown": 0.42,
            "congestion": 0.35,
            "road closure": 0.78,
        }.get(incident.event_type.lower(), 0.5)
        severity_score = {"low": 0.2, "medium": 0.5, "high": 0.75, "critical": 0.95}.get(
            (incident.severity or "").lower(), 0.5
        )
        score = round((0.35 * event_score) + (0.25 * corridor_score) + (0.25 * zone_score) + (0.15 * severity_score), 3)
        level = "critical" if score >= 0.78 else "high" if score >= 0.62 else "medium" if score >= 0.42 else "low"
        return PriorityPrediction(
            priority_level=level,
            priority_score=score,
            factors={"event": event_score, "corridor": corridor_score, "zone": zone_score, "severity": severity_score},
        )

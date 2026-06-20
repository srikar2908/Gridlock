from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction


class PriorityService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, incident: IncidentRequest) -> PriorityPrediction:
        corridor_score = self._lookup_score(getattr(self.registry, "corridor_priority", None), incident.corridor, 0.45)
        zone_score = self._lookup_score(getattr(self.registry, "zone_priority", None), incident.zone, 0.45)
        event_stats_score = self._event_stats_score(incident.event_type)
        event_score = {
            "accident": 0.85,
            "fire": 0.9,
            "flooding": 0.82,
            "water_logging": 0.82,
            "breakdown": 0.42,
            "vehicle_breakdown": 0.52,
            "congestion": 0.35,
            "road closure": 0.78,
            "tree_fall": 0.7,
            "construction": 0.62,
            "road_conditions": 0.48,
        }.get(incident.event_type.lower(), event_stats_score)
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

    def _event_stats_score(self, event_type: str) -> float:
        stats = self.registry.get_model("event_priority_stats")
        if stats is not None and hasattr(stats, "loc"):
            try:
                row = stats.loc[event_type]
                return float(row.get("high_ratio", 0.5))
            except Exception:
                pass
        return 0.5

    @classmethod
    def _lookup_score(cls, lookup, key: str, default: float) -> float:
        if lookup is None:
            return default
        value = None
        try:
            if hasattr(lookup, "get"):
                value = lookup.get(key, None)
        except Exception:
            value = None
        if value is None and hasattr(lookup, "loc"):
            try:
                value = lookup.loc[key]
            except Exception:
                value = None
        if value is None:
            return default
        return cls._normalize_priority_value(value, default)

    @staticmethod
    def _normalize_priority_value(value, default: float) -> float:
        if hasattr(value, "iloc"):
            try:
                value = value.iloc[0]
            except Exception:
                return default
        if isinstance(value, str):
            return {"critical": 0.92, "high": 0.78, "medium": 0.55, "low": 0.28}.get(value.lower(), default)
        try:
            numeric = float(value)
        except Exception:
            return default
        if numeric > 1:
            numeric = numeric / 100
        return max(0.0, min(1.0, numeric))

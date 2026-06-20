from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClosurePrediction


class ClosureService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, incident: IncidentRequest) -> ClosurePrediction:
        model = getattr(self.registry, "closure_model", None)
        if model is not None and hasattr(model, "predict_proba"):
            # Asset schemas can vary; fall back cleanly if feature preparation does not match.
            try:
                features = [[incident.event_type, incident.corridor, incident.zone, incident.description]]
                probability = float(model.predict_proba(features)[0][1])
                return ClosurePrediction(
                    closure_required=probability >= 0.5,
                    confidence=round(probability, 3),
                    model_version=self.registry.closure_metadata.get("version", "closure-v2"),
                )
            except Exception:
                pass

        text = f"{incident.event_type} {incident.description} {incident.severity or ''}".lower()
        high_signal = ["fatal", "major", "pileup", "blocked", "flood", "fire", "critical", "collapse"]
        score = 0.78 if any(token in text for token in high_signal) else 0.34
        if incident.event_type.lower() in {"accident", "road closure", "flooding", "fire"}:
            score = max(score, 0.68)
        return ClosurePrediction(closure_required=score >= 0.55, confidence=score, model_version="fallback-v1")

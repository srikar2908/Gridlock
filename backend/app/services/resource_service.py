from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClearancePrediction, PriorityPrediction, ResourceRecommendation


class ResourceService:
    def recommend(
        self, incident: IncidentRequest, priority: PriorityPrediction, clearance: ClearancePrediction
    ) -> ResourceRecommendation:
        critical = priority.priority_level == "critical"
        accident = incident.event_type.lower() in {"accident", "fire"}
        return ResourceRecommendation(
            officers=4 if critical else 3 if priority.priority_level == "high" else 2,
            tow_trucks=2 if accident or clearance.estimated_minutes > 60 else 1,
            traffic_units=3 if critical else 2 if priority.priority_level == "high" else 1,
            ambulance_units=2 if critical and accident else 1 if accident else 0,
            notes=[
                "Create diversion plan for affected corridor",
                "Notify control room and zone supervisor",
                "Stage resources near nearest junction",
            ],
        )

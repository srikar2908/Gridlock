from app.core.registry import model_registry
from app.database.repositories.incident_repository import IncidentRepository
from app.database.repositories.prediction_repository import PredictionRepository
from app.schemas.requests import IncidentRequest
from app.schemas.responses import AnalyzeResponse
from app.services.clearance_service import ClearanceService
from app.services.closure_service import ClosureService
from app.services.copilot_service import CopilotService
from app.services.intelligence_service import IntelligenceService
from app.services.priority_service import PriorityService
from app.services.resource_service import ResourceService
from app.services.retrieval_service import RetrievalService


class AnalysisService:
    def __init__(self):
        self.closure = ClosureService(model_registry)
        self.priority = PriorityService(model_registry)
        self.retrieval = RetrievalService(model_registry)
        self.clearance = ClearanceService()
        self.resources = ResourceService()
        self.intelligence = IntelligenceService(model_registry)
        self.copilot = CopilotService()

    async def analyze(self, incident: IncidentRequest, incident_repo: IncidentRepository, prediction_repo: PredictionRepository) -> AnalyzeResponse:
        closure = self.closure.predict(incident)
        priority = self.priority.predict(incident)
        similar = self.retrieval.find_similar(incident)
        clearance = self.clearance.predict(incident, similar)
        resources = self.resources.recommend(incident, priority, clearance)
        causes = self.intelligence.causes(incident)
        actions = self.intelligence.recommended_actions(incident, priority)
        analysis_payload = {
            "closure_prediction": closure.model_dump(),
            "priority": priority.model_dump(),
            "clearance": clearance.model_dump(),
            "resources": resources.model_dump(),
            "similar_incidents": [item.model_dump() for item in similar],
            "causes": causes,
            "recommended_actions": actions,
        }
        copilot_summary = await self.copilot.explain(analysis_payload)

        record = await incident_repo.create(
            {
                "event_type": incident.event_type,
                "corridor": incident.corridor,
                "zone": incident.zone,
                "description": incident.description,
                "severity": incident.severity,
                "metadata": incident.metadata,
                "closure_required": closure.closure_required,
                "closure_confidence": closure.confidence,
                "priority_level": priority.priority_level,
                "priority_score": priority.priority_score,
                "estimated_clearance": clearance.estimated_minutes,
                "recommended_resources": resources.model_dump(),
                "causes": causes,
                "recommended_actions": actions,
                "copilot_summary": copilot_summary,
            }
        )
        incident_id = record["id"]

        await prediction_repo.create_many(
            [
                {"incident_id": incident_id, "prediction_type": "closure", "result": closure.model_dump(), "confidence": closure.confidence, "model_version": closure.model_version},
                {"incident_id": incident_id, "prediction_type": "priority", "result": priority.model_dump(), "confidence": priority.priority_score, "model_version": "priority-lookup-v1"},
                {"incident_id": incident_id, "prediction_type": "clearance", "result": clearance.model_dump(), "confidence": clearance.confidence, "model_version": clearance.basis},
            ]
        )
        await prediction_repo.create_similar_many(
            [
                {
                    "incident_id": incident_id,
                    "similar_incident_id": item.similar_incident_id,
                    "similarity_score": item.similarity_score,
                    "clearance_time": item.clearance_time,
                    "historical_outcome": item.historical_outcome,
                }
                for item in similar
            ]
        )
        return AnalyzeResponse(
            incident_id=incident_id,
            closure_prediction=closure,
            priority=priority,
            clearance=clearance,
            resources=resources,
            similar_incidents=similar,
            causes=causes,
            recommended_actions=actions,
            copilot_summary=copilot_summary,
        )

from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction
from app.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/cause", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def cause_intelligence(payload: IncidentRequest) -> dict:
    service = IntelligenceService(model_registry)
    priority = PriorityPrediction(priority_level=payload.severity or "medium", priority_score=0.5, factors={})
    return {
        "causes": service.causes(payload),
        "recommended_actions": service.recommended_actions(payload, priority=priority),
    }

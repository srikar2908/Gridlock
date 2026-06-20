from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.schemas.responses import ResourceRecommendation
from app.services.clearance_service import ClearanceService
from app.services.priority_service import PriorityService
from app.services.resource_service import ResourceService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/resources", response_model=ResourceRecommendation, dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def predict_resources(payload: IncidentRequest) -> ResourceRecommendation:
    priority = PriorityService(model_registry).predict(payload)
    similar = RetrievalService(model_registry).find_similar(payload)
    clearance = ClearanceService().predict(payload, similar)
    return ResourceService().recommend(payload, priority, clearance)

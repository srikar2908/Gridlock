from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction
from app.services.priority_service import PriorityService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/priority", response_model=PriorityPrediction, dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def predict_priority(payload: IncidentRequest) -> PriorityPrediction:
    return PriorityService(model_registry).predict(payload)

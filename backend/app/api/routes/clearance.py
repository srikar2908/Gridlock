from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClearancePrediction
from app.services.clearance_service import ClearanceService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/clearance", response_model=ClearancePrediction, dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def predict_clearance(payload: IncidentRequest) -> ClearancePrediction:
    similar = RetrievalService(model_registry).find_similar(payload)
    return ClearanceService().predict(payload, similar)


retrieve_router = APIRouter(prefix="/retrieve", tags=["retrieval"])


@retrieve_router.post("/similar", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def retrieve_similar(payload: IncidentRequest) -> list[dict]:
    return [item.model_dump() for item in RetrievalService(model_registry).find_similar(payload)]

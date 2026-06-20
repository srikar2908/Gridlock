from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClosurePrediction
from app.services.closure_service import ClosureService

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/closure", response_model=ClosurePrediction, dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def predict_closure(payload: IncidentRequest) -> ClosurePrediction:
    return ClosureService(model_registry).predict(payload)

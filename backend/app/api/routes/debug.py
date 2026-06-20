from fastapi import APIRouter, Depends

from app.core.registry import model_registry
from app.core.security import require_roles
from app.schemas.requests import IncidentRequest
from app.services.closure_service import ClosureService

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/closure", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def debug_closure(payload: IncidentRequest) -> dict:
    return ClosureService(model_registry).debug_prediction(payload)

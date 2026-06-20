from fastapi import APIRouter, Depends

from app.api.dependencies import get_incident_repository, get_prediction_repository
from app.core.security import require_roles
from app.database.repositories import IncidentRepository, PredictionRepository
from app.schemas.requests import IncidentRequest
from app.schemas.responses import AnalyzeResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def analyze(
    payload: IncidentRequest,
    incident_repo: IncidentRepository = Depends(get_incident_repository),
    prediction_repo: PredictionRepository = Depends(get_prediction_repository),
) -> AnalyzeResponse:
    return await AnalysisService().analyze(payload, incident_repo, prediction_repo)

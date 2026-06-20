from fastapi import APIRouter, Depends

from app.core.security import require_roles
from app.schemas.requests import CopilotRequest
from app.services.copilot_service import CopilotService

router = APIRouter(tags=["copilot"])


@router.post("/copilot", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def copilot(payload: CopilotRequest) -> dict:
    return await CopilotService().answer(payload)

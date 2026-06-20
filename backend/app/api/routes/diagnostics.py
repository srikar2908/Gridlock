from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import require_roles
from app.database.client import mongo

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/mongodb", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def mongodb_diagnostics(settings: Settings = Depends(get_settings)) -> dict:
    return await mongo.diagnostics(settings)

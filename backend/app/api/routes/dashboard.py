from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_incident_repository
from app.core.cache import cache_get, cache_set
from app.core.security import require_roles
from app.database.repositories import IncidentRepository
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
service = DashboardService()


@router.get("/kpis", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def kpis(repo: IncidentRepository = Depends(get_incident_repository)) -> dict:
    cached = await cache_get("dashboard:kpis")
    if cached:
        return cached
    data = await service.kpis(repo)
    await cache_set("dashboard:kpis", data, 30)
    return data


@router.get("/incidents", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def incidents(limit: int = Query(50, ge=1, le=200), repo: IncidentRepository = Depends(get_incident_repository)) -> list[dict]:
    return await service.incidents(repo, limit)


@router.get("/heatmap", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def heatmap(repo: IncidentRepository = Depends(get_incident_repository)) -> list[dict]:
    return await service.heatmap(repo)


@router.get("/corridors", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def corridors(repo: IncidentRepository = Depends(get_incident_repository)) -> list[dict]:
    return await service.corridors(repo)


@router.get("/resources", dependencies=[Depends(require_roles(["admin", "operator", "analyst"]))])
async def resources() -> dict:
    return {
        "available": {"officers": 24, "tow_trucks": 8, "ambulance_units": 10, "traffic_units": 42},
        "allocated": {"officers": 0, "tow_trucks": 0, "ambulance_units": 0, "traffic_units": 0},
    }

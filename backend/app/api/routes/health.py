from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.registry import model_registry
from app.database.client import mongo
from app.schemas.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    database_ok = await mongo.health_check()
    registry = model_registry.health_check()
    return HealthResponse(
        status="ok" if database_ok else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        registry_loaded=registry["loaded"],
        dependencies={"mongodb": database_ok, "redis_optional": settings.enable_redis_cache, "models": registry},
    )

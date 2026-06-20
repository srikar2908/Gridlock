from app.core.config import get_settings
from app.database.client import mongo
from app.database.repositories import IncidentRepository, PredictionRepository
from app.database.repositories.memory_repository import MemoryIncidentRepository, MemoryPredictionRepository


async def get_incident_repository():
    settings = get_settings()
    if mongo.database is None:
        try:
            await mongo.connect(settings)
        except Exception:
            if not settings.allow_degraded_mode:
                raise
    if mongo.database is None:
        if settings.allow_degraded_mode:
            return MemoryIncidentRepository()
        raise RuntimeError("MongoDB is unavailable")
    return IncidentRepository(mongo.database)


async def get_prediction_repository():
    settings = get_settings()
    if mongo.database is None:
        try:
            await mongo.connect(settings)
        except Exception:
            if not settings.allow_degraded_mode:
                raise
    if mongo.database is None:
        if settings.allow_degraded_mode:
            return MemoryPredictionRepository()
        raise RuntimeError("MongoDB is unavailable")
    return PredictionRepository(mongo.database)

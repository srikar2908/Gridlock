from app.core.config import get_settings
from app.database.client import mongo
from app.database.repositories import IncidentRepository, PredictionRepository
from app.database.repositories.memory_repository import MemoryIncidentRepository, MemoryPredictionRepository


async def get_incident_repository():
    if mongo.database is None:
        try:
            await mongo.connect(get_settings())
        except Exception:
            pass
    if mongo.database is None:
        return MemoryIncidentRepository()
    return IncidentRepository(mongo.database)


async def get_prediction_repository():
    if mongo.database is None:
        try:
            await mongo.connect(get_settings())
        except Exception:
            pass
    if mongo.database is None:
        return MemoryPredictionRepository()
    return PredictionRepository(mongo.database)

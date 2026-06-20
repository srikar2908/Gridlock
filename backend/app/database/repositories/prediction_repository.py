from datetime import datetime, timezone
from typing import Any, Dict, Iterable

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.repositories.incident_repository import serialize_document


class PredictionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_many(self, predictions: Iterable[Dict[str, Any]]) -> list[dict]:
        payloads = []
        for prediction in predictions:
            item = dict(prediction)
            item.setdefault("created_at", datetime.now(timezone.utc))
            payloads.append(item)
        if not payloads:
            return []
        result = await self.db.predictions.insert_many(payloads)
        cursor = self.db.predictions.find({"_id": {"$in": result.inserted_ids}})
        return [serialize_document(doc) async for doc in cursor]

    async def create_similar_many(self, similar_incidents: Iterable[Dict[str, Any]]) -> None:
        payloads = [dict(item) for item in similar_incidents]
        if payloads:
            await self.db.similar_incidents.insert_many(payloads)

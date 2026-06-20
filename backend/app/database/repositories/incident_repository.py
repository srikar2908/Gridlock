from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING


def serialize_document(document: Optional[dict]) -> Optional[dict]:
    if document is None:
        return None
    data = dict(document)
    data["id"] = str(data.pop("_id"))
    for key, value in list(data.items()):
        if isinstance(value, ObjectId):
            data[key] = str(value)
        elif isinstance(value, list):
            data[key] = [serialize_document(item) if isinstance(item, dict) and "_id" in item else item for item in value]
    return data


class IncidentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create(self, incident: Dict[str, Any]) -> dict:
        payload = dict(incident)
        payload.setdefault("created_at", datetime.now(timezone.utc))
        result = await self.db.incidents.insert_one(payload)
        created = await self.db.incidents.find_one({"_id": result.inserted_id})
        return serialize_document(created) or {}

    async def list_recent(self, limit: int = 50) -> List[dict]:
        cursor = self.db.incidents.find().sort("created_at", DESCENDING).limit(limit)
        return [serialize_document(doc) async for doc in cursor]

    async def count(self, filter_query: Optional[dict] = None) -> int:
        return await self.db.incidents.count_documents(filter_query or {})

    async def aggregate(self, pipeline: list[dict]) -> list[dict]:
        return [doc async for doc in self.db.incidents.aggregate(pipeline)]

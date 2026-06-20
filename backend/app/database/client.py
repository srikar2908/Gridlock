import re
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from app.core.config import Settings, get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class MongoDatabase:
    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self, settings: Settings) -> None:
        if self.client is not None:
            return
        if not settings.mongodb_uri:
            logger.warning("MONGODB_URI is not configured; API will run in degraded persistence mode")
            return
        uri = self._sanitize_uri(settings.mongodb_uri)
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        try:
            await client.admin.command("ping")
            self.client = client
            self.database = client[settings.database_name]
            await self.ensure_indexes()
            logger.info("Connected to MongoDB database %s", settings.database_name)
        except Exception:
            client.close()
            self.client = None
            self.database = None
            raise

    async def ensure_indexes(self) -> None:
        if self.database is None:
            return
        await self.database.incidents.create_index([("created_at", DESCENDING)])
        await self.database.incidents.create_index([("event_type", ASCENDING)])
        await self.database.incidents.create_index([("corridor", ASCENDING)])
        await self.database.incidents.create_index([("zone", ASCENDING)])
        await self.database.predictions.create_index([("incident_id", ASCENDING)])
        await self.database.similar_incidents.create_index([("incident_id", ASCENDING)])
        await self.database.analytics.create_index([("date", ASCENDING), ("zone", ASCENDING)], unique=True)
        await self.database.users.create_index([("email", ASCENDING)], unique=True, sparse=True)

    async def close(self) -> None:
        if self.client is not None:
            self.client.close()
        self.client = None
        self.database = None

    async def health_check(self) -> bool:
        if self.client is None:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    @staticmethod
    def _sanitize_uri(uri: str) -> str:
        return re.sub(r"mongodb(\+srv)?://<([^>]+)>:", r"mongodb\1://\2:", uri)


mongo = MongoDatabase()


async def get_database() -> AsyncIOMotorDatabase:
    if mongo.database is None:
        settings = get_settings()
        await mongo.connect(settings)
    if mongo.database is None:
        raise RuntimeError("MongoDB is not configured")
    return mongo.database

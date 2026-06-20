from motor.motor_asyncio import AsyncIOMotorDatabase


class AnalyticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def upsert_zone_daily(self, date, zone: str, total_incidents: int, critical_incidents: int, average_clearance: float):
        await self.db.analytics.update_one(
            {"date": date, "zone": zone},
            {
                "$set": {
                    "total_incidents": total_incidents,
                    "critical_incidents": critical_incidents,
                    "average_clearance": average_clearance,
                }
            },
            upsert=True,
        )

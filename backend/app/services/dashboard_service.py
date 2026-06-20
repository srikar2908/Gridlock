from app.database.repositories.incident_repository import IncidentRepository


class DashboardService:
    async def kpis(self, repo: IncidentRepository) -> dict:
        total = await repo.count()
        critical = await repo.count({"priority_level": "critical"})
        aggregates = await repo.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "average_clearance": {"$avg": "$estimated_clearance"},
                        "zones": {"$addToSet": "$zone"},
                    }
                }
            ]
        )
        avg_clearance = aggregates[0].get("average_clearance", 0) if aggregates else 0
        zones = len(aggregates[0].get("zones", [])) if aggregates else 0
        return {
            "total_incidents": total,
            "critical_incidents": critical,
            "average_clearance": round(float(avg_clearance or 0), 1),
            "active_zones": zones,
        }

    async def incidents(self, repo: IncidentRepository, limit: int = 50) -> list[dict]:
        return await repo.list_recent(limit)

    async def heatmap(self, repo: IncidentRepository) -> list[dict]:
        result = await repo.aggregate(
            [
                {"$group": {"_id": "$zone", "incident_count": {"$sum": 1}, "risk_score": {"$avg": "$priority_score"}}},
                {"$sort": {"risk_score": -1}},
            ]
        )
        return [
            {"zone": item["_id"], "incident_count": item["incident_count"], "risk_score": round(float(item.get("risk_score") or 0), 3)}
            for item in result
        ]

    async def corridors(self, repo: IncidentRepository) -> list[dict]:
        result = await repo.aggregate(
            [
                {
                    "$group": {
                        "_id": "$corridor",
                        "incident_count": {"$sum": 1},
                        "average_priority": {"$avg": "$priority_score"},
                        "average_clearance": {"$avg": "$estimated_clearance"},
                    }
                },
                {"$sort": {"incident_count": -1}},
            ]
        )
        return [
            {
                "corridor": item["_id"],
                "incident_count": item["incident_count"],
                "average_priority": round(float(item.get("average_priority") or 0), 3),
                "average_clearance": round(float(item.get("average_clearance") or 0), 1),
            }
            for item in result
        ]

from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


class MemoryStore:
    def __init__(self) -> None:
        self.incidents: list[dict] = []
        self.predictions: list[dict] = []
        self.similar_incidents: list[dict] = []


memory_store = MemoryStore()


class MemoryIncidentRepository:
    async def create(self, incident: Dict[str, Any]) -> dict:
        payload = dict(incident)
        payload["id"] = str(uuid4())
        payload.setdefault("created_at", datetime.now(timezone.utc))
        memory_store.incidents.append(payload)
        return payload

    async def list_recent(self, limit: int = 50) -> List[dict]:
        return sorted(memory_store.incidents, key=lambda item: item["created_at"], reverse=True)[:limit]

    async def count(self, filter_query: Optional[dict] = None) -> int:
        if not filter_query:
            return len(memory_store.incidents)
        return sum(1 for item in memory_store.incidents if all(item.get(key) == value for key, value in filter_query.items()))

    async def aggregate(self, pipeline: list[dict]) -> list[dict]:
        if not memory_store.incidents:
            return []
        group_id = pipeline[0].get("$group", {}).get("_id") if pipeline else None
        if group_id == "$zone":
            return self._group_by("zone", "risk_score", "priority_score")
        if group_id == "$corridor":
            return self._group_by_corridor()
        return [
            {
                "_id": None,
                "average_clearance": mean(item.get("estimated_clearance", 0) for item in memory_store.incidents),
                "zones": list({item.get("zone") for item in memory_store.incidents}),
            }
        ]

    @staticmethod
    def _group_by(field: str, avg_name: str, avg_field: str) -> list[dict]:
        groups = {}
        for item in memory_store.incidents:
            key = item.get(field)
            groups.setdefault(key, []).append(item)
        return [
            {"_id": key, "incident_count": len(items), avg_name: mean(i.get(avg_field, 0) for i in items)}
            for key, items in groups.items()
        ]

    @staticmethod
    def _group_by_corridor() -> list[dict]:
        groups = {}
        for item in memory_store.incidents:
            groups.setdefault(item.get("corridor"), []).append(item)
        return [
            {
                "_id": key,
                "incident_count": len(items),
                "average_priority": mean(i.get("priority_score", 0) for i in items),
                "average_clearance": mean(i.get("estimated_clearance", 0) for i in items),
            }
            for key, items in groups.items()
        ]


class MemoryPredictionRepository:
    async def create_many(self, predictions: Iterable[Dict[str, Any]]) -> list[dict]:
        created = []
        for prediction in predictions:
            payload = dict(prediction)
            payload["id"] = str(uuid4())
            payload.setdefault("created_at", datetime.now(timezone.utc))
            memory_store.predictions.append(payload)
            created.append(payload)
        return created

    async def create_similar_many(self, similar_incidents: Iterable[Dict[str, Any]]) -> None:
        for item in similar_incidents:
            payload = dict(item)
            payload["id"] = str(uuid4())
            memory_store.similar_incidents.append(payload)

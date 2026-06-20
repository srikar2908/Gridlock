from typing import List

from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction


class IntelligenceService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def causes(self, incident: IncidentRequest) -> List[str]:
        kb = getattr(self.registry, "event_kb", {}) or {}
        value = kb.get(incident.event_type) or kb.get(incident.event_type.lower())
        if isinstance(value, list):
            return [str(item) for item in value][:5]
        if isinstance(value, str):
            return [value]
        defaults = {
            "accident": ["Driver conflict at merge point", "Overspeeding", "Low visibility"],
            "congestion": ["Demand surge", "Signal delay", "Lane friction"],
            "flooding": ["Drainage overflow", "Low-lying carriageway"],
        }
        return defaults.get(incident.event_type.lower(), ["Historical pattern unavailable; field validation required"])

    @staticmethod
    def recommended_actions(incident: IncidentRequest, priority: PriorityPrediction) -> List[str]:
        actions = ["Validate incident from field unit or CCTV", "Broadcast ETA and diversion advisory"]
        if priority.priority_level in {"critical", "high"}:
            actions.extend(["Activate corridor-level response protocol", "Escalate to command center"])
        if incident.event_type.lower() == "accident":
            actions.append("Dispatch tow and medical support before full closure decision")
        return actions

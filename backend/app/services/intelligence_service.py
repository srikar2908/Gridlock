from typing import List

from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import PriorityPrediction


class IntelligenceService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def causes(self, incident: IncidentRequest) -> List[str]:
        kb = getattr(self.registry, "event_kb", None)
        if kb is not None and hasattr(kb, "iterrows"):
            match = kb[kb["event_cause"].astype(str).str.lower() == incident.event_type.lower()]
            if not match.empty:
                row = match.iloc[0]
                total = int(row.get("total_events", 0) or 0)
                high_ratio = float(row.get("high_priority_ratio", 0) or 0)
                clearance = row.get("median_clearance_minutes")
                evidence = [f"Historical pattern: {total} similar '{incident.event_type}' events in the knowledge base"]
                evidence.append(f"High-priority ratio for this cause: {round(high_ratio, 3)}")
                if clearance == clearance:
                    evidence.append(f"Median historical clearance for this cause: {round(float(clearance), 1)} minutes")
                return evidence
        if isinstance(kb, dict):
            value = kb.get(incident.event_type) or kb.get(incident.event_type.lower())
            if isinstance(value, list):
                return [str(item) for item in value][:5]
            if isinstance(value, str):
                return [value]
        defaults = {
            "accident": ["Driver conflict at merge point", "Overspeeding", "Low visibility"],
            "congestion": ["Demand surge", "Signal delay", "Lane friction"],
            "flooding": ["Drainage overflow", "Low-lying carriageway"],
            "water_logging": ["Drainage overflow", "Low-lying carriageway"],
            "vehicle_breakdown": ["Mechanical failure", "Heavy vehicle obstruction", "Shoulder unavailable"],
            "construction": ["Lane occupation", "Work-zone taper", "Reduced carriageway width"],
            "tree_fall": ["Carriageway obstruction", "Weather-related hazard"],
        }
        return defaults.get(incident.event_type.lower(), ["Historical pattern unavailable; field validation required"])

    @staticmethod
    def recommended_actions(incident: IncidentRequest, priority: PriorityPrediction) -> List[str]:
        actions = ["Validate incident from field unit or CCTV", "Broadcast ETA and diversion advisory"]
        if priority.priority_level in {"critical", "high"}:
            actions.extend(["Activate corridor-level response protocol", "Escalate to command center"])
        event = incident.event_type.lower()
        if event == "accident":
            actions.append("Dispatch tow and medical support before full closure decision")
        elif event == "vehicle_breakdown":
            actions.append("Dispatch tow support and protect the disabled vehicle with traffic units")
        elif event in {"water_logging", "flooding"}:
            actions.append("Alert civic response team and create a dry-route diversion")
        elif event == "tree_fall":
            actions.append("Dispatch clearance crew and hold traffic before obstruction point")
        elif event == "construction":
            actions.append("Verify work-zone permissions and enforce taper/diversion plan")
        return actions

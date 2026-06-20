from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClearancePrediction, PriorityPrediction, ResourceRecommendation


class ResourceService:
    def recommend(
        self, incident: IncidentRequest, priority: PriorityPrediction, clearance: ClearancePrediction
    ) -> ResourceRecommendation:
        event = incident.event_type.lower().replace("_", " ")
        text = f"{event} {incident.description}".lower()
        critical = priority.priority_level == "critical" or (incident.severity or "").lower() == "critical"
        high = priority.priority_level == "high"
        road_blocking = any(term in text for term in ["accident", "tree fall", "water logging", "flood", "construction", "procession"])
        vehicle_issue = any(term in text for term in ["accident", "breakdown", "collision", "crash", "tanker", "vehicle", "truck", "lcv", "tow"])
        medical_risk = any(term in text for term in ["accident", "injury", "fire", "fatal", "crash"])

        if critical:
            officers = 5
        elif high or road_blocking:
            officers = 4
        elif priority.priority_level == "medium":
            officers = 2
        else:
            officers = 1

        tow_trucks = 2 if vehicle_issue and (high or critical or clearance.estimated_minutes >= 60) else 1 if vehicle_issue else 0
        if event == "accident" or "accident" in text or "collision" in text or "crash" in text:
            tow_trucks = max(tow_trucks, 1)
        traffic_units = 3 if critical else 2 if high or road_blocking else 1
        ambulance_units = 2 if critical and medical_risk else 1 if medical_risk else 0
        if critical:
            ambulance_units = max(ambulance_units, 1)
        resource_level = self._resource_level(officers, tow_trucks, traffic_units, ambulance_units)
        rationale = [
            f"Priority is {priority.priority_level} with score {priority.priority_score}.",
            f"Estimated clearance is {clearance.estimated_minutes} minutes based on {clearance.basis}.",
            f"Event type '{incident.event_type}' drives {'vehicle recovery' if vehicle_issue else 'traffic control'} planning.",
        ]
        return ResourceRecommendation(
            officers=officers,
            tow_trucks=tow_trucks,
            traffic_units=traffic_units,
            ambulance_units=ambulance_units,
            officer_requirement=self._officer_label(officers),
            tow_truck_requirement=f"{tow_trucks} Tow Trucks" if tow_trucks != 1 else "1 Tow Truck",
            traffic_unit_requirement=f"{traffic_units} Traffic Units" if traffic_units != 1 else "1 Traffic Unit",
            ambulance_requirement=f"{ambulance_units} Ambulances" if ambulance_units != 1 else "1 Ambulance",
            resource_level=resource_level,
            summary=f"{self._officer_label(officers)}, {self._tow_label(tow_trucks)}, {resource_level}",
            rationale=rationale,
            notes=[
                "Create diversion plan for affected corridor",
                "Notify control room and zone supervisor",
                "Stage resources near nearest junction",
            ],
        )

    @staticmethod
    def _officer_label(officers: int) -> str:
        if officers >= 5:
            return "4-6 Officers"
        if officers == 4:
            return "4 Officers"
        if officers == 3:
            return "3 Officers"
        if officers == 2:
            return "2 Officers"
        return "1 Officer"

    @staticmethod
    def _tow_label(tow_trucks: int) -> str:
        if tow_trucks == 1:
            return "1 Tow Truck"
        return f"{tow_trucks} Tow Trucks"

    @staticmethod
    def _resource_level(officers: int, tow_trucks: int, traffic_units: int, ambulance_units: int) -> str:
        score = officers + (tow_trucks * 2) + traffic_units + (ambulance_units * 2)
        if score >= 10:
            return "High Resource Requirement"
        if score >= 6:
            return "Medium Resource Requirement"
        return "Low Resource Requirement"

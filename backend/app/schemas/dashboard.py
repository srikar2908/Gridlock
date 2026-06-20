from typing import List

from pydantic import BaseModel


class KPIResponse(BaseModel):
    total_incidents: int
    critical_incidents: int
    average_clearance: float
    active_zones: int


class HeatmapCell(BaseModel):
    zone: str
    incident_count: int
    risk_score: float


class CorridorMetric(BaseModel):
    corridor: str
    incident_count: int
    average_priority: float
    average_clearance: float


class ResourceAllocation(BaseModel):
    officers: int
    tow_trucks: int
    ambulance_units: int
    traffic_units: int


class DashboardList(BaseModel):
    items: List[dict]

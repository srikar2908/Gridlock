from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class ClosurePrediction(BaseModel):
    closure_required: bool
    confidence: float
    model_version: str


class PriorityPrediction(BaseModel):
    priority_level: str
    priority_score: float
    factors: Dict[str, float]


class ClearancePrediction(BaseModel):
    estimated_minutes: float
    confidence: float
    basis: str


class ResourceRecommendation(BaseModel):
    officers: int
    tow_trucks: int
    traffic_units: int
    ambulance_units: int
    notes: List[str]


class SimilarIncidentResponse(BaseModel):
    similar_incident_id: int
    similarity_score: float
    clearance_time: float
    historical_outcome: str


class AnalyzeResponse(BaseModel):
    incident_id: str
    closure_prediction: ClosurePrediction
    priority: PriorityPrediction
    clearance: ClearancePrediction
    resources: ResourceRecommendation
    similar_incidents: List[SimilarIncidentResponse]
    causes: List[str]
    recommended_actions: List[str]
    copilot_summary: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    registry_loaded: bool
    dependencies: Dict[str, Any]


class IncidentFeedItem(BaseModel):
    id: str
    event_type: str
    corridor: str
    zone: str
    priority_level: str
    priority_score: float
    estimated_clearance: float
    created_at: datetime

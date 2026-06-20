from typing import Dict, Optional

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    event_type: str = Field(..., examples=["accident"])
    corridor: str = Field(..., examples=["Outer Ring Road"])
    zone: str = Field(..., examples=["East"])
    description: str = Field(default="", max_length=4000)
    severity: Optional[str] = Field(default=None, examples=["critical"])
    metadata: Dict[str, str | int | float | bool] = Field(default_factory=dict)


class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    incident: Optional[IncidentRequest] = None
    analysis: Optional[dict] = None

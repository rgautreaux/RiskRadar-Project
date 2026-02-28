from pydantic import BaseModel
from typing import Optional


class AlertOut(BaseModel):
    id: int
    source: str
    source_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    event_start: Optional[str] = None
    event_end: Optional[str] = None
    fetched_at: str
    created_at: str

    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    total: int
    by_type: dict[str, int]
    by_severity: dict[str, int]

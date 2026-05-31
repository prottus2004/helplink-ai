from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Base schemas
class SOSSignalBase(BaseModel):
    source: str = "whatsapp"
    raw_message: str
    language_detected: str = "English"
    language_confidence: float = 1.0
    has_survivor_signal: bool = False
    survivor_count_estimate: int = 0
    location_extracted: Optional[str] = None
    latitude: float
    longitude: float
    priority_score: float = 0.0
    priority_level: str = "LOW"
    is_verified: bool = False

class SOSSignalCreate(SOSSignalBase):
    pass

class SOSSignalResponse(SOSSignalBase):
    id: int
    created_at: datetime
    processed_at: datetime

    class Config:
        from_attributes = True


class RescueTeamBase(BaseModel):
    team_name: str
    team_code: str
    unit_type: str = "NDRF"
    current_lat: float
    current_lng: float
    status: str = "available"
    assigned_signal_id: Optional[int] = None
    personnel_count: int = 5

class RescueTeamCreate(RescueTeamBase):
    pass

class RescueTeamResponse(RescueTeamBase):
    id: int
    last_updated: datetime
    assigned_signal: Optional[SOSSignalResponse] = None

    class Config:
        from_attributes = True


class SatelliteZoneBase(BaseModel):
    zone_name: str
    center_lat: float
    center_lng: float
    flood_severity: float
    area_sqkm: float
    isolated_structures: int
    water_depth_estimate: float
    scenario_id: str

class SatelliteZoneResponse(SatelliteZoneBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class CellularAnomalyBase(BaseModel):
    tower_id: str
    lat: float
    lng: float
    anomaly_type: str
    anomaly_score: float
    affected_radius_km: float

class CellularAnomalyResponse(CellularAnomalyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DemoScenarioBase(BaseModel):
    scenario_name: str
    location: str
    description: Optional[str] = None
    is_active: bool = False
    disaster_type: str = "Floods"
    severity: str = "Severe"
    total_affected: int = 0

class DemoScenarioResponse(DemoScenarioBase):
    id: str  # Custom ID like "wayanad"

    class Config:
        from_attributes = True


# Custom Request/Response Schemas
class SOSSubmitRequest(BaseModel):
    message: str = Field(..., description="Raw WhatsApp-style distress message")
    source: str = "whatsapp"
    latitude: float = Field(..., description="Message coordinate latitude")
    longitude: float = Field(..., description="Message coordinate longitude")
    language: Optional[str] = None  # Optional client override

class TeamDispatchRequest(BaseModel):
    team_id: int = Field(..., description="ID of the rescue team to dispatch")
    signal_id: int = Field(..., description="ID of the SOS signal destination")

class TeamStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status value ('available', 'en_route', 'on_ground', 'returning')")

class SMSSimulateRequest(BaseModel):
    phone_number: str = Field(..., description="Target Indian mobile number")
    message: str = Field(..., description="SMS distress/broadcast message content")

class OperationsSummary(BaseModel):
    total_sos: int
    critical_count: int
    high_count: int
    teams_deployed: int
    lives_estimated: int
    last_updated: str

class TimelineEvent(BaseModel):
    timestamp: str
    event_type: str  # "sos_received", "satellite_alert", "cellular_anomaly", "dispatch", "save"
    title: str
    description: str
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"

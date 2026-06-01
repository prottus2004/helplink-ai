from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import Base

class SOSSignal(Base):
    __tablename__ = "sos_signals"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default="whatsapp")  # "whatsapp", "twitter", "sms", "manual"
    raw_message = Column(Text, nullable=False)
    language_detected = Column(String, default="English")
    language_confidence = Column(Float, default=1.0)
    has_survivor_signal = Column(Boolean, default=False)
    survivor_count_estimate = Column(Integer, default=0)
    location_extracted = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    priority_score = Column(Float, default=0.0)  # 0.0 to 100.0
    priority_level = Column(String, default="LOW")  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    is_verified = Column(Boolean, default=False)
    data_source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        # Accept and set only known column attributes; ignore unexpected extras
        cols = set(self.__table__.columns.keys()) if hasattr(self, '__table__') else set()
        for k, v in kwargs.items():
            if k in cols:
                setattr(self, k, v)
            else:
                # ignore unknown kwargs like 'data_source' to remain backward-compatible
                continue


class RescueTeam(Base):
    __tablename__ = "rescue_teams"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    team_code = Column(String, unique=True, index=True, nullable=False)  # e.g., "NDRF-BN-01"
    unit_type = Column(String, default="NDRF")  # "NDRF", "SDRF", "Army", "Coast Guard"
    current_lat = Column(Float, nullable=False)
    current_lng = Column(Float, nullable=False)
    status = Column(String, default="available")  # "available", "en_route", "on_ground", "returning"
    assigned_signal_id = Column(Integer, ForeignKey("sos_signals.id"), nullable=True)
    personnel_count = Column(Integer, default=5)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to SOSSignal
    assigned_signal = relationship("SOSSignal", backref="assigned_teams")


class SatelliteZone(Base):
    __tablename__ = "satellite_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String, nullable=False)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    flood_severity = Column(Float, default=0.0)  # 0.0 to 1.0 (SAR-derived)
    area_sqkm = Column(Float, default=0.0)
    isolated_structures = Column(Integer, default=0)  # buildings cut off
    water_depth_estimate = Column(Float, default=0.0)  # in meters
    scenario_id = Column(String, nullable=False)  # links to demo scenario ID (e.g. "wayanad")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CellularAnomaly(Base):
    __tablename__ = "cellular_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    tower_id = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    anomaly_type = Column(String, default="dead_zone")  # "dead_zone", "traffic_spike", "signal_drop"
    anomaly_score = Column(Float, default=0.0)  # 0.0 to 1.0
    affected_radius_km = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class DemoScenario(Base):
    __tablename__ = "demo_scenarios"

    id = Column(String, primary_key=True, index=True)  # custom ID like "wayanad", "assam", "bihar"
    scenario_name = Column(String, nullable=False)
    location = Column(String, nullable=False)  # e.g., "Wayanad, Kerala"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    disaster_type = Column(String, default="Floods")
    severity = Column(String, default="Severe")  # "Severe", "Moderate", "Catastrophic"
    total_affected = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

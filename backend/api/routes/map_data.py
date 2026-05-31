from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sys
import os
from typing import List, Dict, Any

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import get_db
from db.models import SOSSignal, SatelliteZone, CellularAnomaly, RescueTeam
from api.schemas import SatelliteZoneResponse, CellularAnomalyResponse, RescueTeamResponse
from ai.priority_engine import PriorityEngine

router = APIRouter()
priority_engine = PriorityEngine()

@router.get("/heatmap")
async def get_heatmap_data(db: AsyncSession = Depends(get_db)):
    """
    Returns all active SOS points as [{lat, lng, intensity}] scaled for leaflet.heat
    """
    stmt = select(SOSSignal)
    result = await db.execute(stmt)
    signals = result.scalars().all()
    
    heatmap_points = []
    for sig in signals:
        # Scale priority_score (0-100) to intensity (0.0 to 1.0)
        intensity = round(sig.priority_score / 100.0, 2)
        heatmap_points.append({
            "lat": sig.latitude,
            "lng": sig.longitude,
            "intensity": max(intensity, 0.2)  # minimum visibility floor
        })
    return heatmap_points

@router.get("/satellite-zones", response_model=List[SatelliteZoneResponse])
async def get_satellite_zones(db: AsyncSession = Depends(get_db)):
    """
    Returns all active SAR satellite flood zones
    """
    stmt = select(SatelliteZone)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/cellular-anomalies", response_model=List[CellularAnomalyResponse])
async def get_cellular_anomalies(db: AsyncSession = Depends(get_db)):
    """
    Returns all cellular towers signal dropping anomaly logs
    """
    stmt = select(CellularAnomaly)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/priority-clusters")
async def get_priority_clusters(db: AsyncSession = Depends(get_db)):
    """
    Computes and returns the fused priority analysis output dynamically,
    blending the active satellite, cell towers, and NLP SOS messages.
    """
    # Fetch all data from DB
    sos_stmt = select(SOSSignal)
    sos_res = await db.execute(sos_stmt)
    sos_signals = [
        {
            "latitude": s.latitude,
            "longitude": s.longitude,
            "priority_score": s.priority_score,
            "survivor_count_estimate": s.survivor_count_estimate
        } for s in sos_res.scalars().all()
    ]
    
    sat_stmt = select(SatelliteZone)
    sat_res = await db.execute(sat_stmt)
    sat_zones = [
        {
            "zone_name": sz.zone_name,
            "center_lat": sz.center_lat,
            "center_lng": sz.center_lng,
            "flood_severity": sz.flood_severity,
            "area_sqkm": sz.area_sqkm,
            "isolated_structures": sz.isolated_structures,
            "water_depth_estimate": sz.water_depth_estimate,
            "scenario_id": sz.scenario_id
        } for sz in sat_res.scalars().all()
    ]
    
    cell_stmt = select(CellularAnomaly)
    cell_res = await db.execute(cell_stmt)
    cell_anom = [
        {
            "lat": ca.lat,
            "lng": ca.lng,
            "anomaly_type": ca.anomaly_type,
            "anomaly_score": ca.anomaly_score
        } for ca in cell_res.scalars().all()
    ]
    
    # Run geographic priority fusion algorithm
    clusters = priority_engine.calculate_rescue_priority(sos_signals, sat_zones, cell_anom)
    return clusters

@router.get("/rescue-teams", response_model=List[RescueTeamResponse])
async def get_rescue_teams(db: AsyncSession = Depends(get_db)):
    """
    Returns positions, unit details, and status states of all rescue teams
    """
    stmt = select(RescueTeam)
    result = await db.execute(stmt)
    return result.scalars().all()

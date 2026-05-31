from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sys
import os
from typing import List

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import get_db
from db.models import RescueTeam, SOSSignal
from api.schemas import RescueTeamResponse, TeamDispatchRequest, TeamStatusUpdateRequest
from websocket.manager import manager
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.get("/", response_model=List[RescueTeamResponse])
async def get_all_teams(db: AsyncSession = Depends(get_db)):
    """
    Lists all rescue teams and their operational states.
    """
    stmt = select(RescueTeam).options(selectinload(RescueTeam.assigned_signal))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/available", response_model=List[RescueTeamResponse])
async def get_available_teams(db: AsyncSession = Depends(get_db)):
    """
    Retrieves only available rescue teams ready for rapid deployment.
    """
    stmt = select(RescueTeam).where(RescueTeam.status == "available").options(selectinload(RescueTeam.assigned_signal))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/dispatch", response_model=RescueTeamResponse)
async def dispatch_team(payload: TeamDispatchRequest, db: AsyncSession = Depends(get_db)):
    """
    Dispatches a rescue team to a specific survivor SOS signal location.
    Updates the team status to 'en_route', sets coordinate assignments, and broadcasts telemetry.
    """
    # Fetch target team
    stmt_team = select(RescueTeam).where(RescueTeam.id == payload.team_id).options(selectinload(RescueTeam.assigned_signal))
    res_team = await db.execute(stmt_team)
    team = res_team.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="Rescue team not found")
        
    if team.status != "available":
        raise HTTPException(
            status_code=400, 
            detail=f"Rescue team '{team.team_code}' is currently unavailable (status: {team.status})"
        )
        
    # Fetch target SOS signal
    stmt_sig = select(SOSSignal).where(SOSSignal.id == payload.signal_id)
    res_sig = await db.execute(stmt_sig)
    signal = res_sig.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Target SOS signal location not found")
        
    # Bind team to coordinate destination
    team.status = "en_route"
    team.assigned_signal_id = signal.id
    
    await db.commit()
    
    # Re-query fresh team object with selectinload relationship for zero-latency response serialization
    stmt_fresh = select(RescueTeam).where(RescueTeam.id == team.id).options(selectinload(RescueTeam.assigned_signal))
    res_fresh = await db.execute(stmt_fresh)
    team = res_fresh.scalar_one()
    
    # Broadcast dispatch state updates via WebSockets
    ws_event = {
        "type": "team_update",
        "data": {
            "id": team.id,
            "team_code": team.team_code,
            "status": team.status,
            "assigned_signal_id": team.assigned_signal_id,
            "target_lat": signal.latitude,
            "target_lng": signal.longitude
        }
    }
    await manager.broadcast(ws_event)
    
    # Send operation logs event to alerts timelines
    timeline_event = {
        "type": "timeline_update",
        "data": {
            "timestamp": team.last_updated.strftime("%H:%M:%S"),
            "event_type": "dispatch",
            "title": f"Unit {team.team_code} Dispatched",
            "description": f"{team.team_name} ({team.unit_type}) sent to {signal.location_extracted or 'Unknown'} targeting {signal.survivor_count_estimate} survivors.",
            "priority": signal.priority_level
        }
    }
    await manager.broadcast(timeline_event)
    
    return team

@router.put("/{id}/status", response_model=RescueTeamResponse)
async def update_team_status(id: int, payload: TeamStatusUpdateRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually transitions team status (e.g. from 'en_route' -> 'on_ground' -> 'available' or 'returning').
    Clears targets automatically when returned to 'available' readiness.
    """
    stmt = select(RescueTeam).where(RescueTeam.id == id).options(selectinload(RescueTeam.assigned_signal))
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(status_code=404, detail="Rescue team not found")
        
    old_status = team.status
    team.status = payload.status
    
    # If the team completed its mission and returned to 'available' or 'returning'
    if payload.status in ("available", "returning"):
        team.assigned_signal_id = None
        
    await db.commit()
    
    # Re-query fresh team object with selectinload relationship for zero-latency response serialization
    stmt_fresh = select(RescueTeam).where(RescueTeam.id == team.id).options(selectinload(RescueTeam.assigned_signal))
    res_fresh = await db.execute(stmt_fresh)
    team = res_fresh.scalar_one()
    
    # Broadcast status change via WebSockets
    ws_event = {
        "type": "team_update",
        "data": {
            "id": team.id,
            "team_code": team.team_code,
            "status": team.status,
            "assigned_signal_id": team.assigned_signal_id
        }
    }
    await manager.broadcast(ws_event)
    
    # timeline logs
    timeline_event = {
        "type": "timeline_update",
        "data": {
            "timestamp": team.last_updated.strftime("%H:%M:%S"),
            "event_type": "save" if payload.status == "returning" else "status_change",
            "title": f"Unit {team.team_code} Status Updated",
            "description": f"Operational status transitioned from {old_status.upper()} to {team.status.upper()}.",
            "priority": "MEDIUM"
        }
    }
    await manager.broadcast(timeline_event)
    
    return team

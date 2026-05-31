from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import sys
import os
from typing import List

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import get_db
from db.models import SOSSignal, RescueTeam, SatelliteZone, CellularAnomaly
from api.schemas import OperationsSummary, TimelineEvent, SMSSimulateRequest

router = APIRouter()

@router.get("/summary", response_model=OperationsSummary)
async def get_operations_summary(db: AsyncSession = Depends(get_db)):
    """
    Computes high-level operations analytics for top dashboard stat cards.
    """
    try:
        # Total SOS distress counts
        stmt_total_sos = select(func.count(SOSSignal.id))
        res_total = await db.execute(stmt_total_sos)
        total_sos = res_total.scalar_one()
        
        # Priority level splits
        stmt_critical = select(func.count(SOSSignal.id)).where(SOSSignal.priority_level == "CRITICAL")
        res_crit = await db.execute(stmt_critical)
        crit_count = res_crit.scalar_one()
        
        stmt_high = select(func.count(SOSSignal.id)).where(SOSSignal.priority_level == "HIGH")
        res_high = await db.execute(stmt_high)
        high_count = res_high.scalar_one()
        
        # Total deployed teams
        stmt_deployed = select(func.count(RescueTeam.id)).where(RescueTeam.status != "available")
        res_dep = await db.execute(stmt_deployed)
        teams_deployed = res_dep.scalar_one()
        
        # Estimated lives at risk
        stmt_lives = select(func.sum(SOSSignal.survivor_count_estimate))
        res_lives = await db.execute(stmt_lives)
        lives_estimated = res_lives.scalar() or 0
        
        return OperationsSummary(
            total_sos=total_sos,
            critical_count=crit_count,
            high_count=high_count,
            teams_deployed=teams_deployed,
            lives_estimated=int(lives_estimated),
            last_updated=datetime.now().strftime("%d %b %Y, %H:%M:%S")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary calculation failed: {str(e)}")

@router.post("/sms-simulate")
async def simulate_sms(payload: SMSSimulateRequest):
    """
    Simulates sending an SMS to field units or civilians using simulated Twilio gateway logs in the terminal.
    """
    phone = payload.phone_number.strip()
    msg = payload.message.strip()
    
    # Twilio SIMULATION LOG PRINT
    print("\n" + "="*60)
    print(" [TWILIO SMS GATEWAY SIMULATION]")
    print(f" Target Number : {phone}")
    print(f" Time Dispatched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Status        : DELIVERED ✓")
    print(f" Content       : \"{msg}\"")
    print("="*60 + "\n")
    
    return {
        "status": "success",
        "phone_number": phone,
        "message_sent": msg,
        "gateway_response": {
            "sid": f"SM{os.urandom(16).hex()}",
            "status": "delivered",
            "provider": "Twilio-India-Gateway"
        }
    }

@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline_events(db: AsyncSession = Depends(get_db)):
    """
    Returns operations log milestones in chronological order for the demo panel.
    Combines active DB signals with historical scenario milestones.
    """
    events = []
    
    # 1. Fetch active SOS signals and format as timeline incidents
    sos_stmt = select(SOSSignal).order_by(SOSSignal.created_at.desc()).limit(15)
    sos_res = await db.execute(sos_stmt)
    signals = sos_res.scalars().all()
    
    for sig in signals:
        events.append(TimelineEvent(
            timestamp=sig.created_at.strftime("%H:%M:%S"),
            event_type="sos_received",
            title=f"Distress SOS ({sig.language_detected})",
            description=f"Message processed at {sig.location_extracted or 'coordinates'}: '{sig.raw_message[:60]}...'",
            priority=sig.priority_level
        ))
        
    # 2. Fetch deployed rescue teams
    team_stmt = select(RescueTeam).where(RescueTeam.status != "available")
    team_res = await db.execute(team_stmt)
    teams = team_res.scalars().all()
    
    for team in teams:
        events.append(TimelineEvent(
            timestamp=team.last_updated.strftime("%H:%M:%S"),
            event_type="dispatch",
            title=f"Team {team.team_code} Dispatch",
            description=f"{team.team_name} is active with status {team.status.upper()}.",
            priority="HIGH"
        ))

    # 3. Baseline system startup events
    events.append(TimelineEvent(
        timestamp="08:00:00",
        event_type="satellite_alert",
        title="Sentinel-1 SAR Orbit Inundation Pass",
        description="Sentinel-1 satellite synthetic aperture radar imagery processed. Multiple submerged clusters detected.",
        priority="HIGH"
    ))
    events.append(TimelineEvent(
        timestamp="08:05:00",
        event_type="cellular_anomaly",
        title="Cellular Dead Zones Identified",
        description="Abnormal telemetric signal drops logged. Multiple tower nodes reported off-grid in flooded segments.",
        priority="MEDIUM"
    ))
    events.append(TimelineEvent(
        timestamp="08:10:00",
        event_type="sos_received",
        title="HelpLink AI Operational",
        description="FastAPI gateway initialized. Multilingual NLP and Priority Fusion layers ready.",
        priority="LOW"
    ))
    
    # Sort events by timestamp descending so the most recent shows up at the top
    events.sort(key=lambda x: x.timestamp, reverse=True)
    return events

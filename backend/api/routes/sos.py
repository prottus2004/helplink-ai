from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import sys
import os
from typing import List

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import get_db
from db.models import SOSSignal
from api.schemas import SOSSubmitRequest, SOSSignalResponse
from ai.nlp_engine import NLPEngine
from websocket.manager import manager

router = APIRouter()
nlp_engine = NLPEngine()

@router.post("/submit", response_model=SOSSignalResponse)
async def submit_sos(payload: SOSSubmitRequest, db: AsyncSession = Depends(get_db)):
    """
    Submits a WhatsApp/SMS/Twitter distress message.
    Runs it through the multilingual SOS NLP Layer and calculates priorities.
    """
    try:
        # Run classification
        analysis = nlp_engine.classify_sos(payload.message)
        
        # Override language if explicitly provided by client submission
        if payload.language:
            analysis["language_detected"] = payload.language

        # Create database entity
        signal = SOSSignal(
            source=payload.source,
            raw_message=payload.message,
            language_detected=analysis["language_detected"],
            language_confidence=analysis["language_confidence"],
            has_survivor_signal=analysis["has_survivor_signal"],
            survivor_count_estimate=analysis["survivor_count_estimate"],
            location_extracted=analysis["location_extracted"],
            latitude=payload.latitude,
            longitude=payload.longitude,
            priority_score=analysis["priority_score"],
            priority_level=analysis["priority_level"],
            is_verified=False
        )
        
        db.add(signal)
        await db.commit()
        await db.refresh(signal)
        
        # Broadcast the new signal event via WebSocket
        ws_event = {
            "type": "new_sos",
            "data": {
                "id": signal.id,
                "source": signal.source,
                "raw_message": signal.raw_message,
                "language_detected": signal.language_detected,
                "language_confidence": signal.language_confidence,
                "has_survivor_signal": signal.has_survivor_signal,
                "survivor_count_estimate": signal.survivor_count_estimate,
                "location_extracted": signal.location_extracted,
                "latitude": signal.latitude,
                "longitude": signal.longitude,
                "priority_score": signal.priority_score,
                "priority_level": signal.priority_level,
                "is_verified": signal.is_verified,
                "created_at": signal.created_at.isoformat()
            }
        }
        await manager.broadcast(ws_event)
        
        return signal
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SOS submission classification failed: {str(e)}"
        )

@router.get("/feed", response_model=List[SOSSignalResponse])
async def get_sos_feed(db: AsyncSession = Depends(get_db)):
    """
    Returns the latest 50 SOS signals, ordered by priority score descending, then date descending.
    """
    stmt = select(SOSSignal).order_by(desc(SOSSignal.priority_score), desc(SOSSignal.created_at)).limit(50)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=SOSSignalResponse)
async def get_sos_detail(id: int, db: AsyncSession = Depends(get_db)):
    """
    Gets details of a single SOS signal.
    """
    stmt = select(SOSSignal).where(SOSSignal.id == id)
    result = await db.execute(stmt)
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail="SOS distress signal not found")
    return signal

@router.put("/{id}/verify", response_model=SOSSignalResponse)
async def verify_sos(id: int, db: AsyncSession = Depends(get_db)):
    """
    Marks a distress signal as verified by emergency operation center personnel.
    """
    stmt = select(SOSSignal).where(SOSSignal.id == id)
    result = await db.execute(stmt)
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail="SOS signal not found")
        
    signal.is_verified = True
    # Boost priority slightly due to human verification validation
    signal.priority_score = min(signal.priority_score + 15.0, 100.0)
    if signal.priority_score >= 75.0:
        signal.priority_level = "CRITICAL"
        
    await db.commit()
    await db.refresh(signal)
    
    # Broadcast verification update via WebSockets
    ws_event = {
        "type": "sos_verified",
        "data": {
            "id": signal.id,
            "is_verified": signal.is_verified,
            "priority_score": signal.priority_score,
            "priority_level": signal.priority_level
        }
    }
    await manager.broadcast(ws_event)
    
    return signal

@router.delete("/{id}")
async def dismiss_sos(id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes/Dismisses a false-alarm or duplicates SOS signal.
    """
    stmt = select(SOSSignal).where(SOSSignal.id == id)
    result = await db.execute(stmt)
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(status_code=404, detail="SOS signal not found")
        
    await db.delete(signal)
    await db.commit()
    
    # Broadcast dismiss event to clients
    ws_event = {
        "type": "sos_deleted",
        "data": {"id": id}
    }
    await manager.broadcast(ws_event)
    
    return {"status": "success", "message": f"SOS distress signal #{id} dismissed successfully."}

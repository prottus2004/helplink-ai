from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import sys
import os
import httpx
from typing import List

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.database import get_db
from db.models import SOSSignal
from api.schemas import SOSSubmitRequest, SOSSignalResponse, FormSOSRequest
from ai.nlp_engine import NLPEngine
from websocket.manager import manager
from datetime import datetime, timezone

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

async def geocode_location(location_name: str) -> tuple[float, float]:
    """
    Geocodes a free-text location string to latitude/longitude in India.
    Uses a fast local lookup for common districts, falls back to Nominatim OSM API,
    and defaults to the geographic center of India (Nagpur) on failure.
    """
    local_coords = {
        "wayanad": (11.6854, 76.1320),
        "kolkata": (22.5726, 88.3639),
        "behala": (22.4988, 88.3158),
        "shakuntala": (22.4988, 88.3158),
        "west bengal": (22.9868, 87.8550),
        "kerala": (10.8505, 76.2711),
        "assam": (26.2006, 92.9376),
        "bihar": (25.0961, 85.3131),
        "patna": (25.5941, 85.1376),
        "chennai": (13.0827, 80.2707),
        "mumbai": (19.0760, 72.8777),
        "delhi": (28.7041, 77.1025),
        "bengaluru": (12.9716, 77.5946),
        "bangalore": (12.9716, 77.5946),
        "cachar": (24.8333, 92.7789),
        "dhubri": (26.0207, 89.9736),
        "barpeta": (26.3275, 90.9808),
        "nagaon": (26.3484, 92.6838),
        "karimganj": (24.8649, 92.3590),
        "jorhat": (26.7509, 94.2037),
        "dibrugarh": (27.4728, 94.9120),
        "morigaon": (26.2625, 92.3389),
        "goalpara": (26.1744, 90.6278),
        "dhemaji": (27.4750, 94.5750),
        "lakhimpur": (27.2341, 94.0989),
    }

    name_lower = location_name.lower()
    
    # Check local dictionary
    for key, coords in local_coords.items():
        if key in name_lower:
            print(f"[Geocoder] Local match: '{location_name}' -> '{key}': {coords}")
            return coords

    # Call Nominatim OpenStreetMap API
    try:
        headers = {"User-Agent": "HelpLink-Emergency-Coordination-Portal/1.0"}
        params = {"q": f"{location_name}, India", "format": "json", "limit": 1}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params=params,
                headers=headers,
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    print(f"[Geocoder] Nominatim match for '{location_name}': {lat}, {lon}")
                    return lat, lon
    except Exception as e:
        print(f"[Geocoder WARNING] Nominatim lookup failed: {e}")

    # Fallback to geographical center of India (Nagpur)
    fallback = (21.1458, 79.0882)
    print(f"[Geocoder] Fallback to default India center for '{location_name}': {fallback}")
    return fallback

@router.post("/submit-form")
async def submit_from_form(payload: FormSOSRequest, db: AsyncSession = Depends(get_db)):
    """Receives SOS from Google Form via Make.com webhook"""
    try:
        full_message = payload.message
        if payload.location:
            full_message = f"{full_message}. Location: {payload.location}"
        if payload.person_count and payload.person_count > 1:
            full_message = f"{full_message}. {payload.person_count} people need help."

        nlp_result = nlp_engine.classify_sos(full_message)

        if payload.language and payload.language.lower() != "auto":
            nlp_result["language_detected"] = payload.language

        # Dynamically geocode the location string
        loc_name = payload.location or nlp_result.get("location_extracted", "Unknown")
        lat, lon = await geocode_location(loc_name)

        signal = SOSSignal(
            source="google_form",
            raw_message=full_message,
            language_detected=nlp_result.get("language_detected", "English"),
            language_confidence=nlp_result.get("language_confidence", 0.9),
            has_survivor_signal=True,
            survivor_count_estimate=payload.person_count or nlp_result.get("survivor_count_estimate", 1),
            location_extracted=loc_name,
            latitude=lat,
            longitude=lon,
            priority_score=max(nlp_result.get("priority_score", 50), 50),
            priority_level=nlp_result.get("priority_level", "HIGH"),
            data_source="Google Form (Public SOS)",
            is_verified=False,
            created_at=datetime.now(timezone.utc),
            processed_at=datetime.now(timezone.utc),
        )

        db.add(signal)
        await db.commit()
        await db.refresh(signal)

        await manager.broadcast({
            "type": "new_sos",
            "data": {
                "id": signal.id,
                "raw_message": signal.raw_message,
                "priority_level": signal.priority_level,
                "priority_score": signal.priority_score,
                "location_extracted": signal.location_extracted,
                "language_detected": signal.language_detected,
                "survivor_count_estimate": signal.survivor_count_estimate,
                "latitude": signal.latitude,
                "longitude": signal.longitude,
                "source": signal.source,
                "created_at": signal.created_at.isoformat(),
            }
        })

        print(f"[FormSOS] NEW REAL SOS from Google Form: priority={signal.priority_level}, location={signal.location_extracted}, survivors={signal.survivor_count_estimate}")

        return {
            "status": "received",
            "signal_id": signal.id,
            "priority": signal.priority_level,
            "priority_score": signal.priority_score,
            "language_detected": signal.language_detected,
            "survivor_estimate": signal.survivor_count_estimate,
            "message": "SOS received and dispatched to rescue dashboard"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Form submission failed: {e}")


@router.get("/submit-form")
async def verify_form_webhook():
    """Make.com pings this GET endpoint to verify the webhook is alive"""
    return {"status": "ok", "webhook": "google_form_sos_intake", "ready": True}

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

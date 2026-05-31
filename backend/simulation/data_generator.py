from faker import Faker
import random
import sys
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import SOSSignal, RescueTeam, DemoScenario
from ai.nlp_engine import NLPEngine
from websocket.manager import manager
from api.routes.alerts import get_operations_summary

fake = Faker('en_IN')  # Indian locale Faker
nlp_engine = NLPEngine()

# Distress message templates for 10 regional Indian languages
RANDOM_SOS_TEMPLATES = [
    {"template": "madad karo! {name} ke parivar ke {count} log doob rahe hain, yahan paani bohot badh gaya hai.", "lang": "Hindi", "src": "whatsapp"},
    {"template": "ഞങ്ങളെ രക്ഷിക്കൂ! {name} എന്ന സ്ഥലത്ത് {count} പേർ വീടിനുള്ളിൽ കുടുങ്ങിയിരിക്കുന്നു, വെള്ളം കൂടുന്നു.", "lang": "Malayalam", "src": "whatsapp"},
    {"template": "உதவி தேவை! {name} பகுதியில் வெள்ள நீர் சூழ்ந்துள்ளது, {count} பேர் தவித்து வருகிறோம்.", "lang": "Tamil", "src": "sms"},
    {"template": "সাহায্য করুন! {name} এ আমাদের ঘর ভেসে গেছে, {count} জন লোক জলের মাঝে আটকে আছি।", "lang": "Bengali", "src": "whatsapp"},
    {"template": "ସାହାଯ្យ କରନ୍ତୁ! {name} ପାଖରେ {count} ଜଣ ଲୋକ ଫସି ରହିଛନ୍ତି, ଚାରିଆଡେ ପାଣି ଜମିଛି।", "lang": "Odia", "src": "whatsapp"},
    {"template": "సహాయం కావాలి! {name} దగ్గర వరదలు వచ్చాయి, మేము {count} మంది ఇక్కడ చిక్కుకున్నాము.", "lang": "Telugu", "src": "sms"},
    {"template": "मदत करा! {name} जवळ पूर आला आहे, आमच्या घरातील {count} लोक अडकले आहेत.", "lang": "Marathi", "src": "whatsapp"},
    {"template": "ಸಹಾಯ ಮಾಡಿ! {name} ಹತ್ತಿರ ನದಿಯು ತುಂಬಿ ಹರಿಯುತ್ತಿದೆ, {count} ಜನರು ಸಿടുങ്ങಿದ್ದಾರೆ.", "lang": "Kannada", "src": "whatsapp"},
    {"template": "મદદ કરો! {name} વિસ્તારમાં પૂર આવ્યું છે, {count} લોકો અહીં ફસાયા છે.", "lang": "Gujarati", "src": "sms"},
    {"template": "ਮਦਦ ਕਰੋ! {name} ਪਿੰਡ ਵਿੱਚ ਭਾਰੀ ਹੜ੍ਹ ਆ ਗਿਆ ਹੈ, {count} ਲੋਕ ਫਸੇ ਹੋਏ ਹਨ।", "lang": "Punjabi", "src": "whatsapp"},
    {"template": "Emergency! Heavy flood near {name}. Road blocked, {count} people are stranded.", "lang": "English", "src": "twitter"}
]

async def generate_random_sos(scenario_id: str, center_lat: float, center_lng: float, db: AsyncSession) -> SOSSignal:
    """
    Generates a single randomized distress signal around the active scenario center coordinates.
    Classifies it using the NLP Engine and inserts it into the database.
    """
    # Pick a random template
    tpl_info = random.choice(RANDOM_SOS_TEMPLATES)
    
    # Generate random parameters
    indian_first_name = fake.first_name()
    count = random.randint(1, 8)
    
    # Populate template
    message = tpl_info["template"].format(name=indian_first_name, count=count)
    
    # Scramble location near center coordinate
    spread = 0.04 if "wayanad" in scenario_id else 0.08
    lat = float(center_lat + random.gauss(0, spread * 0.4))
    lng = float(center_lng + random.gauss(0, spread * 0.4))
    
    # NLP classification
    analysis = nlp_engine.classify_sos(message)
    analysis["language_detected"] = tpl_info["lang"]
    
    # Construct DB record
    signal = SOSSignal(
        source=tpl_info["src"],
        raw_message=message,
        language_detected=analysis["language_detected"],
        language_confidence=analysis["language_confidence"],
        has_survivor_signal=analysis["has_survivor_signal"],
        survivor_count_estimate=int(count),
        location_extracted=indian_first_name + " Area",
        latitude=lat,
        longitude=lng,
        priority_score=analysis["priority_score"],
        priority_level=analysis["priority_level"],
        is_verified=False,
        created_at=datetime.utcnow()
    )
    
    db.add(signal)
    await db.commit()
    await db.refresh(signal)
    
    return signal

async def simulate_realtime_update(db: AsyncSession):
    """
    This background job runs every 10 seconds. It simulates active events:
    1. Spawns 1-2 new SOS signals randomly (40% probability).
    2. Moves 'en_route' rescue teams closer to their targets using vector mathematics.
    3. Arrives teams to 'on_ground' state when close, and graduates them to 'available' when done.
    4. Computes operations summaries and broadcasts events via WebSockets.
    """
    try:
        # 1. Fetch active scenario
        stmt_scen = select(DemoScenario).where(DemoScenario.is_active == True)
        res_scen = await db.execute(stmt_scen)
        scenario = res_scen.scalar_one_or_none()
        
        if not scenario:
            return
            
        # Get active scenario coordinates
        # Map scenario center coords
        if scenario.id == "wayanad":
            lat, lng = 11.6854, 76.1320
        elif scenario.id == "assam":
            lat, lng = 26.2006, 92.9376
        else:
            lat, lng = 26.1197, 85.5160
            
        # 2. Randomly spawn new SOS signals (35% probability per interval)
        if random.random() < 0.35:
            new_sig = await generate_random_sos(scenario.id, lat, lng, db)
            print(f"[Simulation] Live SOS spawned: {new_sig.raw_message[:50]}...")
            
            # Broadcast the event
            ws_event = {
                "type": "new_sos",
                "data": {
                    "id": new_sig.id,
                    "source": new_sig.source,
                    "raw_message": new_sig.raw_message,
                    "language_detected": new_sig.language_detected,
                    "language_confidence": new_sig.language_confidence,
                    "has_survivor_signal": new_sig.has_survivor_signal,
                    "survivor_count_estimate": new_sig.survivor_count_estimate,
                    "location_extracted": new_sig.location_extracted,
                    "latitude": new_sig.latitude,
                    "longitude": new_sig.longitude,
                    "priority_score": new_sig.priority_score,
                    "priority_level": new_sig.priority_level,
                    "is_verified": new_sig.is_verified,
                    "created_at": new_sig.created_at.isoformat()
                }
            }
            await manager.broadcast(ws_event)
            
        # 3. Simulate rescue team coordinate movement vectors
        stmt_teams = select(RescueTeam).where(RescueTeam.status != "available")
        res_teams = await db.execute(stmt_teams)
        active_teams = res_teams.scalars().all()
        
        for team in active_teams:
            # Skip returning teams for simplicity or let them return
            if team.status == "returning":
                # Graduating returning teams back to available readiness (50% probability)
                if random.random() < 0.5:
                    team.status = "available"
                    team.assigned_signal_id = None
                    await db.commit()
                    
                    ws_event = {
                        "type": "team_update",
                        "data": {"id": team.id, "team_code": team.team_code, "status": team.status, "assigned_signal_id": None}
                    }
                    await manager.broadcast(ws_event)
                continue
                
            if not team.assigned_signal_id:
                continue
                
            # Fetch assigned target destination
            stmt_sig = select(SOSSignal).where(SOSSignal.id == team.assigned_signal_id)
            res_sig = await db.execute(stmt_sig)
            signal = res_sig.scalar_one_or_none()
            
            if not signal:
                # Target was deleted/dismissed, return team to return/available
                team.status = "available"
                team.assigned_signal_id = None
                await db.commit()
                continue
                
            dest_lat = signal.latitude
            dest_lng = signal.longitude
            
            # Step vector math
            # Calculate distance
            lat_diff = dest_lat - team.current_lat
            lng_diff = dest_lng - team.current_lng
            distance = (lat_diff**2 + lng_diff**2)**0.5
            
            if team.status == "en_route":
                # Move closer by 30% of distance remaining per tick
                if distance > 0.002:
                    team.current_lat += lat_diff * 0.3
                    team.current_lng += lng_diff * 0.3
                    await db.commit()
                    
                    # Broadcast step progress
                    ws_event = {
                        "type": "team_update",
                        "data": {
                            "id": team.id,
                            "team_code": team.team_code,
                            "status": team.status,
                            "current_lat": round(team.current_lat, 6),
                            "current_lng": round(team.current_lng, 6)
                        }
                    }
                    await manager.broadcast(ws_event)
                else:
                    # Arrived! Transition to "on_ground" search-and-rescue
                    team.status = "on_ground"
                    team.current_lat = dest_lat
                    team.current_lng = dest_lng
                    await db.commit()
                    
                    ws_event = {
                        "type": "team_update",
                        "data": {"id": team.id, "team_code": team.team_code, "status": team.status}
                    }
                    await manager.broadcast(ws_event)
                    
                    # timeline notification
                    timeline_event = {
                        "type": "timeline_update",
                        "data": {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "event_type": "status_change",
                            "title": f"Unit {team.team_code} Arrived",
                            "description": f"Team {team.team_name} arrived on ground at target {signal.location_extracted or 'distress coordinates'}.",
                            "priority": "HIGH"
                        }
                    }
                    await manager.broadcast(timeline_event)
                    
            elif team.status == "on_ground":
                # Rescuing survivors on-ground (30% probability of successfully completing rescue per tick)
                if random.random() < 0.30:
                    team.status = "returning"
                    await db.commit()
                    
                    # Also mark the assigned SOS signal as verified/processed or remove it
                    # Let's delete the processed SOS signal from active feeds to show progress!
                    await db.delete(signal)
                    await db.commit()
                    
                    # Broadcast team completed mission
                    ws_event = {
                        "type": "team_update",
                        "data": {"id": team.id, "team_code": team.team_code, "status": team.status}
                    }
                    await manager.broadcast(ws_event)
                    
                    # Broadcast processed SOS removal
                    del_event = {
                        "type": "sos_deleted",
                        "data": {"id": signal.id}
                    }
                    await manager.broadcast(del_event)
                    
                    # timeline event
                    timeline_event = {
                        "type": "timeline_update",
                        "data": {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "event_type": "save",
                            "title": f"Rescue Mission Completed",
                            "description": f"Unit {team.team_code} successfully extracted {signal.survivor_count_estimate} survivors from {signal.location_extracted or 'hazard area'}.",
                            "priority": "CRITICAL"
                        }
                    }
                    await manager.broadcast(timeline_event)
                    
        # 3.5. Dynamic Real-time Environmental Fluctuations
        spread = 0.04 if "wayanad" in scenario.id else 0.08
        
        # With a 30% probability, expand an existing satellite flood zone (monsoon rain intensity increase)
        if random.random() < 0.30:
            from db.models import SatelliteZone
            stmt_zones = select(SatelliteZone)
            res_zones = await db.execute(stmt_zones)
            zones = res_zones.scalars().all()
            if zones:
                target_zone = random.choice(zones)
                target_zone.flood_severity = min(target_zone.flood_severity + 0.05, 1.0)
                target_zone.water_depth_estimate = min(target_zone.water_depth_estimate + 0.2, 8.5)
                target_zone.isolated_structures += random.randint(1, 3)
                target_zone.area_sqkm = round(target_zone.area_sqkm + random.uniform(0.1, 0.4), 2)
                await db.commit()
                
                # Fetch all and broadcast updated list
                stmt_all_zones = select(SatelliteZone)
                res_all_zones = await db.execute(stmt_all_zones)
                all_zones = res_all_zones.scalars().all()
                ws_event = {
                    "type": "satellite_zones",
                    "data": [
                        {
                            "id": z.id,
                            "zone_name": z.zone_name,
                            "center_lat": z.center_lat,
                            "center_lng": z.center_lng,
                            "flood_severity": z.flood_severity,
                            "area_sqkm": z.area_sqkm,
                            "isolated_structures": z.isolated_structures,
                            "water_depth_estimate": z.water_depth_estimate,
                            "scenario_id": z.scenario_id
                        } for z in all_zones
                    ]
                }
                await manager.broadcast(ws_event)

        # With a 25% probability, spawn a new cellular tower dead zone / congestion spike
        if random.random() < 0.25:
            from db.models import CellularAnomaly
            # Create a new tower anomaly near the active scenario center
            new_anom = CellularAnomaly(
                tower_id=f"BTS-{random.randint(100, 999)}-{random.randint(10, 99)}",
                lat=lat + random.gauss(0, spread * 0.4),
                lng=lng + random.gauss(0, spread * 0.4),
                anomaly_type=random.choice(["dead_zone", "signal_drop", "traffic_spike"]),
                anomaly_score=round(random.uniform(0.4, 0.95), 2),
                affected_radius_km=round(random.uniform(0.5, 2.8), 1),
                created_at=datetime.utcnow()
            )
            db.add(new_anom)
            await db.commit()
            
            # Fetch all and broadcast updated list
            stmt_all_anoms = select(CellularAnomaly)
            res_all_anoms = await db.execute(stmt_all_anoms)
            all_anoms = res_all_anoms.scalars().all()
            ws_event = {
                "type": "cellular_anomalies",
                "data": [
                    {
                        "id": a.id,
                        "tower_id": a.tower_id,
                        "lat": a.lat,
                        "lng": a.lng,
                        "anomaly_type": a.anomaly_type,
                        "anomaly_score": a.anomaly_score,
                        "affected_radius_km": a.affected_radius_km
                    } for a in all_anoms
                ]
            }
            await manager.broadcast(ws_event)

        # 4. Broadcast updated summary analytics to keep counter widgets alive
        sum_data = await get_operations_summary(db)
        sum_event = {
            "type": "summary_update",
            "data": sum_data.model_dump()
        }
        await manager.broadcast(sum_event)
        
    except Exception as e:
        print(f"[Simulation ERROR] Real-time step iteration failed: {e}")

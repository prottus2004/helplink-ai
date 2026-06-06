from datetime import datetime

import httpx
from fastapi import APIRouter

router = APIRouter()

GDACS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"


@router.get("/api/live/disasters")
async def get_live_disasters():
    """Fetch active flood/cyclone disasters from GDACS (no API key required)."""
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(
                GDACS_URL,
                params={
                    "eventlist": "FL,TC",
                    "alertlevel": "Green,Orange,Red",
                },
            )
            response.raise_for_status()
            data = response.json()

        events = data.get("features", [])

        # CORRECT — only flags events actually in India
        INDIA_ISO3_CODES = {"IND"}
        INDIA_ADJACENT_NAMES = {"india"}  # only exact match

        def is_india_event(props: dict) -> bool:
            """Returns True ONLY if the event is in India — not Sri Lanka, not Bangladesh"""
            iso3 = props.get("iso3", "").upper()
            country = props.get("country", "").lower().strip()
            return iso3 in INDIA_ISO3_CODES or country in INDIA_ADJACENT_NAMES

        # South Asia group for honest naming in responses
        SOUTH_ASIA_ISO3 = {"IND", "LKA", "BGD", "NPL", "PAK"}

        india_events = []
        south_asia_events = []
        all_events = []

        for event in events[:20]:
            props = event.get("properties", {})
            coords = event.get("geometry", {}).get("coordinates", [0, 0])

            is_india = is_india_event(props)
            iso3 = props.get("iso3", "").upper()
            is_south_asia = iso3 in SOUTH_ASIA_ISO3

            entry = {
                "id": props.get("eventid"),
                "type": props.get("eventtype"),
                "name": props.get("name", "Unknown Event"),
                "country": props.get("country", "Unknown"),
                "alert": props.get("alertlevel", "Green"),
                "lat": coords[1] if len(coords) > 1 else 0,
                "lng": coords[0] if len(coords) > 0 else 0,
                "date": props.get("fromdate", ""),
                "affected": props.get("population", 0),
                "source": "GDACS Live API",
                "is_india": is_india,
            }

            all_events.append(entry)
            if is_india:
                india_events.append(entry)
            if is_south_asia:
                south_asia_events.append(entry)

        # After collecting all events, deduplicate by event ID
        seen_ids = set()
        unique_events = []
        for event in all_events:
            eid = event.get("id")
            if eid not in seen_ids:
                seen_ids.add(eid)
                unique_events.append(event)

        return {
            "status": "live",
            "fetched_at": datetime.utcnow().isoformat(),
            # Keep `india_events` for backward compatibility
            "india_events": india_events,
            "south_asia_events": south_asia_events,
            "global_events": unique_events,
            "total": len(unique_events),
            "source": "https://www.gdacs.org",
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "india_events": [],
            "global_events": [],
            "source": "GDACS (unreachable)",
        }


@router.get("/api/live/disaster-status")
async def get_disaster_status():
    """
    Returns India disaster count — reads from the same GDACS source
    as /api/live/disasters so both endpoints are always in sync.
    """
    try:
        full_data = await get_live_disasters()
        india_events = full_data.get("india_events", [])
        critical = [e for e in india_events if e.get("alert") in ["Orange", "Red"]]

        return {
            "active_india_disaster": len(india_events) > 0,
            "critical_count": len(critical),
            "total_india_count": len(india_events),
            "events": india_events[:5],
            "last_check": datetime.utcnow().isoformat(),
            "source": "GDACS Live API (synced)"
        }
    except Exception as e:
        return {
            "active_india_disaster": False,
            "critical_count": 0,
            "total_india_count": 0,
            "events": [],
            "last_check": datetime.utcnow().isoformat(),
            "source": "GDACS (error)"
        }


@router.get("/api/live/data-status")
async def get_data_status():
    """Report which data sources are real vs simulated."""
    from config import USE_REAL_SATELLITE, USE_REAL_TOWERS, USE_REAL_TWEETS
    return {
        "satellite": "real" if USE_REAL_SATELLITE else "simulated",
        "towers": "real" if USE_REAL_TOWERS else "simulated",
        "tweets": "real" if USE_REAL_TWEETS else "simulated",
        "gdacs": "live",
    }

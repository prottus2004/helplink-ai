from datetime import datetime

import httpx
from fastapi import APIRouter

router = APIRouter()

GDACS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

# South Asia ISO3 codes — includes India + 5 neighbouring countries
SOUTH_ASIA_ISO3 = {"IND", "LKA", "BGD", "NPL", "PAK", "MMR"}


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

        # Build raw event list first
        all_events = []
        for event in events[:20]:
            props = event.get("properties", {})
            coords = event.get("geometry", {}).get("coordinates", [0, 0])
            iso3 = props.get("iso3", "").upper()

            all_events.append({
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
                "iso3": iso3,
                "is_india": iso3 == "IND" or props.get("country", "").lower().strip() == "india",
            })

        # Deduplicate by event ID
        seen_ids = set()
        unique_events = []
        for event in all_events:
            if event["id"] not in seen_ids:
                seen_ids.add(event["id"])
                unique_events.append(event)
        all_events = unique_events

        # Build india_events and south_asia_events from the deduped list
        india_events = [e for e in all_events if e.get("iso3", "").upper() == "IND"
                        or e.get("country", "").lower() == "india"]

        south_asia_events = [e for e in all_events
                             if e.get("iso3", "").upper() in SOUTH_ASIA_ISO3
                             and e not in india_events]

        return {
            "status": "live",
            "fetched_at": datetime.utcnow().isoformat(),
            "india_events": india_events,
            "south_asia_events": south_asia_events,
            "global_events": all_events,
            "total": len(all_events),
            "source": "https://www.gdacs.org",
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "india_events": [],
            "south_asia_events": [],
            "global_events": [],
            "source": "GDACS (unreachable)",
        }


@router.get("/api/live/disaster-status")
async def get_disaster_status():
    """Quick check: active India-region disasters and critical count."""
    try:
        result = await get_live_disasters()
        india_events = result.get("india_events", [])
        critical = [event for event in india_events if event.get("alert") in {"Orange", "Red"}]
        return {
            "active_india_disaster": len(india_events) > 0,
            "critical_count": len(critical),
            "events": india_events[:3],
            "last_check": datetime.utcnow().isoformat(),
        }
    except Exception:
        return {"active_india_disaster": False, "critical_count": 0}


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

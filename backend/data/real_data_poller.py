"""
real_data_poller.py
-------------------
Real data ingestion poller for HelpLink production mode.
Schedules are defined in `backend/main.py` and call these async helpers.
This module never generates fake/demo data; it only ingests real sources.
"""
import asyncio
from datetime import datetime, timezone
from typing import List, Dict

import httpx
from sqlalchemy import select

from config import (
    TWITTER_BEARER_TOKEN,
    COPERNICUS_USER,
    COPERNICUS_PASS,
    OPENCELLID_API_KEY,
    USE_REAL_TWEETS,
    USE_REAL_SATELLITE,
    USE_REAL_TOWERS,
)

from ai.nlp_engine import NLPEngine
from ai.cellular_analyzer import CellularAnalyzer
from data.twitter_fetcher import fetch_live_sos_tweets
from data.satellite_fetcher import get_real_satellite_zones
from data.tower_fetcher import fetch_towers_for_scenario
from db.database import async_session
from db.models import SOSSignal, SatelliteZone, CellularAnomaly

GDACS_URL = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

nlp = NLPEngine()
cellular_analyzer = CellularAnalyzer()


async def poll_twitter_sos() -> int:
    """Pull recent SOS-like tweets and store them as SOSSignal records.
    Returns the number of newly ingested signals.
    """
    if not USE_REAL_TWEETS or not TWITTER_BEARER_TOKEN:
        return 0

    # twitter fetcher is synchronous; run in thread to avoid blocking
    tweets = await asyncio.to_thread(fetch_live_sos_tweets, TWITTER_BEARER_TOKEN, 10)
    if not tweets:
        return 0

    ingested = 0
    async with async_session() as session:
        for t in tweets:
            try:
                raw = t.get("raw_message") or t.get("text") or ""

                stmt = select(SOSSignal).where(SOSSignal.source == "twitter", SOSSignal.raw_message == raw)
                res = await session.execute(stmt)
                if res.scalars().first():
                    continue

                nlp_res = nlp.classify_sos(raw)
                if not nlp_res.get("has_survivor_signal"):
                    continue

                created_at = datetime.now(timezone.utc)
                try:
                    if t.get("created_at"):
                        created_at = datetime.fromisoformat(t.get("created_at"))
                except Exception:
                    created_at = datetime.now(timezone.utc)

                signal = SOSSignal(
                    source="twitter",
                    raw_message=raw,
                    data_source="Twitter/X Live API (REAL)",
                    language_detected=nlp_res.get("language_detected", "English"),
                    language_confidence=nlp_res.get("language_confidence", 0.0),
                    has_survivor_signal=True,
                    survivor_count_estimate=int(nlp_res.get("survivor_count_estimate", 1)),
                    location_extracted=nlp_res.get("location_extracted", "Unknown"),
                    latitude=0.0,
                    longitude=0.0,
                    priority_score=float(nlp_res.get("priority_score", 0.0)),
                    priority_level=nlp_res.get("priority_level", "LOW"),
                    is_verified=False,
                    created_at=created_at,
                    processed_at=datetime.now(timezone.utc),
                )
                session.add(signal)
                ingested += 1

            except Exception as e:
                print(f"[Twitter Poll] Error ingesting tweet: {e}")
                continue

        if ingested > 0:
            await session.commit()

    return ingested


async def poll_gdacs_disasters() -> List[Dict]:
    """Fetch active South-Asia disasters from GDACS and return structured list."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                GDACS_URL,
                params={"eventlist": "FL,TC,EQ", "alertlevel": "Orange,Red,Green"},
            )
            data = resp.json()

        events = []
        for feature in data.get("features", [])[:50]:
            props = feature.get("properties", {})
            iso3 = props.get("iso3", "").upper()
            if iso3 not in {"IND", "LKA", "BGD", "NPL", "PAK"}:
                continue

            coords = feature.get("geometry", {}).get("coordinates", [0, 0])
            lat = coords[1] if len(coords) > 1 else 0.0
            lng = coords[0] if len(coords) > 0 else 0.0

            events.append({
                "gdacs_id": props.get("eventid"),
                "type": props.get("eventtype"),
                "name": props.get("name"),
                "alert": props.get("alertlevel"),
                "lat": lat,
                "lng": lng,
                "affected": props.get("population", 0),
                "from_date": props.get("fromdate"),
            })

        return events
    except Exception as e:
        print(f"[GDACS Poll] Error fetching disasters: {e}")
        return []


async def auto_satellite_check():
    """When GDACS reports active disasters, query Copernicus Sentinel-1 and store zones."""
    events = await poll_gdacs_disasters()
    if not events:
        print("[Satellite] No active South-Asia disasters — skipping imagery check")
        return

    for ev in events:
        try:
            zones = await asyncio.to_thread(
                get_real_satellite_zones,
                str(ev.get("gdacs_id") or ev.get("name")),
                COPERNICUS_USER,
                COPERNICUS_PASS,
                ev.get("lat", 0.0),
                ev.get("lng", 0.0),
            )

            if not zones:
                continue

            async with async_session() as session:
                for zone in zones:
                    db_zone = SatelliteZone(
                        zone_name=zone.get("zone_name", "Sentinel-1 Zone"),
                        center_lat=zone.get("center_lat", 0.0),
                        center_lng=zone.get("center_lng", 0.0),
                        flood_severity=zone.get("flood_severity", 0.0),
                        area_sqkm=zone.get("area_sqkm", 0.0),
                        isolated_structures=zone.get("isolated_structures", 0),
                        water_depth_estimate=zone.get("water_depth_estimate", 0.0),
                        scenario_id=str(zone.get("scenario_id") or ev.get("gdacs_id") or ev.get("name")),
                        last_updated=datetime.now(timezone.utc),
                    )
                    session.add(db_zone)
                await session.commit()

            print(f"[Satellite] Saved {len(zones)} real flood zones for {ev.get('name')}")

        except Exception as e:
            print(f"[Satellite] Error processing event {ev.get('name')}: {e}")


async def refresh_opencellid_towers():
    """Refresh cached OpenCelliD towers and derive cellular anomalies for active disasters."""
    events = await poll_gdacs_disasters()
    if not events:
        return

    for ev in events:
        try:
            # Use asynchronous tower fetcher
            towers = await fetch_towers_for_scenario(
                str(ev.get("gdacs_id") or ev.get("name")),
                OPENCELLID_API_KEY,
                center_lat=ev.get("lat"),
                center_lng=ev.get("lng"),
            )

            if not towers:
                continue

            anomalies = cellular_analyzer._build_anomalies_from_real_towers(str(ev.get("gdacs_id") or ev.get("name")), towers)

            async with async_session() as session:
                for an in anomalies:
                    db_an = CellularAnomaly(
                        tower_id=an.get("tower_id"),
                        lat=an.get("lat", 0.0),
                        lng=an.get("lng", 0.0),
                        anomaly_type=an.get("anomaly_type", "dead_zone"),
                        anomaly_score=an.get("anomaly_score", 0.0),
                        affected_radius_km=an.get("affected_radius_km", 1.0),
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(db_an)
                await session.commit()

            print(f"[Towers] Computed {len(anomalies)} anomalies from {len(towers)} OpenCelliD towers for {ev.get('name')}")

        except Exception as e:
            print(f"[Towers] Error for event {ev.get('name')}: {e}")

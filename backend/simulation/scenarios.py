"""
scenarios.py
Pre-built demo scenarios for HelpLink.
These provide realistic disaster data for Samsung SFT 2026 demonstrations.
"""
from datetime import datetime, timezone
from typing import List, Dict

# ─── SCENARIO DEFINITIONS ────────────────────────────────────────────────────

SCENARIOS = {
    "wayanad": {
        "id": "wayanad",
        "scenario_name": "Wayanad Landslide & Flash Flood",
        "location": "Meppadi & Vythiri, Wayanad, Kerala",
        "description": "July 2024 massive cloudburst triggered major hill mudslides in "
                       "Meppadi & Vythiri, separating communities.",
        "disaster_type": "FL",
        "severity": "Catastrophic",
        "total_affected": 48,
        "center_lat": 11.6854,
        "center_lng": 76.1320,
        "zoom": 10,
        "sos_messages": [
            {"message": "Bachao! Hamare ghar mein paani aa gaya, 5 log phanse hain, Meppadi ke paas",
             "language": "Hindi", "lat": 11.69, "lng": 76.12, "survivors": 5},
            {"message": "Sahaayam! Vellam keri, 8 per kettappettu, Vythiri",
             "language": "Malayalam", "lat": 11.65, "lng": 76.13, "survivors": 8},
            {"message": "Help! Flood water rising, 4 people trapped near Meppadi school",
             "language": "English", "lat": 11.70, "lng": 76.11, "survivors": 4},
            {"message": "Udavi! Tanneer vanthuchu, 6 per, Kalpetta road blocked",
             "language": "Tamil", "lat": 11.61, "lng": 76.09, "survivors": 6},
            {"message": "Sahayam! Niru bandide, 7 jana, Sulthan Bathery",
             "language": "Kannada", "lat": 11.68, "lng": 76.26, "survivors": 7},
            {"message": "Bachao! 3 log phanse, Ambalavayal village",
             "language": "Hindi", "lat": 11.63, "lng": 76.17, "survivors": 3},
            {"message": "Help rescue needed, bridge washed out, 5 stranded",
             "language": "English", "lat": 11.72, "lng": 76.08, "survivors": 5},
            {"message": "Sahaayam! Mudslide blocked road, 4 families cut off",
             "language": "Malayalam", "lat": 11.64, "lng": 76.14, "survivors": 10},
        ],
        "satellite_zones": [
            {"zone_name": "Meppadi Inundation Zone", "center_lat": 11.69, "center_lng": 76.12,
             "flood_severity": 0.92, "area_sqkm": 12.4, "isolated_structures": 18,
             "water_depth_estimate": 3.2, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Vythiri Flash Flood Zone", "center_lat": 11.65, "center_lng": 76.13,
             "flood_severity": 0.78, "area_sqkm": 8.6, "isolated_structures": 12,
             "water_depth_estimate": 1.8, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Kalpetta Road Corridor", "center_lat": 11.61, "center_lng": 76.09,
             "flood_severity": 0.55, "area_sqkm": 5.2, "isolated_structures": 6,
             "water_depth_estimate": 1.1, "data_source": "ESA Sentinel-1 SAR"},
        ],
        "rescue_teams": [
            {"team_name": "NDRF Kerala Battalion Unit 1", "team_code": "NDRF-KL-01",
             "unit_type": "NDRF", "current_lat": 11.71, "current_lng": 76.15,
             "personnel_count": 8, "status": "available"},
            {"team_name": "NDRF Kerala Battalion Unit 2", "team_code": "NDRF-KL-02",
             "unit_type": "NDRF", "current_lat": 11.67, "current_lng": 76.10,
             "personnel_count": 6, "status": "available"},
            {"team_name": "SDRF Wayanad Unit 1", "team_code": "SDRF-WY-01",
             "unit_type": "SDRF", "current_lat": 11.60, "current_lng": 76.20,
             "personnel_count": 5, "status": "available"},
            {"team_name": "Coast Guard Fast Rescue", "team_code": "CG-KL-01",
             "unit_type": "Coast Guard", "current_lat": 11.73, "current_lng": 76.07,
             "personnel_count": 4, "status": "available"},
        ],
        "cellular_anomalies": [
            {"tower_id": "T_WY_001", "lat": 11.68, "lng": 76.11,
             "anomaly_type": "dead_zone", "anomaly_score": 0.95, "affected_radius_km": 2.1},
            {"tower_id": "T_WY_002", "lat": 11.63, "lng": 76.16,
             "anomaly_type": "traffic_spike", "anomaly_score": 0.82, "affected_radius_km": 1.4},
            {"tower_id": "T_WY_003", "lat": 11.70, "lng": 76.09,
             "anomaly_type": "dead_zone", "anomaly_score": 0.88, "affected_radius_km": 1.8},
        ],
    },

    "assam": {
        "id": "assam",
        "scenario_name": "Brahmaputra Floods",
        "location": "Cachar, Dhubri, Barpeta — Assam",
        "description": "Major embankment breaches flooded agricultural lowlands. "
                       "High speed currents and stranded clusters.",
        "disaster_type": "FL",
        "severity": "Severe",
        "total_affected": 72,
        "center_lat": 26.2006,
        "center_lng": 92.9376,
        "zoom": 8,
        "sos_messages": [
            {"message": "Bachao! Brahmaputra mein paani badh gaya, 10 log phanse, Dhubri",
             "language": "Hindi", "lat": 26.01, "lng": 89.97, "survivors": 10},
            {"message": "Help! Barpeta flood, 7 families on rooftop, need boat rescue",
             "language": "English", "lat": 26.32, "lng": 91.01, "survivors": 7},
            {"message": "Bachao! Cachar embankment broken, 12 log trapped",
             "language": "Hindi", "lat": 24.83, "lng": 92.79, "survivors": 12},
            {"message": "Sahajya! Bonna eshechhe, 5 jan, Kamrup",
             "language": "Bengali", "lat": 26.18, "lng": 91.74, "survivors": 5},
            {"message": "Flood emergency, Silchar city submerged, many stranded",
             "language": "English", "lat": 24.82, "lng": 92.80, "survivors": 20},
            {"message": "Bachao! Goalpara mein 8 log chhat par hain",
             "language": "Hindi", "lat": 26.17, "lng": 90.62, "survivors": 8},
        ],
        "satellite_zones": [
            {"zone_name": "Silchar Urban Flood Zone", "center_lat": 24.82, "center_lng": 92.80,
             "flood_severity": 0.89, "area_sqkm": 28.4, "isolated_structures": 45,
             "water_depth_estimate": 2.8, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Dhubri River Overflow", "center_lat": 26.01, "center_lng": 89.97,
             "flood_severity": 0.74, "area_sqkm": 18.2, "isolated_structures": 22,
             "water_depth_estimate": 1.9, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Barpeta Agricultural Zone", "center_lat": 26.32, "center_lng": 91.01,
             "flood_severity": 0.61, "area_sqkm": 35.8, "isolated_structures": 14,
             "water_depth_estimate": 1.2, "data_source": "ESA Sentinel-1 SAR"},
        ],
        "rescue_teams": [
            {"team_name": "NDRF Assam Battalion Unit 1", "team_code": "NDRF-AS-01",
             "unit_type": "NDRF", "current_lat": 26.20, "current_lng": 92.94,
             "personnel_count": 10, "status": "available"},
            {"team_name": "NDRF Assam Battalion Unit 2", "team_code": "NDRF-AS-02",
             "unit_type": "NDRF", "current_lat": 24.85, "current_lng": 92.82,
             "personnel_count": 8, "status": "available"},
            {"team_name": "SDRF Cachar Unit", "team_code": "SDRF-CA-01",
             "unit_type": "SDRF", "current_lat": 24.80, "current_lng": 92.76,
             "personnel_count": 6, "status": "available"},
            {"team_name": "Army Flood Relief Dhubri", "team_code": "ARMY-DH-01",
             "unit_type": "Army", "current_lat": 26.03, "current_lng": 89.99,
             "personnel_count": 12, "status": "available"},
        ],
        "cellular_anomalies": [
            {"tower_id": "T_AS_001", "lat": 24.82, "lng": 92.80,
             "anomaly_type": "dead_zone", "anomaly_score": 0.97, "affected_radius_km": 3.2},
            {"tower_id": "T_AS_002", "lat": 26.01, "lng": 89.97,
             "anomaly_type": "traffic_spike", "anomaly_score": 0.85, "affected_radius_km": 2.0},
            {"tower_id": "T_AS_003", "lat": 26.32, "lng": 91.01,
             "anomaly_type": "dead_zone", "anomaly_score": 0.71, "affected_radius_km": 1.6},
        ],
    },

    "bihar": {
        "id": "bihar",
        "scenario_name": "North Bihar Flash Floods",
        "location": "Muzaffarpur, Darbhanga, Sitamarhi — Bihar",
        "description": "Overflow of Bagmati river has submerged residential blocks, "
                       "forcing thousands onto rooftops.",
        "disaster_type": "FL",
        "severity": "Severe",
        "total_affected": 65,
        "center_lat": 26.1197,
        "center_lng": 85.5160,
        "zoom": 9,
        "sos_messages": [
            {"message": "Bachao! Muzaffarpur mein 8 log phanse hain, station ke paas",
             "language": "Hindi", "lat": 26.12, "lng": 85.36, "survivors": 8},
            {"message": "Madad karo! Darbhanga mein 6 log chhat par, paani bahut tez",
             "language": "Hindi", "lat": 26.15, "lng": 85.90, "survivors": 6},
            {"message": "Help! Sitamarhi flood, 10 families stranded, need urgent rescue",
             "language": "English", "lat": 26.59, "lng": 85.49, "survivors": 10},
            {"message": "Bachao! Samastipur mein baadhh aai hai, 5 log",
             "language": "Hindi", "lat": 25.86, "lng": 85.78, "survivors": 5},
            {"message": "Sahayam! Motihari area 9 jan phanse hain",
             "language": "Hindi", "lat": 26.65, "lng": 84.92, "survivors": 9},
            {"message": "Emergency in Hajipur, flood water entered houses, 7 trapped",
             "language": "English", "lat": 25.69, "lng": 85.21, "survivors": 7},
        ],
        "satellite_zones": [
            {"zone_name": "Bagmati River Overflow", "center_lat": 26.12, "center_lng": 85.36,
             "flood_severity": 0.85, "area_sqkm": 22.4, "isolated_structures": 32,
             "water_depth_estimate": 2.4, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Darbhanga Agricultural Flood", "center_lat": 26.15, "center_lng": 85.90,
             "flood_severity": 0.72, "area_sqkm": 18.8, "isolated_structures": 18,
             "water_depth_estimate": 1.6, "data_source": "ESA Sentinel-1 SAR"},
            {"zone_name": "Sitamarhi Inundation", "center_lat": 26.59, "center_lng": 85.49,
             "flood_severity": 0.65, "area_sqkm": 14.2, "isolated_structures": 15,
             "water_depth_estimate": 1.3, "data_source": "ESA Sentinel-1 SAR"},
        ],
        "rescue_teams": [
            {"team_name": "NDRF Bihar Battalion Unit 1", "team_code": "NDRF-BR-01",
             "unit_type": "NDRF", "current_lat": 26.13, "current_lng": 85.38,
             "personnel_count": 9, "status": "available"},
            {"team_name": "NDRF Bihar Battalion Unit 2", "team_code": "NDRF-BR-02",
             "unit_type": "NDRF", "current_lat": 26.16, "current_lng": 85.92,
             "personnel_count": 7, "status": "available"},
            {"team_name": "SDRF Muzaffarpur", "team_code": "SDRF-MZ-01",
             "unit_type": "SDRF", "current_lat": 26.11, "current_lng": 85.34,
             "personnel_count": 5, "status": "available"},
        ],
        "cellular_anomalies": [
            {"tower_id": "T_BR_001", "lat": 26.12, "lng": 85.36,
             "anomaly_type": "dead_zone", "anomaly_score": 0.91, "affected_radius_km": 2.5},
            {"tower_id": "T_BR_002", "lat": 26.59, "lng": 85.49,
             "anomaly_type": "traffic_spike", "anomaly_score": 0.78, "affected_radius_km": 1.8},
        ],
    },
}


async def load_scenario(scenario_id: str, db_session) -> dict:
    """
    Load a demo scenario into the database.
    Clears existing demo data first, then inserts scenario data.
    """
    from datetime import datetime, timezone
    from db.models import (SOSSignal, SatelliteZone, CellularAnomaly,
                           RescueTeam, DemoScenario)
    from config import PRODUCTION_MODE

    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        raise ValueError(f"Unknown scenario: {scenario_id}. "
                         f"Available: {list(SCENARIOS.keys())}")

    # Clear existing demo data
    await db_session.execute(
        __import__("sqlalchemy").text(
            "DELETE FROM sos_signals WHERE source = 'demo'"
        )
    )
    await db_session.execute(
        __import__("sqlalchemy").text("DELETE FROM satellite_zones")
    )
    await db_session.execute(
        __import__("sqlalchemy").text("DELETE FROM cellular_anomalies")
    )
    await db_session.execute(
        __import__("sqlalchemy").text(
            "DELETE FROM rescue_teams WHERE team_code LIKE 'NDRF-%' "
            "OR team_code LIKE 'SDRF-%' OR team_code LIKE 'CG-%' "
            "OR team_code LIKE 'ARMY-%'"
        )
    )

    now = datetime.now(timezone.utc)

    # Insert SOS messages
    for sos in scenario["sos_messages"]:
        from ai.nlp_engine import NLPEngine
        nlp = NLPEngine()
        result = nlp.classify_sos(sos["message"])
        signal = SOSSignal(
            source="demo",
            raw_message=sos["message"],
            language_detected=sos["language"],
            language_confidence=0.92,
            has_survivor_signal=True,
            survivor_count_estimate=sos["survivors"],
            location_extracted=scenario["location"],
            latitude=sos["lat"],
            longitude=sos["lng"],
            priority_score=result.get("priority_score", 75.0),
            priority_level=result.get("priority_level", "HIGH"),
            data_source=f"Demo Scenario: {scenario['scenario_name']}",
            is_verified=False,
            created_at=now,
            processed_at=now,
        )
        db_session.add(signal)

    # Insert satellite zones
    for zone in scenario["satellite_zones"]:
        sat_zone = SatelliteZone(
            zone_name=zone["zone_name"],
            center_lat=zone["center_lat"],
            center_lng=zone["center_lng"],
            flood_severity=zone["flood_severity"],
            area_sqkm=zone["area_sqkm"],
            isolated_structures=zone["isolated_structures"],
            water_depth_estimate=zone["water_depth_estimate"],
            scenario_id=scenario_id,
            data_source=zone["data_source"],
            last_updated=now,
        )
        db_session.add(sat_zone)

    # Insert rescue teams
    for team in scenario["rescue_teams"]:
        rescue_team = RescueTeam(
            team_name=team["team_name"],
            team_code=team["team_code"],
            unit_type=team["unit_type"],
            current_lat=team["current_lat"],
            current_lng=team["current_lng"],
            personnel_count=team["personnel_count"],
            status=team["status"],
            last_updated=now,
        )
        db_session.add(rescue_team)

    # Insert cellular anomalies
    for anomaly in scenario["cellular_anomalies"]:
        cell = CellularAnomaly(
            tower_id=anomaly["tower_id"],
            lat=anomaly["lat"],
            lng=anomaly["lng"],
            anomaly_type=anomaly["anomaly_type"],
            anomaly_score=anomaly["anomaly_score"],
            affected_radius_km=anomaly["affected_radius_km"],
            created_at=now,
        )
        db_session.add(cell)

    await db_session.commit()

    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario["scenario_name"],
        "sos_loaded": len(scenario["sos_messages"]),
        "zones_loaded": len(scenario["satellite_zones"]),
        "teams_loaded": len(scenario["rescue_teams"]),
        "anomalies_loaded": len(scenario["cellular_anomalies"]),
        "status": "loaded",
    }

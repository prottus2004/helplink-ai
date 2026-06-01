import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import SOSSignal, RescueTeam, SatelliteZone, CellularAnomaly, DemoScenario
from ai.nlp_engine import NLPEngine
from ai.satellite_processor import SatelliteProcessor
from ai.cellular_analyzer import CellularAnalyzer
from config import PRODUCTION_MODE

nlp_engine = NLPEngine()
satellite_processor = SatelliteProcessor()
cellular_analyzer = CellularAnalyzer()

# Wayanad Landslide & Floods Scenario Data
WAYANAD_SOS = [
    {"msg": "രക്ഷിക്കൂ! ഞങ്ങളുടെ വീട് വെള്ളത്തിനടിയിലാണ്. 4 പേർ കുടുങ്ങിക്കിടക്കുന്നു. വയനാട് വൈത്തിരിക്ക് സമീപം.", "lang": "Malayalam", "lat_off": 0.012, "lng_off": -0.015, "src": "whatsapp"},
    {"msg": "വെള്ളം കൂടിക്കൊണ്ടിരിക്കുന്നു, കുഞ്ഞിന് പനി ഉണ്ട്. പനമരം പഞ്ചായത്ത് ഓഫീസിന് അടുത്താണ് ഞങ്ങൾ.", "lang": "Malayalam", "lat_off": -0.022, "lng_off": 0.025, "src": "whatsapp"},
    {"msg": "ഒരുപാടു പേർ ഇവിടെ ഒറ്റപ്പെട്ടിരിക്കുന്നു, കൽപറ്റ ഭാഗത്ത് ഭക്ഷണം ഇല്ല. ദയവായി സഹായിക്കൂ!", "lang": "Malayalam", "lat_off": 0.005, "lng_off": -0.003, "src": "whatsapp"},
    {"msg": "உதவி செய்யுங்கள்! மேப்பாடி அருகே நிலச்சரிவில் சிக்கித் தவிக்கிறோம். 3 பேர் உள்ளனர்.", "lang": "Tamil", "lat_off": 0.021, "lng_off": 0.018, "src": "sms"},
    {"msg": "Flash flood swept our road in Vythiri, need immediate NDRF boat team. 5 people stranded on roof.", "lang": "English", "lat_off": -0.011, "lng_off": -0.024, "src": "twitter"},
    {"msg": "മാനം കറുത്തു പെയ്യുന്നു, വീട് തകരാൻ പോകുന്നു. മാനന്തവാടി റോഡിൽ വെള്ളപ്പൊക്കം.", "lang": "Malayalam", "lat_off": -0.035, "lng_off": 0.008, "src": "whatsapp"},
    {"msg": "We are trapped inside our shop near Meppadi Bazar, water level has crossed 5 feet. Please help!", "lang": "English", "lat_off": 0.018, "lng_off": 0.022, "src": "whatsapp"},
    {"msg": "വയനാട്ടിലെ വെങ്ങപ്പള്ളിയിൽ കനത്ത വെള്ളപ്പൊക്കം, 8 വയസ്സുള്ള കുട്ടി അടക്കം 3 പേർ വീടിനുള്ളിൽ കുടുങ്ങി.", "lang": "Malayalam", "lat_off": 0.028, "lng_off": -0.028, "src": "sms"},
    {"msg": "Help! Landslide blocked the road. Elderly patients trapped at Kalpetta clinic. 4 people.", "lang": "English", "lat_off": 0.003, "lng_off": -0.009, "src": "manual"},
    {"msg": "തരിയോട് ഭാഗത്ത് പുഴ കരകവിഞ്ഞു ഒഴുകുന്നു. കുടുംബം മൊത്തം ടെറസിന് മുകളിലാണ്. 5 പേർ.", "lang": "Malayalam", "lat_off": 0.033, "lng_off": 0.015, "src": "whatsapp"},
    {"msg": "sos vellam kayറുന്നു, sahayikku! nattinpuram muzhuvan mungi.", "lang": "Malayalam", "lat_off": -0.018, "lng_off": 0.031, "src": "sms"},
    {"msg": "Road blocked near Sultan Bathery. Heavy rain, landslide danger. Stranded in car.", "lang": "English", "lat_off": -0.008, "lng_off": 0.035, "src": "twitter"},
    {"msg": "ഉരുൾപൊട്ടൽ ഉണ്ടായിരിക്കുന്നു, പനമരത്ത് ആളുകൾ വീടുകളിൽ കുടുങ്ങി കിടക്കുന്നു. വേഗം വരൂ!", "lang": "Malayalam", "lat_off": -0.025, "lng_off": 0.021, "src": "whatsapp"},
    {"msg": "Danger! Water rising fast in Pozhuthana. No network, sending via manual sat relay. 7 survivors.", "lang": "English", "lat_off": 0.026, "lng_off": -0.005, "src": "manual"},
    {"msg": "മേപ്പാടിയിൽ മണ്ണിടിച്ചിൽ, ആളുകൾ മൺകൂനയ്ക്കടിയിലാണ്, രക്ഷാപ്രവർത്തകർ ഉടൻ എത്തണം.", "lang": "Malayalam", "lat_off": 0.019, "lng_off": 0.020, "src": "whatsapp"}
]

WAYANAD_TEAMS = [
    {"name": "NDRF Kerala Battalion Unit 1", "code": "NDRF-KL-01", "type": "NDRF", "lat_off": -0.05, "lng_off": -0.05, "count": 6},
    {"name": "NDRF Kerala Battalion Unit 2", "code": "NDRF-KL-02", "type": "NDRF", "lat_off": 0.05, "lng_off": 0.05, "count": 8},
    {"name": "SDRF Wayanad Rapid Force", "code": "SDRF-WY-01", "type": "SDRF", "lat_off": -0.02, "lng_off": 0.03, "count": 5},
    {"name": "Indian Army Disaster Division", "code": "ARMY-KL-04", "type": "Army", "lat_off": -0.06, "lng_off": 0.01, "count": 12},
    {"name": "Coast Guard Sea Rescue Unit", "code": "CG-KL-09", "type": "Coast Guard", "lat_off": 0.06, "lng_off": -0.03, "count": 8},
    {"name": "NDRF Volunteer Water Squad", "code": "NDRF-KL-VS", "type": "NDRF", "lat_off": 0.01, "lng_off": -0.04, "count": 4}
]

# Assam Brahmaputra Floods Scenario Data
ASSAM_SOS = [
    {"msg": "সাহায্য কৰক! আমাৰ ঘৰ ডুব গৈছে। মৰিগাঁও জিলাৰ ধৰমতুল অঞ্চলত ৫ জন লোক ফচি আছে।", "lang": "Bengali", "lat_off": 0.025, "lng_off": -0.035, "src": "whatsapp"},
    {"msg": "Brahmaputra river overflowed in Morigaon. Heavy floods, water up to chest level. 6 family members stranded.", "lang": "English", "lat_off": -0.035, "lng_off": 0.045, "src": "whatsapp"},
    {"msg": "সাহায্য কৰক, আমাৰ উচৰত খাবলৈ একো নাই। বানপানীত গোটেই গাওঁ বুৰ গৈছে।", "lang": "Bengali", "lat_off": 0.012, "lng_off": 0.022, "src": "whatsapp"},
    {"msg": "बाढ़ आ गया है, घर के सब लोग छत पर बैठे हैं। खाना पानी भिजवाओ, धरमतुल गाँव। 4 लोग।", "lang": "Hindi", "lat_off": 0.041, "lng_off": -0.015, "src": "sms"},
    {"msg": "Please help! 10 villagers stranded on high platform near Laharighat. Water surrounding all sides.", "lang": "English", "lat_off": -0.015, "lng_off": -0.045, "src": "twitter"},
    {"msg": "মৰিগাঁও হস্পিটালৰ ওচৰত পানী সোমাইছে, পেচেণ্টসকলক ইভাকুৱেট কৰিব লাগে। জৰুৰী সাহায্য!", "lang": "Bengali", "lat_off": -0.045, "lng_off": 0.015, "src": "sms"},
    {"msg": "Morigaon river basin flooded. 3 buildings fully submerged. People trapped inside.", "lang": "English", "lat_off": 0.032, "lng_off": 0.038, "src": "whatsapp"},
    {"msg": "bachao! morigaon ghat ke paas paani baha le gaya sab kuch. 4 log dube hain.", "lang": "Hindi", "lat_off": 0.052, "lng_off": -0.052, "src": "whatsapp"},
    {"msg": "Urgent evacuation needed at Bhuragaon. Flood water level rising 2 inches per hour. 8 survivors.", "lang": "English", "lat_off": -0.022, "lng_off": -0.018, "src": "manual"},
    {"msg": "বানপানী আমাৰ ঘৰৰ ভিতৰত সোমাই গৈছে, ৩টা শিশু সৈতে ৫ জন মানুহ আবদ্ধ হৈ আছো।", "lang": "Bengali", "lat_off": 0.061, "lng_off": 0.028, "src": "whatsapp"},
    {"msg": "Help! Stranded in Mayong sanctuary area. Heavy rain and floods, wild animals nearby. 3 people.", "lang": "English", "lat_off": -0.051, "lng_off": -0.031, "src": "twitter"},
    {"msg": "মৰিগাঁও ৰেলৱে ষ্টেচনৰ কাষত বানপানী। ২০ জন লোক আশ্ৰয় শিবিৰ অবিহনে আবদ্ধ হৈ আছে।", "lang": "Bengali", "lat_off": -0.011, "lng_off": 0.055, "src": "sms"},
    {"msg": "Ghar doob gaya hai poora, madad chahiye. Jagiroad area, Assam. 6 log phanse hain.", "lang": "Hindi", "lat_off": 0.029, "lng_off": -0.061, "src": "whatsapp"},
    {"msg": "Severe flood in Laharighat. Old school building collapsed. 5 people need rescue.", "lang": "English", "lat_off": -0.019, "lng_off": -0.042, "src": "whatsapp"},
    {"msg": "জলমগ্ন হৈ পৰিছে সমগ্ৰ অঞ্চল। খোৱা পানী আৰু ঔষধৰ জৰুৰী প্ৰয়োজন। ধৰমতুল জিলা।", "lang": "Bengali", "lat_off": 0.024, "lng_off": -0.031, "src": "whatsapp"},
    {"msg": "Water entered electricity substation in Morigaon. Power down. 4 operators trapped on tower.", "lang": "English", "lat_off": 0.005, "lng_off": 0.005, "src": "manual"},
    {"msg": "Brahmaputra embankment breached near Laharighat. High speed currents. Send immediate NDRF.", "lang": "English", "lat_off": -0.017, "lng_off": -0.048, "src": "twitter"},
    {"msg": "মৰিগাঁৱৰ পুৰণি বজাৰত পানী উঠিছে, দোকানৰ ওপৰত ৩ জন মানুহ ফচি আছে।", "lang": "Bengali", "lat_off": -0.038, "lng_off": 0.012, "src": "sms"},
    {"msg": "बाढ़ में बह गया हमारा मवेशी, अब हम ऊंचे स्थान पर हैं। भूख लगी है मदद करो। 5 लोग।", "lang": "Hindi", "lat_off": 0.048, "lng_off": -0.029, "src": "whatsapp"},
    {"msg": "Evacuate children from primary school Mayong, water surrounded the compound. 12 trapped.", "lang": "English", "lat_off": -0.048, "lng_off": -0.035, "src": "manual"}
]

ASSAM_TEAMS = [
    {"name": "NDRF Assam Battalion Unit 1", "code": "NDRF-AS-01", "type": "NDRF", "lat_off": -0.07, "lng_off": -0.07, "count": 8},
    {"name": "NDRF Assam Battalion Unit 2", "code": "NDRF-AS-02", "type": "NDRF", "lat_off": 0.07, "lng_off": 0.07, "count": 10},
    {"name": "SDRF Morigaon Disaster Force", "code": "SDRF-MR-01", "type": "SDRF", "lat_off": -0.03, "lng_off": 0.04, "count": 6},
    {"name": "Indian Army Assam Rifles", "code": "ARMY-AS-02", "type": "Army", "lat_off": -0.08, "lng_off": 0.02, "count": 15},
    {"name": "NDRF Flood Special Force", "code": "NDRF-AS-SP", "type": "NDRF", "lat_off": 0.04, "lng_off": -0.06, "count": 8},
    {"name": "Assam State Relief Boat Unit", "code": "SDRF-AS-B03", "type": "SDRF", "lat_off": 0.01, "lng_off": -0.05, "count": 5},
    {"name": "Air Force Guwahati Heli Squad", "code": "IAF-AS-Heli", "type": "Army", "lat_off": 0.09, "lng_off": -0.09, "count": 6},
    {"name": "Assam Volunteers Rescue Boat", "code": "VOL-AS-01", "type": "SDRF", "lat_off": -0.05, "lng_off": -0.02, "count": 4}
]

# North Bihar Flash Floods Scenario Data
BIHAR_SOS = [
    {"msg": "बचाओ! हमारे घर में पानी आ गया है, 5 लोग फँसे हैं। मुजफ्फरपुर स्टेशन के पास हैं।", "lang": "Hindi", "lat_off": 0.015, "lng_off": -0.012, "src": "whatsapp"},
    {"msg": "Heavy flash flood in Muzaffarpur rural area. Bagmati river breached. 8 villagers stranded on temple roof.", "lang": "English", "lat_off": -0.028, "lng_off": 0.035, "src": "whatsapp"},
    {"msg": "हम लोग पानी से घिर गए हैं, बच्चा भूखा है। मुजफ्फरपुर सदर अस्पताल के पास। मदद कीजिये!", "lang": "Hindi", "lat_off": 0.005, "lng_off": -0.008, "src": "whatsapp"},
    {"msg": "Flood water entered our village, crops destroyed. 4 people stuck in mud house, danger of collapse.", "lang": "English", "lat_off": 0.032, "lng_off": -0.022, "src": "sms"},
    {"msg": "SOS! Bagmati river bank overflowed in Katra, water entering homes fast. 6 people trapped.", "lang": "English", "lat_off": -0.015, "lng_off": -0.035, "src": "twitter"},
    {"msg": "मदद कीजिये! बाढ़ के पानी में हमारा बुजुर्ग पिता फँस गया है, मुजफ्फरपुर सदर बाजार।", "lang": "Hindi", "lat_off": -0.032, "lng_off": 0.012, "src": "sms"},
    {"msg": "Water level crossed 6 feet in Aurai. 10 families stranded on high school building roof.", "lang": "English", "lat_off": 0.028, "lng_off": 0.031, "src": "whatsapp"},
    {"msg": "bachao bhaiya! ghar doob raha hai, chhath pe hain 4 bachon ke sath. jaldi boat bhejo.", "lang": "Hindi", "lat_off": 0.042, "lng_off": -0.042, "src": "whatsapp"},
    {"msg": "Urgent evacuation requested at Minapur block. Flash floods entered market area. 8 survivors.", "lang": "English", "lat_off": -0.018, "lng_off": -0.012, "src": "manual"},
    {"msg": "मुजफ्फरपुर के गायघाट में पानी बढ़ रहा है। 5 लोग छज्जे पर बैठे हैं। तुरंत एनडीआरएफ भेजिए।", "lang": "Hindi", "lat_off": 0.051, "lng_off": 0.022, "src": "whatsapp"},
    {"msg": "Help! Road flooded near Kanti thermal power plant. Stuck in truck. 3 people.", "lang": "English", "lat_off": -0.041, "lng_off": -0.028, "src": "twitter"},
    {"msg": "पानी का तेज बहाव है, मुजफ्फरपुर सदर के पास। घर बहने का डर है। 4 लोग फंसे हैं।", "lang": "Hindi", "lat_off": -0.008, "lng_off": 0.045, "src": "sms"},
    {"msg": "Flash floods in Kurhani block. Main highway blocked by water. 7 passengers stranded.", "lang": "English", "lat_off": 0.022, "lng_off": -0.052, "src": "whatsapp"},
    {"msg": "danger! Bagmati floods entered Katra block office. 6 officials trapped inside on first floor.", "lang": "English", "lat_off": -0.012, "lng_off": -0.038, "src": "manual"},
    {"msg": "सहायता दीजिये! गायघाट पंचायत भवन के पास २० लोग फंसे हुए हैं, चारो तरफ बाढ़ का पानी है।", "lang": "Hindi", "lat_off": 0.049, "lng_off": 0.018, "src": "whatsapp"},
    {"msg": "Aurai block primary health center flooded. Patients stranded in medical ward. 12 trapped.", "lang": "English", "lat_off": 0.026, "lng_off": 0.036, "src": "manual"},
    {"msg": "River current extremely violent near Minapur. Evacuation boat capsized. 5 people stranded on tree.", "lang": "English", "lat_off": -0.020, "lng_off": -0.015, "src": "twitter"},
    {"msg": "मदद कीजिये! बाढ़ का पानी बहुत तेज़ है, मुजफ्फरपुर स्टेशन रोड। दुकान के ऊपर ३ लोग फँसे हैं।", "lang": "Hindi", "lat_off": 0.012, "lng_off": -0.009, "src": "sms"}
]

BIHAR_TEAMS = [
    {"name": "NDRF Bihar 9th Battalion U1", "code": "NDRF-BH-01", "type": "NDRF", "lat_off": -0.06, "lng_off": -0.06, "count": 7},
    {"name": "NDRF Bihar 9th Battalion U2", "code": "NDRF-BH-02", "type": "NDRF", "lat_off": 0.06, "lng_off": 0.06, "count": 9},
    {"name": "SDRF Muzaffarpur Division", "code": "SDRF-MZ-01", "type": "SDRF", "lat_off": -0.02, "lng_off": 0.03, "count": 6},
    {"name": "Army Flood Response Team", "code": "ARMY-BH-07", "type": "Army", "lat_off": -0.07, "lng_off": 0.01, "count": 14},
    {"name": "NDRF Water Rescue Special Unit", "code": "NDRF-BH-WR", "type": "NDRF", "lat_off": 0.03, "lng_off": -0.05, "count": 8},
    {"name": "Bihar SDRF Boat Squad 5", "code": "SDRF-BH-B05", "type": "SDRF", "lat_off": 0.01, "lng_off": -0.03, "count": 5},
    {"name": "Red Cross Bihar Heli Relief", "code": "RC-BH-Heli", "type": "Army", "lat_off": 0.08, "lng_off": -0.07, "count": 5}
]

async def load_scenario(scenario_id: str, db: AsyncSession) -> DemoScenario:
    """
    Clears all existing database transaction records and loads all static
    pre-loaded coordinates, NLP SOS messages, simulated SAR layers, and NDRF teams.
    """
    if PRODUCTION_MODE:
        raise ValueError(
            "Cannot load demo scenarios in production mode. Only real data from live APIs is accepted."
        )
    # 1. Clear database completely to prevent conflicts
    await db.execute(delete(SOSSignal))
    await db.execute(delete(RescueTeam))
    await db.execute(delete(SatelliteZone))
    await db.execute(delete(CellularAnomaly))
    await db.execute(delete(DemoScenario))
    await db.commit()

    print(f"[Simulation] Database cleared. Loading Scenario '{scenario_id}'...")

    # Define scenario parameters
    if scenario_id.lower() == "wayanad":
        name = "Wayanad Landslide & Flash Flood, Kerala"
        loc = "Wayanad, Kerala"
        desc = "Severe landslide triggered by heavy monsoon rains in Meppadi and Vythiri. Entire hillsides washed away, flooding the rivers and leaving thousands isolated without food, electricity, or cellular coverage."
        lat, lng = 11.6854, 76.1320
        severity_str = "Catastrophic"
        total_aff = 8500
        sos_source = WAYANAD_SOS
        team_source = WAYANAD_TEAMS
    elif scenario_id.lower() == "assam":
        name = "Brahmaputra Floods, Assam"
        loc = "Morigaon, Assam"
        desc = "Brahmaputra river overflowed its banks following torrential cloudbursts. Large agricultural segments submerged across Laharighat, Mayong, and Bhuragaon districts, trapping communities on elevated structures."
        lat, lng = 26.2006, 92.9376
        severity_str = "Severe"
        total_aff = 12000
        sos_source = ASSAM_SOS
        team_source = ASSAM_TEAMS
    elif scenario_id.lower() == "bihar":
        name = "North Bihar Flash Floods"
        loc = "Muzaffarpur, Bihar"
        desc = "Violent overflow of the Bagmati and Gandak rivers inundated Muzaffarpur, Aurai, Katra, and Minapur blocks, forcing hundreds onto roofs and isolating towns within a 40 km radius."
        lat, lng = 26.1197, 85.5160
        severity_str = "Severe"
        total_aff = 9800
        sos_source = BIHAR_SOS
        team_source = BIHAR_TEAMS
    else:
        raise ValueError(f"Unknown scenario ID '{scenario_id}' requested.")

    # 2. Insert Scenario Profile
    scenario = DemoScenario(
        id=scenario_id.lower(),
        scenario_name=name,
        location=loc,
        description=desc,
        is_active=True,
        disaster_type="Floods & Landslides" if "wayanad" in scenario_id.lower() else "Floods",
        severity=severity_str,
        total_affected=total_aff,
        created_at=datetime.utcnow()
    )
    db.add(scenario)
    
    # 3. Generate Satellite SAR zones via NumPy simulation
    print(f"[Simulation] Simulating Sentinel-1 SAR zones around {lat}, {lng}...")
    sat_zones = satellite_processor.generate_flood_zones(scenario_id.lower(), lat, lng)
    for zone in sat_zones:
        db_zone = SatelliteZone(
            zone_name=zone["zone_name"],
            center_lat=zone["center_lat"],
            center_lng=zone["center_lng"],
            flood_severity=zone["flood_severity"],
            area_sqkm=zone["area_sqkm"],
            isolated_structures=zone["isolated_structures"],
            water_depth_estimate=zone["water_depth_estimate"],
            scenario_id=zone["scenario_id"],
            last_updated=datetime.utcnow()
        )
        db.add(db_zone)

    # 4. Generate Cellular BTS Anomalies
    print(f"[Simulation] Generating cellular connectivity anomaly map...")
    anomalies = await cellular_analyzer.generate_anomalies(scenario_id.lower(), lat, lng)
    for anom in anomalies:
        db_anom = CellularAnomaly(
            tower_id=anom["tower_id"],
            lat=anom["lat"],
            lng=anom["lng"],
            anomaly_type=anom["anomaly_type"],
            anomaly_score=anom["anomaly_score"],
            affected_radius_km=anom["affected_radius_km"],
            created_at=datetime.utcnow()
        )
        db.add(db_anom)

    # 5. Load Pre-loaded SOS Signals
    print(f"[Simulation] Classifying and loading {len(sos_source)} pre-loaded distress messages...")
    for idx, item in enumerate(sos_source):
        # Calculate coordinate offsets
        message_lat = lat + item["lat_off"]
        message_lng = lng + item["lng_off"]
        
        # Analyze using NLP engine
        analysis = nlp_engine.classify_sos(item["msg"])
        
        # Force detected language from scenario parameters to ensure exact demo translations
        analysis["language_detected"] = item["lang"]
        
        signal = SOSSignal(
            source=item["src"],
            raw_message=item["msg"],
            data_source="SIMULATION",
            language_detected=analysis["language_detected"],
            language_confidence=analysis["language_confidence"],
            has_survivor_signal=analysis["has_survivor_signal"],
            survivor_count_estimate=analysis["survivor_count_estimate"],
            location_extracted=analysis["location_extracted"],
            latitude=message_lat,
            longitude=message_lng,
            priority_score=analysis["priority_score"],
            priority_level=analysis["priority_level"],
            is_verified=False,
            # Scatter timestamps backwards to look realistic
            created_at=datetime.utcnow() - timedelta(minutes=(len(sos_source) - idx) * 4)
        )
        db.add(signal)

    # 6. Load Pre-positioned Rescue Teams
    print(f"[Simulation] Pre-positioning {len(team_source)} rescue command teams...")
    for item in team_source:
        team = RescueTeam(
            team_name=item["name"],
            team_code=item["code"],
            unit_type=item["type"],
            current_lat=lat + item["lat_off"],
            current_lng=lng + item["lng_off"],
            status="available",
            assigned_signal_id=None,
            personnel_count=item["count"],
            last_updated=datetime.utcnow()
        )
        db.add(team)

    await db.commit()
    await db.refresh(scenario)
    print(f"[Simulation] Scenario '{scenario_id}' loaded completely! [OK]")
    return scenario

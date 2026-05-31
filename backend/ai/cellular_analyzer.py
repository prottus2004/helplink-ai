import random
import sys
import os
from typing import List, Dict, Any

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENCELLID_API_KEY, USE_REAL_TOWERS
from data.tower_fetcher import fetch_towers_for_scenario

class CellularAnalyzer:
    """
    Simulates cellular base transceiver station (BTS) telemetric health analysis.
    In real disasters, cellular signals undergo anomalies indicating where people are:
    1. 'Dead Zones' (Power/equipment failure) - Tower abruptly shuts down, leaving survivors without network.
    2. 'Traffic Spikes' - A massive, abnormal concentration of simultaneous connection requests, 
       typically matching distress message surges.
    3. 'Signal Drops' - Gradual degradation as water rises and impacts infrastructure.
    """
    
    def __init__(self):
        pass

    async def generate_anomalies(self, scenario_id: str, center_lat: float, center_lng: float) -> List[Dict[str, Any]]:
        """
        Uses real OpenCelliD towers when API key is present, then infers anomaly patterns.
        Falls back to full simulation if live fetch fails or returns no towers.
        """
        if USE_REAL_TOWERS:
            try:
                towers = await fetch_towers_for_scenario(
                    scenario=scenario_id,
                    api_key=OPENCELLID_API_KEY,
                    center_lat=center_lat,
                    center_lng=center_lng,
                )
                if towers:
                    anomalies = self._build_anomalies_from_real_towers(scenario_id, towers)
                    print(f"[Cellular] Using REAL OpenCelliD towers for {scenario_id} ({len(anomalies)} anomalies)")
                    return anomalies
                print("[Cellular] OpenCelliD returned no towers; using simulated anomalies.")
            except Exception as exc:
                print(f"[Cellular] OpenCelliD fetch failed: {exc} - using simulated anomalies.")

        return self._generate_simulated_anomalies(scenario_id, center_lat, center_lng)

    def _generate_simulated_anomalies(self, scenario_id: str, center_lat: float, center_lng: float) -> List[Dict[str, Any]]:
        """
        Simulates tower-level anomalies around the epicenter of the flood scenario.
        Returns a list of 15 to 30 cellular anomaly points.
        """
        # Seeds for reproducibility
        if "wayanad" in scenario_id.lower():
            random.seed(24)
            num_anomalies = 15
            spread = 0.05
        elif "assam" in scenario_id.lower():
            random.seed(88)
            num_anomalies = 25
            spread = 0.09
        else:
            random.seed(456)
            num_anomalies = 18
            spread = 0.07

        anomalies = []
        anomaly_types = ["dead_zone", "traffic_spike", "signal_drop"]
        
        for i in range(num_anomalies):
            # Place towers in cluster nodes around center coordinate
            lat = float(center_lat + random.gauss(0, spread * 0.5))
            lng = float(center_lng + random.gauss(0, spread * 0.5))
            
            anomaly_type = random.choices(
                anomaly_types, 
                weights=[0.45, 0.35, 0.20],  # mostly dead zones and spikes in severe floods
                k=1
            )[0]
            
            # Anomaly score between 0.0 and 1.0 (1.0 = fully disabled tower or extreme peak congestion)
            anomaly_score = round(random.uniform(0.3, 1.0), 2)
            
            # Sub-type dependent radius
            if anomaly_type == "dead_zone":
                affected_radius_km = round(random.uniform(1.2, 3.5), 1)
                # Dead zone score represents power status loss (higher is more critical)
            elif anomaly_type == "traffic_spike":
                affected_radius_km = round(random.uniform(0.5, 1.5), 1)
                # Traffic spike represents active survivors sending distress packets
            else:
                affected_radius_km = round(random.uniform(0.8, 2.0), 1)
            
            tower_id = f"BTS-{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            anomalies.append({
                "tower_id": tower_id,
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "anomaly_type": anomaly_type,
                "anomaly_score": anomaly_score,
                "affected_radius_km": affected_radius_km
            })
            
        return anomalies

    def _build_anomalies_from_real_towers(self, scenario_id: str, towers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Scenario-specific target anomaly volume.
        if "wayanad" in scenario_id.lower():
            random.seed(124)
            target_count = 15
        elif "assam" in scenario_id.lower():
            random.seed(188)
            target_count = 25
        else:
            random.seed(256)
            target_count = 18

        selected = towers[:target_count] if len(towers) >= target_count else towers[:]
        anomalies: List[Dict[str, Any]] = []
        anomaly_types = ["dead_zone", "traffic_spike", "signal_drop"]

        for idx, tower in enumerate(selected):
            # Infer anomaly strength from tower crowd metrics with bounded randomness.
            samples = max(1, int(tower.get("samples", 1)))
            tower_range_m = max(100.0, float(tower.get("range", 1000.0)))
            density_factor = min(samples / 50.0, 1.0)
            range_factor = min(tower_range_m / 5000.0, 1.0)

            anomaly_score = round(min(1.0, 0.35 + (0.4 * density_factor) + (0.2 * range_factor) + random.uniform(0.0, 0.2)), 2)
            anomaly_type = random.choices(anomaly_types, weights=[0.42, 0.38, 0.20], k=1)[0]
            affected_radius_km = round(max(0.4, min(3.8, tower_range_m / 1000.0)), 1)

            anomalies.append({
                "tower_id": tower.get("tower_id", f"OCID-{idx}"),
                "lat": round(float(tower["lat"]), 6),
                "lng": round(float(tower["lng"]), 6),
                "anomaly_type": anomaly_type,
                "anomaly_score": anomaly_score,
                "affected_radius_km": affected_radius_km,
            })

        return anomalies

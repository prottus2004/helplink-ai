import numpy as np
import sys
import os
from typing import List, Dict, Any

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PriorityEngine:
    def __init__(self):
        pass

    def calculate_rescue_priority(
        self,
        sos_signals: List[Dict[str, Any]],
        satellite_zones: List[Dict[str, Any]],
        cellular_anomalies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Geographically fuses:
        1. Satellite SAR severity (Weight: 35%)
        2. SOS NLP distress density (Weight: 40%)
        3. Cellular tower anomaly scores (Weight: 25%)
        
        Computes a unified geopriority index for rescue coordinators.
        """
        priority_clusters = []
        
        # If there are no satellite zones, construct a default grid cluster around the average SOS signals
        if not satellite_zones and sos_signals:
            # Fallback mock zone based on average SOS coordinates
            lats = [s["latitude"] for s in sos_signals]
            lngs = [s["longitude"] for s in sos_signals]
            satellite_zones = [{
                "zone_name": "Grid-Cluster-01",
                "center_lat": float(np.mean(lats)),
                "center_lng": float(np.mean(lngs)),
                "flood_severity": 0.5,
                "area_sqkm": 5.0,
                "isolated_structures": 5,
                "water_depth_estimate": 1.5,
                "scenario_id": "fallback"
            }]
        elif not satellite_zones:
            return []

        # For each satellite flood zone, compute proximity statistics from SOS signals and Cellular anomalies
        for zone in satellite_zones:
            zone_lat = zone["center_lat"]
            zone_lng = zone["center_lng"]
            severity = zone["flood_severity"]
            
            # 1. Filter SOS signals within ~6 km radius (approx 0.05 degrees)
            signals_nearby = []
            total_survivors = 0
            for sig in sos_signals:
                dist = np.sqrt((sig["latitude"] - zone_lat)**2 + (sig["longitude"] - zone_lng)**2)
                if dist <= 0.05:
                    signals_nearby.append(sig)
                    total_survivors += sig.get("survivor_count_estimate", 1)
            
            # Compute SOS signal density score (0.0 to 1.0)
            if signals_nearby:
                avg_sos_priority = np.mean([s["priority_score"] for s in signals_nearby]) / 100.0
                density_factor = min(len(signals_nearby) * 0.15, 0.5)  # cap signal counts component at 0.5
                sos_density = min(avg_sos_priority * 0.5 + density_factor, 1.0)
            else:
                sos_density = 0.0
                
            # 2. Filter Cellular Anomalies within ~6 km radius (approx 0.05 degrees)
            anomalies_nearby = []
            for anom in cellular_anomalies:
                dist = np.sqrt((anom["lat"] - zone_lat)**2 + (anom["lng"] - zone_lng)**2)
                if dist <= 0.05:
                    anomalies_nearby.append(anom)
            
            # Compute cellular anomaly score (0.0 to 1.0)
            if anomalies_nearby:
                # Maximize anomaly priority if a tower is a DEAD ZONE near a flood area
                dead_zones = [a["anomaly_score"] for a in anomalies_nearby if a["anomaly_type"] == "dead_zone"]
                spikes = [a["anomaly_score"] for a in anomalies_nearby if a["anomaly_type"] == "traffic_spike"]
                
                if dead_zones:
                    cellular_score = max(dead_zones)
                elif spikes:
                    cellular_score = max(spikes) * 0.8  # traffic spikes are high but dead zones are silent traps
                else:
                    cellular_score = np.mean([a["anomaly_score"] for a in anomalies_nearby])
            else:
                cellular_score = 0.0
                
            # 3. CORE FUSION ALGORITHM
            # priority_score = ((satellite_severity * 0.35) + (sos_signal_density * 0.40) + (cellular_anomaly_score * 0.25)) * 100
            priority_score = ((severity * 0.35) + (sos_density * 0.40) + (cellular_score * 0.25)) * 100
            
            # Clamp between 0.0 and 100.0
            priority_score = min(max(priority_score, 0.0), 100.0)
            
            # 4. Classify priority levels
            if priority_score >= 75:
                priority_level = "CRITICAL"
            elif priority_score >= 50:
                priority_level = "HIGH"
            elif priority_score >= 25:
                priority_level = "MEDIUM"
            else:
                priority_level = "LOW"
                
            # 5. Recommend Team Type based on flood and survivor conditions
            water_depth = zone.get("water_depth_estimate", 0.0)
            isolated_count = zone.get("isolated_structures", 0)
            
            if water_depth >= 2.5:
                recommended_team = "Water Rescue (NDRF Boat)"
            elif priority_level == "CRITICAL" and (total_survivors >= 8 or isolated_count >= 15):
                recommended_team = "Evacuation & Food Supply (Army Helicopter)"
            else:
                recommended_team = "Medical Support & Relief (SDRF Ambulance)"
                
            priority_clusters.append({
                "zone_name": zone["zone_name"],
                "latitude": round(zone_lat, 6),
                "longitude": round(zone_lng, 6),
                "priority_score": round(float(priority_score), 2),
                "priority_level": priority_level,
                "recommended_team": recommended_team,
                "survivors_estimate": total_survivors,
                "signal_count": len(signals_nearby),
                "water_depth": water_depth,
                "severity": round(severity, 2)
            })
            
        # Sort priority clusters: CRITICAL -> HIGH -> MEDIUM -> LOW
        priority_clusters.sort(key=lambda x: x["priority_score"], reverse=True)
        return priority_clusters

    def calculate_priority(self, zone_data: dict) -> dict:
        """
        Calculate rescue priority from the three data layers.
        Weights: Satellite 35% + SOS density 40% + Cellular 25%
        """
        satellite = float(zone_data.get("satellite_severity", 0))
        sos = float(zone_data.get("sos_signal_density", 0))
        cellular = float(zone_data.get("cellular_anomaly_score", 0))

        score = ((satellite * 0.35) + (sos * 0.40) + (cellular * 0.25)) * 100
        score = round(min(max(score, 0), 100), 2)

        if score >= 75:
            level = "CRITICAL"
            team_type = "Water Rescue (NDRF Boat)"
        elif score >= 50:
            level = "HIGH"
            team_type = "Multi-purpose Rescue (NDRF)"
        elif score >= 25:
            level = "MEDIUM"
            team_type = "Evacuation Support (SDRF)"
        else:
            level = "LOW"
            team_type = "Medical Aid (Civil Defence)"

        return {
            "priority_score": score,
            "priority_level": level,
            "recommended_team": team_type,
            "score_breakdown": {
                "satellite_component": round(satellite * 35, 2),
                "sos_component": round(sos * 40, 2),
                "cellular_component": round(cellular * 25, 2),
            }
        }

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from ai.priority_engine import PriorityEngine

engine = PriorityEngine()

# Test fuse
sos_signals = [
    {"latitude": 22.485, "longitude": 88.289, "survivor_count_estimate": 5, "priority_score": 87.0},
    {"latitude": 22.486, "longitude": 88.290, "survivor_count_estimate": 1, "priority_score": 45.0},
]

satellite_zones = [
    {"zone_name": "TestZone", "center_lat": 22.485, "center_lng": 88.289, "flood_severity": 0.85,
     "area_sqkm": 44, "isolated_structures": 18, "water_depth_estimate": 2.8}
]

cellular_anomalies = [
    {"lat": 22.485, "lng": 88.289, "anomaly_type": "dead_zone", "anomaly_score": 0.8}
]

result = engine.calculate_rescue_priority(sos_signals, satellite_zones, cellular_anomalies)
print(f"Generated {len(result)} priority clusters")

with open('test_priority_output.json', 'w') as f:
    json.dump(result, f, indent=2)
print("Results written to test_priority_output.json")
import asyncio
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from ai.satellite_processor import SatelliteProcessor

proc = SatelliteProcessor()

def test():
    zones = proc.generate_flood_zones("test", 22.48508, 88.28958)
    with open('test_satellite_output.json', 'w', encoding='utf-8') as f:
        json.dump(zones, f, indent=2)
    print(f"Generated {len(zones)} flood zones")
    return zones

test()
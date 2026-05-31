import numpy as np
import random
import sys
import os
from typing import List, Dict, Any

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import COPERNICUS_USER, COPERNICUS_PASS, USE_REAL_SATELLITE
from data.satellite_fetcher import get_real_satellite_zones

class SatelliteProcessor:
    """
    Simulates Sentinel-1 SAR (Synthetic Aperture Radar) processing.
    SAR satellite sensors can 'see' through cloud cover and during night-time,
    which is essential for mapping flood inundation in monsoon season.
    
    Real implementation notes (Copernicus API integration):
    -------------------------------------------------------
    In production, this module would:
    1. Query Copernicus Open Access Hub API (sentinel.esa.int) or a cloud repository like Google Earth Engine
       using a region-of-interest (ROI) bounding box and acquisition date.
    2. Download Level-1 GRD (Ground Range Detected) Sentinel-1 SAR products (VV + VH dual-polarization).
    3. Perform preprocessing via SNAP (Sentinel Application Platform) or python libraries (snappy, pyroSAR):
       - Orbit file application
       - Thermal noise removal
       - Radiometric calibration (backscatter coefficient sigma-nought σ0)
       - Speckle filtering (e.g., Refined Lee filter)
       - Terrain correction (using SRTM 1-arcsec DEM)
    4. Perform binarization/thresholding:
       - Since water is smooth, it exhibits specular reflection and very low backscatter (typically VH < -20 dB).
       - A threshold is applied to classify pixels into 'water' vs 'land'.
    5. Detect changes by comparing flood images to a pre-flood dry reference co-registered image.
    6. Vectorize water bodies to output geoJSON clusters representing submerged zones and count intersected building footprints from OpenStreetMap data.
    """
    
    def __init__(self):
        pass

    def generate_flood_zones(self, scenario_id: str, center_lat: float, center_lng: float) -> List[Dict[str, Any]]:
        """
        Try real Sentinel-1 metadata first, then fall back to deterministic simulation.
        """
        if USE_REAL_SATELLITE:
            real_zones = get_real_satellite_zones(
                scenario=scenario_id,
                username=COPERNICUS_USER,
                password=COPERNICUS_PASS,
                fallback_center_lat=center_lat,
                fallback_center_lng=center_lng,
            )
            if real_zones:
                print(f"[Satellite] Using REAL Sentinel-1 data for {scenario_id} ({len(real_zones)} zones)")
                return real_zones
            print("[Satellite] Real data unavailable - using simulation fallback.")

        return self._generate_simulated_zones(scenario_id, center_lat, center_lng)

    def _generate_simulated_zones(self, scenario_id: str, center_lat: float, center_lng: float) -> List[Dict[str, Any]]:
        """
        Generates realistic flood zones using NumPy to simulate a SAR backscatter map.
        Uses geographic Gaussian distribution around epicenters to model real river basins.
        """
        # Seeds for consistency based on scenario
        if "wayanad" in scenario_id.lower():
            random.seed(42)
            np.random.seed(42)
            num_zones = 8
            spread = 0.04  # degree spread (~4-5 km)
        elif "assam" in scenario_id.lower():
            random.seed(99)
            np.random.seed(99)
            num_zones = 14
            spread = 0.08  # larger river basin spread
        else:
            random.seed(123)
            np.random.seed(123)
            num_zones = 10
            spread = 0.06

        zones = []
        
        # We model 3 main "river overflow epicenters" for the scenario
        epicenters = [
            (center_lat + np.random.normal(0, spread * 0.4), center_lng + np.random.normal(0, spread * 0.4)),
            (center_lat + np.random.normal(0, spread * 0.6), center_lng + np.random.normal(0, spread * 0.6)),
            (center_lat + np.random.normal(0, spread * 0.3), center_lng + np.random.normal(0, spread * 0.3))
        ]

        for i in range(num_zones):
            # Choose a random epicenter to cluster near
            epicenter = random.choice(epicenters)
            
            # Generate zone center using Gaussian distribution
            lat = float(epicenter[0] + np.random.normal(0, spread * 0.3))
            lng = float(epicenter[1] + np.random.normal(0, spread * 0.3))
            
            # Calculate distance from closest epicenter to scale severity
            distances = [np.sqrt((lat - ep[0])**2 + (lng - ep[1])**2) for ep in epicenters]
            min_dist = min(distances)
            
            # Flood severity is higher near epicenters (simulating low elevation valleys)
            # Uses exponential decay model
            severity = float(np.exp(-min_dist / (spread * 0.8)))
            # Add a bit of natural variance
            severity = min(max(severity * random.uniform(0.85, 1.15), 0.1), 1.0)
            
            # Scale other metrics logically based on severity
            area_sqkm = round(float(severity * random.uniform(2.5, 9.5)), 2)
            # Higher severity = more structures cut off
            isolated_structures = int(severity * random.randint(12, 45))
            # Severity correlates with estimated water depth
            water_depth_estimate = round(float(severity * random.uniform(1.5, 5.0)), 1)
            
            # Zone naming based on coordinate quadrant
            direction = ""
            if lat > center_lat: direction += "North"
            else: direction += "South"
            if lng > center_lng: direction += "East"
            else: direction += "West"
            
            zone_name = f"SAR-Zone-{direction}-{i+1:02d}"
            
            zones.append({
                "zone_name": zone_name,
                "center_lat": round(lat, 6),
                "center_lng": round(lng, 6),
                "flood_severity": round(severity, 2),
                "area_sqkm": area_sqkm,
                "isolated_structures": isolated_structures,
                "water_depth_estimate": water_depth_estimate,
                "scenario_id": scenario_id,
                "last_updated": None  # Will be populated by the DB model default
            })
            
        # Sort by severity descending so commanders see critical ones first
        zones.sort(key=lambda x: x["flood_severity"], reverse=True)
        return zones

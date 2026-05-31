import asyncio
import json
from pathlib import Path
from typing import Dict, List, Tuple

import httpx

OPENCELLID_BASE = "https://opencellid.org/cell/getInArea"
CACHE_DIR = Path(__file__).resolve().parent / "tower_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SCENARIO_CENTERS = {
    "wayanad": (11.6854, 76.1320),
    "assam": (26.2006, 92.9376),
    "bihar": (26.1197, 85.5160),
}

# Regional fallback scan anchors when the exact scenario epicenter has sparse coverage.
SCENARIO_FALLBACK_CENTERS = {
    "assam": [
        (26.2500, 92.3500),  # Morigaon region
        (26.3500, 92.6800),  # Nagaon corridor
    ],
    "bihar": [
        (26.1200, 85.4500),  # Muzaffarpur west corridor
        (26.0300, 85.6200),  # Muzaffarpur east corridor
    ],
}


def _build_bbox(center_lat: float, center_lng: float, box_size_deg: float) -> str:
    half = box_size_deg / 2.0
    min_lat = center_lat - half
    min_lng = center_lng - half
    max_lat = center_lat + half
    max_lng = center_lng + half
    return f"{min_lat:.6f},{min_lng:.6f},{max_lat:.6f},{max_lng:.6f}"


async def _fetch_tile_cells(
    client: httpx.AsyncClient,
    api_key: str,
    bbox: str,
    mcc: int | None = 404,
    limit: int = 250,
) -> List[Dict]:
    params = {
        "key": api_key,
        "BBOX": bbox,
        "format": "json",
        "limit": str(limit),
    }
    if mcc is not None:
        params["mcc"] = str(mcc)

    resp = await client.get(OPENCELLID_BASE, params=params)
    payload = resp.json()

    # OpenCelliD returns {"error": "...", "code": 3/5} for oversized bbox.
    if isinstance(payload, dict) and payload.get("error"):
        return []
    return payload.get("cells", []) if isinstance(payload, dict) else []


def _dedupe_cells(cells: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for cell in cells:
        key = (
            cell.get("mcc"),
            cell.get("mnc"),
            cell.get("lac"),
            cell.get("cellid"),
            cell.get("lat"),
            cell.get("lon"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(cell)
    return unique


def _normalize_cell(cell: Dict) -> Dict:
    lat = float(cell.get("lat", 0.0))
    lng = float(cell.get("lon", 0.0))
    mcc = cell.get("mcc", "404")
    mnc = cell.get("mnc", "00")
    cellid = cell.get("cellid", "0")

    return {
        "tower_id": f"OCID-{mcc}-{mnc}-{cellid}",
        "lat": lat,
        "lng": lng,
        "mcc": mcc,
        "mnc": mnc,
        "lac": cell.get("lac"),
        "cellid": cellid,
        "radio": cell.get("radio", "UNKNOWN"),
        "range": float(cell.get("range", 1000) or 1000),
        "samples": int(cell.get("samples", 1) or 1),
    }


async def _fetch_plan_cells(
    client: httpx.AsyncClient,
    api_key: str,
    center_lat: float,
    center_lng: float,
    offsets: Tuple[float, ...],
    box_size: float,
    mcc: int | None = 404,
    limit: int = 250,
) -> List[Dict]:
    semaphore = asyncio.Semaphore(10)

    async def fetch_one(dlat: float, dlng: float) -> List[Dict]:
        bbox = _build_bbox(center_lat + dlat, center_lng + dlng, box_size)
        async with semaphore:
            try:
                return await _fetch_tile_cells(client, api_key, bbox, mcc=mcc, limit=limit)
            except Exception as exc:
                print(f"[Towers] Tile fetch failed for {bbox}: {exc}")
                return []

    tasks = [fetch_one(dlat, dlng) for dlat in offsets for dlng in offsets]
    results = await asyncio.gather(*tasks)

    merged: List[Dict] = []
    for part in results:
        merged.extend(part)
    return merged


async def _collect_cells_for_center(
    client: httpx.AsyncClient,
    api_key: str,
    center_lat: float,
    center_lng: float,
    search_plans: List[Dict],
    mcc: int | None,
) -> List[Dict]:
    collected: List[Dict] = []
    for plan in search_plans:
        collected.extend(
            await _fetch_plan_cells(
                client=client,
                api_key=api_key,
                center_lat=center_lat,
                center_lng=center_lng,
                offsets=plan["offsets"],
                box_size=plan["box_size"],
                mcc=mcc,
            )
        )
        if len(_dedupe_cells(collected)) >= 120:
            break
    return collected


async def fetch_towers_for_scenario(
    scenario: str,
    api_key: str,
    center_lat: float | None = None,
    center_lng: float | None = None,
) -> List[Dict]:
    """
    Fetch real tower coordinates from OpenCelliD.
    We query multiple small tiles because getInArea enforces a 4,000,000 sq.m limit.
    """
    scenario_key = scenario.lower()
    cache_file = CACHE_DIR / f"towers_{scenario_key}.json"

    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as fh:
            cached = json.load(fh)
        if cached:
            print(f"[Towers] Using cached OpenCelliD data for {scenario_key}: {len(cached)} towers")
            return cached
        print(f"[Towers] Empty cache found for {scenario_key}; refetching OpenCelliD tiles.")

    if center_lat is None or center_lng is None:
        center_lat, center_lng = SCENARIO_CENTERS.get(scenario_key, SCENARIO_CENTERS["wayanad"])

    # Adaptive tile search: start tight, then widen if sparse.
    search_plans = [
        {"offsets": (-0.010, 0.000, 0.010), "box_size": 0.008},
        {"offsets": (-0.030, -0.015, 0.000, 0.015, 0.030), "box_size": 0.010},
        {"offsets": (-0.060, -0.030, 0.000, 0.030, 0.060), "box_size": 0.012},
    ]
    all_cells: List[Dict] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Primary search around scenario center (India MCC=404).
        all_cells.extend(
            await _collect_cells_for_center(
                client=client,
                api_key=api_key,
                center_lat=center_lat,
                center_lng=center_lng,
                search_plans=search_plans,
                mcc=404,
            )
        )

        # Regional fallback anchors for sparse districts.
        if not all_cells:
            for alt_lat, alt_lng in SCENARIO_FALLBACK_CENTERS.get(scenario_key, []):
                print(
                    f"[Towers] No cells near scenario center for {scenario_key}; "
                    f"retrying regional anchor ({alt_lat}, {alt_lng})."
                )
                all_cells.extend(
                    await _collect_cells_for_center(
                        client=client,
                        api_key=api_key,
                        center_lat=alt_lat,
                        center_lng=alt_lng,
                        search_plans=search_plans,
                        mcc=404,
                    )
                )
                if all_cells:
                    break

        # Final sweep without MCC filter in case regional MCC labeling differs.
        if not all_cells:
            print(f"[Towers] No cells with MCC=404 for {scenario_key}; retrying without MCC filter.")
            all_cells.extend(
                await _collect_cells_for_center(
                    client=client,
                    api_key=api_key,
                    center_lat=center_lat,
                    center_lng=center_lng,
                    search_plans=search_plans,
                    mcc=None,
                )
            )

    unique_cells = _dedupe_cells(all_cells)
    towers = [_normalize_cell(cell) for cell in unique_cells if "lat" in cell and "lon" in cell]

    # Keep the geographically nearest towers to the scenario epicenter.
    towers.sort(key=lambda t: (t["lat"] - center_lat) ** 2 + (t["lng"] - center_lng) ** 2)

    # Keep payload bounded for dashboard usage.
    towers = towers[:1200]

    # Cache only non-empty results to avoid sticky empty-cache fallbacks.
    if towers:
        with cache_file.open("w", encoding="utf-8") as fh:
            json.dump(towers, fh, ensure_ascii=False)
        print(f"[Towers] Cached OpenCelliD towers for {scenario_key}: {len(towers)}")
    else:
        print(f"[Towers] No OpenCelliD towers found for {scenario_key} after adaptive search.")

    return towers

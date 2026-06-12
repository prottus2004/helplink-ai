"""
data_generator.py
Generates incremental demo data during live simulation.
Only used when DEMO_MODE is enabled.
"""
import random
from datetime import datetime, timezone
from config import PRODUCTION_MODE


async def simulate_realtime_update(db_session=None) -> int:
    """Blocked in production mode."""
    if PRODUCTION_MODE:
        return 0
    return 0

import os
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

# Local dev uses SQLite (no asyncpg needed on Windows)
# Railway sets DATABASE_URL automatically to postgresql://...
_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./helplink_dev.db")

# SQLAlchemy async needs postgresql+asyncpg://, not postgresql://
if _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url  # SQLite for local dev
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
WEBSOCKET_REFRESH_INTERVAL = int(os.getenv("WEBSOCKET_REFRESH_INTERVAL", 10))  # seconds

# DEMO_MODE is disabled by default for production deployments
# Use environment variable DEMO_MODE=true only for local demo development
DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "yes")

# Production mode flag (explicit). When True:
# - Simulation endpoints are disabled
# - No fake SOS generation runs
# - Real data pollers are scheduled
PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "True").lower() in ("true", "1", "yes")

# Default NLP_MODE to "keyword" to ensure 100% offline, zero-latency execution.
# To activate the advanced HuggingFace multilingual transformer model, switch this to "transformer".
NLP_MODE = os.getenv("NLP_MODE", "keyword")  # "keyword" or "transformer"

# Copernicus Sentinel-1 integration (optional; falls back to simulation when absent/failing)
COPERNICUS_USER = os.getenv("COPERNICUS_USER", "")
COPERNICUS_PASS = os.getenv("COPERNICUS_PASS", "")
USE_REAL_SATELLITE = bool(COPERNICUS_USER and COPERNICUS_PASS)

# OpenCelliD integration (optional; falls back to simulation when missing/failing)
OPENCELLID_API_KEY = os.getenv("OPENCELLID_API_KEY", "")
USE_REAL_TOWERS = bool(OPENCELLID_API_KEY)

# Twitter/X integration for live SOS tweet monitoring (optional)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
USE_REAL_TWEETS = bool(TWITTER_BEARER_TOKEN)

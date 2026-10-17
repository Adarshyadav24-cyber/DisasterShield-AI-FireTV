"""
DisasterShield AI - Configuration Module
Tagline: Early Awareness. Verified Information. Safer Decisions.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Brand & Disclaimers
APP_NAME = "DisasterShield AI"
TAGLINE = "Early Awareness. Verified Information. Safer Decisions."
PROTOTYPE_NOTICE = (
    "DisasterShield AI is an informational prototype, not an official emergency service. "
    "Verify alerts and follow instructions from authorized local authorities. "
    "Do not rely on this prototype alone for evacuation decisions."
)

# AI Model Configuration (Google Gemma 4 ONLY)
GEMMA_ENDPOINT_URL = os.getenv("GEMMA_ENDPOINT_URL", "http://localhost:11434").rstrip("/")
GEMMA_MODEL_NAME = os.getenv("GEMMA_MODEL_NAME", "gemma4:e2b")
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY", "")
GEMMA_TIMEOUT_SECONDS = int(os.getenv("GEMMA_TIMEOUT_SECONDS", "8"))

# Demonstration Cities (Documented approximate city-centre coordinates)
DEMO_CITIES = {
    "Prayagraj, Uttar Pradesh": {
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 25.4358,
        "lon": 81.8463,
        "zoom": 13,
        "river": "Ganga & Yamuna Confluence (Sangam)",
        "description": "Confluence basin prone to seasonal monsoon river inundation.",
    },
    "Lucknow, Uttar Pradesh": {
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 26.8467,
        "lon": 80.9462,
        "zoom": 13,
        "river": "Gomti River Basin",
        "description": "State capital sector with Gomti riverfront drainage corridors.",
    },
    "Varanasi, Uttar Pradesh": {
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 25.3176,
        "lon": 82.9739,
        "zoom": 13,
        "river": "Ganga Riverfront (Ghats)",
        "description": "Ancient dense riverfront settlement with terraced ghat flood surveillance.",
    },
    "New Delhi, India": {
        "city": "New Delhi",
        "state": "National Capital Territory",
        "country": "India",
        "lat": 28.6139,
        "lon": 77.2090,
        "zoom": 12,
        "river": "Yamuna River Floodplain",
        "description": "National capital territory with Yamuna floodplain and urban stormwater corridors.",
    },
}

# Geospatial Demonstration Defaults
DEFAULT_LOCATION_NAME = "Prayagraj, Uttar Pradesh"
DEFAULT_LAT = DEMO_CITIES[DEFAULT_LOCATION_NAME]["lat"]
DEFAULT_LON = DEMO_CITIES[DEFAULT_LOCATION_NAME]["lon"]
DEFAULT_ZOOM = DEMO_CITIES[DEFAULT_LOCATION_NAME]["zoom"]

# Administrator Verification
ADMIN_VERIFY_PIN = os.getenv("ADMIN_VERIFY_PIN", "1122")

# Weather API (Open-Meteo public free service)
ENABLE_LIVE_WEATHER = os.getenv("ENABLE_LIVE_WEATHER", "true").lower() in ("true", "1", "yes")
WEATHER_API_TIMEOUT = int(os.getenv("WEATHER_API_TIMEOUT", "6"))

# File Storage Paths
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEMO_INCIDENTS_PATH = DATA_DIR / "demo_incidents.json"
DEMO_RESOURCES_PATH = DATA_DIR / "demo_resources.json"
USER_INCIDENTS_PATH = DATA_DIR / "user_incidents.json"

# Categorization & Enums
CATEGORIES = ["flood", "fire", "earthquake", "storm", "landslide", "other"]
SEVERITY_LEVELS = ["Low", "Moderate", "High", "Critical"]
VERIFICATION_STATUSES = ["UNVERIFIED", "VERIFIED", "REJECTED", "INVESTIGATING"]

SEVERITY_COLORS = {
    "Low": "#10B981",       # Emerald
    "Moderate": "#F59E0B",  # Amber
    "High": "#EF4444",      # Rose Red
    "Critical": "#7F1D1D",  # Dark Crimson
}

CATEGORY_ICONS = {
    "flood": "🌊",
    "fire": "🔥",
    "earthquake": "🌋",
    "storm": "⛈️",
    "landslide": "⛰️",
    "other": "⚠️",
}

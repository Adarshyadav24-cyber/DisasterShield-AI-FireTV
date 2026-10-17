"""
DisasterShield AI - Weather & Environmental Data Service
Queries the public Open-Meteo API without requiring any API keys.
Maintains strict separation from generative AI components.
Provides transparent fallbacks when network or public API is unreachable.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests

import config

# WMO Weather Interpretation Codes
WMO_CODE_MAP = {
    0: "Clear Sky ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing Rime Fog 🌫️",
    51: "Light Drizzle 🌧️",
    53: "Moderate Drizzle 🌧️",
    55: "Dense Drizzle 🌧️",
    61: "Slight Rain 🌦️",
    63: "Moderate Rain 🌧️",
    65: "Heavy Monsoon Rain ⛈️",
    71: "Slight Snow Fall ❄️",
    73: "Moderate Snow Fall ❄️",
    75: "Heavy Snow Fall ❄️",
    80: "Slight Rain Showers 🌦️",
    81: "Moderate Rain Showers 🌧️",
    82: "Violent Rain Showers ⛈️",
    95: "Thunderstorm ⚡⛈️",
    96: "Thunderstorm with Slight Hail ⛈️🌨️",
    99: "Thunderstorm with Heavy Hail ⛈️🌨️",
}


class WeatherService:
    """Provides public meteorological telemetry with clear source attribution."""

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or config.WEATHER_API_TIMEOUT

    def get_weather(self, latitude: float, longitude: float, location_name: str = "") -> Dict[str, Any]:
        """
        Fetches live weather from Open-Meteo public API.
        If unavailable, returns a clearly labeled simulated demo record.
        """
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
            f"&timezone=auto"
        )

        try:
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                code = current.get("weather_code", 0)
                condition_desc = WMO_CODE_MAP.get(code, f"Weather Code {code}")

                return {
                    "status": "SUCCESS",
                    "is_simulated": False,
                    "source": "Open-Meteo Public Meteorological API",
                    "timestamp": current.get("time", now_iso),
                    "location_name": location_name or f"Coords ({latitude:.3f}, {longitude:.3f})",
                    "latitude": latitude,
                    "longitude": longitude,
                    "temperature_c": current.get("temperature_2m"),
                    "humidity_percent": current.get("relative_humidity_2m"),
                    "precipitation_mm": current.get("precipitation"),
                    "wind_speed_kmh": current.get("wind_speed_10m"),
                    "weather_code": code,
                    "condition": condition_desc,
                    "disclaimer": "Live telemetry provided by public Open-Meteo API. Check official IMD/district bulletins for alerts.",
                }
        except Exception as e:
            # Network failed or timeout
            print(f"[Notice] Weather API query for ({latitude}, {longitude}) failed: {e}. Using labeled demo fallback.")

        # Clearly labeled Demo / Simulated Fallback
        return {
            "status": "DEMO_FALLBACK",
            "is_simulated": True,
            "source": "Simulated Demo Telemetry (API Offline/Unreachable)",
            "timestamp": now_iso,
            "location_name": location_name or f"Prayagraj Sector ({latitude:.3f}, {longitude:.3f})",
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": 28.5,
            "humidity_percent": 84,
            "precipitation_mm": 12.4,
            "wind_speed_kmh": 22.0,
            "weather_code": 63,
            "condition": "Moderate Rain [Simulated Demo] 🌧️",
            "disclaimer": "DEMO DATA: Weather service could not connect to live API. This reading is simulated for demonstration only.",
        }

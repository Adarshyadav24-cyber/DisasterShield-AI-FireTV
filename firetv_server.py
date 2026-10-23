"""
DisasterShield AI - Fire TV Server & REST Bridge
Serves the Fire TV 10-foot web application and provides REST APIs connecting
the TV interface with IncidentManager, WeatherService, and Google Gemma 4 client.
"""
from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure project root in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from modules.incident_manager import IncidentManager
from modules.gemma_client import GemmaClient
from modules.weather_service import WeatherService
from modules.simulation_3d import build_3d_simulation_html
from modules.safety_briefing import get_safety_protocol, STANDARD_SAFETY_GUIDANCE

from flask import Flask, request, jsonify, send_from_directory, Response

app = Flask(__name__, static_folder="firetv", static_url_path="")

# Initialize backend services
incident_mgr = IncidentManager()
gemma_client = GemmaClient()
weather_svc = WeatherService()

# In-memory active sector state
active_sector = {
    "name": config.DEFAULT_LOCATION_NAME,
    "lat": config.DEFAULT_LAT,
    "lon": config.DEFAULT_LON,
}


@app.after_request
def add_cors_headers(response):
    """Enable CORS for TV emulators and local network clients."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/")
def serve_tv_index():
    """Serves the Fire TV 10-foot user interface."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_tv_static(path):
    """Serves static assets (css, js, manifest)."""
    return send_from_directory(app.static_folder, path)


@app.route("/simulation-embed")
def serve_simulation_embed():
    """Renders the standalone 3D Three.js simulation canvas for TV embedding."""
    city_name = request.args.get("city", active_sector["name"])
    disaster_mode = request.args.get("mode", "Flood")
    
    city_meta = config.DEMO_CITIES.get(city_name, config.DEMO_CITIES[config.DEFAULT_LOCATION_NAME])
    city_short = city_meta.get("city", "Prayagraj")
    
    incidents = incident_mgr.filter_incidents(city=city_short)
    resources = incident_mgr.get_all_resources(city=city_short)
    
    html = build_3d_simulation_html(
        incidents=incidents,
        resources=resources,
        center_lat=city_meta["lat"],
        center_lon=city_meta["lon"],
        city_name=city_name,
        disaster_mode=disaster_mode,
        water_level=3.5,
        earthquake_intensity=4.2,
        rainfall_rate=45.0,
    )
    return Response(html, mimetype="text/html")


@app.route("/api/health", methods=["GET"])
def api_health():
    """System health check endpoint."""
    return jsonify({
        "status": "HEALTHY",
        "app": config.APP_NAME,
        "platform": "Amazon Fire TV / Fire OS Compatible",
        "tagline": config.TAGLINE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/status", methods=["GET"])
def api_status():
    """Aggregates telemetry, metrics, and AI status for the TV dashboard."""
    city_name = request.args.get("city", active_sector["name"])
    city_meta = config.DEMO_CITIES.get(city_name, config.DEMO_CITIES[config.DEFAULT_LOCATION_NAME])
    city_short = city_meta.get("city", "Prayagraj")

    # Fetch weather
    weather_data = weather_svc.get_weather(city_meta["lat"], city_meta["lon"], city_name)
    
    # Incident summary metrics
    metrics = incident_mgr.get_summary_metrics(city=city_short)
    
    # Active incidents
    incidents = incident_mgr.filter_incidents(city=city_short)
    
    # AI Probe status
    is_connected, msg = gemma_client.probe_connection()

    return jsonify({
        "sector": {
            "name": city_name,
            "short_city": city_short,
            "lat": city_meta["lat"],
            "lon": city_meta["lon"],
            "river": city_meta.get("river", ""),
            "description": city_meta.get("description", ""),
        },
        "metrics": {
            "total": metrics["total_reports"],
            "verified": metrics["verified_count"],
            "unverified": metrics["unverified_count"],
            "critical": metrics["high_priority_count"],
            "threat": metrics["overall_risk"].upper(),
            "threatColor": metrics["risk_color"],
        },
        "weather": {
            "temp": weather_data.get("temperature_c", 28),
            "condition": weather_data.get("condition", "Partly Cloudy ⛅"),
            "wind": weather_data.get("wind_speed_kmh", 12),
            "precip": weather_data.get("precipitation_mm", 0),
            "isSimulated": weather_data.get("is_simulated", False),
            "source": weather_data.get("source", "Open-Meteo API"),
        },
        "ai": {
            "is_connected": is_connected,
            "model_name": config.GEMMA_MODEL_NAME,
            "endpoint_url": gemma_client.endpoint_url,
            "status_message": msg,
        },
        "incidents": incidents[:6],
    })


@app.route("/api/sector", methods=["POST"])
def api_set_sector():
    """Switches the active demonstration city sector."""
    data = request.get_json(silent=True) or {}
    city_name = data.get("city", config.DEFAULT_LOCATION_NAME)
    if city_name in config.DEMO_CITIES:
        active_sector["name"] = city_name
        active_sector["lat"] = config.DEMO_CITIES[city_name]["lat"]
        active_sector["lon"] = config.DEMO_CITIES[city_name]["lon"]
        return jsonify({"status": "SUCCESS", "active_sector": active_sector})
    return jsonify({"status": "ERROR", "message": f"Unknown city {city_name}"}), 400


@app.route("/api/ai/probe", methods=["GET"])
def api_ai_probe():
    """Forces an active network probe of the Google Gemma 4 inference server."""
    is_connected, msg = gemma_client.probe_connection(force_refresh=True)
    return jsonify({
        "is_connected": is_connected,
        "message": msg,
        "model": config.GEMMA_MODEL_NAME,
        "endpoint": gemma_client.endpoint_url,
    })


@app.route("/api/ai/ask", methods=["POST"])
def api_ai_ask():
    """Grounded AI situation synthesis or plain-language guidance query."""
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    city_name = data.get("city", active_sector["name"])
    city_meta = config.DEMO_CITIES.get(city_name, config.DEMO_CITIES[config.DEFAULT_LOCATION_NAME])
    city_short = city_meta.get("city", "Prayagraj")

    incidents = incident_mgr.filter_incidents(city=city_short)
    weather_data = weather_svc.get_weather(city_meta["lat"], city_meta["lon"], city_name)
    resources = incident_mgr.get_all_resources(city=city_short)

    prompt_lower = prompt.lower()

    if "shelter" in prompt_lower or "briefing" in prompt_lower or "situation" in prompt_lower:
        result = gemma_client.generate_situation_briefing(incidents, weather_data, resources)
    elif "flood" in prompt_lower:
        proto = get_safety_protocol("flood")
        result = gemma_client.rewrite_safety_instructions("flood", proto["official_guidance"])
    elif "fire" in prompt_lower:
        proto = get_safety_protocol("fire")
        result = gemma_client.rewrite_safety_instructions("fire", proto["official_guidance"])
    elif "earthquake" in prompt_lower:
        proto = get_safety_protocol("earthquake")
        result = gemma_client.rewrite_safety_instructions("earthquake", proto["official_guidance"])
    elif "storm" in prompt_lower:
        proto = get_safety_protocol("storm")
        result = gemma_client.rewrite_safety_instructions("storm", proto["official_guidance"])
    else:
        result = gemma_client.summarize_incidents(incidents)

    return jsonify({
        "content": result.content,
        "is_ai_generated": result.is_ai_generated,
        "model_identifier": result.model_identifier,
        "status": result.status,
        "latency_ms": result.latency_ms,
        "disclaimer": result.disclaimer,
    })


@app.route("/api/guidance/<category>", methods=["GET"])
def api_guidance(category):
    """Fetches verified standard safety protocol for a category."""
    protocol = get_safety_protocol(category)
    return jsonify(protocol)


def run_server(port: int = 8000, host: str = "0.0.0.0"):
    """Starts the Flask server."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("\n========================================================")
    print("DisasterShield AI - Fire TV Server")
    print(f"Tagline: {config.TAGLINE}")
    print(f"Fire TV App URL:  http://localhost:{port}/")
    print(f"Health Endpoint:  http://localhost:{port}/api/health")
    print("Target: Amazon Fire TV / Fire OS 10-foot UI")
    print("========================================================\n")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    port = int(os.environ.get("FIRETV_PORT", 8000))
    run_server(port=port)

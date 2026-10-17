"""
Unit tests for DisasterShield AI 3D Simulation Module (simulation_3d.py).
Covers:
- HTML / WebGL generation
- Disaster scenario matrix support (Flood, Fire, Earthquake, Storm)
- Incident and emergency resource injection
- Dynamic water elevation, seismic tremor, and precipitation parameter bindings
- Safety disclaimers and demo simulation watermarks
"""
import pytest
from modules.simulation_3d import build_3d_simulation_html


@pytest.fixture
def sample_3d_data():
    incidents = [
        {
            "id": "INC-3D-001",
            "category": "flood",
            "title": "Low-lying Ghat Inundation",
            "description": "River water overflowing lower ghat steps.",
            "location_name": "Daraganj Riverbank",
            "latitude": 25.4285,
            "longitude": 81.8742,
            "severity": "High",
            "verification_status": "VERIFIED",
            "report_time": "2026-10-17T08:00:00Z",
            "reporter_label": "Civil Defense",
            "is_demo": True,
        },
        {
            "id": "INC-3D-002",
            "category": "fire",
            "title": "Warehouse Attic Sparks",
            "description": "Smoke visible above commercial godown.",
            "location_name": "Katra Market",
            "latitude": 25.4628,
            "longitude": 81.8519,
            "severity": "Critical",
            "verification_status": "UNVERIFIED",
            "report_time": "2026-10-17T09:00:00Z",
            "reporter_label": "Citizen Post",
            "is_demo": True,
        },
    ]
    resources = [
        {
            "id": "RES-3D-001",
            "name": "District Trauma Hospital",
            "type": "Medical Facility",
            "description": "Emergency triage beds.",
            "location_name": "George Town",
            "latitude": 25.4420,
            "longitude": 81.8545,
            "capacity": "250 Beds",
            "status": "Operational",
            "official_helpline_info": "Dial 112",
            "is_demo": True,
        }
    ]
    return incidents, resources


def test_build_3d_simulation_html_structure(sample_3d_data):
    incidents, resources = sample_3d_data
    html = build_3d_simulation_html(
        incidents=incidents,
        resources=resources,
        disaster_mode="Flood",
        water_level=4.5,
    )

    # Core Structural Assertions
    assert "<!DOCTYPE html>" in html
    assert "canvas-container" in html
    assert "3D DIGITAL TWIN" in html
    assert "DEMO SIMULATION" in html
    assert "WebGLRenderer" in html or "THREE" in html


def test_disaster_modes_and_parameters(sample_3d_data):
    incidents, resources = sample_3d_data

    # Test Flood
    flood_html = build_3d_simulation_html(incidents, resources, disaster_mode="Flood", water_level=6.2)
    assert "FLOOD" in flood_html
    assert "6.2" in flood_html

    # Test Earthquake
    quake_html = build_3d_simulation_html(incidents, resources, disaster_mode="Earthquake", earthquake_intensity=7.4)
    assert "QUAKE" in quake_html
    assert "7.4" in quake_html

    # Test Storm
    storm_html = build_3d_simulation_html(incidents, resources, disaster_mode="Storm", rainfall_rate=80.0)
    assert "STORM" in storm_html
    assert "80" in storm_html

    # Test Fire
    fire_html = build_3d_simulation_html(incidents, resources, disaster_mode="Fire")
    assert "FIRE" in fire_html


def test_data_injection_and_disclaimer(sample_3d_data):
    incidents, resources = sample_3d_data
    html = build_3d_simulation_html(incidents, resources)

    # Both incidents and resources should be serialized in JS
    assert "INC-3D-001" in html
    assert "RES-3D-001" in html
    assert "Daraganj Riverbank" in html
    assert "District Trauma Hospital" in html

    # Mandatory Safety Notice
    assert "FICTIONAL DEMO SIMULATION DATA" in html or "DEMO SIMULATION" in html

"""
Unit tests for DisasterShield AI Fire TV Server and REST API Bridge.
"""
import json
import pytest
from firetv_server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_health(client):
    """Verifies the health endpoint responds with system details."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "HEALTHY"
    assert "DisasterShield AI" in data["app"]
    assert "Fire TV" in data["platform"]


def test_api_status(client):
    """Verifies telemetry, metrics, and AI probe aggregation."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "sector" in data
    assert "metrics" in data
    assert "weather" in data
    assert "ai" in data
    assert data["metrics"]["total"] >= 0
    assert data["metrics"]["threat"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_api_sector_switch(client):
    """Verifies switching the demonstration sector."""
    payload = {"city": "Lucknow, Uttar Pradesh"}
    response = client.post("/api/sector", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "SUCCESS"
    assert data["active_sector"]["name"] == "Lucknow, Uttar Pradesh"

    # Invalid city rejection
    invalid_resp = client.post("/api/sector", json={"city": "NonExistentCity"})
    assert invalid_resp.status_code == 400


def test_api_guidance_categories(client):
    """Verifies verified NDMA protocols are returned for hazard types."""
    for cat in ["flood", "fire", "earthquake", "storm", "landslide"]:
        resp = client.get(f"/api/guidance/{cat}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "official_guidance" in data
        assert "critical_donts" in data
        assert len(data["critical_donts"]) > 0


def test_api_ai_ask(client):
    """Verifies AI query endpoint responds with safe structure."""
    payload = {
        "prompt": "Synthesize flood evacuation protocol",
        "city": "Prayagraj, Uttar Pradesh",
    }
    response = client.post("/api/ai/ask", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "content" in data
    assert "is_ai_generated" in data
    assert "disclaimer" in data
    assert len(data["content"]) > 10


def test_simulation_embed(client):
    """Verifies the 3D simulation canvas renders valid HTML."""
    response = client.get("/simulation-embed?mode=Flood")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "<!DOCTYPE html>" in html
    assert "three" in html.lower() or "canvas" in html.lower()


def test_serve_tv_index(client):
    """Verifies root endpoint serves the Fire TV web interface."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "DisasterShield AI" in html
    assert "Fire TV Edition" in html
    assert "tv_nav.js" in html

"""
Unit tests for DisasterShield AI Gemma 4 Client Module.
Covers:
- Safe initialization & configuration
- Connection probe failure handling (graceful fallback)
- Strict AI model isolation (only Gemma 4 permitted)
- Deterministic Demo Mode synthesis templates (clearly labeled, not pretending to be AI)
- Grounded verification separation (distinguishes verified from unverified)
- Category heuristic suggestion
"""
import pytest
from modules.gemma_client import GemmaClient, GemmaResult


@pytest.fixture
def offline_gemma_client():
    """Client pointing to a non-existent port to guarantee offline / demo-mode path."""
    return GemmaClient(
        endpoint_url="http://127.0.0.1:59999",
        model_name="gemma4:e2b",
        timeout_seconds=1,
    )


def test_client_init_and_model_restriction(offline_gemma_client):
    assert offline_gemma_client.model_name == "gemma4:e2b"
    assert "gemma4" in offline_gemma_client.model_name.lower()


def test_connection_probe_graceful_failure(offline_gemma_client):
    is_connected, message = offline_gemma_client.probe_connection(force_refresh=True)
    # Must report False and descriptive message without raising uncaught exceptions
    assert is_connected is False
    assert "transparent DEMO MODE" in message or "No active Gemma" in message


def test_summarize_incidents_demo_fallback(offline_gemma_client):
    sample_incidents = [
        {
            "id": "INC-01",
            "category": "flood",
            "title": "Water rising at Ghat",
            "location_name": "Ghat Sector",
            "severity": "High",
            "verification_status": "VERIFIED",
            "description": "Monsoon waters overflowing lowest steps.",
        },
        {
            "id": "INC-02",
            "category": "storm",
            "title": "Tree leaning on lane",
            "location_name": "Sector 4",
            "severity": "Low",
            "verification_status": "UNVERIFIED",
            "description": "Citizen saw cracked branch.",
        },
    ]

    result: GemmaResult = offline_gemma_client.summarize_incidents(sample_incidents)

    # Core Requirements:
    # 1. Must NOT claim to be AI-generated in demo mode
    assert result.is_ai_generated is False
    assert result.status == "DEMO_MODE"
    assert "Rule-based Template Fallback" in result.model_identifier
    # 2. Must distinguish verified vs unverified
    assert "Verified Reports" in result.content
    assert "Unverified Citizen Submissions" in result.content
    # 3. Must contain transparency disclaimer
    assert "Rule-based template" in result.content or "transparent" in result.content


def test_situation_briefing_demo_fallback(offline_gemma_client):
    sample_incidents = [
        {"id": "INC-01", "severity": "High", "verification_status": "VERIFIED"}
    ]
    sample_weather = {
        "status": "SUCCESS",
        "temperature_c": 28.0,
        "condition": "Cloudy",
        "wind_speed_kmh": 15.0,
        "precipitation_mm": 5.0,
        "source": "Open-Meteo Public API",
    }
    sample_resources = [
        {"name": "GIC Shelter", "status": "Ready", "capacity": "500"}
    ]

    result = offline_gemma_client.generate_situation_briefing(
        incidents=sample_incidents,
        weather_data=sample_weather,
        resources=sample_resources,
    )

    assert result.is_ai_generated is False
    assert result.status == "DEMO_MODE"
    assert "Situation Briefing" in result.content
    # Must explicitly state unknown route safety (Safety constraint)
    assert "Route Safety Status" in result.content
    assert "UNKNOWN" in result.content


def test_rewrite_safety_instructions_demo_fallback(offline_gemma_client):
    raw_text = (
        "1. Disconnect high voltage electrical fuses.\n"
        "2. Avoid crossing water channels deeper than ankle depth."
    )
    result = offline_gemma_client.rewrite_safety_instructions("flood", raw_text)

    assert result.is_ai_generated is False
    assert "Plain-Language" in result.content
    assert "Step:" in result.content


def test_suggest_category_heuristic(offline_gemma_client):
    cat, explanation, is_ai = offline_gemma_client.suggest_category(
        title="Submerged road and drain overflow",
        description="Water has filled the lower basement car parking.",
    )
    assert cat == "flood"
    assert is_ai is False
    assert "Rule-based Heuristic Suggestion" in explanation

    cat_fire, _, _ = offline_gemma_client.suggest_category(
        title="Black smoke rising from transformer",
        description="Sparks and short circuit flames seen.",
    )
    assert cat_fire == "fire"

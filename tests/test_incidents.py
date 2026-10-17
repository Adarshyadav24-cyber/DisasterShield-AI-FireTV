"""
Unit tests for DisasterShield AI Incident Manager.
Covers:
- Incident data validation (coordinates, category, length, severity)
- Citizen report submission lifecycle (strictly starts UNVERIFIED)
- JSON loading and local persistence
- Trusted administrator verification workflow
- Incident filtering and risk metrics calculation
"""
import json
import pytest
from pathlib import Path
import tempfile
import shutil

from modules.incident_manager import IncidentManager, IncidentValidationError
import config


@pytest.fixture
def temp_incident_env():
    """Sets up an isolated temporary directory for demo and user incident JSON files."""
    temp_dir = Path(tempfile.mkdtemp())
    demo_file = temp_dir / "demo_incidents.json"
    user_file = temp_dir / "user_incidents.json"
    resources_file = temp_dir / "demo_resources.json"

    # Seed demo incidents
    sample_demos = [
        {
            "id": "INC-TEST-001",
            "category": "flood",
            "title": "Test River Swell",
            "description": "River water rising past ghat markers.",
            "location_name": "Test Ghat",
            "latitude": 25.43,
            "longitude": 81.85,
            "severity": "High",
            "verification_status": "VERIFIED",
            "report_time": "2026-10-17T08:00:00Z",
            "reporter_label": "Official Monitor",
            "is_demo": True,
            "verified_by": "District Officer",
            "verified_at": "2026-10-17T08:30:00Z",
            "verification_notes": "Ground inspected.",
        },
        {
            "id": "INC-TEST-002",
            "category": "storm",
            "title": "Test Branch Down",
            "description": "Fallen branch on residential sidewalk.",
            "location_name": "Test Lane",
            "latitude": 25.44,
            "longitude": 81.84,
            "severity": "Low",
            "verification_status": "UNVERIFIED",
            "report_time": "2026-10-17T09:00:00Z",
            "reporter_label": "Citizen",
            "is_demo": True,
            "verified_by": None,
            "verified_at": None,
            "verification_notes": "",
        },
    ]
    with open(demo_file, "w", encoding="utf-8") as f:
        json.dump(sample_demos, f)

    # Empty user file initially
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump([], f)

    # Seed sample resource
    sample_resources = [
        {
            "id": "RES-TEST-001",
            "name": "Test Relief Center",
            "type": "Shelter",
            "description": "Community center.",
            "location_name": "Test Center",
            "latitude": 25.45,
            "longitude": 81.86,
            "capacity": "100",
            "status": "Operational",
            "official_helpline_info": "Dial 112",
            "is_demo": True,
        }
    ]
    with open(resources_file, "w", encoding="utf-8") as f:
        json.dump(sample_resources, f)

    manager = IncidentManager(
        demo_path=demo_file,
        user_path=user_file,
        resources_path=resources_file,
    )

    yield manager, user_file, demo_file

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_initial_load(temp_incident_env):
    manager, _, _ = temp_incident_env
    incidents = manager.get_all_incidents()
    assert len(incidents) == 2
    assert incidents[0]["id"] == "INC-TEST-002"  # Latest report_time first
    assert manager.get_all_resources()[0]["id"] == "RES-TEST-001"


def test_validation_success(temp_incident_env):
    manager, _, _ = temp_incident_env
    clean = manager.validate_report(
        category="flood",
        title="Valid Flood Incident",
        description="Water has entered the main bazaar alleyway.",
        latitude=25.45,
        longitude=81.82,
        severity="High",
        location_name="Bazaar",
        reporter_label="Local Trader",
    )
    assert clean["category"] == "flood"
    assert clean["severity"] == "High"
    assert clean["latitude"] == 25.45


def test_validation_invalid_category(temp_incident_env):
    manager, _, _ = temp_incident_env
    with pytest.raises(IncidentValidationError) as exc_info:
        manager.validate_report(
            category="alien_invasion",
            title="Invalid Category Report",
            description="Something that is not supported by standard disaster taxonomy.",
            latitude=25.45,
            longitude=81.82,
            severity="Low",
            location_name="City",
        )
    assert "Invalid category" in str(exc_info.value)


def test_validation_invalid_coordinates(temp_incident_env):
    manager, _, _ = temp_incident_env
    # Out of latitude range
    with pytest.raises(IncidentValidationError):
        manager.validate_report(
            category="fire",
            title="Out of Bounds",
            description="Coordinates latitude out of bounds.",
            latitude=125.0,
            longitude=81.82,
            severity="Low",
            location_name="City",
        )


def test_validation_short_description(temp_incident_env):
    manager, _, _ = temp_incident_env
    with pytest.raises(IncidentValidationError):
        manager.validate_report(
            category="fire",
            title="Short Text",
            description="Too short",  # < 10 chars
            latitude=25.4,
            longitude=81.8,
            severity="Low",
            location_name="City",
        )


def test_citizen_report_submission_starts_unverified(temp_incident_env):
    manager, user_file, _ = temp_incident_env
    report = manager.submit_citizen_report(
        category="fire",
        title="Smoke behind school building",
        description="Dense grey smoke coming from behind playground shed.",
        latitude=25.435,
        longitude=81.845,
        severity="Moderate",
        location_name="North School",
        reporter_label="Passerby",
    )

    # Core Rule Check: Citizen report must start as UNVERIFIED
    assert report["verification_status"] == "UNVERIFIED"
    assert report["is_demo"] is False
    assert report["verified_by"] is None
    assert "INC-CITIZEN" in report["id"]

    # Verify saved in user file
    with open(user_file, "r", encoding="utf-8") as f:
        stored = json.load(f)
    assert len(stored) == 1
    assert stored[0]["id"] == report["id"]


def test_admin_verification_workflow(temp_incident_env):
    manager, _, _ = temp_incident_env
    # Submit citizen report
    report = manager.submit_citizen_report(
        category="storm",
        title="Roof sheet displaced",
        description="Tin roof sheet loose on main roadway.",
        latitude=25.435,
        longitude=81.845,
        severity="Moderate",
        location_name="Market",
    )
    inc_id = report["id"]

    # Admin verifies report
    success, msg = manager.update_verification_status(
        incident_id=inc_id,
        new_status="VERIFIED",
        verifier_name="Inspector Sharma",
        verification_notes="Constable on scene confirmed hazard. Area cordoned off.",
    )
    assert success is True

    # Check updated record
    updated = manager.get_incident_by_id(inc_id)
    assert updated["verification_status"] == "VERIFIED"
    assert updated["verified_by"] == "Inspector Sharma"
    assert "Area cordoned off" in updated["verification_notes"]
    assert updated["verified_at"] is not None


def test_admin_rejection_workflow(temp_incident_env):
    manager, _, _ = temp_incident_env
    report = manager.submit_citizen_report(
        category="flood",
        title="Fake flood alert",
        description="Claiming entire bridge is submerged when it is dry.",
        latitude=25.435,
        longitude=81.845,
        severity="Critical",
        location_name="Bridge",
    )
    inc_id = report["id"]

    success, _ = manager.update_verification_status(
        incident_id=inc_id,
        new_status="REJECTED",
        verifier_name="Control Room",
        verification_notes="CCTV footage confirms no water present. Erroneous report.",
    )
    assert success is True

    updated = manager.get_incident_by_id(inc_id)
    assert updated["verification_status"] == "REJECTED"


def test_summary_metrics(temp_incident_env):
    manager, _, _ = temp_incident_env
    metrics = manager.get_summary_metrics()
    assert metrics["total_reports"] == 2
    assert metrics["verified_count"] == 1
    assert metrics["unverified_count"] == 1
    assert metrics["high_priority_count"] == 1
    assert metrics["overall_risk"] in ["High", "Critical", "Moderate", "Low"]

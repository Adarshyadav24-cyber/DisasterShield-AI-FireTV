"""
DisasterShield AI - Incident Manager Module
Handles incident report loading, citizen submission validation, local JSON persistence,
and trusted administrator verification workflows.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import config


class IncidentValidationError(Exception):
    """Raised when an incident report fails data validation."""
    pass


class IncidentManager:
    """Manages disaster incident reports and trusted verification lifecycle."""

    def __init__(
        self,
        demo_path: Optional[Path] = None,
        user_path: Optional[Path] = None,
        resources_path: Optional[Path] = None,
    ):
        self.demo_path = demo_path or config.DEMO_INCIDENTS_PATH
        self.user_path = user_path or config.USER_INCIDENTS_PATH
        self.resources_path = resources_path or config.DEMO_RESOURCES_PATH
        self._incidents: List[Dict[str, Any]] = []
        self._resources: List[Dict[str, Any]] = []
        self.reload_data()

    def reload_data(self) -> None:
        """Reloads demo incidents, user-submitted reports, and emergency resources."""
        self._incidents = []
        self._resources = []

        # Load demo incidents
        if self.demo_path.exists():
            try:
                with open(self.demo_path, "r", encoding="utf-8") as f:
                    demos = json.load(f)
                    for item in demos:
                        item.setdefault("is_demo", True)
                        self._incidents.append(item)
            except Exception as e:
                print(f"[Warning] Failed to load demo incidents from {self.demo_path}: {e}")

        # Load user submissions
        if self.user_path.exists():
            try:
                with open(self.user_path, "r", encoding="utf-8") as f:
                    user_reports = json.load(f)
                    for item in user_reports:
                        item.setdefault("is_demo", False)
                        self._incidents.append(item)
            except Exception as e:
                print(f"[Warning] Failed to load user incidents from {self.user_path}: {e}")

        # Load emergency resources
        if self.resources_path.exists():
            try:
                with open(self.resources_path, "r", encoding="utf-8") as f:
                    self._resources = json.load(f)
            except Exception as e:
                print(f"[Warning] Failed to load resources from {self.resources_path}: {e}")

    def get_all_incidents(self) -> List[Dict[str, Any]]:
        """Returns all loaded incidents sorted by report_time descending."""
        return sorted(
            self._incidents,
            key=lambda x: x.get("report_time", ""),
            reverse=True,
        )

    def get_all_resources(self, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all emergency resource facilities, optionally filtered by city."""
        if city and city != "All Sectors":
            return [r for r in self._resources if r.get("city", "Prayagraj").lower() == city.lower()]
        return list(self._resources)

    def get_incident_by_id(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Finds an incident by its ID."""
        for inc in self._incidents:
            if inc.get("id") == incident_id:
                return inc
        return None

    def validate_report(
        self,
        category: str,
        title: str,
        description: str,
        latitude: float,
        longitude: float,
        severity: str,
        location_name: str,
        reporter_label: str = "Citizen Report",
    ) -> Dict[str, Any]:
        """
        Validates citizen incident submission parameters.
        Raises IncidentValidationError if any constraint fails.
        Includes robust coordinate bounds and latitude/longitude swap detection.
        """
        if not category or category.lower() not in config.CATEGORIES:
            raise IncidentValidationError(
                f"Invalid category '{category}'. Allowed categories: {', '.join(config.CATEGORIES)}"
            )

        if not title or len(title.strip()) < 3 or len(title.strip()) > 120:
            raise IncidentValidationError(
                "Incident title must be between 3 and 120 characters."
            )

        if not description or len(description.strip()) < 10 or len(description.strip()) > 1000:
            raise IncidentValidationError(
                "Incident description must be between 10 and 1000 characters to provide sufficient detail."
            )

        try:
            lat = float(latitude)
            lon = float(longitude)
        except (ValueError, TypeError):
            raise IncidentValidationError("Coordinates must be valid floating point numbers.")

        # Coordinate range & swap validation
        if not (-90.0 <= lat <= 90.0):
            raise IncidentValidationError(
                f"Latitude {lat} is out of valid range [-90.0, 90.0]. (Check if latitude and longitude were accidentally swapped)."
            )

        if not (-180.0 <= lon <= 180.0):
            raise IncidentValidationError(
                f"Longitude {lon} is out of valid range [-180.0, 180.0]."
            )

        # Detect likely swapped coordinates for Indian subcontinent (Lat ~ 8-38, Lon ~ 68-98)
        if lat > 60.0 and 0.0 <= lon <= 40.0:
            raise IncidentValidationError(
                f"Latitude ({lat}) and Longitude ({lon}) appear to be accidentally swapped. "
                "In India, Latitude is typically between 8° and 38° N, and Longitude is between 68° and 98° E."
            )

        if severity not in config.SEVERITY_LEVELS:
            raise IncidentValidationError(
                f"Invalid severity '{severity}'. Allowed levels: {', '.join(config.SEVERITY_LEVELS)}"
            )

        clean_location = location_name.strip() if location_name else "Unspecified Location"
        clean_reporter = reporter_label.strip()[:50] if reporter_label else "Citizen Report"

        return {
            "category": category.lower(),
            "title": title.strip(),
            "description": description.strip(),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "severity": severity,
            "location_name": clean_location,
            "reporter_label": clean_reporter,
        }

    def submit_citizen_report(
        self,
        category: str,
        title: str,
        description: str,
        latitude: float,
        longitude: float,
        severity: str,
        location_name: str,
        reporter_label: str = "Citizen Report",
        city: str = "Prayagraj",
    ) -> Dict[str, Any]:
        """
        Submits a new citizen report.
        Strict rule: EVERY new report begins in UNVERIFIED status.
        """
        clean_data = self.validate_report(
            category=category,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            location_name=location_name,
            reporter_label=reporter_label,
        )

        # Generate unique report identifier
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d")
        short_token = uuid.uuid4().hex[:6].upper()
        incident_id = f"INC-CITIZEN-{timestamp_slug}-{short_token}"
        report_time_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        new_incident: Dict[str, Any] = {
            "id": incident_id,
            "city": city,
            "category": clean_data["category"],
            "title": clean_data["title"],
            "description": clean_data["description"],
            "location_name": clean_data["location_name"],
            "latitude": clean_data["latitude"],
            "longitude": clean_data["longitude"],
            "severity": clean_data["severity"],
            "verification_status": "UNVERIFIED",  # Strictly UNVERIFIED by default
            "report_time": report_time_iso,
            "reporter_label": clean_data["reporter_label"],
            "is_demo": False,
            "verified_by": None,
            "verified_at": None,
            "verification_notes": "Awaiting review by authorized emergency response coordinator.",
        }

        # Save to user storage
        self._save_user_incident(new_incident)
        self._incidents.append(new_incident)
        return new_incident

    def update_verification_status(
        self,
        incident_id: str,
        new_status: str,
        verifier_name: str,
        verification_notes: str,
    ) -> Tuple[bool, str]:
        """
        Trusted Administrator Verification Workflow.
        Updates verification status, records verifier name, timestamp, and audit notes.
        """
        if new_status not in config.VERIFICATION_STATUSES:
            return False, f"Invalid status '{new_status}'. Allowed: {config.VERIFICATION_STATUSES}"

        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return False, f"Incident ID '{incident_id}' not found."

        verifier_clean = verifier_name.strip() if verifier_name else "Emergency Operations Officer"
        notes_clean = verification_notes.strip() if verification_notes else "Verification status updated."
        verified_at_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        incident["verification_status"] = new_status
        incident["verified_by"] = verifier_clean
        incident["verified_at"] = verified_at_iso
        incident["verification_notes"] = notes_clean

        # Persist update
        self._persist_all()
        return True, f"Incident {incident_id} updated to {new_status} by {verifier_clean}."

    def _save_user_incident(self, incident: Dict[str, Any]) -> None:
        """Appends new incident to the user_incidents.json file."""
        current_user_reports: List[Dict[str, Any]] = []
        if self.user_path.exists():
            try:
                with open(self.user_path, "r", encoding="utf-8") as f:
                    current_user_reports = json.load(f)
            except Exception:
                current_user_reports = []

        current_user_reports.append(incident)
        with open(self.user_path, "w", encoding="utf-8") as f:
            json.dump(current_user_reports, f, indent=2, ensure_ascii=False)

    def _persist_all(self) -> None:
        """Synchronizes in-memory updates back to demo and user JSON files."""
        demos = [inc for inc in self._incidents if inc.get("is_demo") is True]
        user_reports = [inc for inc in self._incidents if inc.get("is_demo") is not True]

        if demos and self.demo_path.exists():
            with open(self.demo_path, "w", encoding="utf-8") as f:
                json.dump(demos, f, indent=2, ensure_ascii=False)

        with open(self.user_path, "w", encoding="utf-8") as f:
            json.dump(user_reports, f, indent=2, ensure_ascii=False)

    def get_summary_metrics(self, city: Optional[str] = None) -> Dict[str, Any]:
        """Calculates emergency dashboard summary metrics, optionally scoped to a city/sector."""
        all_inc = self._incidents
        if city and city != "All Sectors":
            all_inc = [i for i in all_inc if i.get("city", "Prayagraj").lower() == city.lower()]
        total = len(all_inc)
        verified = sum(1 for i in all_inc if i.get("verification_status") == "VERIFIED")
        unverified = sum(1 for i in all_inc if i.get("verification_status") == "UNVERIFIED")
        investigating = sum(1 for i in all_inc if i.get("verification_status") == "INVESTIGATING")
        rejected = sum(1 for i in all_inc if i.get("verification_status") == "REJECTED")

        # Active high priority incidents (High or Critical, not Rejected)
        high_priority = [
            i for i in all_inc
            if i.get("severity") in ["High", "Critical"] and i.get("verification_status") != "REJECTED"
        ]
        high_priority_count = len(high_priority)

        # Risk level determination based on verified & high priority situation
        verified_critical = sum(
            1 for i in all_inc
            if i.get("severity") == "Critical" and i.get("verification_status") == "VERIFIED"
        )
        verified_high = sum(
            1 for i in all_inc
            if i.get("severity") == "High" and i.get("verification_status") == "VERIFIED"
        )

        if verified_critical > 0 or verified_high >= 3:
            overall_risk = "Critical"
            risk_color = config.SEVERITY_COLORS["Critical"]
            risk_desc = "Severe active emergencies confirmed by authorized monitors."
        elif verified_high > 0 or high_priority_count >= 3:
            overall_risk = "High"
            risk_color = config.SEVERITY_COLORS["High"]
            risk_desc = "Heightened risk with multiple urgent incidents reported."
        elif total > 0:
            overall_risk = "Moderate"
            risk_color = config.SEVERITY_COLORS["Moderate"]
            risk_desc = "Moderate localized incidents active under observation."
        else:
            overall_risk = "Low"
            risk_color = config.SEVERITY_COLORS["Low"]
            risk_desc = "Calm operational status. No active threat reports."

        return {
            "total_reports": total,
            "verified_count": verified,
            "unverified_count": unverified,
            "investigating_count": investigating,
            "rejected_count": rejected,
            "high_priority_count": high_priority_count,
            "overall_risk": overall_risk,
            "risk_color": risk_color,
            "risk_description": risk_desc,
            "demo_count": sum(1 for i in all_inc if i.get("is_demo") is True),
            "live_count": sum(1 for i in all_inc if i.get("is_demo") is not True),
        }

    def filter_incidents(
        self,
        severities: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        city: Optional[str] = None,
        include_demo: bool = True,
        include_live: bool = True,
    ) -> List[Dict[str, Any]]:
        """Filters incidents matching specified criteria, including city scoping."""
        filtered = []
        for inc in self.get_all_incidents():
            is_demo = inc.get("is_demo", False)
            if is_demo and not include_demo:
                continue
            if not is_demo and not include_live:
                continue

            if city and city != "All Sectors":
                if inc.get("city", "Prayagraj").lower() != city.lower():
                    continue

            if severities and inc.get("severity") not in severities:
                continue

            if statuses and inc.get("verification_status") not in statuses:
                continue

            if categories and inc.get("category") not in categories:
                continue

            filtered.append(inc)

        return filtered

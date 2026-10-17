"""
DisasterShield AI - Interactive Disaster Map Module
Generates a Folium map rendering incident markers, emergency facilities,
verification indicators, popups, and transparent demo data notices.
"""
from __future__ import annotations
from typing import Dict, List, Any
import folium
from folium import plugins

import config


def get_severity_marker_color(severity: str) -> str:
    """Maps incident severity to standard folium marker colors."""
    mapping = {
        "Critical": "darkred",
        "High": "red",
        "Moderate": "orange",
        "Low": "green",
    }
    return mapping.get(severity, "blue")


def get_category_icon_name(category: str) -> str:
    """Returns an icon identifier suitable for Folium markers."""
    mapping = {
        "flood": "tint",
        "fire": "fire",
        "storm": "flash",
        "earthquake": "warning-sign",
        "landslide": "chevron-down",
        "other": "exclamation-sign",
    }
    return mapping.get(category.lower(), "info-sign")


def create_incident_popup_html(incident: Dict[str, Any]) -> str:
    """Constructs a responsive, readable HTML popup for an incident marker."""
    is_demo = incident.get("is_demo", False)
    demo_badge = (
        '<div style="background:#fee2e2;color:#991b1b;padding:4px 8px;border-radius:4px;'
        'font-size:11px;font-weight:700;margin-bottom:8px;border:1px solid #f87171;">'
        '⚠️ FICTIONAL DEMO INCIDENT - NOT A REAL EMERGENCY</div>'
        if is_demo else
        '<div style="background:#ecfdf5;color:#065f46;padding:4px 8px;border-radius:4px;'
        'font-size:11px;font-weight:700;margin-bottom:8px;">'
        '📍 CITIZEN/FIELD SUBMISSION</div>'
    )

    ver_status = incident.get("verification_status", "UNVERIFIED")
    ver_colors = {
        "VERIFIED": ("#dcfce7", "#166534", "✅ VERIFIED BY OFFICIAL"),
        "UNVERIFIED": ("#fef9c3", "#854d0e", "⚠️ UNVERIFIED (PENDING CHECK)"),
        "INVESTIGATING": ("#e0f2fe", "#075985", "🔍 UNDER INVESTIGATION"),
        "REJECTED": ("#f1f5f9", "#475569", "❌ REJECTED / DISMISSED"),
    }
    bg, fg, label = ver_colors.get(ver_status, ("#f1f5f9", "#475569", ver_status))

    sev_color = config.SEVERITY_COLORS.get(incident.get("severity", "Low"), "#10B981")

    notes_html = ""
    if incident.get("verification_notes"):
        notes_html = (
            f'<div style="margin-top:8px;padding-top:6px;border-top:1px solid #e2e8f0;font-size:11px;color:#475569;">'
            f'<strong>Verification Notes:</strong> {incident.get("verification_notes")}<br>'
            f'<em>Verifier:</em> {incident.get("verified_by", "Field Officer")}</div>'
        )

    html = f"""
    <div style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;width:280px;line-height:1.4;">
        {demo_badge}
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="background:{sev_color};color:white;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:bold;">
                {incident.get('severity')} Severity
            </span>
            <span style="font-size:11px;color:#64748b;font-weight:600;">{incident.get('id')}</span>
        </div>
        <h4 style="margin:4px 0 6px 0;font-size:14px;color:#0f172a;">{incident.get('title')}</h4>
        <div style="background:{bg};color:{fg};padding:3px 6px;border-radius:4px;font-size:11px;font-weight:bold;display:inline-block;margin-bottom:6px;">
            {label}
        </div>
        <div style="font-size:12px;color:#334155;margin-bottom:6px;">
            {incident.get('description')}
        </div>
        <div style="font-size:11px;color:#64748b;">
            <strong>Location:</strong> {incident.get('location_name')}<br>
            <strong>Reported:</strong> {incident.get('report_time')}<br>
            <strong>Source:</strong> {incident.get('reporter_label', 'Citizen')}
        </div>
        {notes_html}
    </div>
    """
    return html


def create_resource_popup_html(resource: Dict[str, Any]) -> str:
    """Constructs HTML popup for emergency resource markers."""
    html = f"""
    <div style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;width:270px;line-height:1.4;">
        <div style="background:#eff6ff;color:#1e40af;padding:4px 8px;border-radius:4px;font-size:11px;font-weight:700;margin-bottom:6px;">
            🏥 EMERGENCY FACILITY (DEMO CATALOG)
        </div>
        <h4 style="margin:4px 0 6px 0;font-size:14px;color:#0f172a;">{resource.get('name')}</h4>
        <div style="font-size:12px;color:#475569;margin-bottom:6px;">
            <strong>Role:</strong> {resource.get('type')}<br>
            <strong>Status:</strong> <span style="color:#16a34a;font-weight:bold;">{resource.get('status')}</span><br>
            <strong>Capacity:</strong> {resource.get('capacity')}
        </div>
        <div style="font-size:11px;color:#334155;margin-bottom:6px;">
            {resource.get('description')}
        </div>
        <div style="background:#f8fafc;border-left:3px solid #3b82f6;padding:6px;font-size:11px;color:#1e293b;">
            <strong>Official Access:</strong><br>{resource.get('official_helpline_info')}
        </div>
        <div style="margin-top:6px;font-size:10px;color:#94a3b8;font-style:italic;">
            Note: Route safety to this site is UNCONFIRMED. Follow traffic authorities.
        </div>
    </div>
    """
    return html


def build_disaster_map(
    incidents: List[Dict[str, Any]],
    resources: List[Dict[str, Any]],
    center_lat: float = config.DEFAULT_LAT,
    center_lon: float = config.DEFAULT_LON,
    zoom: int = config.DEFAULT_ZOOM,
    show_resources: bool = True,
    city_name: str = "Prayagraj",
) -> folium.Map:
    """
    Builds the Folium map view populated with incident markers, resource locations,
    and a persistent floating legend.
    Includes strict coordinate validation and swap detection.
    """
    # Create base map with clean OpenStreetMap tiles (free, no API key required)
    disaster_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Feature groups for toggleable map layers
    incidents_group = folium.FeatureGroup(name="Incident Reports", show=True)
    resources_group = folium.FeatureGroup(name="Emergency Facilities", show=show_resources)

    # 1. Add Incident Markers with coordinate validation
    for inc in incidents:
        try:
            lat = float(inc.get("latitude"))
            lon = float(inc.get("longitude"))
        except (TypeError, ValueError):
            continue

        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            continue

        # Detect accidentally swapped coordinates for India
        if lat > 60.0 and 0.0 <= lon <= 40.0:
            lat, lon = lon, lat

        sev = inc.get("severity", "Low")
        marker_color = get_severity_marker_color(sev)
        ver_status = inc.get("verification_status", "UNVERIFIED")

        # Visual indicator: checkmark for verified, info/question for unverified
        icon_name = "ok" if ver_status == "VERIFIED" else "flag"

        popup_content = create_incident_popup_html(inc)
        popup = folium.Popup(folium.IFrame(popup_content, width=300, height=260), max_width=320)

        # Main marker
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=f"[{ver_status}] {inc.get('title')} ({sev} Severity)",
            icon=folium.Icon(color=marker_color, icon=icon_name, prefix="glyphicon"),
        ).add_to(incidents_group)

        # Subtle pulsing ring around Critical incidents
        if sev == "Critical":
            folium.CircleMarker(
                location=[lat, lon],
                radius=14,
                color="#7F1D1D",
                weight=2,
                fill=True,
                fill_color="#EF4444",
                fill_opacity=0.25,
            ).add_to(incidents_group)

    incidents_group.add_to(disaster_map)

    # 2. Add Emergency Resources Markers with coordinate validation
    if show_resources:
        for res in resources:
            try:
                r_lat = float(res.get("latitude"))
                r_lon = float(res.get("longitude"))
            except (TypeError, ValueError):
                continue

            if not (-90.0 <= r_lat <= 90.0 and -180.0 <= r_lon <= 180.0):
                continue

            if r_lat > 60.0 and 0.0 <= r_lon <= 40.0:
                r_lat, r_lon = r_lon, r_lat

            res_popup = folium.Popup(
                folium.IFrame(create_resource_popup_html(res), width=290, height=220),
                max_width=300,
            )

            folium.Marker(
                location=[r_lat, r_lon],
                popup=res_popup,
                tooltip=f"Facility: {res.get('name')}",
                icon=folium.Icon(color="blue", icon="plus-sign", prefix="glyphicon"),
            ).add_to(resources_group)

        resources_group.add_to(disaster_map)

    # Layer Control
    folium.LayerControl(position="topright").add_to(disaster_map)

    # Embed Legend and Demo Notice directly in the map HTML
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 250px;
        background-color: rgba(255, 255, 255, 0.94);
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 14px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 11px;
        color: #1e293b;
        z-index: 9999;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
        <div style="font-weight: 700; margin-bottom: 6px; font-size: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">
            🗺️ Map Legend & Indicators ({city_name})
        </div>
        <div style="margin-bottom: 4px;"><strong>Severity Color:</strong></div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span><span style="display:inline-block;width:10px;height:10px;background:#7F1D1D;border-radius:2px;"></span> Critical</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#EF4444;border-radius:2px;"></span> High</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#F59E0B;border-radius:2px;"></span> Mod</span>
            <span><span style="display:inline-block;width:10px;height:10px;background:#10B981;border-radius:2px;"></span> Low</span>
        </div>
        <div style="margin-bottom: 4px;"><strong>Marker Type:</strong></div>
        <div style="line-height: 1.5; margin-bottom: 6px;">
            <div><span style="color:#16a34a;font-weight:bold;">✔</span> Verified Official Incident</div>
            <div><span style="color:#d97706;font-weight:bold;">⚐</span> Unverified Citizen Report</div>
            <div><span style="color:#2563eb;font-weight:bold;">✚</span> Emergency Facility/Shelter</div>
        </div>
        <div style="background:#fee2e2;color:#991b1b;padding:4px;border-radius:4px;text-align:center;font-weight:700;font-size:10px;">
            ⚠️ DEMO MODE: Fictional markers. Not real emergencies.
        </div>
    </div>
    """
    disaster_map.get_root().html.add_child(folium.Element(legend_html))

    return disaster_map

"""
DisasterShield AI - Command Center & Disaster Awareness Dashboard
Tagline: Early Awareness. Verified Information. Safer Decisions.
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project directory is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from streamlit_folium import st_folium

import config
from modules.incident_manager import IncidentManager, IncidentValidationError
from modules.gemma_client import GemmaClient
from modules.weather_service import WeatherService
from modules.map_view import build_disaster_map
from modules.safety_briefing import get_safety_protocol, STANDARD_SAFETY_GUIDANCE
from modules.simulation_3d import build_3d_simulation_html

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Modern Command Center Theming
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{config.APP_NAME} | Emergency Operations Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ultra-Professional Command Center CSS Styling
st.markdown(
    """
    <style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.0rem;
        padding-bottom: 2.5rem;
    }

    /* Emergency Warning Banner */
    .prototype-disclaimer {
        background: linear-gradient(90deg, #450a0a 0%, #7f1d1d 100%);
        color: #fecaca;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 1.0rem;
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Top Command Header */
    .command-header {
        background: linear-gradient(135deg, #0b1329 0%, #070d1a 100%);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 1.2rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    }
    .header-tagline {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .live-beacon {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 16px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .status-verified {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .status-unverified {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .status-investigating {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .status-rejected {
        background-color: rgba(100, 116, 139, 0.15);
        color: #94a3b8;
        border: 1px solid rgba(100, 116, 139, 0.3);
    }
    .status-demo {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .status-live {
        background-color: rgba(52, 211, 153, 0.15);
        color: #6ee7b7;
        border: 1px solid rgba(52, 211, 153, 0.4);
    }

    /* Metric Cards */
    .metric-card {
        background: #0d1527;
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-label {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-top: 4px;
    }

    /* AI Engine Telemetry Card */
    .engine-badge {
        background: #0b1329;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 12px;
        margin-bottom: 12px;
    }
    
    /* Weather Widget Card */
    .weather-card {
        background: linear-gradient(135deg, #0b1329 0%, #060b14 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: white;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    /* Incident Item Card */
    .incident-feed-card {
        background: #0d1527;
        border: 1px solid #1e293b;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: border-color 0.15s ease;
    }
    .incident-feed-card:hover {
        border-color: #38bdf8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Service Initializations & Caching
# -----------------------------------------------------------------------------
@st.cache_resource
def get_incident_manager() -> IncidentManager:
    return IncidentManager()

@st.cache_resource
def get_gemma_client() -> GemmaClient:
    return GemmaClient()

@st.cache_resource
def get_weather_service() -> WeatherService:
    return WeatherService()

incident_mgr = get_incident_manager()
gemma = get_gemma_client()
weather_svc = get_weather_service()

# -----------------------------------------------------------------------------
# Demonstration City Selection State
# -----------------------------------------------------------------------------
city_options = list(config.DEMO_CITIES.keys())
if "selected_city_name" not in st.session_state:
    st.session_state["selected_city_name"] = config.DEFAULT_LOCATION_NAME

# Ensure active city exists in options
if st.session_state["selected_city_name"] not in city_options:
    st.session_state["selected_city_name"] = config.DEFAULT_LOCATION_NAME

active_city_name = st.session_state["selected_city_name"]
active_city_meta = config.DEMO_CITIES[active_city_name]
selected_lat = active_city_meta["lat"]
selected_lon = active_city_meta["lon"]
selected_zoom = active_city_meta["zoom"]
sector_name = active_city_name
sector_short_city = active_city_meta["city"]

# -----------------------------------------------------------------------------
# Sidebar: Command Sector Switcher, Telemetry, & Navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ DisasterShield AI")
    st.caption(f"**{config.TAGLINE}**")
    st.markdown("---")

    # Primary Location Selector
    st.markdown("#### 📍 Command Sector / City")
    sidebar_city_choice = st.selectbox(
        "Demonstration City",
        options=city_options,
        index=city_options.index(active_city_name),
        key="sidebar_city_select",
        help="Switches active sector coordinates, map center, weather telemetry, and 3D simulation.",
    )
    if sidebar_city_choice != st.session_state["selected_city_name"]:
        st.session_state["selected_city_name"] = sidebar_city_choice
        st.rerun()

    st.markdown(
        f"""
        <div style="background:#0b1329;padding:10px 12px;border-radius:6px;border-left:3px solid #38bdf8;font-size:11px;margin-bottom:12px;">
            <strong>River/Corridor:</strong> {active_city_meta['river']}<br>
            <strong>Coordinates:</strong> {selected_lat:.4f}° N, {selected_lon:.4f}° E<br>
            <span style="color:#94a3b8;font-style:italic;">{active_city_meta['description']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Gemma 4 Engine Connectivity Check
    is_gemma_connected, gemma_status_msg = gemma.probe_connection()
    if is_gemma_connected:
        st.markdown(
            f"""
            <div class="engine-badge" style="border-left: 4px solid #10b981;">
                <strong>🤖 AI Engine: CONNECTED</strong><br>
                <span style="font-size:11px;color:#34d399;">Model: {config.GEMMA_MODEL_NAME}</span><br>
                <span style="font-size:10px;color:#94a3b8;">Endpoint: {gemma.endpoint_url}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="engine-badge" style="border-left: 4px solid #f59e0b;">
                <strong>🛡️ AI Engine: DEMO MODE</strong><br>
                <span style="font-size:11px;color:#fbbf24;">Rule-based transparent templates</span><br>
                <span style="font-size:10px;color:#94a3b8;">Gemma 4 offline / optional local endpoint</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("🔄 Probe Gemma 4 Connection", width="stretch"):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔍 Filter Criteria")

    filter_scope = st.radio(
        "Data View Scope",
        options=[f"Active Sector ({sector_short_city})", "All Sectors (Nationwide)"],
        index=0,
    )
    city_filter_param = sector_short_city if "Active Sector" in filter_scope else None

    filter_severities = st.multiselect(
        "Incident Severity",
        options=config.SEVERITY_LEVELS,
        default=config.SEVERITY_LEVELS,
    )
    filter_statuses = st.multiselect(
        "Verification Status",
        options=config.VERIFICATION_STATUSES,
        default=config.VERIFICATION_STATUSES,
    )
    filter_categories = st.multiselect(
        "Incident Category",
        options=config.CATEGORIES,
        default=config.CATEGORIES,
    )
    show_demo_records = st.checkbox("Include Demo Records", value=True)
    show_user_records = st.checkbox("Include Citizen Submissions", value=True)

    st.markdown("---")
    st.markdown("#### 📞 Official Emergency Helplines")
    st.markdown(
        """
        - **National Emergency Number:** `112`
        - **State Disaster Control Room:** `1077`
        - **Ambulance Services:** `108`
        - **Fire Control:** `101`
        
        *Notice: DisasterShield AI does not invent emergency numbers. Always consult official municipal helplines.*
        """
    )

# -----------------------------------------------------------------------------
# Top Disclaimer Notice
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="prototype-disclaimer">
        <span>⚠️</span>
        <div><strong>SAFETY & TRANSPARENCY NOTICE:</strong> {config.PROTOTYPE_NOTICE}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Top Command Header with Direct City Switcher
# -----------------------------------------------------------------------------
head_c1, head_c2, head_c3 = st.columns([2.6, 1.4, 0.8])
with head_c1:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:26px;">🛡️</span>
            <div>
                <h2 style="margin:0;font-size:22px;color:#f8fafc;font-weight:800;letter-spacing:-0.5px;">DisasterShield AI</h2>
                <div class="header-tagline"><span class="live-beacon"></span><strong>{config.TAGLINE}</strong> | Sector: <span style="color:#38bdf8;">{sector_name}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with head_c2:
    st.caption("Active Demonstration Sector")
    top_city_choice = st.selectbox(
        "Sector Selector",
        options=city_options,
        index=city_options.index(active_city_name),
        key="top_header_city_select",
        label_visibility="collapsed",
    )
    if top_city_choice != st.session_state["selected_city_name"]:
        st.session_state["selected_city_name"] = top_city_choice
        st.rerun()

with head_c3:
    current_time_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
    st.markdown(f"<div style='text-align:right;font-size:11px;color:#94a3b8;margin-bottom:4px;'>Telemetry Sync:<br><strong style='color:#38bdf8;font-family:monospace;'>{current_time_str}</strong></div>", unsafe_allow_html=True)
    if st.button("🔄 Sync", width="stretch"):
        incident_mgr.reload_data()
        st.success("Ledger synchronized.")

# Fetch filtered incidents & resources based on city filter
incidents = incident_mgr.filter_incidents(
    severities=filter_severities,
    statuses=filter_statuses,
    categories=filter_categories,
    city=city_filter_param,
    include_demo=show_demo_records,
    include_live=show_user_records,
)
resources = incident_mgr.get_all_resources(city=city_filter_param)
metrics = incident_mgr.get_summary_metrics(city=city_filter_param)

# -----------------------------------------------------------------------------
# Main Application Tabs
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "📊 Operational Dashboard",
    "🌐 3D Digital Twin & Simulation",
    "🗺️ Interactive Disaster Map",
    "📢 Citizen Incident Reporting",
    "🔐 Administrator Verification Desk",
    "🤖 Gemma 4 AI Intelligence Hub",
    "ℹ️ Guidance & Ethics Disclosure",
])

# =============================================================================
# TAB 0: OPERATIONAL DASHBOARD
# =============================================================================
with tabs[0]:
    # Key Summary Cards
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_reports']}</div>
                <div class="metric-label">Total Reports ({sector_short_city if city_filter_param else 'All'})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #10b981;">
                <div class="metric-value" style="color:#34d399;">{metrics['verified_count']}</div>
                <div class="metric-label">Verified Official</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #f59e0b;">
                <div class="metric-value" style="color:#fbbf24;">{metrics['unverified_count']}</div>
                <div class="metric-label">Unverified Citizen</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #ef4444;">
                <div class="metric-value" style="color:#f87171;">{metrics['high_priority_count']}</div>
                <div class="metric-label">High Priority</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m5:
        risk_lvl = metrics['overall_risk']
        risk_color = metrics['risk_color']
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid {risk_color};background:#0f172a;">
                <div class="metric-value" style="color:{risk_color};">{risk_lvl.upper()}</div>
                <div class="metric-label">Sector Threat Index</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Weather Widget & Environmental Telemetry for Selected City
    weather_info = weather_svc.get_weather(selected_lat, selected_lon, sector_name)
    w_col1, w_col2, w_col3, w_col4 = st.columns([2, 1, 1, 1])
    with w_col1:
        sim_tag = " [DEMO SIMULATION]" if weather_info.get("is_simulated") else " [LIVE TELEMETRY]"
        st.markdown(
            f"""
            <div class="weather-card">
                <div style="font-size:11px;color:#94a3b8;font-weight:700;letter-spacing:0.5px;">ENVIRONMENTAL TELEMETRY {sim_tag}</div>
                <div style="font-size:20px;font-weight:700;margin:3px 0;color:#f8fafc;">{weather_info.get('condition')}</div>
                <div style="font-size:11px;color:#cbd5e1;">Target: <strong>{sector_name}</strong> | Source: {weather_info.get('source')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with w_col2:
        st.metric("Temperature", f"{weather_info.get('temperature_c', '--')} °C")
    with w_col3:
        st.metric("Wind Velocity", f"{weather_info.get('wind_speed_kmh', '--')} km/h")
    with w_col4:
        st.metric("Precipitation", f"{weather_info.get('precipitation_mm', '--')} mm")

    st.markdown("---")

    # Visual Analytics & Recent Incident Feed
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown(f"#### 📊 Category Distribution ({sector_short_city if city_filter_param else 'All Sectors'})")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            cat_counts = df_inc["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Reports"]
            st.bar_chart(cat_counts.set_index("Category"), color="#38bdf8")
        else:
            st.info("No incident records match the active filter criteria for this sector.")

    with c2:
        st.markdown(f"#### 🛡️ Verification Pipeline Status")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            ver_counts = df_inc["verification_status"].value_counts().reset_index()
            ver_counts.columns = ["Status", "Count"]
            st.dataframe(ver_counts, width="stretch", hide_index=True)
            st.caption("Public submissions start as UNVERIFIED until validated by the command desk.")
        else:
            st.info("No records to summarize.")

    st.markdown(f"#### 📋 Recent Incident Ledger Feed ({len(incidents)} Reports)")
    if incidents:
        for inc in incidents[:6]:
            with st.container():
                sev_color = config.SEVERITY_COLORS.get(inc.get("severity", "Low"), "#10b981")
                ver_class = f"status-{inc.get('verification_status', 'unverified').lower()}"
                demo_class = "status-demo" if inc.get("is_demo") else "status-live"
                demo_text = "DEMO DATA" if inc.get("is_demo") else "CITIZEN SUBMISSION"
                city_badge = inc.get("city", sector_short_city)

                st.markdown(
                    f"""
                    <div class="incident-feed-card" style="border-left: 5px solid {sev_color};">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <span style="font-weight:700;font-size:14px;color:#f8fafc;">{inc.get('title')}</span>
                            <div>
                                <span class="status-pill" style="background:#1e293b;color:#38bdf8;">📍 {city_badge}</span>
                                <span class="status-pill {demo_class}">{demo_text}</span>
                                <span class="status-pill {ver_class}">{inc.get('verification_status')}</span>
                            </div>
                        </div>
                        <div style="font-size:12px;color:#cbd5e1;margin-bottom:6px;">{inc.get('description')}</div>
                        <div style="font-size:11px;color:#94a3b8;">
                            <strong>Category:</strong> {inc.get('category').upper()} | 
                            <strong>Location:</strong> {inc.get('location_name')} ({inc.get('latitude')}, {inc.get('longitude')}) | 
                            <strong>Reported:</strong> {inc.get('report_time')} | 
                            <strong>Source:</strong> {inc.get('reporter_label', 'Citizen')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning(f"No incidents currently recorded for sector '{sector_name}' matching filters.")

# =============================================================================
# TAB 1: 3D DIGITAL TWIN & DISASTER SIMULATION
# =============================================================================
with tabs[1]:
    st.subheader(f"🌐 3D Digital Twin & Disaster Simulation Studio ({sector_short_city})")
    st.markdown(
        """
        > ⚠️ **DEMO SIMULATION NOTICE:** *This 3D environment is a tactical preparedness simulation prototype. 
        > Floods, tremors, flame particles, and storms are synthesized for situational awareness and civil defense training. 
        > Never imply that 3D simulations predict real disasters or guaranteed safe evacuation routes.*
        """
    )

    # Simulation Telemetry Metrics Row
    sim_m1, sim_m2, sim_m3, sim_m4 = st.columns(4)
    with sim_m1:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #38bdf8;">
                <div class="metric-value" style="font-size:18px;color:#38bdf8;">{sector_short_city}</div>
                <div class="metric-label">Command Sector</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sim_m2:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #0284c7;">
                <div class="metric-value" style="font-size:18px;color:#0284c7;">{len(incidents)} Pins</div>
                <div class="metric-label">Active 3D Incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sim_m3:
        st.markdown(
            f"""
            <div class="metric-card" style="border-top: 3px solid #10b981;">
                <div class="metric-value" style="font-size:18px;color:#10b981;">{len(resources)} Sites</div>
                <div class="metric-label">Emergency Facilities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sim_m4:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #f59e0b;">
                <div class="metric-value" style="font-size:18px;color:#f59e0b;">60 FPS WebGL</div>
                <div class="metric-label">3D Engine Telemetry</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main 3D Canvas and Side Control Matrix
    col_3d_main, col_3d_panel = st.columns([2.7, 1.3])

    with col_3d_panel:
        st.markdown("#### 🎛️ Simulation Matrix")
        sim_scenario = st.selectbox(
            "Disaster Scenario",
            options=["Flood", "Fire", "Earthquake", "Storm"],
            index=0,
            help="Visibly toggles procedural shaders, particle emitters, or seismic oscillation matrices in the 3D viewport.",
        )
        sim_level = st.select_slider(
            "Simulation Intensity",
            options=["Low", "Medium", "High"],
            value="Medium",
        )

        # Reactive simulation sliders that update 3D parameters
        if sim_scenario == "Flood":
            water_elevation = st.slider(
                "Flood Water Elevation (m)",
                min_value=0.0,
                max_value=12.0,
                value=4.2 if sim_level == "Medium" else (2.0 if sim_level == "Low" else 7.5),
                step=0.2,
                help="Visibly raises translucent blue water plane above riverbanks and low-lying quays.",
            )
            quake_amplitude = 0.0
            storm_rain_rate = 10.0
        elif sim_scenario == "Earthquake":
            quake_amplitude = st.slider(
                "Seismic Tremor (Richter Scale)",
                min_value=0.0,
                max_value=10.0,
                value=5.4 if sim_level == "Medium" else (2.8 if sim_level == "Low" else 8.2),
                step=0.2,
                help="Visibly oscillates terrain and buildings with harmonic seismic frequency.",
            )
            water_elevation = 1.5
            storm_rain_rate = 10.0
        elif sim_scenario == "Storm":
            storm_rain_rate = st.slider(
                "Precipitation Velocity (mm/h)",
                min_value=0.0,
                max_value=100.0,
                value=60.0 if sim_level == "Medium" else (25.0 if sim_level == "Low" else 95.0),
                step=5.0,
                help="Visibly drives 2,000 falling 3D rain streaks and lightning illumination bursts.",
            )
            water_elevation = 2.5
            quake_amplitude = 0.0
        else:  # Fire
            st.info("🔥 Fire Scenario Active: Dynamic particle flame emitter and smoke plume active at commercial warehouse locations.")
            water_elevation = 1.5
            quake_amplitude = 0.0
            storm_rain_rate = 0.0

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            chk_3d_inc = st.checkbox("Show 3D Pins", value=True)
        with c_opt2:
            chk_3d_res = st.checkbox("Show Facilities", value=True)

        st.markdown("---")
        st.markdown("#### 🎯 3D Incident Detail Inspector")
        inc_map = {inc["id"]: f"{inc['title']} ({inc['severity']})" for inc in incidents}
        selected_inc_key = st.selectbox(
            "Select Incident to Inspect",
            options=["None"] + list(inc_map.keys()),
            format_func=lambda x: "Click 3D marker or select..." if x == "None" else f"{x}: {inc_map.get(x, '')[:30]}...",
        )

        selected_inc_obj = incident_mgr.get_incident_by_id(selected_inc_key) if selected_inc_key != "None" else None

        if selected_inc_obj:
            sev_col = config.SEVERITY_COLORS.get(selected_inc_obj.get("severity", "Low"), "#10b981")
            ver_text = selected_inc_obj.get("verification_status")
            demo_flag = "⚠️ FICTIONAL DEMO SIMULATION DATA" if selected_inc_obj.get("is_demo") else "📍 CITIZEN/FIELD SUBMISSION"
            st.markdown(
                f"""
                <div style="background:#0b1329;border:1px solid #1e293b;border-left:4px solid {sev_col};padding:10px 12px;border-radius:6px;font-size:12px;line-height:1.4;">
                    <div style="font-weight:700;color:#f8fafc;font-size:13px;margin-bottom:3px;">{selected_inc_obj.get('title')}</div>
                    <div style="color:#94a3b8;font-size:11px;margin-bottom:6px;">{selected_inc_obj.get('description')}</div>
                    <div style="border-top:1px solid #1e293b;padding-top:4px;font-size:11px;color:#cbd5e1;">
                        <strong>Sector:</strong> {selected_inc_obj.get('city', sector_short_city)}<br>
                        <strong>Severity:</strong> <span style="color:{sev_col};font-weight:bold;">{selected_inc_obj.get('severity')}</span> | 
                        <strong>Status:</strong> <span style="color:#38bdf8;font-weight:bold;">{ver_text}</span><br>
                        <strong>Location:</strong> {selected_inc_obj.get('location_name')}<br>
                        <strong>Timestamp:</strong> {selected_inc_obj.get('report_time')}<br>
                        <strong>Source:</strong> {selected_inc_obj.get('reporter_label', 'Citizen')}<br>
                        <span style="color:#f87171;font-weight:bold;font-size:10px;">{demo_flag}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("Tip: You can also click directly on any 3D pin in the canvas to inspect its tactical telemetry.")

    with col_3d_main:
        # Build self-contained Three.js WebGL simulation scoped to active city
        html_3d = build_3d_simulation_html(
            incidents=incidents,
            resources=resources,
            center_lat=selected_lat,
            center_lon=selected_lon,
            city_name=sector_name,
            disaster_mode=sim_scenario,
            simulation_intensity=sim_level,
            water_level=water_elevation,
            earthquake_intensity=quake_amplitude,
            rainfall_rate=storm_rain_rate,
            show_incidents=chk_3d_inc,
            show_resources=chk_3d_res,
            selected_incident_id=selected_inc_key if selected_inc_key != "None" else None,
        )
        components.html(html_3d, height=650)

# =============================================================================
# TAB 2: INTERACTIVE DISASTER MAP
# =============================================================================
with tabs[2]:
    st.subheader(f"🗺️ Tactical Geospatial Map View — {sector_name}")
    st.markdown(
        """
        > ⚠️ **TRANSPARENCY WATERMARK:** Map markers depict demonstration scenarios or citizen submissions. 
        > This prototype **does not** compute live flood boundaries, road closures, or guaranteed safe evacuation routes.
        """
    )

    col_map_opts1, col_map_opts2 = st.columns([2, 1])
    with col_map_opts1:
        st.caption(f"Rendering {len(incidents)} incident markers and {len(resources)} emergency facilities centered at {sector_name} ({selected_lat:.4f}° N, {selected_lon:.4f}° E).")
    with col_map_opts2:
        toggle_res = st.checkbox("Show Emergency Facilities Overlay", value=True)

    # Render Folium map with error boundary and city-aware key
    try:
        folium_map_obj = build_disaster_map(
            incidents=incidents,
            resources=resources,
            center_lat=selected_lat,
            center_lon=selected_lon,
            zoom=selected_zoom,
            show_resources=toggle_res,
            city_name=sector_short_city,
        )
        st_folium(
            folium_map_obj,
            key=f"disaster_map_{sector_short_city.replace(' ', '_')}_{len(incidents)}",
            width="100%",
            height=580,
            returned_objects=[],
        )
    except Exception as map_err:
        st.error(f"⚠️ Map View Notice: Leaflet map canvas encountered an error: {map_err}. Please ensure browser WebGL and network permissions are active.")

# =============================================================================
# TAB 3: CITIZEN INCIDENT REPORTING
# =============================================================================
with tabs[3]:
    st.subheader(f"📢 Citizen Incident Reporting Portal — {sector_short_city}")
    st.info(
        "💡 **Public Contribution Notice:** Community reports provide crucial early awareness. "
        "Every submission is initially recorded as **UNVERIFIED** to ensure accurate verification by authorized field coordinators. "
        "Do not submit false alarms or test spam."
    )

    # City-specific quick-fill demonstration landmarks
    city_landmarks = {
        "Prayagraj": [
            ("Daraganj Riverbank", 25.4285, 81.8742),
            ("Phaphamau Bridge Area", 25.5012, 81.8540),
            ("Civil Lines High Court Sector", 25.4522, 81.8341),
            ("Katra Market", 25.4628, 81.8519),
            ("Naini Industrial Crossing", 25.3985, 81.8680),
        ],
        "Lucknow": [
            ("Gomti Riverfront Promenade", 26.8520, 80.9510),
            ("Hazratganj Main Market", 26.8500, 80.9450),
            ("Charbagh Railway Station Approach", 26.8310, 80.9220),
            ("Aminabad Commercial Hub", 26.8450, 80.9320),
            ("KGMU Hospital Chowk", 26.8680, 80.9160),
        ],
        "Varanasi": [
            ("Assi Ghat Waterfront", 25.2890, 83.0060),
            ("Dashashwamedh Ghat Steps", 25.3070, 83.0100),
            ("Godowlia Market Intersection", 25.3110, 83.0030),
            ("BHU University Campus Gate", 25.2750, 82.9990),
            ("Sigra Municipal Crossing", 25.3190, 82.9850),
        ],
        "New Delhi": [
            ("ITO Ring Road Floodplain", 28.6280, 77.2480),
            ("Minto Road Underpass", 28.6360, 77.2240),
            ("Chandni Chowk Heritage Bazaar", 28.6550, 77.2300),
            ("Connaught Place Outer Circle", 28.6320, 77.2190),
            ("Yamuna Bazar / Kashmere Gate", 28.6670, 77.2340),
        ],
    }

    current_city_landmarks = city_landmarks.get(sector_short_city, city_landmarks["Prayagraj"])

    with st.expander(f"📍 Quick Fill Demonstration Coordinates ({sector_short_city} Landmarks)"):
        landmark = st.selectbox(
            "Select reference location to autofill coordinates",
            options=current_city_landmarks,
            format_func=lambda x: f"{x[0]} ({x[1]:.4f}, {x[2]:.4f})",
        )
        if st.button("Apply Selected Coordinates", width="stretch"):
            st.session_state["form_lat"] = landmark[1]
            st.session_state["form_lon"] = landmark[2]
            st.session_state["form_loc_name"] = landmark[0]
            st.rerun()

    # Reporting Form
    with st.form("citizen_report_form"):
        form_title = st.text_input("Incident Title *", placeholder="e.g. Water inundating lower ghat steps")
        form_desc = st.text_area(
            "Detailed Description *",
            placeholder="Describe what you observe, approximate water depth, visible hazards, or damaged infrastructure...",
            help="Minimum 10 characters required for validation.",
        )

        c_f1, c_f2 = st.columns(2)
        with c_f1:
            form_cat = st.selectbox("Disaster Category *", options=config.CATEGORIES, index=0)
            form_sev = st.selectbox("Observed Severity *", options=config.SEVERITY_LEVELS, index=1)
        with c_f2:
            form_loc = st.text_input("Location / Landmark Name *", value=st.session_state.get("form_loc_name", f"{sector_short_city} Sector"))
            form_rep = st.text_input("Your Name / Organization (Optional)", value="Local Resident")

        c_c1, c_c2 = st.columns(2)
        with c_c1:
            form_lat = st.number_input("Latitude *", value=st.session_state.get("form_lat", selected_lat), format="%.5f")
        with c_c2:
            form_lon = st.number_input("Longitude *", value=st.session_state.get("form_lon", selected_lon), format="%.5f")

        submitted = st.form_submit_button("🚨 Submit Incident Report", width="stretch")

        if submitted:
            try:
                new_rep = incident_mgr.submit_citizen_report(
                    category=form_cat,
                    title=form_title,
                    description=form_desc,
                    latitude=form_lat,
                    longitude=form_lon,
                    severity=form_sev,
                    location_name=form_loc,
                    reporter_label=form_rep,
                    city=sector_short_city,
                )
                st.success(
                    f"✅ Report successfully filed in **{sector_short_city}** with ID: **{new_rep['id']}**. "
                    f"Status: **UNVERIFIED** (Awaiting review by emergency coordinator)."
                )
                # Suggest category via Gemma or heuristic to assist verification
                suggested_cat, explanation, is_ai = gemma.suggest_category(form_title, form_desc)
                if suggested_cat != form_cat:
                    st.info(f"💡 Suggestion Engine: You selected '{form_cat}', but automated classification indicated '{suggested_cat}' ({explanation}).")
            except IncidentValidationError as val_err:
                st.error(f"❌ Submission Validation Failed: {val_err}")
            except Exception as e:
                st.error(f"❌ Error saving submission: {e}")

# =============================================================================
# TAB 4: ADMINISTRATOR VERIFICATION DESK
# =============================================================================
with tabs[4]:
    st.subheader("🔐 Trusted Administrator Verification Workflow")
    st.caption("Authorized emergency operations personnel review incoming public reports, confirm ground validity, and update verification records.")

    # Simple secure PIN verification for hackathon demo
    admin_pin = st.text_input("Enter Administrator PIN", type="password", help="Default demo PIN: 1122")
    if admin_pin == config.ADMIN_VERIFY_PIN:
        st.success("🔓 Administrator Console Unlocked.")

        all_reports = incident_mgr.get_all_incidents()
        unverified_list = [i for i in all_reports if i.get("verification_status") in ["UNVERIFIED", "INVESTIGATING"]]

        st.markdown(f"**Reports Pending Review ({len(unverified_list)}):**")
        if unverified_list:
            selected_inc_id = st.selectbox(
                "Select Incident to Inspect & Verify",
                options=[i["id"] for i in unverified_list],
                format_func=lambda x: f"{x} [{incident_mgr.get_incident_by_id(x).get('city', 'Regional')}] - {incident_mgr.get_incident_by_id(x).get('title')} ({incident_mgr.get_incident_by_id(x).get('category')})",
            )
            inspect_item = incident_mgr.get_incident_by_id(selected_inc_id)
            if inspect_item:
                st.markdown(
                    f"""
                    <div style="background:#0b1329;padding:14px;border:1px solid #1e293b;border-radius:8px;margin-bottom:12px;">
                        <strong>ID:</strong> {inspect_item.get('id')} | <strong>Sector:</strong> {inspect_item.get('city', sector_short_city)} | <strong>Reported By:</strong> {inspect_item.get('reporter_label')}<br>
                        <strong>Title:</strong> {inspect_item.get('title')}<br>
                        <strong>Description:</strong> {inspect_item.get('description')}<br>
                        <strong>Location:</strong> {inspect_item.get('location_name')} ({inspect_item.get('latitude')}, {inspect_item.get('longitude')})<br>
                        <strong>Category:</strong> {inspect_item.get('category')} | <strong>Severity:</strong> {inspect_item.get('severity')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("verify_action_form"):
                    new_status = st.selectbox("Set Verification Decision", options=["VERIFIED", "INVESTIGATING", "REJECTED"])
                    verifier_name = st.text_input("Verifier Name / Badge ID", value="Duty Officer - Disaster Command")
                    v_notes = st.text_area("Verification / Ground Inspection Notes", placeholder="e.g. Field patrol confirmed water level encroaching on pedestrian path.")

                    apply_btn = st.form_submit_button("💾 Commit Verification Status", width="stretch")
                    if apply_btn:
                        ok, msg = incident_mgr.update_verification_status(
                            incident_id=selected_inc_id,
                            new_status=new_status,
                            verifier_name=verifier_name,
                            verification_notes=v_notes,
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No unverified or investigating reports pending review.")
    else:
        st.warning("Please enter the administrator PIN (Default: 1122) to access verification controls.")

# =============================================================================
# TAB 5: GEMMA 4 AI INTELLIGENCE HUB
# =============================================================================
with tabs[5]:
    st.subheader(f"🤖 Google Gemma 4 Intelligence Hub — {sector_short_city}")
    st.caption("Grounded, hallucination-resistant operational synthesis powered strictly and exclusively by Google Gemma 4.")

    if is_gemma_connected:
        st.success(f"🟢 Gemma 4 Live Inference Active ({config.GEMMA_MODEL_NAME} @ {gemma.endpoint_url})")
    else:
        st.info("🟡 Gemma 4 Offline: Application is operating in transparent, deterministic DEMO MODE.")

    ai_subtab1, ai_subtab2, ai_subtab3, ai_subtab4 = st.tabs([
        "📋 Incident Ledger Synthesis",
        "🛡️ Executive Situation Briefing",
        "📢 Plain-Language Safety Rewriting",
        "🏥 Emergency Resource Inventory",
    ])

    # 1. Incident Ledger Summarization
    with ai_subtab1:
        st.markdown("#### Automated Incident Ledger Synthesis")
        st.caption(f"Consolidates active verified and unverified reports in {sector_short_city} without inventing external facts.")
        if st.button("Generate Incident Summary", key="btn_sum_inc", width="stretch"):
            with st.spinner("Synthesizing incident ledger..."):
                res = gemma.summarize_incidents(incidents)
                st.markdown(res.content)
                st.markdown("---")
                badge_type = "AI-GENERATED" if res.is_ai_generated else "DEMO MODE (RULE-BASED)"
                st.caption(f"**Status:** `{badge_type}` | **Model:** `{res.model_identifier}` | **Latency:** `{res.latency_ms} ms`")
                st.caption(f"**Disclaimer:** {res.disclaimer}")

    # 2. Executive Situation Briefing
    with ai_subtab2:
        st.markdown("#### Executive Situation Briefing")
        st.caption(f"Pairs active incident load with current meteorological telemetry in {sector_name}.")
        if st.button("Generate Executive Briefing", key="btn_briefing", width="stretch"):
            with st.spinner("Compiling tactical briefing..."):
                res = gemma.generate_situation_briefing(incidents, weather_info, resources)
                st.markdown(res.content)
                st.markdown("---")
                badge_type = "AI-GENERATED" if res.is_ai_generated else "DEMO MODE (RULE-BASED)"
                st.caption(f"**Status:** `{badge_type}` | **Model:** `{res.model_identifier}` | **Latency:** `{res.latency_ms} ms`")
                st.caption(f"**Disclaimer:** {res.disclaimer}")

    # 3. Plain-Language Safety Translation
    with ai_subtab3:
        st.markdown("#### Clear-Language Safety Guidance Rewriting")
        st.caption("Translates technical civil defense bulletins into clear, calm, accessible instructions.")
        chosen_cat = st.selectbox("Select Hazard Category for Guidance", options=config.CATEGORIES, key="guidance_cat")
        protocol_data = get_safety_protocol(chosen_cat)
        st.text_area("Official Civil Defense Source Bulletin", value=protocol_data["official_guidance"], height=130, disabled=True)

        if st.button("Translate to Plain Citizen Language", key="btn_rewrite_safety", width="stretch"):
            with st.spinner("Rewriting official guidance for public clarity..."):
                res = gemma.rewrite_safety_instructions(chosen_cat, protocol_data["official_guidance"])
                st.markdown(res.content)
                st.markdown("---")
                badge_type = "AI-GENERATED" if res.is_ai_generated else "DEMO MODE (RULE-BASED)"
                st.caption(f"**Status:** `{badge_type}` | **Model:** `{res.model_identifier}` | **Latency:** `{res.latency_ms} ms`")
                st.caption(f"**Disclaimer:** {res.disclaimer}")

    # 4. Resource Inventory Synthesis
    with ai_subtab4:
        st.markdown("#### Emergency Resources Summary")
        st.caption(f"Summarizes relief shelters, trauma centers, and staging depots in {sector_short_city} without hallucinating availability.")
        if st.button("Synthesize Resource Readiness", key="btn_res_sum", width="stretch"):
            with st.spinner("Analyzing emergency facilities..."):
                res = gemma.summarize_resources(resources)
                st.markdown(res.content)
                st.markdown("---")
                badge_type = "AI-GENERATED" if res.is_ai_generated else "DEMO MODE (RULE-BASED)"
                st.caption(f"**Status:** `{badge_type}` | **Model:** `{res.model_identifier}` | **Latency:** `{res.latency_ms} ms`")
                st.caption(f"**Disclaimer:** {res.disclaimer}")

# =============================================================================
# TAB 6: GUIDANCE & ETHICS DISCLOSURE
# =============================================================================
with tabs[6]:
    st.subheader("ℹ️ Ethical AI Disaster Management & System Architecture")

    st.markdown(
        """
        ### 1. Mandatory Grounding & Safety Principles
        - **Model Isolation:** DisasterShield AI restricts generative AI inference exclusively to **Google Gemma 4**. No proprietary black-box APIs are invoked.
        - **Strict Grounding:** The model is constrained to facts present in the incident ledger and verified environmental telemetry. It is explicitly forbidden from inventing casualty counts, safe evacuation corridors, or official government orders.
        - **Verification Separation:** Every citizen-submitted report begins as **UNVERIFIED**. An emergency officer must confirm the report via the Administrator Verification Desk before it is classified as official.
        - **Transparent Fallbacks:** If a local Gemma 4 inference server is unavailable, the entire application functions reliably in clearly labeled **Demo Mode** using deterministic rule-based templates without pretending to be AI-generated.

        ### 2. Supported Demonstration Command Sectors
        """
    )

    for c_title, c_meta in config.DEMO_CITIES.items():
        with st.expander(f"📍 {c_title} — {c_meta['river']}"):
            st.markdown(f"- **Latitude:** `{c_meta['lat']}` | **Longitude:** `{c_meta['lon']}` | **Default Zoom:** `{c_meta['zoom']}`")
            st.markdown(f"- **Description:** {c_meta['description']}")

    st.markdown("---")
    st.markdown(
        """
        ### 3. Open-Source Compliance & Licensing
        - **Application Code:** Apache License 2.0.
        - **Gemma Open Model:** Subject to Google Gemma Terms of Use.
        - **Weather Telemetry:** Open-Meteo Public API (Attribution CC BY 4.0).
        - **Mapping:** OpenStreetMap contributors.
        """
    )

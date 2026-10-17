"""
DisasterShield AI - 3D Digital Twin & Disaster Simulation Module
Generates an interactive, WebGL-powered 3D disaster awareness environment
using Three.js embedded directly inside Streamlit without external pip dependencies.
Supports Flood, Fire, Earthquake, and Storm procedural simulations with genuine 3D controls.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

import config

STATIC_DIR = Path(__file__).resolve().parent / "static"


def get_local_js(filename: str) -> str:
    """Reads local cached JS library, or returns empty string if missing."""
    file_path = STATIC_DIR / filename
    if file_path.exists():
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


def build_3d_simulation_html(
    incidents: List[Dict[str, Any]],
    resources: List[Dict[str, Any]],
    center_lat: float = config.DEFAULT_LAT,
    center_lon: float = config.DEFAULT_LON,
    city_name: str = config.DEFAULT_LOCATION_NAME,
    disaster_mode: str = "Flood",
    simulation_intensity: str = "Medium",
    water_level: float = 3.5,
    earthquake_intensity: float = 4.2,
    rainfall_rate: float = 45.0,
    show_incidents: bool = True,
    show_resources: bool = True,
    selected_incident_id: Optional[str] = None,
) -> str:
    """
    Constructs a complete, standalone, responsive Three.js 3D simulation canvas
    with procedural city terrain, animated water surfaces, particle fire systems,
    seismic earthquake tremor physics, and storm rain visualizations.
    """
    three_js_code = get_local_js("three.min.js")
    orbit_controls_code = get_local_js("OrbitControls.js")

    # Serialize incidents & resources safely
    incidents_json = json.dumps(incidents, ensure_ascii=False)
    resources_json = json.dumps(resources, ensure_ascii=False)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DisasterShield AI 3D Simulation</title>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                user-select: none;
            }}
            body, html {{
                width: 100%;
                height: 100%;
                overflow: hidden;
                background-color: #070d19;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                color: #e2e8f0;
            }}
            #canvas-container {{
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
            }}
            
            /* Top Telemetry & Mode Bar */
            .telemetry-bar {{
                position: absolute;
                top: 14px;
                left: 16px;
                right: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(10, 20, 38, 0.88);
                border: 1px solid rgba(56, 189, 248, 0.28);
                border-radius: 10px;
                padding: 10px 18px;
                backdrop-filter: blur(8px);
                z-index: 100;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            }}
            .telemetry-left {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .brand-pill {{
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                color: #ffffff;
                font-weight: 800;
                font-size: 11px;
                padding: 4px 10px;
                border-radius: 6px;
                letter-spacing: 0.5px;
            }}
            .demo-watermark {{
                background: rgba(220, 38, 38, 0.2);
                border: 1px solid #ef4444;
                color: #fca5a5;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 6px;
            }}
            .telemetry-metrics {{
                display: flex;
                gap: 16px;
                font-size: 12px;
            }}
            .metric-item {{
                display: flex;
                flex-direction: column;
                align-items: flex-end;
            }}
            .metric-item span:first-child {{
                color: #94a3b8;
                font-size: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .metric-item span:last-child {{
                font-weight: 700;
                color: #38bdf8;
                font-size: 13px;
            }}
            
            /* Interactive Simulation Control HUD */
            .controls-panel {{
                position: absolute;
                top: 76px;
                left: 16px;
                width: 290px;
                background: rgba(10, 20, 38, 0.90);
                border: 1px solid rgba(56, 189, 248, 0.24);
                border-radius: 10px;
                padding: 14px;
                backdrop-filter: blur(8px);
                z-index: 90;
                box-shadow: 0 4px 16px rgba(0,0,0,0.35);
            }}
            .panel-header {{
                font-size: 12px;
                font-weight: 700;
                color: #38bdf8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 12px;
                border-bottom: 1px solid rgba(56, 189, 248, 0.2);
                padding-bottom: 6px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .control-group {{
                margin-bottom: 12px;
            }}
            .control-group label {{
                display: flex;
                justify-content: space-between;
                font-size: 11px;
                color: #cbd5e1;
                font-weight: 600;
                margin-bottom: 4px;
            }}
            .btn-mode-row {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 4px;
                margin-bottom: 10px;
            }}
            .btn-mode {{
                background: #1e293b;
                border: 1px solid #334155;
                color: #cbd5e1;
                padding: 6px 2px;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.15s ease;
                text-align: center;
            }}
            .btn-mode:hover {{
                background: #334155;
                color: #ffffff;
            }}
            .btn-mode.active {{
                background: #0284c7;
                border-color: #38bdf8;
                color: #ffffff;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
            }}
            
            input[type=range] {{
                width: 100%;
                height: 6px;
                background: #1e293b;
                border-radius: 4px;
                outline: none;
                -webkit-appearance: none;
            }}
            input[type=range]::-webkit-slider-thumb {{
                -webkit-appearance: none;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #38bdf8;
                cursor: pointer;
                box-shadow: 0 0 6px rgba(56, 189, 248, 0.6);
            }}
            
            .toggle-row {{
                display: flex;
                gap: 8px;
                margin-top: 10px;
            }}
            .btn-toggle {{
                flex: 1;
                background: #1e293b;
                border: 1px solid #334155;
                color: #cbd5e1;
                padding: 6px 4px;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
                cursor: pointer;
                text-align: center;
            }}
            .btn-toggle.active {{
                background: #0369a1;
                border-color: #38bdf8;
                color: #ffffff;
            }}

            /* Incident Detail Card */
            .detail-card {{
                position: absolute;
                bottom: 20px;
                left: 16px;
                width: 320px;
                background: rgba(10, 20, 38, 0.94);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 10px;
                padding: 14px;
                backdrop-filter: blur(8px);
                z-index: 95;
                box-shadow: 0 6px 20px rgba(0,0,0,0.5);
                display: none;
            }}
            .detail-card.visible {{
                display: block;
                animation: fadeIn 0.2s ease;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(6px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            /* Tactical Legend */
            .legend-panel {{
                position: absolute;
                bottom: 20px;
                right: 16px;
                background: rgba(10, 20, 38, 0.88);
                border: 1px solid rgba(56, 189, 248, 0.24);
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 11px;
                z-index: 90;
                backdrop-filter: blur(6px);
            }}
            .legend-title {{
                font-weight: 700;
                color: #38bdf8;
                font-size: 11px;
                text-transform: uppercase;
                margin-bottom: 6px;
                border-bottom: 1px solid rgba(56, 189, 248, 0.2);
                padding-bottom: 3px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 4px;
                font-size: 11px;
            }}
            .legend-dot {{
                width: 10px;
                height: 10px;
                border-radius: 2px;
            }}
            
            /* Camera navigation hints */
            .camera-hints {{
                position: absolute;
                top: 76px;
                right: 16px;
                background: rgba(10, 20, 38, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 10px;
                color: #94a3b8;
                z-index: 80;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container"></div>

        <!-- Top Telemetry Bar -->
        <div class="telemetry-bar">
            <div class="telemetry-left">
                <span class="brand-pill">3D DIGITAL TWIN</span>
                <span class="demo-watermark">⚠️ DEMO SIMULATION</span>
                <span style="font-size: 12px; font-weight: 600; color: #f1f5f9;">{city_name} Command Sector</span>
            </div>
            <div class="telemetry-metrics">
                <div class="metric-item">
                    <span>Active Mode</span>
                    <span id="hud-mode-display">{disaster_mode.upper()}</span>
                </div>
                <div class="metric-item">
                    <span>Simulated Flood Level</span>
                    <span id="hud-water-display">{water_level:.1f} m</span>
                </div>
                <div class="metric-item">
                    <span>Seismic Shaking</span>
                    <span id="hud-shake-display">{earthquake_intensity:.1f} Richter</span>
                </div>
                <div class="metric-item">
                    <span>Precipitation</span>
                    <span id="hud-rain-display">{rainfall_rate:.0f} mm/h</span>
                </div>
            </div>
        </div>

        <!-- Camera Hints -->
        <div class="camera-hints">
            🖱️ Left Drag: Orbit | Right Drag: Pan | Scroll: Zoom
        </div>

        <!-- Simulation Controls Panel -->
        <div class="controls-panel">
            <div class="panel-header">
                <span>Simulation Matrix</span>
                <button id="btn-play-pause" style="background:#0284c7;border:none;color:white;border-radius:4px;padding:2px 8px;font-size:10px;cursor:pointer;">PAUSE</button>
            </div>

            <!-- Disaster Mode Switcher -->
            <div class="control-group">
                <label><span>Disaster Scenario</span></label>
                <div class="btn-mode-row">
                    <button class="btn-mode {'active' if disaster_mode == 'Flood' else ''}" onclick="setDisasterMode('Flood')">🌊 FLOOD</button>
                    <button class="btn-mode {'active' if disaster_mode == 'Fire' else ''}" onclick="setDisasterMode('Fire')">🔥 FIRE</button>
                    <button class="btn-mode {'active' if disaster_mode == 'Earthquake' else ''}" onclick="setDisasterMode('Earthquake')">🌋 QUAKE</button>
                    <button class="btn-mode {'active' if disaster_mode == 'Storm' else ''}" onclick="setDisasterMode('Storm')">⛈️ STORM</button>
                </div>
            </div>

            <!-- Dynamic Flood Water Level Slider -->
            <div class="control-group" id="group-water">
                <label>
                    <span>Flood Water Elevation</span>
                    <span id="val-water">{water_level:.1f} m</span>
                </label>
                <input type="range" id="slider-water" min="0" max="12" step="0.2" value="{water_level}" oninput="updateWaterLevel(this.value)">
                <div style="font-size:9px;color:#64748b;margin-top:2px;">Fictional flood plain depth simulation</div>
            </div>

            <!-- Dynamic Earthquake Shaking Slider -->
            <div class="control-group" id="group-shake">
                <label>
                    <span>Earthquake Tremor Amplitude</span>
                    <span id="val-shake">{earthquake_intensity:.1f}</span>
                </label>
                <input type="range" id="slider-shake" min="0" max="10" step="0.5" value="{earthquake_intensity}" oninput="updateShake(this.value)">
                <div style="font-size:9px;color:#64748b;margin-top:2px;">Seismic ground vibration harmonic frequency</div>
            </div>

            <!-- Dynamic Storm Rain Slider -->
            <div class="control-group" id="group-rain">
                <label>
                    <span>Precipitation & Lightning Rate</span>
                    <span id="val-rain">{rainfall_rate:.0f} mm/h</span>
                </label>
                <input type="range" id="slider-rain" min="0" max="100" step="5" value="{rainfall_rate}" oninput="updateRain(this.value)">
                <div style="font-size:9px;color:#64748b;margin-top:2px;">3D particle velocity & flash illumination</div>
            </div>

            <!-- Toggles & Reset -->
            <div class="toggle-row">
                <button id="toggle-incidents" class="btn-toggle {'active' if show_incidents else ''}" onclick="toggleIncidents()">Incidents (ON)</button>
                <button id="toggle-resources" class="btn-toggle {'active' if show_resources else ''}" onclick="toggleResources()">Resources (ON)</button>
                <button class="btn-toggle" onclick="resetCamera()">Reset View</button>
            </div>
        </div>

        <!-- Selected Incident Detail Panel -->
        <div id="incident-card" class="detail-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span id="card-badge" style="background:#dc2626;color:white;font-size:10px;font-weight:bold;padding:2px 8px;border-radius:10px;">HIGH SEVERITY</span>
                <button onclick="closeIncidentCard()" style="background:none;border:none;color:#94a3b8;font-size:14px;cursor:pointer;">✕</button>
            </div>
            <h4 id="card-title" style="font-size:13px;color:#ffffff;margin-bottom:4px;">Incident Title</h4>
            <div id="card-desc" style="font-size:11px;color:#cbd5e1;line-height:1.4;margin-bottom:8px;">Description text...</div>
            <div style="font-size:10px;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.1);padding-top:6px;line-height:1.5;">
                <strong>Status:</strong> <span id="card-status" style="color:#10b981;font-weight:bold;">VERIFIED</span><br>
                <strong>Location:</strong> <span id="card-location">Daraganj Ghat</span><br>
                <strong>Data Source:</strong> <span id="card-source">Civil Defense Volunteer</span><br>
                <span id="card-demo" style="color:#f87171;font-weight:bold;">⚠️ FICTIONAL DEMO SIMULATION DATA</span>
            </div>
        </div>

        <!-- Tactical 3D Legend -->
        <div class="legend-panel">
            <div class="legend-title">Tactical 3D Symbols</div>
            <div class="legend-item"><div class="legend-dot" style="background:#7f1d1d;"></div> Critical Incident</div>
            <div class="legend-item"><div class="legend-dot" style="background:#dc2626;"></div> High Severity</div>
            <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div> Moderate Severity</div>
            <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Low Severity</div>
            <div class="legend-item"><div class="legend-dot" style="background:#0284c7;"></div> Verified Official (Shield Ring)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#eab308;"></div> Unverified Citizen (Flag Halo)</div>
            <div class="legend-item"><div class="legend-dot" style="background:#3b82f6;"></div> Emergency Facility / Shelter</div>
        </div>

        <!-- Embedded Three.js Engine Scripts (Local Offline Cache) -->
        <script>
            {three_js_code}
        </script>
        <script>
            {orbit_controls_code}
        </script>

        <!-- Main 3D Simulation Logic -->
        <script>
            // Data bindings from Python backend
            const INCIDENTS_DATA = {incidents_json};
            const RESOURCES_DATA = {resources_json};
            const CENTER_LAT = {center_lat};
            const CENTER_LON = {center_lon};

            // Simulation state variables
            let currentDisasterMode = "{disaster_mode}";
            let currentWaterLevel = {water_level};
            let currentShakeIntensity = {earthquake_intensity};
            let currentRainRate = {rainfall_rate};
            let isSimulationPaused = false;
            let showIncidentsFlag = {str(show_incidents).lower()};
            let showResourcesFlag = {str(show_resources).lower()};
            let selectedIncidentId = "{selected_incident_id or ''}";

            // Three.js Core Objects
            let scene, camera, renderer, controls;
            let terrainMesh, riverWaterMesh;
            let buildingsGroup, incidentsGroup, resourcesGroup, roadGroup;
            let fireParticleGroup, rainParticleSystem;
            let ambientLight, directionalLight, firePointLight, lightningLight;
            let clock = new THREE.Clock();
            let raycaster = new THREE.Raycaster();
            let mouse = new THREE.Vector2();

            // Coordinate conversion: GPS Lat/Lon to 3D X/Z (Prayagraj Region Scale)
            function gpsTo3D(lat, lon) {{
                const scale = 800.0;
                const x = (lon - CENTER_LON) * scale;
                const z = -(lat - CENTER_LAT) * scale;
                return {{ x, z }};
            }}

            function init() {{
                const container = document.getElementById('canvas-container');

                // 1. Scene setup
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x070d19);
                scene.fog = new THREE.FogExp2(0x070d19, 0.0035);

                // 2. Camera setup
                camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 1000);
                camera.position.set(0, 75, 130);

                // 3. Renderer setup
                renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                container.appendChild(renderer.domElement);

                // 4. OrbitControls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.maxPolarAngle = Math.PI / 2.1;
                controls.minDistance = 20;
                controls.maxDistance = 350;
                controls.target.set(0, 0, 0);

                // 5. Lighting
                ambientLight = new THREE.AmbientLight(0x1e293b, 1.2);
                scene.add(ambientLight);

                directionalLight = new THREE.DirectionalLight(0x38bdf8, 1.4);
                directionalLight.position.set(60, 100, 40);
                directionalLight.castShadow = true;
                scene.add(directionalLight);

                // Fire point light for dramatic flickering
                firePointLight = new THREE.PointLight(0xff6600, 0, 40);
                firePointLight.position.set(10, 8, -5);
                scene.add(firePointLight);

                // Lightning directional light for storm mode
                lightningLight = new THREE.DirectionalLight(0xdbeafe, 0);
                lightningLight.position.set(-20, 120, -30);
                scene.add(lightningLight);

                // 6. Groups
                buildingsGroup = new THREE.Group();
                incidentsGroup = new THREE.Group();
                resourcesGroup = new THREE.Group();
                roadGroup = new THREE.Group();
                fireParticleGroup = new THREE.Group();

                scene.add(buildingsGroup);
                scene.add(incidentsGroup);
                scene.add(resourcesGroup);
                scene.add(roadGroup);
                scene.add(fireParticleGroup);

                // 7. Procedural World Generation
                createTerrain();
                createRiverAndWater();
                createRoadsAndBridges();
                createProceduralCity();
                createIncidentMarkers();
                createEmergencyResourceMarkers();
                createFireParticles();
                createRainSystem();

                // 8. Event listeners
                window.addEventListener('resize', onWindowResize, false);
                window.addEventListener('click', onCanvasClick, false);

                // Apply initial UI mode
                applyDisasterMode(currentDisasterMode);

                // Check if an initial incident was selected from Streamlit
                if (selectedIncidentId) {{
                    focusIncidentById(selectedIncidentId);
                }}

                // Start Render Loop
                animate();
            }}

            // -----------------------------------------------------------------
            // Procedural Terrain & Rivers
            // -----------------------------------------------------------------
            function createTerrain() {{
                const gridWidth = 320;
                const gridHeight = 320;
                const geometry = new THREE.PlaneGeometry(gridWidth, gridHeight, 64, 64);
                geometry.rotateX(-Math.PI / 2);

                const pos = geometry.attributes.position;
                for (let i = 0; i < pos.count; i++) {{
                    const x = pos.getX(i);
                    const z = pos.getZ(i);

                    // Carve winding S-riverbed cutting diagonally (representing Ganga-Yamuna basin)
                    const riverCenter = Math.sin(x * 0.02) * 25 + Math.cos(z * 0.02) * 15;
                    const distToRiver = Math.abs(z - riverCenter);

                    let y = 0;
                    if (distToRiver < 22) {{
                        // Depressed riverbed channel
                        y = -5.0 + Math.pow(distToRiver / 22, 2) * 3.5;
                    }} else {{
                        // Gentle surrounding topography
                        y = Math.sin(x * 0.04) * 1.5 + Math.cos(z * 0.04) * 1.5 + (distToRiver - 22) * 0.05;
                    }}
                    pos.setY(i, y);
                }}
                geometry.computeVertexNormals();

                const material = new THREE.MeshStandardMaterial({{
                    color: 0x0f172a,
                    roughness: 0.85,
                    metalness: 0.2,
                    flatShading: true,
                }});

                terrainMesh = new THREE.Mesh(geometry, material);
                terrainMesh.receiveShadow = true;
                scene.add(terrainMesh);

                // Subtle tactical cyan wireframe overlay
                const wireframe = new THREE.LineSegments(
                    new THREE.WireframeGeometry(geometry),
                    new THREE.LineBasicMaterial({{ color: 0x1e3a5f, transparent: true, opacity: 0.35 }})
                );
                terrainMesh.add(wireframe);
            }}

            function createRiverAndWater() {{
                // Translucent animated water surface plane
                const waterGeo = new THREE.PlaneGeometry(320, 100, 64, 32);
                waterGeo.rotateX(-Math.PI / 2);

                const waterMat = new THREE.MeshStandardMaterial({{
                    color: 0x0284c7,
                    roughness: 0.1,
                    metalness: 0.8,
                    transparent: true,
                    opacity: 0.72,
                }});

                riverWaterMesh = new THREE.Mesh(waterGeo, waterMat);
                // Position water at initial simulation water level
                riverWaterMesh.position.set(0, currentWaterLevel - 3.5, 0);
                riverWaterMesh.receiveShadow = true;
                scene.add(riverWaterMesh);
            }}

            function createRoadsAndBridges() {{
                // Arterial road network crossing city
                const roadMat = new THREE.MeshBasicMaterial({{ color: 0x334155 }});
                const roadLinesMat = new THREE.LineDashedMaterial({{ color: 0x38bdf8, dashSize: 2, gapSize: 2 }});

                // East-West arterial road
                const road1 = new THREE.Mesh(new THREE.PlaneGeometry(300, 4).rotateX(-Math.PI / 2), roadMat);
                road1.position.set(0, 0.2, -15);
                roadGroup.add(road1);

                // North-South Bridge (representing Phaphamau/Naini bridge crossing the riverbed)
                const bridgeGeo = new THREE.BoxGeometry(6, 1.2, 90);
                const bridgeMat = new THREE.MeshStandardMaterial({{ color: 0x475569, metalness: 0.6, roughness: 0.3 }});
                const bridge = new THREE.Mesh(bridgeGeo, bridgeMat);
                bridge.position.set(-10, 4.5, 0);
                bridge.castShadow = true;
                roadGroup.add(bridge);

                // Bridge support pillars
                for (let z of [-25, 0, 25]) {{
                    const pillar = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.5, 9, 8), bridgeMat);
                    pillar.position.set(-10, 0, z);
                    roadGroup.add(pillar);
                }}
            }}

            // -----------------------------------------------------------------
            // Procedural City Districts
            // -----------------------------------------------------------------
            function createProceduralCity() {{
                const buildingMat = new THREE.MeshStandardMaterial({{
                    color: 0x1e293b,
                    metalness: 0.5,
                    roughness: 0.4,
                }});

                const windowMatLit = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});
                const windowMatAmber = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});

                // City sectors (Daraganj, Civil Lines, Katra, Naini)
                const sectors = [
                    {{ xRange: [15, 75], zRange: [20, 60], count: 32, maxH: 14, name: "Daraganj" }},
                    {{ xRange: [-75, -20], zRange: [-65, -20], count: 40, maxH: 26, name: "Civil Lines" }},
                    {{ xRange: [-20, 35], zRange: [-70, -30], count: 35, maxH: 18, name: "Katra" }},
                    {{ xRange: [-50, 40], zRange: [40, 85], count: 28, maxH: 12, name: "Naini Sector" }},
                ];

                sectors.forEach(sec => {{
                    for (let i = 0; i < sec.count; i++) {{
                        const bx = sec.xRange[0] + Math.random() * (sec.xRange[1] - sec.xRange[0]);
                        const bz = sec.zRange[0] + Math.random() * (sec.zRange[1] - sec.zRange[0]);
                        const bw = 4 + Math.random() * 5;
                        const bd = 4 + Math.random() * 5;
                        const bh = 5 + Math.random() * sec.maxH;

                        const bMesh = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, bd), buildingMat);
                        bMesh.position.set(bx, bh / 2, bz);
                        bMesh.castShadow = true;
                        bMesh.receiveShadow = true;
                        buildingsGroup.add(bMesh);

                        // Illuminated window strips on high-rise structures
                        if (bh > 14) {{
                            const winMesh = new THREE.Mesh(
                                new THREE.PlaneGeometry(bw * 0.7, bh * 0.6),
                                (i % 2 === 0) ? windowMatLit : windowMatAmber
                            );
                            winMesh.position.set(bx, bh / 2, bz + bd / 2 + 0.05);
                            buildingsGroup.add(winMesh);
                        }}

                        // Rooftop communication antenna with emergency beacon
                        if (bh > 20) {{
                            const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 4), new THREE.MeshBasicMaterial({{ color: 0x94a3b8 }}));
                            mast.position.set(bx, bh + 2, bz);
                            buildingsGroup.add(mast);

                            const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.35, 6, 6), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
                            beacon.position.set(bx, bh + 4, bz);
                            buildingsGroup.add(beacon);
                        }}
                    }}
                }});
            }}

            // -----------------------------------------------------------------
            // 3D Incident & Resource Pins
            // -----------------------------------------------------------------
            let incidentMeshes = [];

            function createIncidentMarkers() {{
                incidentsGroup.clear();
                incidentMeshes = [];

                const severityColors = {{
                    "Critical": 0x7f1d1d,
                    "High": 0xdc2626,
                    "Moderate": 0xf59e0b,
                    "Low": 0x10b981
                }};

                INCIDENTS_DATA.forEach(inc => {{
                    const pos = gpsTo3D(inc.latitude, inc.longitude);
                    const colorHex = severityColors[inc.severity] || 0xdc2626;

                    // Diamond floating prism
                    const pinGeo = new THREE.OctahedronGeometry(1.6, 0);
                    const pinMat = new THREE.MeshStandardMaterial({{
                        color: colorHex,
                        emissive: colorHex,
                        emissiveIntensity: 0.6,
                        metalness: 0.3,
                        roughness: 0.2
                    }});
                    const pinMesh = new THREE.Mesh(pinGeo, pinMat);
                    pinMesh.position.set(pos.x, 8.5, pos.z);
                    pinMesh.userData = {{ isIncident: true, data: inc }};
                    incidentsGroup.add(pinMesh);
                    incidentMeshes.push(pinMesh);

                    // Ground vertical beacon line
                    const lineGeo = new THREE.CylinderGeometry(0.08, 0.08, 8.5);
                    const lineMat = new THREE.MeshBasicMaterial({{ color: colorHex, transparent: true, opacity: 0.6 }});
                    const line = new THREE.Mesh(lineGeo, lineMat);
                    line.position.set(pos.x, 4.25, pos.z);
                    incidentsGroup.add(line);

                    // Distinguish Verified vs Unverified indicator rings
                    if (inc.verification_status === "VERIFIED") {{
                        // Smooth cyan tactical shield ring
                        const ringGeo = new THREE.RingGeometry(2.2, 2.6, 24);
                        ringGeo.rotateX(-Math.PI / 2);
                        const ringMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, side: THREE.DoubleSide }});
                        const ring = new THREE.Mesh(ringGeo, ringMat);
                        ring.position.set(pos.x, 0.4, pos.z);
                        incidentsGroup.add(ring);
                    }} else {{
                        // Dotted yellow caution halo for unverified citizen posts
                        const ringGeo = new THREE.RingGeometry(2.0, 2.3, 12);
                        ringGeo.rotateX(-Math.PI / 2);
                        const ringMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b, wireframe: true, side: THREE.DoubleSide }});
                        const ring = new THREE.Mesh(ringGeo, ringMat);
                        ring.position.set(pos.x, 0.4, pos.z);
                        incidentsGroup.add(ring);
                    }}

                    // If fire incident, position fire light near here
                    if (inc.category === "fire") {{
                        firePointLight.position.set(pos.x, 6, pos.z);
                    }}
                }});

                incidentsGroup.visible = showIncidentsFlag;
            }}

            function createEmergencyResourceMarkers() {{
                resourcesGroup.clear();
                RESOURCES_DATA.forEach(res => {{
                    const pos = gpsTo3D(res.latitude, res.longitude);
                    // Blue emergency medical/shelter cross
                    const crossMat = new THREE.MeshStandardMaterial({{
                        color: 0x3b82f6,
                        emissive: 0x1d4ed8,
                        emissiveIntensity: 0.5,
                        metalness: 0.4
                    }});

                    const bar1 = new THREE.Mesh(new THREE.BoxGeometry(0.8, 2.4, 0.4), crossMat);
                    const bar2 = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.8, 0.4), crossMat);
                    const resCross = new THREE.Group();
                    resCross.add(bar1);
                    resCross.add(bar2);
                    resCross.position.set(pos.x, 7.5, pos.z);
                    resCross.userData = {{ isResource: true, data: res }};
                    resourcesGroup.add(resCross);
                    incidentMeshes.push(bar1); // Register for raycasting
                    bar1.userData = {{ isResource: true, data: res }};

                    // White ground marker
                    const gDisk = new THREE.Mesh(
                        new THREE.CircleGeometry(2.0, 16).rotateX(-Math.PI / 2),
                        new THREE.MeshBasicMaterial({{ color: 0x60a5fa, transparent: true, opacity: 0.4 }})
                    );
                    gDisk.position.set(pos.x, 0.3, pos.z);
                    resourcesGroup.add(gDisk);
                }});

                resourcesGroup.visible = showResourcesFlag;
            }}

            // -----------------------------------------------------------------
            // Particle Systems: Fire & Storm Rain
            // -----------------------------------------------------------------
            let fireParticles = [];
            function createFireParticles() {{
                fireParticleGroup.clear();
                fireParticles = [];
                const pCount = 140;

                // Find fire incident coords or use fallback Katra market coords
                let fPos = {{ x: 10, z: -10 }};
                const fireInc = INCIDENTS_DATA.find(i => i.category === "fire");
                if (fireInc) {{
                    fPos = gpsTo3D(fireInc.latitude, fireInc.longitude);
                }}

                const pGeo = new THREE.SphereGeometry(0.25, 4, 4);
                const colors = [0xff2200, 0xff7700, 0xffcc00, 0x444444];

                for (let i = 0; i < pCount; i++) {{
                    const pMat = new THREE.MeshBasicMaterial({{
                        color: colors[i % colors.length],
                        transparent: true,
                        opacity: 0.8
                    }});
                    const p = new THREE.Mesh(pGeo, pMat);
                    resetFireParticle(p, fPos);
                    fireParticleGroup.add(p);
                    fireParticles.push({{ mesh: p, basePos: fPos, speed: 0.08 + Math.random() * 0.12 }});
                }}
            }}

            function resetFireParticle(p, base) {{
                p.position.set(
                    base.x + (Math.random() - 0.5) * 4.0,
                    1.0 + Math.random() * 1.5,
                    base.z + (Math.random() - 0.5) * 4.0
                );
                p.scale.setScalar(0.4 + Math.random() * 0.8);
            }}

            let rainGeometry, rainPositions;
            function createRainSystem() {{
                const rainCount = 2000;
                rainGeometry = new THREE.BufferGeometry();
                rainPositions = new Float32Array(rainCount * 3);

                for (let i = 0; i < rainCount * 3; i += 3) {{
                    rainPositions[i] = (Math.random() - 0.5) * 260;
                    rainPositions[i + 1] = Math.random() * 100;
                    rainPositions[i + 2] = (Math.random() - 0.5) * 260;
                }}
                rainGeometry.setAttribute('position', new THREE.BufferAttribute(rainPositions, 3));

                const rainMat = new THREE.PointsMaterial({{
                    color: 0x93c5fd,
                    size: 0.45,
                    transparent: true,
                    opacity: 0.65,
                }});

                rainParticleSystem = new THREE.Points(rainGeometry, rainMat);
                scene.add(rainParticleSystem);
                rainParticleSystem.visible = (currentDisasterMode === "Storm");
            }}

            // -----------------------------------------------------------------
            // Simulation Controls & Real-Time Parameter Updates
            // -----------------------------------------------------------------
            window.setDisasterMode = function(mode) {{
                currentDisasterMode = mode;
                document.querySelectorAll('.btn-mode').forEach(b => b.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById('hud-mode-display').innerText = mode.toUpperCase();
                applyDisasterMode(mode);
            }};

            function applyDisasterMode(mode) {{
                // Update visuals based on mode
                if (mode === "Flood") {{
                    rainParticleSystem.visible = false;
                    fireParticleGroup.visible = false;
                    firePointLight.intensity = 0;
                    lightningLight.intensity = 0;
                }} else if (mode === "Fire") {{
                    rainParticleSystem.visible = false;
                    fireParticleGroup.visible = true;
                    firePointLight.intensity = 2.5;
                    lightningLight.intensity = 0;
                }} else if (mode === "Earthquake") {{
                    rainParticleSystem.visible = false;
                    fireParticleGroup.visible = false;
                    firePointLight.intensity = 0;
                    lightningLight.intensity = 0;
                }} else if (mode === "Storm") {{
                    rainParticleSystem.visible = true;
                    fireParticleGroup.visible = false;
                    firePointLight.intensity = 0;
                }}
            }}

            window.updateWaterLevel = function(val) {{
                currentWaterLevel = parseFloat(val);
                document.getElementById('val-water').innerText = currentWaterLevel.toFixed(1) + " m";
                document.getElementById('hud-water-display').innerText = currentWaterLevel.toFixed(1) + " m";
                if (riverWaterMesh) {{
                    riverWaterMesh.position.y = currentWaterLevel - 3.5;
                }}
            }};

            window.updateShake = function(val) {{
                currentShakeIntensity = parseFloat(val);
                document.getElementById('val-shake').innerText = currentShakeIntensity.toFixed(1);
                document.getElementById('hud-shake-display').innerText = currentShakeIntensity.toFixed(1) + " Richter";
            }};

            window.updateRain = function(val) {{
                currentRainRate = parseFloat(val);
                document.getElementById('val-rain').innerText = Math.round(currentRainRate) + " mm/h";
                document.getElementById('hud-rain-display').innerText = Math.round(currentRainRate) + " mm/h";
            }};

            window.toggleIncidents = function() {{
                showIncidentsFlag = !showIncidentsFlag;
                incidentsGroup.visible = showIncidentsFlag;
                const btn = document.getElementById('toggle-incidents');
                btn.classList.toggle('active', showIncidentsFlag);
                btn.innerText = "Incidents (" + (showIncidentsFlag ? "ON" : "OFF") + ")";
            }};

            window.toggleResources = function() {{
                showResourcesFlag = !showResourcesFlag;
                resourcesGroup.visible = showResourcesFlag;
                const btn = document.getElementById('toggle-resources');
                btn.classList.toggle('active', showResourcesFlag);
                btn.innerText = "Resources (" + (showResourcesFlag ? "ON" : "OFF") + ")";
            }};

            window.resetCamera = function() {{
                camera.position.set(0, 75, 130);
                controls.target.set(0, 0, 0);
            }};

            document.getElementById('btn-play-pause').onclick = function() {{
                isSimulationPaused = !isSimulationPaused;
                this.innerText = isSimulationPaused ? "RESUME" : "PAUSE";
                this.style.background = isSimulationPaused ? "#16a34a" : "#0284c7";
            }};

            // -----------------------------------------------------------------
            // Raycasting & Incident Card Interaction
            // -----------------------------------------------------------------
            function onCanvasClick(event) {{
                // Ignore clicks if clicking UI control panels
                if (event.target.closest('.controls-panel') || event.target.closest('.telemetry-bar') || event.target.closest('.detail-card')) {{
                    return;
                }}

                mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(incidentMeshes, true);

                if (intersects.length > 0) {{
                    const hit = intersects[0].object;
                    let targetData = hit.userData;
                    if (!targetData.data && hit.parent && hit.parent.userData.data) {{
                        targetData = hit.parent.userData;
                    }}

                    if (targetData.isIncident) {{
                        showIncidentCard(targetData.data);
                        focusCameraOn(hit.position.x, hit.position.z);
                    }} else if (targetData.isResource) {{
                        showResourceCard(targetData.data);
                        focusCameraOn(hit.position.x, hit.position.z);
                    }}
                }}
            }}

            function showIncidentCard(data) {{
                const card = document.getElementById('incident-card');
                document.getElementById('card-title').innerText = data.title;
                document.getElementById('card-desc').innerText = data.description;
                document.getElementById('card-badge').innerText = data.severity.toUpperCase() + " SEVERITY";
                document.getElementById('card-status').innerText = data.verification_status;
                document.getElementById('card-status').style.color = (data.verification_status === "VERIFIED") ? "#10b981" : "#f59e0b";
                document.getElementById('card-location').innerText = data.location_name;
                document.getElementById('card-source').innerText = data.reporter_label || "Citizen Report";
                document.getElementById('card-demo').innerText = data.is_demo ? "⚠️ FICTIONAL DEMO SIMULATION DATA" : "📍 CITIZEN FIELD SUBMISSION";
                card.classList.add('visible');
            }}

            function showResourceCard(data) {{
                const card = document.getElementById('incident-card');
                document.getElementById('card-title').innerText = data.name;
                document.getElementById('card-desc').innerText = data.description + " (Capacity: " + data.capacity + ")";
                document.getElementById('card-badge').innerText = "EMERGENCY FACILITY";
                document.getElementById('card-badge').style.background = "#2563eb";
                document.getElementById('card-status').innerText = data.status.toUpperCase();
                document.getElementById('card-status').style.color = "#38bdf8";
                document.getElementById('card-location').innerText = data.location_name;
                document.getElementById('card-source').innerText = data.official_helpline_info;
                document.getElementById('card-demo').innerText = "🏥 DEMO EMERGENCY RESOURCE CATALOG";
                card.classList.add('visible');
            }}

            window.closeIncidentCard = function() {{
                document.getElementById('incident-card').classList.remove('visible');
            }};

            function focusCameraOn(x, z) {{
                controls.target.set(x, 4, z);
                camera.position.set(x, 25, z + 35);
            }}

            function focusIncidentById(id) {{
                const inc = INCIDENTS_DATA.find(i => i.id === id);
                if (inc) {{
                    const pos = gpsTo3D(inc.latitude, inc.longitude);
                    focusCameraOn(pos.x, pos.z);
                    showIncidentCard(inc);
                }}
            }}

            function onWindowResize() {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }}

            // -----------------------------------------------------------------
            // Main Animation & Physics Loop
            // -----------------------------------------------------------------
            function animate() {{
                requestAnimationFrame(animate);

                const delta = clock.getDelta();
                const time = clock.getElapsedTime();

                if (!isSimulationPaused) {{
                    // 1. Water Surface Wave Ripple
                    if (riverWaterMesh) {{
                        const pos = riverWaterMesh.geometry.attributes.position;
                        for (let i = 0; i < pos.count; i++) {{
                            const u = pos.getX(i);
                            const v = pos.getY(i);
                            const wave = Math.sin(u * 0.08 + time * 1.8) * 0.35 + Math.cos(v * 0.08 + time * 1.5) * 0.25;
                            pos.setZ(i, wave);
                        }}
                        riverWaterMesh.geometry.attributes.position.needsUpdate = true;
                    }}

                    // 2. Incident Pin Floating Oscillation
                    incidentMeshes.forEach((mesh, idx) => {{
                        mesh.rotation.y += 0.015;
                        mesh.position.y = 8.5 + Math.sin(time * 2.0 + idx) * 0.6;
                    }});

                    // 3. Fire Particles Physics
                    if (currentDisasterMode === "Fire") {{
                        fireParticles.forEach(fp => {{
                            fp.mesh.position.y += fp.speed;
                            fp.mesh.position.x += (Math.random() - 0.5) * 0.15;
                            fp.mesh.position.z += (Math.random() - 0.5) * 0.15;
                            fp.mesh.scale.multiplyScalar(0.985);

                            if (fp.mesh.position.y > 14.0) {{
                                resetFireParticle(fp.mesh, fp.basePos);
                            }}
                        }});
                        // Random fire flickering light
                        firePointLight.intensity = 2.0 + Math.sin(time * 12.0) * 0.8;
                    }}

                    // 4. Earthquake Harmonic Seismic Vibration Physics
                    if (currentDisasterMode === "Earthquake" && currentShakeIntensity > 0) {{
                        const shakeAmp = currentShakeIntensity * 0.08;
                        const shakeFreq = 22.0;
                        const quakeX = Math.sin(time * shakeFreq) * shakeAmp;
                        const quakeZ = Math.cos(time * shakeFreq * 0.9) * shakeAmp;

                        terrainMesh.position.set(quakeX, 0, quakeZ);
                        buildingsGroup.position.set(quakeX, 0, quakeZ);
                    }} else {{
                        terrainMesh.position.set(0, 0, 0);
                        buildingsGroup.position.set(0, 0, 0);
                    }}

                    // 5. Storm Rainfall & Dynamic Lightning
                    if (currentDisasterMode === "Storm") {{
                        const positions = rainGeometry.attributes.position.array;
                        const fallSpeed = 1.2 + (currentRainRate / 100.0) * 1.8;

                        for (let i = 1; i < positions.length; i += 3) {{
                            positions[i] -= fallSpeed;
                            if (positions[i] < 0) {{
                                positions[i] = 90;
                            }}
                        }}
                        rainGeometry.attributes.position.needsUpdate = true;

                        // Lightning flash probability
                        if (Math.random() < 0.018 && currentRainRate > 20) {{
                            lightningLight.intensity = 3.5;
                        }} else {{
                            lightningLight.intensity = Math.max(0, lightningLight.intensity - 0.35);
                        }}
                    }}
                }}

                controls.update();
                renderer.render(scene, camera);
            }}

            // Run initialization once DOM loaded
            window.onload = init;
        </script>
    </body>
    </html>
    """
    return html_content

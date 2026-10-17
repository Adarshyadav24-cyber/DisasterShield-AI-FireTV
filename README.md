# 🛡️ DisasterShield AI
### Early Awareness. Verified Information. Safer Decisions.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B.svg)](https://streamlit.io/)
[![Folium](https://img.shields.io/badge/Folium-0.20.0-77B800.svg)](https://python-visualization.github.io/folium/)
[![AI Engine](https://img.shields.io/badge/AI%20Model-Google%20Gemma%204-purple.svg)](https://ai.google.dev/gemma)

---

## ⚠️ Mandatory Public Safety & Transparency Notice

> **"DisasterShield AI is an informational prototype, not an official emergency service. Verify alerts and follow instructions from authorized local authorities. Do not rely on this prototype alone for evacuation decisions."**

- **Official Emergency Contact:** In an active emergency in India, dial **112** (All-in-One Emergency Helpline), **1077** (State Disaster Control Room), or **108** (Emergency Medical Services). DisasterShield AI does not invent phone numbers or issue binding evacuation directives.
- **No Fictional Hazards Represented as Real:** All initial pre-loaded data points in Prayagraj, UP, are explicitly demarcated with the `DEMO DATA` watermark.

---

## 🌟 Executive Summary

**DisasterShield AI** is an open-source, hackathon-ready disaster awareness and response platform built to address information chaos during climate catastrophes. It combines real-time citizen crowdsourcing, trusted official verification workflows, live meteorological telemetry via Open-Meteo, interactive geospatial Folium mapping, and strictly grounded synthesis powered exclusively by **Google Gemma 4**.

---

## 🎯 Key Architectural Pillars

1. **Incident Verification Pipeline (Anti-Disinformation):**
   - Every public citizen report strictly starts in **UNVERIFIED** status.
   - An authorized emergency coordinator validates or rejects incoming reports via the PIN-protected **Administrator Verification Desk**.
   - Audit metadata (verifier name, ground inspection notes, timestamp) is permanently recorded.

2. **Strict Generative AI Restriction (Google Gemma 4 Only):**
   - Restricted **strictly and exclusively** to Google Gemma 4 models (e.g., `gemma4:e2b`).
   - Does **not** use or depend on OpenAI, Anthropic, or Gemini generative endpoints.
   - Grounded prompt constraints: Gemma 4 only synthesizes facts present in the active incident ledger and weather telemetry. It is strictly prohibited from inventing casualties, safe evacuation corridors, or official orders.

3. **Graceful, Transparent Demo Mode:**
   - If no local or remote Gemma 4 inference server is active, the application operates in **Safe Demo Mode**.
   - Demo mode uses transparent, deterministic rule-based templates that are explicitly labeled as rule-based and never masquerade as AI-generated text.

4. **Live Meteorological Telemetry (Open-Meteo):**
   - Fetches live temperature, precipitation, wind speed, and weather conditions from the public, keyless Open-Meteo API.
   - If disconnected, presents clearly labeled simulated telemetry without fabricating live disaster alerts.

5. **3D Digital Twin & Disaster Simulation Studio (Three.js WebGL):**
   - Immersive 3D procedural terrain and urban sectors representing Prayagraj, UP.
   - **Flood Simulation:** Translucent blue animated water plane with sinusoidal waves whose elevation dynamically rises and submerges riverbank quays.
   - **Fire Simulation:** Controlled dynamic particle flame and rising smoke plumes with point light flickering on building facades.
   - **Earthquake Simulation:** Harmonic seismic tremor equations oscillate terrain and building geometry with intensity tied directly to Richter scale controls.
   - **Storm Simulation:** 2,000 falling 3D rain streaks with directional wind velocity and periodic ambient lightning illumination bursts.
   - **Interactive 3D Controls:** OrbitControls (orbit, pan, zoom), scenario selector, intensity sliders, on-canvas HUD, and 3D raycasting to inspect incident metadata.
   - **Zero Extra Dependencies:** Uses high-performance WebGL via Three.js embedded directly via Streamlit components, backed by local offline JS caches.

6. **Multi-City Geospatial Tactical 2D Map (Folium + Streamlit):**
   - Dynamic location selector covering key urban and riverine centers:
     - **Prayagraj, Uttar Pradesh** (Default — Ganga & Yamuna Sangam Basin)
     - **Lucknow, Uttar Pradesh** (Gomti Riverfront Corridor)
     - **Varanasi, Uttar Pradesh** (Assi Ghat & Ganges Riverfront)
     - **New Delhi, India** (Yamuna Floodplain Corridor)
   - Color-coded severity pins (Low, Moderate, High, Critical).
   - Distinct icons for Verified (checkmark) vs. Unverified (flag) reports.
   - Emergency resource overlays (relief camps, trauma centers, staging depots).
   - Clear on-map floating legend, coordinate bounds validation, swap-detection heuristics, and demo notices.

---

## 📁 Repository Structure

```
DisasterShield-AI/
├── app.py                     # Main Streamlit web application & UI tabs
├── config.py                  # Environment config, color tokens, and constants
├── requirements.txt           # Verified Python 3.11 package dependencies
├── .env.example               # Template for Gemma 4 endpoint and configuration
├── .gitignore                 # Ignores venvs, cache, credentials, model weights
├── LICENSE                    # Apache 2.0 open-source license with Gemma attribution
├── README.md                  # Comprehensive setup, transparency, and usage guide
├── run_app.bat                # Windows 1-click launch batch script
├── data/
│   ├── demo_incidents.json    # Initial realistic Prayagraj demonstration incident dataset
│   ├── demo_resources.json    # Emergency facilities (shelters, trauma centers)
│   └── user_incidents.json    # Local JSON storage for citizen submissions
├── modules/
│   ├── __init__.py
│   ├── simulation_3d.py       # WebGL 3D Digital Twin & procedural disaster simulation
│   ├── static/                # Cached local Three.js and OrbitControls libraries (offline ready)
│   ├── gemma_client.py        # Modular Gemma 4 client with safe demo fallbacks
│   ├── incident_manager.py    # Report validation, persistence, and verification desk
│   ├── weather_service.py     # Public Open-Meteo weather integration
│   ├── map_view.py            # Folium geospatial builder, popups, and custom legend
│   └── safety_briefing.py     # Grounded NDMA/civil defense safety guidance principles
└── tests/
    ├── __init__.py
    ├── test_incidents.py      # Unit tests for validation, persistence, and verification
    ├── test_gemma_client.py   # Unit tests for Gemma 4 isolation and demo fallbacks
    └── test_simulation_3d.py  # Unit tests for 3D WebGL generation, modes, and parameters
```

---

## 🚀 Setup & Launch Guide (Windows 11 & VS Code)

### Prerequisites
- **Python 3.11.x** (Verify with `python --version`)
- **Git**
- Optional: **Ollama** with `gemma4:e2b` installed (if testing live Gemma 4 inference)

### Step 1: Open PowerShell in Project Directory
In VS Code, open a PowerShell terminal:
```powershell
cd "c:\Users\ay351\OneDrive\Desktop\DisasterShield AI\DisasterShield-AI"
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first).*

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)
Copy the example environment configuration:
```powershell
Copy-Item .env.example .env
```
Default parameters in `.env`:
- `GEMMA_ENDPOINT_URL=http://localhost:11434`
- `GEMMA_MODEL_NAME=gemma4:e2b`
- `ADMIN_VERIFY_PIN=1122`
- `DEFAULT_LOCATION_NAME=Prayagraj, Uttar Pradesh, India`
- `DEFAULT_LAT=25.4358`
- `DEFAULT_LON=81.8463`

### Step 5: Run Automated Unit Tests
```powershell
python -m pytest tests/ -v
```
*(Expected: 15/15 tests passing).*

### Step 6: Launch the DisasterShield AI Dashboard
```powershell
python -m streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

---

## 🤖 Configuring Google Gemma 4 Inference

### Option A: Local Ollama (Recommended for Local Dev)
1. Download Ollama from [ollama.com](https://ollama.com).
2. Pull the model:
   ```bash
   ollama pull gemma4:e2b
   ```
3. Start Ollama (`ollama serve`). The app will automatically connect at `http://localhost:11434`.

### Option B: Remote / Hosted Gemma 4 Endpoint
If running Gemma 4 on a cloud GPU instance or remote inference gateway:
1. Update `.env`:
   ```ini
   GEMMA_ENDPOINT_URL=https://your-remote-gemma-server.com
   GEMMA_MODEL_NAME=gemma4:e2b
   GEMMA_API_KEY=your_optional_token
   ```
2. Restart the Streamlit app or click **"Probe Gemma 4 Connection"** in the sidebar.

### Option C: Standalone Demo Mode (Zero AI Installation Required)
If you do not have a GPU or Ollama installed, **no problem**. The system detects the offline state and seamlessly activates **Transparent Demo Mode**. You can experience the entire dashboard, verification workflow, geospatial mapping, and deterministic plain-language safety briefings without installing any models.

---

## 🧪 Test Verification Summary

Automated tests verified:
- **`tests/test_incidents.py`**:
  - Valid report parameters acceptance
  - Coordinate bounding box validation (`[-90, 90]`, `[-180, 180]`)
  - Description length constraints (>= 10 chars)
  - Default status: Citizen reports **strictly** start as `UNVERIFIED`
  - JSON atomic persistence to `user_incidents.json`
  - Admin approval workflow (`VERIFIED` status, timestamp, audit notes)
  - Admin rejection workflow (`REJECTED` status)
  - Overall sector risk calculation
- **`tests/test_gemma_client.py`**:
  - Safe initialization and model restriction enforcement
  - Graceful connection probe handling on unreachable endpoints
  - Deterministic Demo Mode synthesis output labeling
  - Grounded verification status separation in summaries
  - Rule-based disaster category keyword suggestion

---

## 🪪 Hackathon AI Transparency Disclosure

In adherence to hackathon integrity and open-source disclosure policies:
- **AI Coding Assistant Used:** Google Antigravity IDE (powered by Gemini 3.8 Flash).
- **Embedded Generative AI:** Strictly Google Gemma 4 (`gemma4:e2b`) via local or compatible inference endpoint. No proprietary generative models (OpenAI, Gemini API, Claude) are invoked in application runtime logic.
- **Dataset Attribution:** Demonstration incident coordinates reference geographic landmarks in Prayagraj, UP. Fictional demo incident flags are clearly displayed on all cards and map markers.
- **Weather Telemetry:** Open-Meteo Public API (free, open data).

---

## 📜 License & Compliance

This software is licensed under the **Apache License 2.0**.
Usage of Google Gemma 4 weights and inference outputs is subject to the **Gemma Terms of Use** and the **Gemma Open Model License**.

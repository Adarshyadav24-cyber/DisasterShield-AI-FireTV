# 🛡️ DisasterShield AI
### Early Awareness. Verified Information. Safer Decisions.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Folium](https://img.shields.io/badge/Folium-0.20.0-77B800.svg)](https://python-visualization.github.io/folium/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL%203D-black.svg?logo=three.js&logoColor=white)](https://threejs.org/)
[![AI Engine](https://img.shields.io/badge/AI%20Model-Google%20Gemma%204-purple.svg)](https://ai.google.dev/gemma)
[![Tests](https://img.shields.io/badge/Tests-18%2F18%20Passed-brightgreen.svg)](tests/)

---

## 📌 Project Overview

- **Project Name:** **DisasterShield AI**
- **Tagline:** Early Awareness. Verified Information. Safer Decisions.
- **Repository:** [https://github.com/Adarshyadav24-cyber/DisasterShield-AI](https://github.com/Adarshyadav24-cyber/DisasterShield-AI)
- **Live Demo Link:** [https://ripe-eggs-pay.loca.lt](https://ripe-eggs-pay.loca.lt) *(Tunnel Password: `106.194.27.1`)*

---

## ⚠️ Mandatory Public Safety Notice

> **"DisasterShield AI is an informational prototype, not an official emergency service. Verify alerts and follow instructions from authorized local authorities. Do not rely on this prototype alone for evacuation decisions."**
>
> - **Official Emergency Helpline (India):** Dial **112** (National Emergency Helpline), **1077** (State Disaster Control Room), or **108** (Ambulance).
> - **Demo Data Notice:** All initial disaster reports and 3D simulations are explicitly watermarked as `DEMO DATA` / `DEMO SIMULATION`. No fictional hazards are represented as real ground events.

---

## 🛑 Problem Statement: What problem does it solve?

During extreme climate emergencies (flash floods, urban fires, severe storms, and seismic shocks), two compounding disasters unfold simultaneously:
1. **The Physical Disaster:** Flooding rivers, structural fires, blocked corridors, and strained medical triage.
2. **The Information Chaos Disaster:** Rumors, unverified social media panics, outdated weather reports, and contradictory evacuation instructions.

Traditional disaster portals are either static government notification boards that lag behind real-time ground events or uncurated social feeds rife with misinformation. Furthermore, traditional 2D maps fail to give emergency managers and citizens an intuitive spatial understanding of rising river elevations, storm cloud cover, and topographic inundation zones.

---

## 💡 Solution: How does DisasterShield AI help?

**DisasterShield AI** provides an open-source, cyber-command-center dashboard combining multi-city situational telemetry, immersive 3D digital twins, crowdsourced citizen reporting, and responsible AI synthesis:

1. **Anti-Disinformation Verification Pipeline:** Every incoming citizen submission strictly begins in **`UNVERIFIED`** status. An authorized emergency coordinator inspects ground reports and validates or rejects them via a PIN-protected **Administrator Verification Desk** (`PIN: 1122`), preventing fake rumors from polluting the public feed.
2. **Interactive 3D Digital Twin Simulation Studio (Three.js WebGL):** Procedural 3D cityscapes dynamically visualize:
   - **Flood Inundation:** Rising water planes submerging quays and low-lying sectors.
   - **Structural Fire:** Controlled dynamic flame particles, smoke plumes, and flickering ambient lighting.
   - **Earthquake Tremors:** Harmonic seismic wave equations oscillating urban building geometry based on Richter scale controls.
   - **Severe Storm:** 2,000 animated rain streak vectors, directional wind velocity, and ambient lightning bursts.
3. **Multi-City Geospatial Awareness:** Pre-calibrated tactical centers for key Indian riverine and urban corridors:
   - **Prayagraj, Uttar Pradesh** (Default — Ganga & Yamuna Sangam Basin)
   - **Lucknow, Uttar Pradesh** (Gomti Riverfront Corridor)
   - **Varanasi, Uttar Pradesh** (Ganges Ghats & Cultural Quarter)
   - **New Delhi, India** (Yamuna Floodplain Corridor)
4. **Live Meteorological Telemetry:** Direct integration with the public, keyless Open-Meteo API for real-time temperature, wind speed, precipitation, and conditions.
5. **Strictly Grounded AI Safety Synthesis:** Powered exclusively by **Google Gemma 4**, delivering factual situation summaries and accessible NDMA-aligned safety protocols with zero hallucinations.

---

## 🛠️ Technologies Used

| Category | Technologies | Purpose |
| :--- | :--- | :--- |
| **Language & Backend** | **Python 3.11** | Core application logic, validation engine, and state management |
| **App Framework** | **Streamlit (v1.64.0)** | Reactive dashboard with custom obsidian dark-glassmorphism command center styling |
| **3D Graphics & Engine** | **Three.js & WebGL** | Client-side 3D digital twin rendering (flood, fire, quake, storm physics) |
| **Geospatial & Mapping** | **Folium (v0.20.0)** & **Streamlit-Folium** | Interactive multi-city maps, marker clustering, popups, and custom on-map legends |
| **Basemap Provider** | **OpenStreetMap** | Open-source, dependency-free cartographic map tiles |
| **AI / LLM Engine** | **Google Gemma 4 (`gemma4:e2b`)** | Grounded situation summaries and citizen advisory synthesis |
| **Local Inference Host** | **Ollama** | Local, privacy-preserving, zero-latency Gemma 4 model inference |
| **Data & Telemetry** | **Pandas (v3.0.3)** & **Requests** | Incident data manipulation and Open-Meteo weather API integration |
| **Quality Assurance** | **Pytest (v9.1.1)** | 18 automated unit tests covering validation, model restrictions, and 3D scenes |
| **Version Control** | **Git & GitHub** | Distributed version control and collaboration |

---

## 🧠 AI Model Specification

- **Exact Model Name / Identifier:** **Google Gemma 4** (specifically tested with `gemma4:e2b` via Ollama; compatible with Gemma 4 open weights).
- **Official Model Information:** [Google Gemma Open Models](https://ai.google.dev/gemma)
- **Model Terms of Use & License:**
  - [Google Gemma Terms of Use](https://ai.google.dev/gemma/terms)
  - [Gemma Open Model License Agreement](https://ai.google.dev/gemma/license)
- **Strict Architectural Model Restriction:**
  - DisasterShield AI is architecturally restricted **exclusively** to Google Gemma 4.
  - The codebase contains **zero** dependencies on OpenAI, Anthropic, or proprietary Gemini generative API keys.
  - All model calls originate through `modules/gemma_client.py` with strict safety guards.

---

## 🤖 AI Integration: How & Where AI is Used

DisasterShield AI integrates Google Gemma 4 into four specialized modules:

1. **Grounded Situation Briefings (`modules/gemma_client.py`):**
   - Summarizes verified emergency reports, weather alerts, and sector risk.
   - **Anti-Hallucination Guardrails:** Prompt engineering strictly constrains Gemma 4 to facts explicitly present in the active incident ledger. It is barred from fabricating casualties, safe evacuation corridors, or binding official directives.
2. **Heuristic & AI Incident Classification (`modules/incident_manager.py`):**
   - Analyzes raw citizen report descriptions (e.g., *"water entered ground floor"* or *"transformer explosion on main street"*) to suggest accurate disaster categories (Flood, Fire, Infrastructure, Medical).
3. **Safety Protocol Synthesis (`modules/safety_briefing.py`):**
   - Ingests standard NDMA (National Disaster Management Authority) guidelines and generates plain-language, jargon-free step-by-step safety actions for affected citizens.
4. **Transparent Safe Demo Mode Fallback:**
   - If no local or remote Gemma 4 inference server is detected, the application automatically switches to **Safe Demo Mode**.
   - Demo mode uses transparent, deterministic rule-based templates that are explicitly labeled as rule-based and never masquerade as AI-generated text.

---

## 💻 Installation and Usage

### Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** Version 3.11.x installed (`python --version`)
- **Git:** Installed for repository cloning

### 1. Clone the Repository
```powershell
git clone https://github.com/Adarshyadav24-cyber/DisasterShield-AI.git
cd DisasterShield-AI
```

### 2. Create and Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Verified Dependencies
```powershell
pip install -r requirements.txt
```

### 4. (Optional) Configure Google Gemma 4 via Ollama
To run live Gemma 4 inference locally:
```bash
# Install Ollama from https://ollama.com, then pull Gemma 4:
ollama pull gemma4:e2b
ollama serve
```
*(If you do not run Ollama, DisasterShield AI automatically runs in full functionality using transparent Safe Demo Mode).*

### 5. Run the Automated Test Suite
```powershell
python -m pytest tests/ -v
```
*(All 18 automated unit tests will execute and pass).*

### 6. Launch the Application
```powershell
python -m streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## 🎮 How to Test & Evaluate the Application

1. **Location Selector:** Use the top command header or sidebar dropdown to toggle between **Prayagraj**, **Lucknow**, **Varanasi**, and **New Delhi**. The 2D Folium map, 3D digital twin, and weather telemetry update instantaneously.
2. **Interactive 3D Digital Twin (Tab 1):**
   - Click and drag to orbit, scroll to zoom, right-click to pan.
   - Switch simulation scenarios: **Flood**, **Fire**, **Earthquake**, or **Storm**.
   - Adjust the **Water Elevation (meters)** or **Earthquake Amplitude** sliders to observe real-time physics deformation.
3. **Tactical 2D Geospatial Map (Tab 2):**
   - Inspect color-coded severity pins, emergency shelters, and relief depots.
   - Filter by disaster category, severity, or verification status.
4. **Citizen Incident Reporting (Tab 3):**
   - Submit a new report (e.g., *"Waterlogging near civil hospital"*).
   - Use the quick landmark coordinate picker or enter manual GPS coordinates (with auto-detection for accidental lat/lon swap).
   - Notice the report immediately appears marked as **`UNVERIFIED`**.
5. **Administrator Verification Desk (Tab 4):**
   - Enter Administrator PIN: **`1122`**.
   - Review unverified citizen reports, enter audit notes, and mark as **`VERIFIED`** or **`REJECTED`**.
6. **AI Safety Protocol & Situation Briefing (Tab 5):**
   - Generate grounded situational summaries and safety checklists powered by Google Gemma 4 (or Safe Demo Mode).

---

## 🌐 Live Demo & Media

- **Live Web Application URL:** [https://ripe-eggs-pay.loca.lt](https://ripe-eggs-pay.loca.lt) *(Tunnel Password: `106.194.27.1`)*
- **Local Application URL:** `http://localhost:8501/`
- **GitHub Repository:** [https://github.com/Adarshyadav24-cyber/DisasterShield-AI](https://github.com/Adarshyadav24-cyber/DisasterShield-AI)

---

## 📜 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for full details.

```
Copyright 2026 Adarsh Yadav / DisasterShield AI Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

*Google Gemma is a trademark of Google LLC. Use of Gemma open models is subject to the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).*

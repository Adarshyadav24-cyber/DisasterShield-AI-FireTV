/**
 * DisasterShield AI - Fire TV Application Controller
 * Manages all TV screens, household checklist persistence, AI assistant interaction,
 * meteorological telemetry, and TV-safe Leaflet mapping.
 */

(function () {
  'use strict';

  // Default demonstration configuration matching config.py
  const DEMO_CITIES = {
    "Prayagraj, Uttar Pradesh": {
      city: "Prayagraj",
      state: "Uttar Pradesh",
      lat: 25.4358,
      lon: 81.8463,
      river: "Ganga & Yamuna Confluence (Sangam)",
      description: "Confluence basin prone to seasonal monsoon river inundation."
    },
    "Lucknow, Uttar Pradesh": {
      city: "Lucknow",
      state: "Uttar Pradesh",
      lat: 26.8467,
      lon: 80.9462,
      river: "Gomti River Basin",
      description: "State capital sector with Gomti riverfront drainage corridors."
    },
    "Varanasi, Uttar Pradesh": {
      city: "Varanasi",
      state: "Uttar Pradesh",
      lat: 25.3176,
      lon: 82.9739,
      river: "Ganga Riverfront (Ghats)",
      description: "Ancient dense riverfront settlement with terraced ghat flood surveillance."
    },
    "New Delhi, India": {
      city: "New Delhi",
      state: "National Capital Territory",
      lat: 28.6139,
      lon: 77.2090,
      river: "Yamuna River Floodplain",
      description: "National capital territory with Yamuna floodplain corridors."
    }
  };

  // Standard household emergency checklist items (NDMA / Red Cross aligned)
  const DEFAULT_CHECKLIST_ITEMS = [
    { id: 'water', category: 'Water & Food', title: 'Drinking Water (1 gal/person/day for 3 days)', desc: 'Store sealed containers away from heat and direct sunlight.' },
    { id: 'food', category: 'Water & Food', title: 'Non-Perishable Food Supply (3-Day Minimum)', desc: 'Canned ready-to-eat meats, fruits, vegetables, and manual can opener.' },
    { id: 'firstaid', category: 'Medical', title: 'Comprehensive First Aid Medical Kit', desc: 'Bandages, antiseptic solution, burn ointment, prescription medications.' },
    { id: 'flashlight', category: 'Power & Tools', title: 'High-Lumen Flashlight & Spare Batteries', desc: 'Avoid using candles due to gas leak explosion risks.' },
    { id: 'radio', category: 'Communications', title: 'Battery or Hand-Crank Emergency Radio', desc: 'For monitoring civil defense broadcasts and weather alerts.' },
    { id: 'powerbank', category: 'Power & Tools', title: 'Fully Charged Mobile Power Bank & Cables', desc: 'Preserve battery by enabling power-saving mode on phones.' },
    { id: 'documents', category: 'Important Records', title: 'Waterproof Bag with Identity & Insurance Papers', desc: 'Aadhaar, passports, property deeds, cash, and emergency contacts list.' },
    { id: 'plan', category: 'Communications', title: 'Family Communication & Meeting Point Plan', desc: 'Designate out-of-neighborhood assembly point and contact.' },
    { id: 'whistle', category: 'Safety & Tools', title: 'Signal Whistle & N95 Dust Masks', desc: 'For signaling search teams through collapsed rubble or thick dust.' },
    { id: 'sanitation', category: 'Sanitation', title: 'Sanitation Wipes, Chlorine Bleach & Trash Bags', desc: 'For personal hygiene when municipal water mains are shut down.' }
  ];

  // Verified NDMA Safety Guidance
  const HAZARD_GUIDANCE = {
    flood: {
      title: "🌊 Monsoon Flooding & Inundation Safety",
      dos: [
        "Disconnect domestic gas lines and shut off main circuit breaker switches if water enters house.",
        "Move to higher floors immediately. Keep emergency supplies and phone within reach.",
        "Boil all drinking water for at least 3 minutes before consuming.",
        "Tune in to emergency battery radio for rescue signals from District Disaster Control Room."
      ],
      donts: [
        "Do NOT walk, swim, or drive through moving water. 6 inches of moving water can knock you down.",
        "Do NOT touch submerged power cables, transformers, or appliances standing in water.",
        "Do NOT drive around police road closed barriers or barricades."
      ]
    },
    fire: {
      title: "🔥 Structural & Residential Fire Protocol",
      dos: [
        "Evacuate immediately upon detecting smoke or flames. Do not pause to collect belongings.",
        "Crawl low under smoke where air is cooler and cleaner.",
        "Feel door handles with the back of hand; if hot, keep closed and use secondary escape route.",
        "If clothing catches fire: STOP, DROP, and ROLL immediately."
      ],
      donts: [
        "Do NOT use elevators during a fire evacuation under any circumstances.",
        "Do NOT re-enter a burning structure for pets or valuables once outside.",
        "Do NOT open doors rapidly, which feeds fresh oxygen and triggers explosive backdrafts."
      ]
    },
    earthquake: {
      title: "🌋 Earthquake & Structural Tremor Protocol",
      dos: [
        "DROP to your hands and knees immediately.",
        "COVER your head and neck under a sturdy table or desk.",
        "HOLD ON to your shelter until shaking completely stops.",
        "Expect aftershocks. Check gas pipes and turn off main shutoff valve if odor is detected."
      ],
      donts: [
        "Do NOT run outside or dash for stairs while ground is actively shaking.",
        "Do NOT use matches, lighters, or open flames post-quake due to potential gas leaks.",
        "Do NOT enter visibly cracked masonry buildings until inspected by structural engineers."
      ]
    },
    storm: {
      title: "⛈️ Gale-Force Storm & Cyclone Protocol",
      dos: [
        "Secure loose rooftop objects, tin sheets, flowerpots, and water tank lids.",
        "Stay indoors away from exterior windows, glass skylights, and metal doors.",
        "Unplug sensitive electronic appliances to avoid power surge damage from lightning strikes.",
        "Keep flashlights and battery power banks fully charged in an easily accessible pouch."
      ],
      donts: [
        "Do NOT venture outside during the calm 'eye of the storm'; extreme winds resume abruptly.",
        "Do NOT park vehicles or seek shelter beneath large trees or high-voltage electric pylons.",
        "Do NOT walk near downed power lines; treat all dangling wires as live and lethal."
      ]
    },
    landslide: {
      title: "⛰️ Landslide & Slope Debris Protocol",
      dos: [
        "Listen for warning sounds: rumbling earth, cracking timber, or sudden muddy water surge.",
        "Evacuate quickly perpendicular to the path of the slide, never down the slope.",
        "Move to stable ground away from steep unconsolidated banks and drainage gullies."
      ],
      donts: [
        "Do NOT cross roads covered with fresh slurry, mud, or rockfall.",
        "Do NOT sleep in lower ground-floor rooms adjacent to steep hillside slopes during torrential rains.",
        "Do NOT enter stream channels or ravines after a slide due to high danger of flash floods."
      ]
    },
    general: {
      title: "🛡️ General Public Emergency Readiness",
      dos: [
        "Keep calm and verify notices with official authorities before sharing on social groups.",
        "Call 112 for national emergency response or 1077 for state disaster control.",
        "Assist elderly neighbors, young children, and persons with disabilities if safe to do so."
      ],
      donts: [
        "Do NOT dial emergency lines for non-urgent questions or general weather inquiries.",
        "Do NOT block emergency vehicle access corridors or convoy lanes.",
        "Do NOT circulate unverified rumors or panic-inducing audio clips."
      ]
    }
  };

  class TVApplication {
    constructor() {
      this.currentScreen = 'home';
      this.activeCityName = 'Prayagraj, Uttar Pradesh';
      this.checklistState = {};
      this.incidents = [];
      this.resources = [];
      this.metrics = {
        total: 12,
        verified: 7,
        unverified: 5,
        critical: 3,
        threat: 'MODERATE',
        threatColor: '#f59e0b'
      };
      this.weather = {
        temp: 28,
        condition: 'Partly Cloudy ⛅',
        wind: 14,
        precip: 0,
        isSimulated: false,
        source: 'Open-Meteo API'
      };
      this.aiConnected = false;
      this.aiStatusText = 'Probing...';
      this.map = null;
      this.mapMarkers = [];
    }

    init() {
      this.loadChecklistState();
      this.setupClock();
      this.bindUI();
      this.fetchBackendData();
      this.renderChecklist();
      this.renderGuidance('flood');
      this.updateMetricsUI();
      this.updateWeatherUI();
    }

    setupClock() {
      const clockEl = document.getElementById('tv-clock');
      const update = () => {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        if (clockEl) clockEl.textContent = timeStr;
      };
      update();
      setInterval(update, 1000);
    }

    bindUI() {
      // Navigation tab buttons
      const navButtons = document.querySelectorAll('.nav-tab-btn');
      navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          const targetScreen = btn.getAttribute('data-screen');
          if (targetScreen) this.navigateTo(targetScreen);
        });
      });

      // Quick action cards on Home screen
      document.querySelectorAll('.action-tile-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const targetScreen = btn.getAttribute('data-target');
          if (targetScreen) this.navigateTo(targetScreen);
        });
      });

      // Guidance category buttons
      document.querySelectorAll('.guidance-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          document.querySelectorAll('.guidance-tab-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const cat = btn.getAttribute('data-cat');
          this.renderGuidance(cat);
        });
      });

      // AI quick prompt cards
      document.querySelectorAll('.prompt-chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const prompt = btn.getAttribute('data-prompt');
          this.executeAIQuery(prompt);
        });
      });

      // City selection buttons in Settings
      document.querySelectorAll('.city-option-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const cityName = btn.getAttribute('data-city');
          this.switchCity(cityName);
        });
      });

      // Audio toggle button
      const audioBtn = document.getElementById('btn-toggle-audio');
      if (audioBtn) {
        audioBtn.addEventListener('click', () => {
          window.TVNav.soundEnabled = !window.TVNav.soundEnabled;
          audioBtn.textContent = window.TVNav.soundEnabled ? '🔊 Sound: ON' : '🔇 Sound: OFF';
          this.showToast(window.TVNav.soundEnabled ? 'Audio feedback enabled' : 'Audio feedback muted', 'info');
        });
      }

      // Gemma Probe button in Settings
      const probeBtn = document.getElementById('btn-probe-gemma');
      if (probeBtn) {
        probeBtn.addEventListener('click', () => {
          this.probeGemmaAPI();
        });
      }

      // Reset Checklist button
      const resetChecklistBtn = document.getElementById('btn-reset-checklist');
      if (resetChecklistBtn) {
        resetChecklistBtn.addEventListener('click', () => {
          this.resetChecklist();
        });
      }
    }

    navigateTo(screenId) {
      if (this.currentScreen === screenId) return;

      // Update Nav Buttons
      document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        if (btn.getAttribute('data-screen') === screenId) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      // Update Screen Containers
      document.querySelectorAll('.screen').forEach(scr => {
        if (scr.id === `screen-${screenId}`) {
          scr.classList.add('active');
        } else {
          scr.classList.remove('active');
        }
      });

      this.currentScreen = screenId;

      // Special screen handlers
      if (screenId === 'map') {
        setTimeout(() => this.initOrUpdateMap(), 100);
      } else if (screenId === 'simulation') {
        setTimeout(() => this.initSimulationFrame(), 100);
        setTimeout(() => this.initSimulationFrame(), 350);
      }

      // Focus first element on the newly active screen
      setTimeout(() => {
        window.TVNav.focusFirstAvailable();
      }, 80);
    }

    showToast(message, type = 'info') {
      let toast = document.getElementById('tv-app-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'tv-app-toast';
        toast.className = 'tv-toast';
        document.body.appendChild(toast);
      }
      toast.textContent = message;
      toast.style.display = 'block';
      setTimeout(() => {
        toast.style.display = 'none';
      }, 2800);
    }

    loadChecklistState() {
      try {
        const stored = localStorage.getItem('disastershield_tv_checklist_v1');
        if (stored) {
          this.checklistState = JSON.parse(stored);
        } else {
          // Initialize with some sensible defaults checked
          this.checklistState = { water: true, flashlight: true };
          this.saveChecklistState();
        }
      } catch (e) {
        this.checklistState = {};
      }
    }

    saveChecklistState() {
      try {
        localStorage.setItem('disastershield_tv_checklist_v1', JSON.stringify(this.checklistState));
      } catch (e) {}
    }

    resetChecklist() {
      this.checklistState = {};
      this.saveChecklistState();
      this.renderChecklist();
      this.showToast('Checklist reset', 'info');
    }

    toggleChecklistItem(id) {
      this.checklistState[id] = !this.checklistState[id];
      this.saveChecklistState();
      this.renderChecklist();
      window.TVNav.playSelectSound();
    }

    renderChecklist() {
      const container = document.getElementById('checklist-items-list');
      if (!container) return;

      container.innerHTML = '';
      let completedCount = 0;

      DEFAULT_CHECKLIST_ITEMS.forEach(item => {
        const isCompleted = !!this.checklistState[item.id];
        if (isCompleted) completedCount++;

        const card = document.createElement('button');
        card.className = `checklist-item-card tv-card ${isCompleted ? 'completed' : ''}`;
        card.setAttribute('tabindex', '0');
        card.innerHTML = `
          <div style="text-align: left; padding-right: 14px;">
            <div style="font-size: 11px; text-transform: uppercase; color: var(--primary); font-weight: 700; margin-bottom: 2px;">${item.category}</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 15px; font-weight: 700; color: #fff;">${item.title}</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">${item.desc}</div>
          </div>
          <div class="checklist-check-circle">✓</div>
        `;

        card.addEventListener('click', () => {
          this.toggleChecklistItem(item.id);
        });

        container.appendChild(card);
      });

      // Update progress
      const total = DEFAULT_CHECKLIST_ITEMS.length;
      const pct = Math.round((completedCount / total) * 100);
      const fillEl = document.getElementById('checklist-progress-fill');
      const textEl = document.getElementById('checklist-progress-text');
      if (fillEl) fillEl.style.width = `${pct}%`;
      if (textEl) textEl.textContent = `${completedCount} of ${total} items completed (${pct}%)`;

      // Update Home dashboard readiness preview
      const homeReadinessEl = document.getElementById('home-readiness-stat');
      if (homeReadinessEl) homeReadinessEl.textContent = `${pct}%`;
    }

    renderGuidance(category) {
      const data = HAZARD_GUIDANCE[category] || HAZARD_GUIDANCE.general;
      const titleEl = document.getElementById('guidance-title');
      const dosEl = document.getElementById('guidance-dos-list');
      const dontsEl = document.getElementById('guidance-donts-list');

      if (titleEl) titleEl.textContent = data.title;

      if (dosEl) {
        dosEl.innerHTML = data.dos.map(item => `
          <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
            <span style="color: #10b981; font-weight: 800; font-size: 16px;">✓</span>
            <span style="font-size: 14px; color: #e2e8f0;">${item}</span>
          </div>
        `).join('');
      }

      if (dontsEl) {
        dontsEl.innerHTML = data.donts.map(item => `
          <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
            <span style="color: #ef4444; font-weight: 800; font-size: 16px;">✗</span>
            <span style="font-size: 14px; color: #fecaca;">${item}</span>
          </div>
        `).join('');
      }
    }

    updateMetricsUI() {
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setVal('metric-total', this.metrics.total);
      setVal('metric-verified', this.metrics.verified);
      setVal('metric-unverified', this.metrics.unverified);
      setVal('metric-threat', this.metrics.threat);

      const threatEl = document.getElementById('metric-threat');
      if (threatEl) {
        threatEl.style.color = this.metrics.threatColor;
      }
    }

    updateWeatherUI() {
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setVal('weather-cond', this.weather.condition);
      setVal('weather-temp', `${this.weather.temp}°C`);
      setVal('weather-wind', `${this.weather.wind} km/h`);
      setVal('weather-precip', `${this.weather.precip} mm`);
      setVal('weather-source', this.weather.source);

      const badgeEl = document.getElementById('weather-badge');
      if (badgeEl) {
        badgeEl.textContent = this.weather.isSimulated ? 'DEMO SIMULATION' : 'LIVE TELEMETRY';
        badgeEl.style.color = this.weather.isSimulated ? '#fbbf24' : '#34d399';
      }
    }

    switchCity(cityName) {
      if (!DEMO_CITIES[cityName]) return;
      this.activeCityName = cityName;

      // Update City badges across UI
      document.querySelectorAll('.active-sector-label').forEach(el => {
        el.textContent = cityName;
      });

      // Update button active state
      document.querySelectorAll('.city-option-btn').forEach(btn => {
        if (btn.getAttribute('data-city') === cityName) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      this.showToast(`Switched sector to ${cityName}`, 'info');

      // Notify backend if available
      fetch('/api/sector', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: cityName })
      }).catch(() => {});

      // Refresh data
      this.fetchBackendData();
    }

    async fetchBackendData() {
      try {
        const res = await fetch(`/api/status?city=${encodeURIComponent(this.activeCityName)}`);
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            this.metrics = data.metrics;
            this.updateMetricsUI();
          }
          if (data.weather) {
            this.weather = data.weather;
            this.updateWeatherUI();
          }
          if (data.ai) {
            this.aiConnected = data.ai.is_connected;
            this.aiStatusText = data.ai.status_message;
            this.updateAIStatusUI();
          }
          if (data.incidents) {
            this.incidents = data.incidents;
            this.renderIncidentsFeed();
          }
          return;
        }
      } catch (e) {
        // Backend not reachable; use fallback demo values gracefully
      }

      // Offline / standalone fallback values
      this.aiConnected = false;
      this.aiStatusText = 'Offline / Transparent Safe Demo Mode';
      this.updateAIStatusUI();
      this.loadDemoFallbackData();
    }

    loadDemoFallbackData() {
      // Safe fallback data
      this.incidents = [
        { id: "INC-001", title: "Rising water level at Sangam Ghat", category: "flood", severity: "High", verification_status: "VERIFIED", location_name: "Sangam Ghat, Prayagraj", description: "Water level rose by 1.8m following monsoon discharges." },
        { id: "INC-002", title: "Low-voltage transformer sparking", category: "fire", severity: "Moderate", verification_status: "VERIFIED", location_name: "Civil Lines Ward 4, Prayagraj", description: "Civic team isolated transformer. No structural fire." },
        { id: "INC-003", title: "Citizen report: Waterlogging in basement", category: "flood", severity: "Low", verification_status: "UNVERIFIED", location_name: "Daraganj Sector B, Prayagraj", description: "Resident reports 4 inches water in residential ground corridor." }
      ];
      this.renderIncidentsFeed();
    }

    renderIncidentsFeed() {
      const container = document.getElementById('home-incidents-feed');
      if (!container) return;

      container.innerHTML = this.incidents.slice(0, 4).map(inc => {
        const isVer = inc.verification_status === 'VERIFIED';
        const badgeColor = isVer ? '#10b981' : '#f59e0b';
        const badgeText = isVer ? 'VERIFIED' : 'UNVERIFIED';

        return `
          <div class="tv-card" style="padding: 12px 16px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-size: 11px; font-weight: 700; color: ${badgeColor}; background: rgba(255,255,255,0.06); padding: 2px 8px; border-radius: 4px;">
                ${badgeText}
              </span>
              <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">${inc.id}</span>
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700; color: #f8fafc;">${inc.title}</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">${inc.location_name}</div>
          </div>
        `;
      }).join('');
    }

    updateAIStatusUI() {
      const statusPill = document.getElementById('ai-status-pill');
      const statusDesc = document.getElementById('ai-status-desc');
      if (statusPill) {
        if (this.aiConnected) {
          statusPill.textContent = 'CONNECTED: GOOGLE GEMMA 4';
          statusPill.style.background = 'rgba(16, 185, 129, 0.2)';
          statusPill.style.color = '#34d399';
          statusPill.style.borderColor = '#10b981';
        } else {
          statusPill.textContent = 'TRANSPARENT DEMO MODE (RULE-BASED)';
          statusPill.style.background = 'rgba(245, 158, 11, 0.2)';
          statusPill.style.color = '#fbbf24';
          statusPill.style.borderColor = '#f59e0b';
        }
      }
      if (statusDesc) {
        statusDesc.textContent = this.aiStatusText;
      }
    }

    async probeGemmaAPI() {
      this.showToast('Probing Google Gemma 4 endpoint...', 'info');
      try {
        const res = await fetch('/api/ai/probe');
        if (res.ok) {
          const data = await res.json();
          this.aiConnected = data.is_connected;
          this.aiStatusText = data.message;
          this.updateAIStatusUI();
          this.showToast(this.aiStatusText, 'info');
          return;
        }
      } catch (e) {}

      this.aiConnected = false;
      this.aiStatusText = 'No active Gemma 4 inference server found at http://localhost:11434. Running in transparent Demo Mode.';
      this.updateAIStatusUI();
      this.showToast('Demo Mode active (Gemma 4 offline)', 'info');
    }

    async executeAIQuery(userPrompt) {
      const outputEl = document.getElementById('ai-output-box');
      const badgeEl = document.getElementById('ai-query-badge');
      if (outputEl) {
        outputEl.textContent = 'Analyzing grounded incident ledger and synthesizing safety briefing...\n';
      }

      this.showToast('Synthesizing safety advisory...', 'info');

      try {
        const res = await fetch('/api/ai/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: userPrompt,
            city: this.activeCityName
          })
        });

        if (res.ok) {
          const data = await res.json();
          if (outputEl) outputEl.textContent = data.content;
          if (badgeEl) {
            badgeEl.textContent = data.is_ai_generated ? `Generated by ${data.model_identifier}` : `Deterministic Template (${data.model_identifier})`;
            badgeEl.style.color = data.is_ai_generated ? '#38bdf8' : '#fbbf24';
          }
          return;
        }
      } catch (e) {}

      // Fallback deterministic synthesis when API is offline
      setTimeout(() => {
        let fallbackText = '';
        if (userPrompt.toLowerCase().includes('flood')) {
          fallbackText = "### 🌊 Flood Safety Synthesis (Safe Demo Template)\n" +
            "> **Transparency Notice:** Generated using deterministic safety template logic (Gemma 4 endpoint inactive).\n\n" +
            "1. **Immediate Action:** Disconnect electrical mains before water reaches outlets. Move to upper floors with your 3-day emergency supply.\n" +
            "2. **Water Safety:** NEVER walk or drive through moving water. 6 inches can knock down an adult.\n" +
            "3. **Drinking Water:** Boil municipal tap water for 3 minutes before drinking.\n" +
            "4. **Emergency Helpline:** Dial **112** or State Disaster Room **1077** for verified rescue coordination.\n\n" +
            "*Advisory Disclaimer: Non-official information prototype. Always heed sirens from District Administration.*";
        } else if (userPrompt.toLowerCase().includes('earthquake')) {
          fallbackText = "### 🌋 Earthquake Tremor Protocol (Safe Demo Template)\n" +
            "> **Transparency Notice:** Generated using deterministic safety template logic.\n\n" +
            "1. **DROP, COVER, and HOLD ON** beneath a sturdy table or against an interior wall.\n" +
            "2. **Stay Indoors** until shaking completely halts. Do not run for doorways or stairwells.\n" +
            "3. **Inspect Utilities:** Check for gas odors. Turn off main valve if damage is suspected.\n\n" +
            "*Advisory Disclaimer: Follow instructions from National Disaster Management Authority (NDMA).*";
        } else {
          fallbackText = "### 🛡️ Disaster Preparedness Synthesis (Safe Demo Template)\n" +
            "> **Transparency Notice:** Deterministic plain-language advisory.\n\n" +
            "- **Active Sector:** " + this.activeCityName + "\n" +
            "- **Current Readiness:** Complete household checklist items and monitor battery radio broadcasts.\n" +
            "- **Helpline Reference:** National Emergency 112 | Fire 101 | Ambulance 108.\n\n" +
            "*Do not spread unverified rumors. Follow official municipal bulletins.*";
        }

        if (outputEl) outputEl.textContent = fallbackText;
        if (badgeEl) {
          badgeEl.textContent = "Deterministic Template (Gemma 4 Offline)";
          badgeEl.style.color = "#fbbf24";
        }
      }, 350);
    }

    initOrUpdateMap() {
      const mapContainer = document.getElementById('firetv-map-view');
      if (!mapContainer || typeof L === 'undefined') return;

      const cityMeta = DEMO_CITIES[this.activeCityName] || DEMO_CITIES["Prayagraj, Uttar Pradesh"];

      if (!this.map) {
        this.map = L.map('firetv-map-view', {
          zoomControl: false,
          attributionControl: false
        }).setView([cityMeta.lat, cityMeta.lon], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18
        }).addTo(this.map);
      } else {
        this.map.setView([cityMeta.lat, cityMeta.lon], 13);
      }

      // Clear old markers
      this.mapMarkers.forEach(m => this.map.removeLayer(m));
      this.mapMarkers = [];

      // Add center sector marker
      const centerMarker = L.circleMarker([cityMeta.lat, cityMeta.lon], {
        radius: 10,
        fillColor: '#38bdf8',
        color: '#fff',
        weight: 2,
        fillOpacity: 0.9
      }).addTo(this.map);
      centerMarker.bindPopup(`<b>${this.activeCityName}</b><br>Command Sector Center`);
      this.mapMarkers.push(centerMarker);

      // Render incident markers
      this.incidents.forEach(inc => {
        const lat = inc.latitude || (cityMeta.lat + (Math.random() - 0.5) * 0.03);
        const lon = inc.longitude || (cityMeta.lon + (Math.random() - 0.5) * 0.03);
        const color = inc.severity === 'High' ? '#ef4444' : (inc.severity === 'Moderate' ? '#f59e0b' : '#10b981');

        const m = L.circleMarker([lat, lon], {
          radius: 8,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          fillOpacity: 0.85
        }).addTo(this.map);

        m.bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; color: #000;">
            <strong>${inc.title}</strong><br>
            <span>Severity: ${inc.severity} | Status: ${inc.verification_status}</span><br>
            <span>${inc.location_name}</span>
          </div>
        `);
        this.mapMarkers.push(m);
      });

      this.map.invalidateSize();
    }

    initSimulationFrame() {
      const frame = document.getElementById('simulation-canvas-frame');
      if (!frame) return;

      // Ensure proper relative source for static hosting (Vercel) & local server
      if (!frame.src || frame.src.endsWith('/simulation-embed')) {
        frame.src = './simulation_embed.html';
      }

      // Notify the embedded Three.js scene to recalculate dimensions now that its container is visible
      try {
        if (frame.contentWindow) {
          frame.contentWindow.postMessage({ action: 'resize' }, '*');
        }
      } catch (e) {
        console.warn('Simulation frame postMessage warning:', e);
      }
    }
  }

  // Export to window
  window.TVApp = new TVApplication();
  document.addEventListener('DOMContentLoaded', () => {
    window.TVApp.init();
  });

})();

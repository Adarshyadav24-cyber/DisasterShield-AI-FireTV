"""
DisasterShield AI - Google Gemma 4 Client Module
Provides modular inference connectivity strictly and exclusively for Google Gemma 4 (e.g., gemma4:e2b).
If no local or remote Gemma 4 inference server is active, falls back cleanly to transparent rule-based demo templates.
DO NOT use Gemini API, OpenAI, Anthropic, or any other generative model.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import requests

import config


@dataclass
class GemmaResult:
    """Represents the output from Gemma 4 or transparent demo mode fallback."""
    content: str
    is_ai_generated: bool
    model_identifier: str
    status: str  # "CONNECTED" | "DEMO_MODE" | "CONNECTION_ERROR" | "TIMEOUT"
    latency_ms: float
    disclaimer: str


class GemmaClient:
    """
    Modular client restricted exclusively to Google Gemma 4 models.
    Supports Ollama local endpoints or OpenAI/REST-compatible Gemma 4 endpoints.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        self.endpoint_url = (endpoint_url or config.GEMMA_ENDPOINT_URL).rstrip("/")
        self.model_name = model_name or config.GEMMA_MODEL_NAME
        self.timeout = timeout_seconds or config.GEMMA_TIMEOUT_SECONDS
        self.api_key = api_key or config.GEMMA_API_KEY
        self._cached_connection_status: Optional[Tuple[bool, str]] = None
        self._last_probe_time: float = 0.0

    def probe_connection(self, force_refresh: bool = False) -> Tuple[bool, str]:
        """
        Tests whether the Gemma 4 inference server is live and responsive.
        Caches result for 15 seconds unless force_refresh is True.
        """
        now = time.time()
        if not force_refresh and self._cached_connection_status and (now - self._last_probe_time < 15.0):
            return self._cached_connection_status

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # 1. Probe Ollama standard tags endpoint
        ollama_tags_url = f"{self.endpoint_url}/api/tags"
        try:
            resp = requests.get(ollama_tags_url, headers=headers, timeout=min(self.timeout, 3))
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check for gemma 4 or configured model
                matching_models = [m for m in models if "gemma" in m.lower()]
                if any(self.model_name.lower() in m.lower() for m in models):
                    self._cached_connection_status = (True, f"Connected to Gemma 4 ({self.model_name}) via Ollama")
                elif matching_models:
                    self._cached_connection_status = (
                        True,
                        f"Connected to Ollama. Configured model: {self.model_name} (Found Gemma models: {', '.join(matching_models[:2])})"
                    )
                else:
                    self._cached_connection_status = (
                        False,
                        f"Ollama running at {self.endpoint_url}, but model '{self.model_name}' not downloaded."
                    )
                self._last_probe_time = now
                return self._cached_connection_status
        except Exception:
            pass

        # 2. Probe generic OpenAI-compatible v1/models endpoint
        openai_models_url = f"{self.endpoint_url}/v1/models"
        try:
            resp = requests.get(openai_models_url, headers=headers, timeout=min(self.timeout, 3))
            if resp.status_code == 200:
                data = resp.json()
                model_ids = [m.get("id", "") for m in data.get("data", [])]
                if any("gemma" in m.lower() for m in model_ids):
                    self._cached_connection_status = (True, f"Connected to OpenAI-compatible Gemma 4 endpoint ({self.model_name})")
                    self._last_probe_time = now
                    return self._cached_connection_status
                else:
                    self._cached_connection_status = (False, f"Endpoint reachable, but no Gemma 4 model listed ({model_ids[:3]})")
                    self._last_probe_time = now
                    return self._cached_connection_status
        except Exception:
            pass

        # If neither probe succeeded
        self._cached_connection_status = (
            False,
            f"No active Gemma 4 inference server at {self.endpoint_url}. Operating in transparent DEMO MODE."
        )
        self._last_probe_time = now
        return self._cached_connection_status

    def _call_ollama_generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Sends generation request to local/remote Ollama endpoint."""
        url = f"{self.endpoint_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "").strip()
        return None

    # =========================================================================
    # High-Level Feature Implementations (Live Gemma 4 or Transparent Demo)
    # =========================================================================

    def summarize_incidents(self, incidents: List[Dict[str, Any]]) -> GemmaResult:
        """
        Synthesizes a structured incident report summary.
        Distinguishes verified from unverified reports.
        """
        start_time = time.time()
        is_connected, _ = self.probe_connection()

        if not incidents:
            return GemmaResult(
                content="No incidents have been recorded in the system. The incident feed is currently clear.",
                is_ai_generated=False,
                model_identifier="Rule-based Template Fallback (No AI)",
                status="DEMO_MODE",
                latency_ms=round((time.time() - start_time) * 1000, 2),
                disclaimer="Informational summary based on empty incident ledger.",
            )

        verified = [i for i in incidents if i.get("verification_status") == "VERIFIED"]
        unverified = [i for i in incidents if i.get("verification_status") == "UNVERIFIED"]
        investigating = [i for i in incidents if i.get("verification_status") == "INVESTIGATING"]
        critical_items = [i for i in incidents if i.get("severity") in ["High", "Critical"] and i.get("verification_status") != "REJECTED"]

        if is_connected:
            # Gemma 4 grounded prompt
            system_prompt = (
                "You are an assistant within DisasterShield AI powered strictly by Google Gemma 4. "
                "Synthesize the provided disaster incident ledger into a concise situational summary. "
                "CRITICAL RULES: "
                "1. Strictly use ONLY the facts provided. Never invent missing details, evacuations, casualties, or weather. "
                "2. Explicitly distinguish VERIFIED reports from UNVERIFIED citizen submissions. "
                "3. Emphasize that unverified citizen reports require ground validation before action. "
                "4. Do NOT issue official emergency directives. State that citizens must follow local authorities."
            )

            prompt_records = []
            for inc in incidents[:12]:
                status_tag = f"[{inc.get('verification_status')}]"
                prompt_records.append(
                    f"- {status_tag} {inc.get('title')} ({inc.get('category').upper()}, Severity: {inc.get('severity')}) at {inc.get('location_name')}. Details: {inc.get('description')}"
                )

            user_prompt = (
                f"Incident Ledger ({len(incidents)} total incidents):\n"
                + "\n".join(prompt_records)
                + "\n\nProvide a concise 3-part summary: 1. Critical & Verified Threats, 2. Unverified Citizen Reports to Monitor, 3. Cautionary Guidance."
            )

            try:
                ai_output = self._call_ollama_generate(user_prompt, system_prompt)
                if ai_output:
                    latency = round((time.time() - start_time) * 1000, 2)
                    return GemmaResult(
                        content=ai_output,
                        is_ai_generated=True,
                        model_identifier=f"Google Gemma 4 ({self.model_name})",
                        status="CONNECTED",
                        latency_ms=latency,
                        disclaimer="AI-generated synthesis powered by Gemma 4. Non-official advisory. Follow district administration.",
                    )
            except Exception as e:
                print(f"[Warning] Gemma 4 query failed: {e}. Falling back to transparent rule-based demo template.")

        # Transparent Rule-Based Demo Mode Fallback
        latency = round((time.time() - start_time) * 1000, 2)
        demo_content = (
            "### 📋 Incident Ledger Summary\n"
            "> **Transparency Label:** Generated via transparent rule-based template logic (Gemma 4 inference endpoint not active).\n\n"
            f"- **Total Incident Reports:** {len(incidents)} active entries recorded in database.\n"
            f"- **Verified Reports ({len(verified)}):** Confirmed by emergency officers or civic ward teams.\n"
            f"- **Unverified Citizen Submissions ({len(unverified)}):** Require physical reconnaissance prior to resource mobilization.\n"
            f"- **Under Investigation ({len(investigating)}):** Active field checks underway.\n"
            f"- **High-Priority Incidents ({len(critical_items)}):** Incidents assessed as High or Critical severity.\n\n"
            "**Key Active Focus Areas:**\n"
        )

        for c in critical_items[:3]:
            ver_label = "✅ Verified" if c.get("verification_status") == "VERIFIED" else "⚠️ Unverified Citizen Report"
            demo_content += f"- **[{c.get('category').upper()}] {c.get('title')}** ({c.get('location_name')}): {ver_label}. Severity: {c.get('severity')}.\n"

        demo_content += (
            "\n*Safety Reminder: DisasterShield AI does not verify emergency alerts itself. "
            "Citizens must rely on verified official alerts from district administration.*"
        )

        return GemmaResult(
            content=demo_content,
            is_ai_generated=False,
            model_identifier="Rule-based Template Fallback (No AI)",
            status="DEMO_MODE",
            latency_ms=latency,
            disclaimer="Deterministic synthesis template. Not generative AI.",
        )

    def generate_situation_briefing(
        self,
        incidents: List[Dict[str, Any]],
        weather_data: Optional[Dict[str, Any]],
        resources: List[Dict[str, Any]],
    ) -> GemmaResult:
        """
        Creates an executive situation briefing strictly from supplied incident,
        weather, and emergency resource facts.
        """
        start_time = time.time()
        is_connected, _ = self.probe_connection()

        verified_count = sum(1 for i in incidents if i.get("verification_status") == "VERIFIED")
        unverified_count = sum(1 for i in incidents if i.get("verification_status") == "UNVERIFIED")
        critical_count = sum(1 for i in incidents if i.get("severity") in ["High", "Critical"] and i.get("verification_status") != "REJECTED")

        weather_snippet = "No telemetry available."
        if weather_data and weather_data.get("status") == "SUCCESS":
            weather_snippet = (
                f"Temp: {weather_data.get('temperature_c')}°C, "
                f"Conditions: {weather_data.get('condition')}, "
                f"Wind: {weather_data.get('wind_speed_kmh')} km/h, "
                f"Precipitation: {weather_data.get('precipitation_mm')} mm"
            )

        if is_connected:
            system_prompt = (
                "You are DisasterShield AI's briefing officer powered by Google Gemma 4. "
                "Generate a formal situation briefing based strictly on the provided facts. "
                "RULES: "
                "1. State only known facts. If shelter capacity or routes are unknown, say 'unknown'. "
                "2. Clearly separate verified facts from unverified citizen submissions. "
                "3. Never claim any evacuation route or road is safe without explicit route verification. "
                "4. Explicitly state this is an informational aid, not an official governmental order."
            )

            prompt_text = (
                f"SITUATION DATA:\n"
                f"- Total Incidents: {len(incidents)} (Verified: {verified_count}, Unverified: {unverified_count}, High-Priority: {critical_count})\n"
                f"- Live Environmental Telemetry ({weather_data.get('source', 'External')}): {weather_snippet}\n"
                f"- Registered Facilities ({len(resources)}): {', '.join(r.get('name', '') for r in resources[:4])}\n"
                f"Write an executive briefing in 3 clear sections: (1) Current Threat Posture, (2) Resource Preparedness, (3) Operational Disclaimers."
            )

            try:
                ai_output = self._call_ollama_generate(prompt_text, system_prompt)
                if ai_output:
                    return GemmaResult(
                        content=ai_output,
                        is_ai_generated=True,
                        model_identifier=f"Google Gemma 4 ({self.model_name})",
                        status="CONNECTED",
                        latency_ms=round((time.time() - start_time) * 1000, 2),
                        disclaimer="Executive briefing synthesized by Gemma 4 from active database records.",
                    )
            except Exception as e:
                print(f"[Warning] Gemma 4 situation briefing failed: {e}. Falling back to demo template.")

        # Transparent Demo Template Fallback
        briefing_text = (
            "### 🛡️ Situation Briefing Report\n"
            "> **Transparency Notice:** Generated using deterministic rule-based template logic. (Gemma 4 endpoint inactive).\n\n"
            "#### 1. Current Threat Posture\n"
            f"- **Active Incident Load:** {len(incidents)} total incidents reported across the demonstration zone.\n"
            f"- **Verified Incidents:** {verified_count} confirmed by field personnel.\n"
            f"- **Unverified Submissions:** {unverified_count} pending field reconnaissance. Caution is advised.\n"
            f"- **High Priority Threats:** {critical_count} critical/high reports require immediate inter-agency attention.\n\n"
            "#### 2. Environmental Factors\n"
            f"- **Current Weather Status:** {weather_snippet} (Source: {weather_data.get('source', 'Simulated') if weather_data else 'Unavailable'}).\n\n"
            "#### 3. Emergency Resources on Standby\n"
            f"- **Identified Relief Facilities:** {len(resources)} facilities registered in municipal catalog.\n"
            "- **Route Safety Status:** *UNKNOWN*. Do not assume roads connecting to shelters are hazard-free without official traffic clearances.\n\n"
            "#### 4. Mandatory Safety Notice\n"
            "This briefing is an informational compilation. Follow orders issued by the District Magistrate, NDMA, and emergency sirens."
        )

        return GemmaResult(
            content=briefing_text,
            is_ai_generated=False,
            model_identifier="Rule-based Template Fallback (No AI)",
            status="DEMO_MODE",
            latency_ms=round((time.time() - start_time) * 1000, 2),
            disclaimer="Rule-based synthesized briefing. Not generative AI.",
        )

    def rewrite_safety_instructions(self, category: str, raw_guidance: str) -> GemmaResult:
        """
        Rewrites formal, complex official safety instructions into clear, accessible plain language.
        """
        start_time = time.time()
        is_connected, _ = self.probe_connection()

        if is_connected:
            system_prompt = (
                "You are a public safety communicator in DisasterShield AI powered by Google Gemma 4. "
                "Rewrite the provided safety guidance into crystal-clear, calm, and actionable plain language for everyday citizens. "
                "RULES: "
                "1. Keep sentences short and readable at an 8th-grade reading level. "
                "2. Preserve all factual safety constraints (e.g. avoid downed wires, do not walk through floodwaters). "
                "3. Never invent new rules, contacts, or safe zones not present in the input. "
                "4. Always include a reminder to obey local sirens and law enforcement."
            )
            prompt = f"Category: {category}\nOfficial Text:\n{raw_guidance}\n\nRewrite into plain language bullet points for immediate citizen awareness."
            try:
                ai_output = self._call_ollama_generate(prompt, system_prompt)
                if ai_output:
                    return GemmaResult(
                        content=ai_output,
                        is_ai_generated=True,
                        model_identifier=f"Google Gemma 4 ({self.model_name})",
                        status="CONNECTED",
                        latency_ms=round((time.time() - start_time) * 1000, 2),
                        disclaimer="Plain-language translation generated by Google Gemma 4.",
                    )
            except Exception as e:
                print(f"[Warning] Gemma 4 safety rewrite failed: {e}")

        # Deterministic Demo Mode Translation
        plain_points = []
        lines = [line.strip() for line in raw_guidance.split("\n") if line.strip()]
        for line in lines:
            cleaned = line.lstrip("-*•0123456789. ")
            plain_points.append(f"• **Step:** {cleaned}")

        fallback_output = (
            "### 📢 Plain-Language Safety Guide\n"
            "> **Transparency Label:** Deterministic plain-language format (Rule-based template, not AI-generated).\n\n"
            f"**Disaster Type:** {category.capitalize()}\n\n"
            "**What You Should Do Right Now:**\n"
            + "\n".join(plain_points)
            + "\n\n"
            "**Official Guidance Reminder:**\n"
            "Keep emergency battery radios active. Follow sirens and official announcements from local administration."
        )

        return GemmaResult(
            content=fallback_output,
            is_ai_generated=False,
            model_identifier="Rule-based Template Fallback (No AI)",
            status="DEMO_MODE",
            latency_ms=round((time.time() - start_time) * 1000, 2),
            disclaimer="Deterministic translation template. Not generative AI.",
        )

    def suggest_category(self, title: str, description: str) -> Tuple[str, str, bool]:
        """
        Suggests an incident category from title and description.
        Returns: (suggested_category, explanation, is_ai_generated)
        """
        text = f"{title} {description}".lower()
        is_connected, _ = self.probe_connection()

        if is_connected:
            prompt = (
                f"Classify this disaster report into exactly one of: {', '.join(config.CATEGORIES)}.\n"
                f"Title: {title}\nDescription: {description}\n"
                f"Output only the category name in lowercase, followed by a semicolon and 1 sentence explanation."
            )
            system_prompt = "You are an automated disaster classifier. Return only 'category; explanation'."
            try:
                ai_output = self._call_ollama_generate(prompt, system_prompt)
                if ai_output and ";" in ai_output:
                    parts = ai_output.split(";", 1)
                    cat_candidate = parts[0].strip().lower()
                    if cat_candidate in config.CATEGORIES:
                        return (
                            cat_candidate,
                            f"[AI-Suggested via Gemma 4]: {parts[1].strip()}",
                            True,
                        )
            except Exception:
                pass

        # Rule-based transparent keyword heuristic
        keywords = {
            "flood": ["flood", "water", "inundat", "river", "ghat", "drain", "waterlog", "submerg", "overflow"],
            "fire": ["fire", "smoke", "blaze", "burn", "flame", "short circuit", "spark", "explosion"],
            "storm": ["storm", "wind", "cyclone", "tree", "roof", "gust", "thunder", "rain", "hail"],
            "earthquake": ["earthquake", "quake", "tremor", "shake", "crack", "collapse", "structural damage"],
            "landslide": ["landslide", "mudslide", "slope", "rockfall", "debris", "hillside"],
        }

        for cat, kws in keywords.items():
            if any(kw in text for kw in kws):
                return (
                    cat,
                    f"[Rule-based Heuristic Suggestion]: Matched disaster keywords relating to '{cat}'. Please verify before submitting.",
                    False,
                )

        return (
            "other",
            "[Rule-based Heuristic Suggestion]: General incident parameters. Selected default 'other' category.",
            False,
        )

    def summarize_resources(self, resources: List[Dict[str, Any]]) -> GemmaResult:
        """Summarizes registered emergency resources."""
        start_time = time.time()
        is_connected, _ = self.probe_connection()

        if not resources:
            return GemmaResult(
                content="No emergency facilities registered in the current sector catalog.",
                is_ai_generated=False,
                model_identifier="Rule-based Template Fallback (No AI)",
                status="DEMO_MODE",
                latency_ms=round((time.time() - start_time) * 1000, 2),
                disclaimer="Empty catalog.",
            )

        if is_connected:
            prompt = (
                f"Available Resources ({len(resources)} total):\n"
                + "\n".join(f"- {r.get('name')} ({r.get('type')}) - Status: {r.get('status')}, Capacity: {r.get('capacity')}" for r in resources)
                + "\n\nSummarize these facilities concisely by role and operational readiness. State that route safety to these facilities is unknown."
            )
            system_prompt = (
                "You are DisasterShield AI using Google Gemma 4. "
                "Summarize facilities truthfully. Never invent phone numbers or claim routes are safe."
            )
            try:
                ai_output = self._call_ollama_generate(prompt, system_prompt)
                if ai_output:
                    return GemmaResult(
                        content=ai_output,
                        is_ai_generated=True,
                        model_identifier=f"Google Gemma 4 ({self.model_name})",
                        status="CONNECTED",
                        latency_ms=round((time.time() - start_time) * 1000, 2),
                        disclaimer="Resource summary generated by Gemma 4 from active database records.",
                    )
            except Exception as e:
                print(f"[Warning] Gemma 4 resource query failed: {e}")

        # Deterministic Demo Mode
        output = (
            "### 🏥 Emergency Resources Inventory Summary\n"
            "> **Transparency Label:** Generated via transparent rule-based template logic (Gemma 4 endpoint inactive).\n\n"
            f"**Total Registered Facilities:** {len(resources)}\n\n"
        )
        for r in resources:
            output += (
                f"- **{r.get('name')}** (`{r.get('type')}`)\n"
                f"  - **Status:** {r.get('status')} | **Capacity:** {r.get('capacity')}\n"
                f"  - **Contact Guidance:** {r.get('official_helpline_info')}\n"
            )

        output += "\n*Note: Route safety to all shelters is UNCONFIRMED. Follow police and district traffic orders.*"

        return GemmaResult(
            content=output,
            is_ai_generated=False,
            model_identifier="Rule-based Template Fallback (No AI)",
            status="DEMO_MODE",
            latency_ms=round((time.time() - start_time) * 1000, 2),
            disclaimer="Deterministic catalog summary.",
        )

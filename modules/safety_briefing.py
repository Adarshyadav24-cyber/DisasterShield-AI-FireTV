"""
DisasterShield AI - Safety Protocols & Grounded Emergency Guidance
Provides verified standard disaster management principles (NDMA & Red Cross protocols).
Explicitly disclaims all guidance as informational, non-directive aid.
"""
from typing import Dict, List, Any

# Curated reference safety protocols from standard civil defense guidelines
STANDARD_SAFETY_GUIDANCE: Dict[str, Dict[str, Any]] = {
    "flood": {
        "title": "Monsoon Flooding & Inundation Safety Protocols",
        "official_guidance": (
            "1. Turn off main circuit breaker switches and disconnect domestic gas lines if water enters building.\n"
            "2. Never walk, swim, or drive through moving water. Six inches of rapid water can knock a person down.\n"
            "3. Move to designated high ground or an upper floor. Avoid basements and low-lying ground floor areas.\n"
            "4. Do not touch downed electrical lines or electrical appliances standing in water.\n"
            "5. Boil or chemically purify drinking water before consumption to prevent waterborne contamination.\n"
            "6. Await official rescue boats or signals from the district magistrate control center."
        ),
        "critical_donts": [
            "Do NOT drive past flood warning barriers.",
            "Do NOT drink unboiled tap water in flooded zones.",
            "Do NOT touch submerged power cables or transformers.",
        ],
    },
    "fire": {
        "title": "Commercial & Residential Fire Safety Protocols",
        "official_guidance": (
            "1. Evacuate immediately upon detecting fire or dense smoke. Do not pause to gather personal belongings.\n"
            "2. Stay low to the ground to breathe cooler, clearer air beneath rising toxic smoke.\n"
            "3. Feel door handles with the back of your hand before opening. If hot, do not open.\n"
            "4. Use stairwells strictly. Never use elevators during an active structural fire.\n"
            "5. If clothing catches fire: Stop, Drop, and Roll until flames are extinguished.\n"
            "6. Assemble at the designated open ground and await fire service headcount."
        ),
        "critical_donts": [
            "Do NOT use elevators during a fire evacuation.",
            "Do NOT re-enter a burning building for pets or valuables.",
            "Do NOT open hot doors or windows causing sudden backdrafts.",
        ],
    },
    "earthquake": {
        "title": "Earthquake & Structural Tremor Safety Protocols",
        "official_guidance": (
            "1. Drop, Cover, and Hold On beneath a sturdy desk, table, or against an interior wall.\n"
            "2. Stay away from glass windows, exterior walls, mirrors, and unanchored tall furniture.\n"
            "3. If indoors, remain inside until shaking stops. Do not dash for building exits while shaking occurs.\n"
            "4. If outdoors, move to an open area clear of buildings, power lines, overpasses, and trees.\n"
            "5. Expect aftershocks. Inspect gas and electrical connections before turning on switches."
        ),
        "critical_donts": [
            "Do NOT use matches, lighters, or open flames post-quake until gas leaks are ruled out.",
            "Do NOT stand in doorways; modern doorways are not reinforced more than walls.",
            "Do NOT enter visibly cracked or damaged masonry structures.",
        ],
    },
    "storm": {
        "title": "Severe Cyclone & Gale-Force Storm Safety Protocols",
        "official_guidance": (
            "1. Secure loose outdoor objects including tin roofing, water tanks, banners, and flowerpots.\n"
            "2. Stay indoors away from windows, skylights, and glass doors during maximum wind velocity.\n"
            "3. Unplug sensitive electrical appliances to prevent surge damage from lightning strikes.\n"
            "4. Keep battery-powered emergency radios, flashlights, and mobile power banks fully charged.\n"
            "5. Avoid parking or sheltering beneath large trees, old hoardings, or high-voltage electric towers."
        ),
        "critical_donts": [
            "Do NOT venture outside during the calm 'eye of the storm' as severe reverse winds follow quickly.",
            "Do NOT touch dangling overhead cables.",
            "Do NOT operate two-wheelers during gale-force gusts.",
        ],
    },
    "landslide": {
        "title": "Landslide & Slope Debris Safety Protocols",
        "official_guidance": (
            "1. Stay alert to warning sounds: rumbling, cracking trees, or sudden increase in creek water sediment.\n"
            "2. Evacuate quickly if you suspect imminent slope movement. Move across the path of the slide, never down it.\n"
            "3. Avoid river valleys and low drainage paths where debris flows can travel miles downstream.\n"
            "4. Curl into a tight ball and protect your head if escape is impossible.\n"
            "5. Beware of flash flooding and secondary slides following the initial debris movement."
        ),
        "critical_donts": [
            "Do NOT cross roads covered with fresh rockfall or slurry.",
            "Do NOT stay in low hollows or drainage gullies.",
            "Do NOT sleep on ground floors adjacent to steep unconsolidated slopes during heavy rainfall.",
        ],
    },
    "other": {
        "title": "General Disaster Awareness & Incident Safety",
        "official_guidance": (
            "1. Stay calm and maintain situation awareness.\n"
            "2. Tune in to official district administration radio and verified emergency broadcasts.\n"
            "3. Assist elderly neighbors, children, and persons with disabilities if safe to do so.\n"
            "4. Preserve phone battery for genuine emergency calls. Use SMS/text where networks are congested.\n"
            "5. Follow instructions of local law enforcement, civil defense volunteers, and NDRF/SDRF personnel."
        ),
        "critical_donts": [
            "Do NOT spread unverified rumors on social media.",
            "Do NOT block emergency vehicle access corridors.",
            "Do NOT dial emergency lines for non-urgent inquiries.",
        ],
    },
}


def get_safety_protocol(category: str) -> Dict[str, Any]:
    """Retrieves standard guidance for a disaster category."""
    cat = category.lower()
    return STANDARD_SAFETY_GUIDANCE.get(cat, STANDARD_SAFETY_GUIDANCE["other"])

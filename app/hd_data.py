"""
Human Design static reference data.
Gate sequence verified against bodygraph.io using May 8 1982 02:57 AM Santarém PT.
"""

# 64 gates mapped to tropical zodiac starting at 0° Aries.
# Each gate spans 5.625° (360 / 64). Gate at index i covers i*5.625° to (i+1)*5.625°.
GATE_SEQUENCE = [
    25, 17, 21, 51, 42,  3,  # Aries  (0°   – 33.75°)
    27, 24,  2, 23,  8, 20,  # Taurus (33.75° – 67.5°)
    16, 35, 45, 12, 15, 52,  # Gemini
    39, 53, 62, 56, 31, 33,  # Cancer
     7,  4, 29, 59, 40, 64,  # Leo
    47,  6, 46, 18, 48, 57,  # Virgo / Libra
    32, 50, 28, 44,  1, 43,  # Libra / Scorpio
    14, 34,  9,  5, 26, 11,  # Scorpio / Sag
    10, 58, 38, 54, 61, 60,  # Capricorn
    41, 19, 13, 49, 30, 55,  # Aquarius
    37, 63, 22, 36,           # Pisces  (337.5° – 360°)
]

DEGREES_PER_GATE  = 360.0 / 64        # 5.625°
DEGREES_PER_LINE  = DEGREES_PER_GATE / 6   # 0.9375°
DEGREES_PER_COLOR = DEGREES_PER_LINE / 6   # 0.15625°
DEGREES_PER_TONE  = DEGREES_PER_COLOR / 6  # ~0.026042°

# The 36 channels as (gate_a, gate_b) pairs (always lower number first).
# Source: verified list including the 6 integration circuit channels.
CHANNELS = [
    ( 1,  8), ( 2, 14), ( 3, 60), ( 4, 63), ( 5, 15), ( 6, 59),
    ( 7, 31), ( 9, 52), (10, 20), (10, 34), (10, 57), (11, 56),
    (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49),
    (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (25, 51),
    (26, 44), (27, 50), (28, 38), (29, 46), (30, 41), (32, 54),
    (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64),
]

# 9 centers with their gates and whether they are motor centers.
CENTERS = {
    "Head":          {"gates": [64, 61, 63],                       "is_motor": False},
    "Ajna":          {"gates": [47, 24,  4, 17, 11, 43],           "is_motor": False},
    "Throat":        {"gates": [62, 23, 56, 35, 12, 45, 33,  8, 31, 20, 16], "is_motor": False},
    "G":             {"gates": [ 7,  1, 13, 10, 25, 15, 46,  2],   "is_motor": False},
    "Heart":         {"gates": [21, 40, 26, 51],                   "is_motor": True},
    "Solar Plexus":  {"gates": [36, 22, 37,  6, 49, 55, 30],      "is_motor": True},
    "Sacral":        {"gates": [34,  5, 14, 29, 59,  9,  3, 42, 27], "is_motor": True},
    "Spleen":        {"gates": [48, 57, 44, 50, 32, 28, 18],      "is_motor": False},
    "Root":          {"gates": [53, 60, 52, 19, 39, 41, 58, 38, 54], "is_motor": True},
}

# Reverse map: gate → center name
GATE_TO_CENTER = {}
for _center, _data in CENTERS.items():
    for _gate in _data["gates"]:
        GATE_TO_CENTER[_gate] = _center

# Channel → (center_a, center_b)
CHANNEL_TO_CENTERS = {}
for _g1, _g2 in CHANNELS:
    CHANNEL_TO_CENTERS[(_g1, _g2)] = (GATE_TO_CENTER[_g1], GATE_TO_CENTER[_g2])

# Planet display info (swe constant, display name, symbol)
PLANET_ORDER = [
    ("sun",        "Sun",        "☉"),
    ("earth",      "Earth",      "⊕"),  # derived: Sun + 180°
    ("north_node", "North Node", "☊"),
    ("south_node", "South Node", "☋"),  # derived: North Node + 180°
    ("moon",       "Moon",       "☽"),
    ("mercury",    "Mercury",    "☿"),
    ("venus",      "Venus",      "♀"),
    ("mars",       "Mars",       "♂"),
    ("jupiter",    "Jupiter",    "♃"),
    ("saturn",     "Saturn",     "♄"),
    ("uranus",     "Uranus",     "♅"),
    ("neptune",    "Neptune",    "♆"),
    ("pluto",      "Pluto",      "♇"),
]

# Type metadata
TYPE_META = {
    "Gerador": {
        "strategy":       "Responder",
        "signature":      "Satisfação",
        "not_self_theme": "Frustração",
    },
    "Gerador Manifestante": {
        "strategy":       "Responder",
        "signature":      "Satisfação & Paz",
        "not_self_theme": "Frustração & Raiva",
    },
    "Projector": {
        "strategy":       "Aguardar o Convite",
        "signature":      "Sucesso",
        "not_self_theme": "Amargura",
    },
    "Manifestor": {
        "strategy":       "Informar",
        "signature":      "Paz",
        "not_self_theme": "Raiva",
    },
    "Reflector": {
        "strategy":       "Aguardar Ciclo Lunar (28 dias)",
        "signature":      "Surpresa",
        "not_self_theme": "Desapontamento",
    },
}

# ── Variables (Determinação, Cognição, Motivação, Perspectiva, Ambiente) ────
# Each derived from Color (1-6) or Tone (1-6) of specific planetary positions.
# Design Sun  → Digestão (Tone) + Sentido de Design (Color)
# Personality Sun   → Motivação (Color)
# Personality Earth → Perspectiva (Color)
# Design Earth      → Ambiente (Tone)

DIGESTION_PT   = {1:"Consecutiva", 2:"Seletiva", 3:"Aberta",
                  4:"Paladar Fechado", 5:"Direto", 6:"Indireto"}
COGNITION_PT   = {1:"Olfato", 2:"Visão Interior", 3:"Visão Exterior",
                  4:"Paladar", 5:"Audição", 6:"Toque"}
MOTIVATION_PT  = {1:"Medo", 2:"Esperança", 3:"Desejo",
                  4:"Necessidade", 5:"Culpa", 6:"Inocência"}
PERSPECTIVE_PT = {1:"Querer", 2:"Desejo/Vontade", 3:"Sobrevivência",
                  4:"Poder", 5:"Natureza", 6:"Determinação"}
ENVIRONMENT_PT = {1:"Cavernas", 2:"Mercados", 3:"Vales",
                  4:"Costas", 5:"Montanhas", 6:"Florestas"}

# English → Portuguese type name mapping (for type determination)
TYPE_PT = {
    "Generator":            "Gerador",
    "Manifesting Generator":"Gerador Manifestante",
    "Projector":            "Projector",
    "Manifestor":           "Manifestor",
    "Reflector":            "Reflector",
}

# Incarnation Cross type by profile
CROSS_TYPE_BY_PROFILE = {
    "1/3": "Right Angle Cross", "1/4": "Right Angle Cross",
    "2/4": "Right Angle Cross", "2/5": "Right Angle Cross",
    "3/5": "Right Angle Cross", "3/6": "Right Angle Cross",
    "4/1": "Juxtaposition Cross",
    "4/6": "Left Angle Cross",  "5/1": "Left Angle Cross",
    "5/2": "Left Angle Cross",  "6/2": "Left Angle Cross",
    "6/3": "Left Angle Cross",
}

# Incarnation Cross name lookup
# Key: (personality_sun_gate, design_sun_gate, cross_type)
# cross_type: "RA" = Right Angle, "LA" = Left Angle, "J" = Juxtaposition
_RA, _LA, _J = "RA", "LA", "J"
CROSS_NAMES: dict = {
    (1,7,_RA):"the Sphinx",(1,4,_J):"Self-Expression",(1,4,_LA):"Defiance",
    (2,13,_RA):"the Sphinx",(2,49,_J):"the Driver",(2,49,_LA):"Defiance",
    (3,60,_RA):"Laws",(3,41,_J):"Mutation",(3,41,_LA):"Wishes",
    (4,23,_RA):"Explanation",(4,8,_J):"Formulization",(4,8,_LA):"Revolution",
    (5,64,_RA):"Consciousness",(5,47,_J):"Habits",(5,47,_LA):"Separation",
    (6,12,_RA):"Eden",(6,15,_J):"Conflict",(6,15,_LA):"the Plane",
    (7,2,_RA):"the Sphinx",(7,23,_J):"Interaction",(7,23,_LA):"Masks",
    (8,30,_RA):"Contagion",(8,55,_J):"Contribution",(8,55,_LA):"Uncertainty",
    (9,40,_RA):"Planning",(9,64,_J):"Focus",(9,64,_LA):"Identification",
    (10,46,_RA):"the Vessel of Love",(10,18,_J):"Behavior",(10,18,_LA):"Prevention",
    (11,6,_RA):"Eden",(11,46,_J):"Ideas",(11,46,_LA):"Education",
    (12,36,_RA):"Eden",(12,25,_J):"Articulation",(12,25,_LA):"Education",
    (13,1,_RA):"the Sphinx",(13,43,_J):"Listening",(13,43,_LA):"Masks",
    (14,29,_RA):"Contagion",(14,59,_J):"Empowering",(14,59,_LA):"Uncertainty",
    (15,25,_RA):"the Vessel of Love",(15,17,_J):"Extremes",(15,17,_LA):"Prevention",
    (16,37,_RA):"Planning",(16,63,_J):"Experimentation",(16,63,_LA):"Identification",
    (17,58,_RA):"Service",(17,38,_J):"Opinions",(17,38,_LA):"Upheaval",
    (18,52,_RA):"Service",(18,39,_J):"Correction",(18,39,_LA):"Upheaval",
    (19,44,_RA):"the Four Ways",(19,1,_J):"Need",(19,1,_LA):"Refinement",
    (20,55,_RA):"the Sleeping Phoenix",(20,37,_J):"the Now",(20,37,_LA):"Duality",
    (21,38,_RA):"Tension",(21,54,_J):"Control",(21,54,_LA):"Endeavour",
    (22,26,_RA):"Rulership",(22,11,_J):"Grace",(22,11,_LA):"Informing",
    (23,49,_RA):"Explanation",(23,30,_J):"Assimilation",(23,30,_LA):"Dedication",
    (24,19,_RA):"the Four Ways",(24,13,_J):"Rationalization",(24,13,_LA):"Incarnation",
    (25,10,_RA):"the Vessel of Love",(25,58,_J):"Innocence",(25,58,_LA):"Healing",
    (26,47,_RA):"Rulership",(26,6,_J):"the Trickster",(26,6,_LA):"Confrontation",
    (27,41,_RA):"the Unexpected",(27,19,_J):"Caring",(27,19,_LA):"Alignment",
    (28,31,_RA):"the Unexpected",(28,33,_J):"Risks",(28,33,_LA):"Alignment",
    (29,8,_RA):"Contagion",(29,20,_J):"Commitment",(29,20,_LA):"Industry",
    (30,14,_RA):"Contagion",(30,34,_J):"Fates",(30,34,_LA):"Industry",
    (31,27,_RA):"the Unexpected",(31,24,_J):"Influence",(31,24,_LA):"the Alpha",
    (32,62,_RA):"Maya",(32,56,_J):"Conservation",(32,56,_LA):"Limitation",
    (33,24,_RA):"the Four Ways",(33,2,_J):"Retreat",(33,2,_LA):"Refinement",
    (34,59,_RA):"the Sleeping Phoenix",(34,40,_J):"Power",(34,40,_LA):"Duality",
    (35,63,_RA):"Consciousness",(35,22,_J):"Experience",(35,22,_LA):"Separation",
    (36,11,_RA):"Eden",(36,10,_J):"Crisis",(36,10,_LA):"the Plane",
    (37,9,_RA):"Planning",(37,5,_J):"Bargains",(37,5,_LA):"Migration",
    (38,48,_RA):"Tension",(38,57,_J):"Opposition",(38,57,_LA):"Individualism",
    (39,21,_RA):"Tension",(39,51,_J):"Provocation",(39,51,_LA):"Individualism",
    (40,16,_RA):"Planning",(40,35,_J):"Denial",(40,35,_LA):"Migration",
    (41,28,_RA):"the Unexpected",(41,44,_J):"Fantasy",(41,44,_LA):"the Alpha",
    (42,61,_RA):"Maya",(42,60,_J):"Completion",(42,60,_LA):"Limitation",
    (43,4,_RA):"Explanation",(43,29,_J):"Insight",(43,29,_LA):"Dedication",
    (44,33,_RA):"the Four Ways",(44,7,_J):"Alertness",(44,7,_LA):"Incarnation",
    (45,22,_RA):"Rulership",(45,36,_J):"Possession",(45,36,_LA):"Confrontation",
    (46,15,_RA):"the Vessel of Love",(46,52,_J):"Serendipity",(46,52,_LA):"Healing",
    (47,45,_RA):"Rulership",(47,12,_J):"Oppression",(47,12,_LA):"Informing",
    (48,39,_RA):"Tension",(48,53,_J):"Depth",(48,53,_LA):"Endeavour",
    (49,43,_RA):"Explanation",(49,14,_J):"Principles",(49,14,_LA):"Revolution",
    (50,56,_RA):"Laws",(50,31,_J):"Values",(50,31,_LA):"Wishes",
    (51,54,_RA):"Penetration",(51,61,_J):"Shock",(51,61,_LA):"the Clarion",
    (52,17,_RA):"Service",(52,21,_J):"Stillness",(52,21,_LA):"Demands",
    (53,51,_RA):"Penetration",(53,42,_J):"Beginnings",(53,42,_LA):"Cycles",
    (54,57,_RA):"Penetration",(54,32,_J):"Ambition",(54,32,_LA):"Cycles",
    (55,34,_RA):"the Sleeping Phoenix",(55,9,_J):"Moods",(55,9,_LA):"Spirit",
    (56,3,_RA):"Laws",(56,27,_J):"Stimulation",(56,27,_LA):"Distraction",
    (57,53,_RA):"Penetration",(57,62,_J):"Intuition",(57,62,_LA):"the Clarion",
    (58,18,_RA):"Service",(58,48,_J):"Vitality",(58,48,_LA):"Demands",
    # Gates 59-64
    (59,20,_RA):"the Sleeping Phoenix",(59,16,_J):"Moods",(59,16,_LA):"Spirit",
    (60,50,_RA):"Laws",(60,28,_J):"Conservation",(60,28,_LA):"Limitation",
    (61,32,_RA):"Maya",(61,50,_J):"Completion",(61,50,_LA):"Limitation",
    (62,42,_RA):"Maya",(62,3,_J):"Stimulation",(62,3,_LA):"Distraction",
    (63,5,_RA):"Consciousness",(63,26,_J):"Experience",(63,26,_LA):"Separation",
    (64,35,_RA):"Consciousness",(64,45,_J):"Habits",(64,45,_LA):"Separation",
}

def get_cross_name(pers_sun: int, design_sun: int, profile: str) -> str:
    """Return the Incarnation Cross base name, or empty string if unknown."""
    ct = CROSS_TYPE_BY_PROFILE.get(profile, "")
    if "Right" in ct:
        key = (pers_sun, design_sun, _RA)
    elif "Juxtaposition" in ct:
        key = (pers_sun, design_sun, _J)
    else:
        key = (pers_sun, design_sun, _LA)
    return CROSS_NAMES.get(key, "")

# Authority priority (checked in order) — labels in Portuguese
AUTHORITY_ORDER = [
    ("Solar Plexus", "Emocional"),
    ("Sacral",       "Sacral"),
    ("Spleen",       "Esplénica"),
    ("Heart",        "Ego"),
    ("G",            "Self / Centro G"),
]

# Definition labels in Portuguese
DEFINITION_PT = {
    "Single Definition":     "Definição Simples",
    "Split Definition":      "Definição Bipartida",
    "Triple Split":          "Tripla Divisão",
    "Quadruple Split":       "Quadrupla Divisão",
    "No Definition":         "Sem Definição",
}

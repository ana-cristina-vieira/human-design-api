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

DEGREES_PER_GATE = 360.0 / 64  # 5.625°
DEGREES_PER_LINE = DEGREES_PER_GATE / 6  # 0.9375°

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
    "Generator": {
        "strategy":       "To Respond",
        "signature":      "Satisfaction",
        "not_self_theme": "Frustration",
    },
    "Manifesting Generator": {
        "strategy":       "To Respond",
        "signature":      "Satisfaction & Peace",
        "not_self_theme": "Frustration & Anger",
    },
    "Projector": {
        "strategy":       "Wait for the Invitation",
        "signature":      "Success",
        "not_self_theme": "Bitterness",
    },
    "Manifestor": {
        "strategy":       "To Inform",
        "signature":      "Peace",
        "not_self_theme": "Anger",
    },
    "Reflector": {
        "strategy":       "Wait a Lunar Cycle (28 days)",
        "signature":      "Surprise",
        "not_self_theme": "Disappointment",
    },
}

# Incarnation Cross type by profile
CROSS_TYPE_BY_PROFILE = {
    "1/3": "Right Angle Cross",
    "1/4": "Right Angle Cross",
    "2/4": "Right Angle Cross",
    "2/5": "Right Angle Cross",
    "3/5": "Right Angle Cross",
    "3/6": "Right Angle Cross",
    "4/1": "Juxtaposition Cross",
    "4/6": "Left Angle Cross",
    "5/1": "Left Angle Cross",
    "5/2": "Left Angle Cross",
    "6/2": "Left Angle Cross",
    "6/3": "Left Angle Cross",
}

# Authority priority (checked in order)
AUTHORITY_ORDER = [
    ("Solar Plexus", "Emotional"),
    ("Sacral",       "Sacral"),
    ("Spleen",       "Splenic"),
    ("Heart",        "Ego"),
    ("G",            "Self / G Center"),
]

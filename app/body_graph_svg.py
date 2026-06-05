"""
Generates a branded Body Graph SVG for Negócios com ALMA.
Colors follow the brand palette: cremes, terracota, espresso.
"""

from __future__ import annotations
from typing import Set, List, Tuple, Dict
from .hd_data import CENTERS, CHANNELS, CHANNEL_TO_CENTERS, GATE_TO_CENTER

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
C_DEFINED_FILL   = "#B2967D"   # Terracota Suave — defined centers
C_DEFINED_STROKE = "#7D5A44"   # Castanho Médio
C_UNDEFINED_FILL = "#F5F1EA"   # Creme Suave
C_UNDEF_STROKE   = "#D4C4B0"   # Bege Cálido
C_CHANNEL_DEF    = "#7D5A44"   # Castanho Médio — defined channel
C_CHANNEL_UNDEF  = "#EDE4D8"   # Creme Médio — background channel lines
C_TEXT_DEF       = "#FDFAF6"   # Creme Puro on dark centers
C_TEXT_UNDEF     = "#7D5A44"   # Castanho on light centers
C_BG             = "#FDFAF6"
C_BOTH_GATE      = "#4A342A"   # Castanho Escuro — gate activated by both
C_PERS_GATE      = "#B2967D"   # Personality gate (conscious)
C_DES_GATE       = "#7D5A44"   # Design gate (unconscious)

# ---------------------------------------------------------------------------
# Center geometry  (shape_type, geometry_dict, visual_center)
# ---------------------------------------------------------------------------
# Visual center coordinates used for channel routing
CENTER_POS: Dict[str, Tuple[float, float]] = {
    "Head":         (200, 72),
    "Ajna":         (200, 148),
    "Throat":       (200, 212),
    "G":            (200, 292),
    "Heart":        (318, 262),
    "Solar Plexus": (322, 378),
    "Sacral":       (200, 390),
    "Spleen":       ( 88, 326),
    "Root":         (200, 474),
}

def _triangle_points(cx, cy, size, inverted=False) -> str:
    if not inverted:
        return f"{cx},{cy - size*0.7} {cx - size},{cy + size*0.3} {cx + size},{cy + size*0.3}"
    else:
        return f"{cx - size},{cy - size*0.3} {cx + size},{cy - size*0.3} {cx},{cy + size*0.7}"

def _diamond_points(cx, cy, hw, hh) -> str:
    return f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"

# center_name → SVG shape element(s)
def _center_shape(name: str, defined: bool) -> str:
    fill   = C_DEFINED_FILL   if defined else C_UNDEFINED_FILL
    stroke = C_DEFINED_STROKE if defined else C_UNDEF_STROKE
    sw     = 2.5 if defined else 1.5
    tc     = C_TEXT_DEF       if defined else C_TEXT_UNDEF
    label  = name if name != "Solar Plexus" else "Sol.Plex."
    cx, cy = CENTER_POS[name]

    common = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'

    if name == "Head":
        pts = _triangle_points(cx, cy, 38)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 8
    elif name == "Ajna":
        pts = _triangle_points(cx, cy, 36, inverted=True)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 4
    elif name in ("Throat", "Sacral", "Root"):
        w, h = (76, 32) if name == "Throat" else (104, 52) if name == "Sacral" else (104, 42)
        x, y = cx - w/2, cy - h/2
        shape = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" {common}/>'
        tx, ty = cx, cy + 5
    elif name == "G":
        pts = _diamond_points(cx, cy, 62, 54)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 5
    elif name == "Heart":
        pts = _triangle_points(cx, cy, 34)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 6
    elif name == "Solar Plexus":
        pts = _triangle_points(cx, cy, 38)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 8
    elif name == "Spleen":
        pts = _triangle_points(cx, cy, 40)
        shape = f'<polygon points="{pts}" {common}/>'
        tx, ty = cx, cy + 8
    else:
        return ""

    txt = (f'<text x="{tx}" y="{ty}" text-anchor="middle" '
           f'font-family="sans-serif" font-size="9" fill="{tc}" '
           f'font-weight="600" letter-spacing="0.5">{label.upper()}</text>')
    return shape + "\n  " + txt


# ---------------------------------------------------------------------------
# Gate number dots
# ---------------------------------------------------------------------------
def _gate_dot(x: float, y: float, gate: int,
               in_personality: bool, in_design: bool) -> str:
    if in_personality and in_design:
        fill, tc = C_BOTH_GATE, C_TEXT_DEF
    elif in_personality:
        fill, tc = C_PERS_GATE, C_TEXT_DEF
    else:
        fill, tc = C_DES_GATE, C_TEXT_DEF

    return (f'<circle cx="{x}" cy="{y}" r="8" fill="{fill}" opacity="0.9"/>'
            f'<text x="{x}" y="{y+3.5}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="7" fill="{tc}" font-weight="700">'
            f'{gate}</text>')


# Gate positions around each center (offset from center_pos)
_GATE_OFFSETS: Dict[str, List[Tuple[float, float]]] = {
    "Head":         [(-18, -30), (0, -42), (18, -30)],          # 3 gates
    "Ajna":         [(-28, 0), (-14, -20), (0, 28), (14, -20), (28, 0), (0, -28)],
    "Throat":       [(-38, 0), (-24, 0), (-10, 0), (4, 0),
                     (18, 0), (32, 0), (-32, 16), (-16, 16),
                     (0, 16), (16, 16), (30, 16)],
    "G":            [(-38, -16), (-22, -30), (0, -44), (22, -30),
                     (38, -16), (38, 16), (0, 44), (-38, 16)],
    "Heart":        [(-18, -30), (18, -30), (0, 28), (-18, 10)],
    "Solar Plexus": [(-20, -30), (20, -30), (0, -44), (-24, 0), (24, 0), (0, 28), (-12, 14)],
    "Sacral":       [(-46, 0), (-30, 0), (-14, 0), (0, 0),
                     (14, 0), (28, 0), (-38, 20), (-24, 20),
                     (0, -24)],
    "Spleen":       [(-26, -26), (0, -38), (26, -26), (-32, 0), (32, 0), (0, 28), (-16, 14)],
    "Root":         [(-46, 0), (-30, 0), (-14, 0), (2, 0),
                     (16, 0), (30, 0), (-38, -20), (-22, -20),
                     (4, -20)],
}

# Map center → ordered gate list for offset indexing
_CENTER_GATE_ORDER: Dict[str, List[int]] = {
    "Head":         [64, 61, 63],
    "Ajna":         [47, 24,  4, 17, 11, 43],
    "Throat":       [62, 23, 56, 35, 12, 45, 33,  8, 31, 20, 16],
    "G":            [ 7,  1, 13, 10, 25, 15, 46,  2],
    "Heart":        [21, 40, 26, 51],
    "Solar Plexus": [36, 22, 37,  6, 49, 55, 30],
    "Sacral":       [34,  5, 14, 29, 59,  9,  3, 42, 27],
    "Spleen":       [48, 57, 44, 50, 32, 28, 18],
    "Root":         [53, 60, 52, 19, 39, 41, 58, 38, 54],
}


def _gate_dots_for_center(
    center_name: str,
    p_gates: Set[int],
    d_gates: Set[int],
) -> str:
    cx, cy = CENTER_POS[center_name]
    gates   = _CENTER_GATE_ORDER[center_name]
    offsets = _GATE_OFFSETS.get(center_name, [])
    out = []
    for i, gate in enumerate(gates):
        in_p = gate in p_gates
        in_d = gate in d_gates
        if not (in_p or in_d):
            continue
        if i < len(offsets):
            dx, dy = offsets[i]
        else:
            dx, dy = 0, 0
        out.append(_gate_dot(cx + dx, cy + dy, gate, in_p, in_d))
    return "\n  ".join(out)


# ---------------------------------------------------------------------------
# Channel lines
# ---------------------------------------------------------------------------
def _channel_lines(defined_channels: List[Tuple[int, int]]) -> str:
    # Group defined channels by center-pair
    defined_pairs: Set[Tuple[str, str]] = set()
    for g1, g2 in defined_channels:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        defined_pairs.add((min(c1, c2), max(c1, c2)))

    # All possible center-pair connections
    all_pairs: Set[Tuple[str, str]] = set()
    for g1, g2 in CHANNELS:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        all_pairs.add((min(c1, c2), max(c1, c2)))

    bg_lines  = []   # undefined channels — rendered first (bottom)
    top_lines = []   # defined channels  — rendered last (top)

    for pair in all_pairs:
        x1, y1 = CENTER_POS[pair[0]]
        x2, y2 = CENTER_POS[pair[1]]
        is_def  = pair in defined_pairs
        color   = C_CHANNEL_DEF  if is_def else C_CHANNEL_UNDEF
        width   = "3.5"          if is_def else "1.5"
        opacity = "1"            if is_def else "0.7"
        el = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
              f'stroke="{color}" stroke-width="{width}" opacity="{opacity}" '
              f'stroke-linecap="round"/>')
        (top_lines if is_def else bg_lines).append(el)

    return "\n  ".join(bg_lines + top_lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_body_graph_svg(
    defined_centers: Set[str],
    defined_channels: List[Tuple[int, int]],
    personality_gates: Set[int],
    design_gates: Set[int],
    width: int = 400,
    height: int = 560,
) -> str:
    centers_svg  = "\n  ".join(
        _center_shape(name, name in defined_centers)
        for name in CENTER_POS
    )
    channels_svg = _channel_lines(defined_channels)
    gate_dots    = "\n  ".join(
        _gate_dots_for_center(name, personality_gates, design_gates)
        for name in CENTER_POS
    )

    # Legend
    legend = f"""
  <g transform="translate(8, {height - 52})">
    <circle cx="8" cy="8" r="6" fill="{C_PERS_GATE}"/>
    <text x="18" y="12" font-family="sans-serif" font-size="8" fill="#7D5A44">Personality</text>
    <circle cx="8" cy="24" r="6" fill="{C_DES_GATE}"/>
    <text x="18" y="28" font-family="sans-serif" font-size="8" fill="#7D5A44">Design</text>
    <circle cx="8" cy="40" r="6" fill="{C_BOTH_GATE}"/>
    <text x="18" y="44" font-family="sans-serif" font-size="8" fill="#7D5A44">Both</text>
  </g>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="{C_BG}"/>
  <!-- Channel lines (background then defined) -->
  {channels_svg}
  <!-- Center shapes -->
  {centers_svg}
  <!-- Active gate dots -->
  {gate_dots}
  {legend}
</svg>"""

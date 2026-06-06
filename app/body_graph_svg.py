"""
Body Graph SVG — Negócios com ALMA.
Gates inside centers, square shapes, rounded triangles, thick channels.
"""
from __future__ import annotations
from typing import Set, List, Tuple, Dict
from .hd_data import CHANNELS, GATE_TO_CENTER

# ── Colours ────────────────────────────────────────────────────────────────────
C_CTR_DEF    = "#B2967D"   # defined center fill (lighter than gate)
C_CTR_UNDEF  = "#FFFFFF"   # open center: white
C_CTR_STR    = "#7D5A44"   # center stroke
C_GATE_ON    = "#4A342A"   # active gate fill (dark)
C_GATE_OFF   = "#FFFFFF"   # inactive gate fill (white)
C_GATE_ON_T  = "#FDFAF6"   # active gate text
C_GATE_OFF_T = "#7D5A44"   # inactive gate text
C_GATE_STR   = "#7D5A44"   # gate stroke (active)
C_GATE_OSTR  = "#D4C4B0"   # gate stroke (inactive)
C_CHAN_DEF   = "#1E1612"   # defined channel (espresso, very dark)
C_CHAN_UNDEF = "#EDE4D8"   # undefined channel (very light)
C_BG         = "#FDFAF6"

# ── Center positions ───────────────────────────────────────────────────────────
CENTER_POS: Dict[str, Tuple[float, float]] = {
    "Head":         (220,  58),
    "Ajna":         (220, 140),
    "Throat":       (220, 215),
    "G":            (220, 305),
    "Heart":        (326, 262),
    "Solar Plexus": (328, 378),
    "Sacral":       (220, 398),
    "Spleen":       ( 90, 332),
    "Root":         (220, 480),
}

# ── Gate layouts inside each center (gate, rel_x, rel_y) ──────────────────────
# Gates spread toward the EDGES of each center shape, matching original HD charts.
# Spacing ~18px centre-to-centre to fill the shape width.
_GATE_LAYOUT: Dict[str, List[Tuple[int, float, float]]] = {
    # HEAD triangle — 3 gates in a row near the base
    "Head": [
        (64,-18, 8), (61, 0, 8), (63,18, 8),
    ],
    # AJNA — 6 gates, 2 rows spanning the full width
    "Ajna": [
        (47,-18,-10),(24, 0,-10),(4, 18,-10),
        (17,-18, 10),(11, 0, 10),(43,18, 10),
    ],
    # THROAT square — 11 gates, 3 rows 4+4+3, spread to ±27px
    "Throat": [
        (62,-27,-19),(23,-9,-19),(56, 9,-19),(35,27,-19),
        (12,-27,  0),(45,-9,  0),(33, 9,  0),( 8,27,  0),
        (31,-18, 19),(20, 0, 19),(16,18, 19),
    ],
    # G diamond — 8 gates in 3 rows, spread ±22px
    "G": [
        ( 7,-22,-20),(1, 0,-20),(13,22,-20),
        (10,-22,  0),(25, 0,  0),(15,22,  0),
        (46,-11, 20),(2, 11, 20),
    ],
    # HEART triangle — 4 gates 2×2, spread ±16px
    "Heart": [
        (21,-16,-9),(40,16,-9),
        (26,-16, 9),(51,16,  9),
    ],
    # SOLAR PLEXUS — 7 gates 3+2+2, spread ±20px
    "Solar Plexus": [
        (36,-20,-14),(22, 0,-14),(37,20,-14),
        ( 6,-10,  0),(49,10,  0),
        (55,-10, 14),(30,10, 14),
    ],
    # SACRAL square — 9 gates 3×3, spread ±26px
    "Sacral": [
        (34,-26,-24),(5,  0,-24),(14,26,-24),
        (29,-26,  0),(59, 0,  0),( 9,26,  0),
        ( 3,-26, 24),(42, 0, 24),(27,26, 24),
    ],
    # SPLEEN triangle — 7 gates 3+2+2, spread ±20px
    "Spleen": [
        (48,-20,-16),(57, 0,-16),(44,20,-16),
        (50,-10,  0),(32,10,  0),
        (28,-10, 16),(18,10, 16),
    ],
    # ROOT square — 9 gates 3×3, spread ±24px
    "Root": [
        (53,-24,-18),(60, 0,-18),(52,24,-18),
        (19,-24,  0),(39, 0,  0),(41,24,  0),
        (58,-24, 18),(38, 0, 18),(54,24, 18),
    ],
}

# ── Rounded triangle path ──────────────────────────────────────────────────────
def _rtri_path(verts: List[Tuple[float,float]], r: float = 12) -> str:
    """SVG path for a polygon with rounded corners (quadratic bezier)."""
    n = len(verts)
    def lerp(a, b, t):
        return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t)

    parts = []
    for i in range(n):
        prev_v = verts[(i-1) % n]
        curr_v = verts[i]
        next_v = verts[(i+1) % n]

        d1 = ((curr_v[0]-prev_v[0])**2 + (curr_v[1]-prev_v[1])**2)**0.5
        d2 = ((next_v[0]-curr_v[0])**2 + (next_v[1]-curr_v[1])**2)**0.5
        t1 = min(r / d1, 0.5) if d1 > 0 else 0
        t2 = min(r / d2, 0.5) if d2 > 0 else 0

        sp = lerp(prev_v, curr_v, 1 - t1)
        ep = lerp(curr_v, next_v, t2)

        if i == 0:
            parts.append(f"M{sp[0]:.1f},{sp[1]:.1f}")
        else:
            parts.append(f"L{sp[0]:.1f},{sp[1]:.1f}")
        parts.append(f"Q{curr_v[0]:.1f},{curr_v[1]:.1f} {ep[0]:.1f},{ep[1]:.1f}")

    parts.append("Z")
    return " ".join(parts)


def _tri_verts(cx, cy, hw, hh, inv=False):
    if not inv:
        return [(cx, cy-hh), (cx-hw, cy+hh*0.42), (cx+hw, cy+hh*0.42)]
    return [(cx-hw, cy-hh*0.42), (cx+hw, cy-hh*0.42), (cx, cy+hh)]


def _diamond_path(cx, cy, hw, hh, r=10):
    verts = [(cx, cy-hh), (cx+hw, cy), (cx, cy+hh), (cx-hw, cy)]
    return _rtri_path(verts, r)

# ── Center shapes ──────────────────────────────────────────────────────────────
def _center_shape(name: str, defined: bool) -> str:
    fill   = C_CTR_DEF   if defined else C_CTR_UNDEF
    stroke = C_CTR_STR
    sw     = 2.5 if defined else 1.5
    cx, cy = CENTER_POS[name]
    s = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'

    if name == "Head":
        path = _rtri_path(_tri_verts(cx, cy, 44, 36), r=12)
        return f'<path d="{path}" {s}/>'
    elif name == "Ajna":
        path = _rtri_path(_tri_verts(cx, cy, 40, 32, inv=True), r=12)
        return f'<path d="{path}" {s}/>'
    elif name == "Throat":
        sz = 68  # SQUARE
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    elif name == "G":
        path = _diamond_path(cx, cy, 70, 58, r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Heart":
        path = _rtri_path(_tri_verts(cx, cy, 32, 28), r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Solar Plexus":
        path = _rtri_path(_tri_verts(cx, cy, 34, 30), r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Sacral":
        sz = 74  # SQUARE
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    elif name == "Spleen":
        path = _rtri_path(_tri_verts(cx, cy, 38, 34), r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Root":
        sz = 68  # SQUARE
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    return ""

# ── Gates as rounded squares inside centers ────────────────────────────────────
def _center_gates(name: str, p_gates: Set[int], d_gates: Set[int]) -> str:
    cx, cy = CENTER_POS[name]
    elems = []
    for gate, rx, ry in _GATE_LAYOUT.get(name, []):
        gx, gy = cx + rx, cy + ry
        in_p = gate in p_gates
        in_d = gate in d_gates
        active = in_p or in_d

        fill   = C_GATE_ON  if active else C_GATE_OFF
        tc     = C_GATE_ON_T if active else C_GATE_OFF_T
        sc     = C_GATE_STR  if active else C_GATE_OSTR
        sw     = "1.5" if active else "0.8"
        fw     = "700" if active else "400"
        r      = "8"   if active else "7.5"
        fs     = "6.5"

        # Gate = circle (matching original HD charts)
        elems.append(
            f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{r}" '
            f'fill="{fill}" stroke="{sc}" stroke-width="{sw}"/>'
            f'<text x="{gx:.1f}" y="{gy+2.5:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{fs}" fill="{tc}" '
            f'font-weight="{fw}">{gate}</text>'
        )
    return "\n  ".join(elems)

# ── Channel lines ──────────────────────────────────────────────────────────────
def _channel_lines(defined_channels: List[Tuple[int,int]]) -> str:
    def_pairs: Set[Tuple[str,str]] = set()
    for g1, g2 in defined_channels:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        def_pairs.add((min(c1,c2), max(c1,c2)))

    all_pairs: Set[Tuple[str,str]] = set()
    for g1, g2 in CHANNELS:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        all_pairs.add((min(c1,c2), max(c1,c2)))

    bg, top = [], []
    for pair in all_pairs:
        x1, y1 = CENTER_POS[pair[0]]
        x2, y2 = CENTER_POS[pair[1]]
        is_def  = pair in def_pairs
        col = C_CHAN_DEF   if is_def else C_CHAN_UNDEF
        w   = "10"         if is_def else "2"
        op  = "1"          if is_def else "0.5"
        el  = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
               f'stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
        (top if is_def else bg).append(el)
    return "\n  ".join(bg + top)

# ── Legend ─────────────────────────────────────────────────────────────────────
def _legend(height: int) -> str:
    y = height - 56
    items = [(C_GATE_ON,"Personalidade / Design"),(C_GATE_OFF,"Gate aberto")]
    rows = []
    for i,(c,lbl) in enumerate(items):
        ry = y + i*20
        rows.append(
            f'<rect x="2" y="{ry}" width="14" height="14" rx="2" '
            f'fill="{c}" stroke="{C_GATE_STR}" stroke-width="1"/>'
            f'<text x="20" y="{ry+11}" font-family="sans-serif" font-size="9" '
            f'fill="#7D5A44">{lbl}</text>'
        )
    return f'<g>{"".join(rows)}</g>'

# ── Public API ─────────────────────────────────────────────────────────────────
def generate_body_graph_svg(
    defined_centers:   Set[str],
    defined_channels:  List[Tuple[int,int]],
    personality_gates: Set[int],
    design_gates:      Set[int],
    width:  int = 430,
    height: int = 565,
) -> str:
    channels = _channel_lines(defined_channels)
    centers  = "\n  ".join(_center_shape(n, n in defined_centers) for n in CENTER_POS)
    gates    = "\n  ".join(_center_gates(n, personality_gates, design_gates) for n in CENTER_POS)
    legend   = _legend(height)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        f'  <rect width="{width}" height="{height}" fill="{C_BG}"/>\n'
        f'  {channels}\n  {centers}\n  {gates}\n  {legend}\n'
        f'</svg>'
    )

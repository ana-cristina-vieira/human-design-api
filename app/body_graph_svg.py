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
_GATE_LAYOUT: Dict[str, List[Tuple[int, float, float]]] = {
    # HEAD triangle (3 gates, single row)
    "Head": [
        (64,-18, 2), (61, 0, 2), (63,18, 2),
    ],
    # AJNA inv-triangle (6 gates, 2 rows of 3)
    "Ajna": [
        (47,-18,-9),(24, 0,-9),(4, 18,-9),
        (17,-18, 9),(11, 0, 9),(43,18, 9),
    ],
    # THROAT — square 70×70, 11 gates: rows 4+4+3
    "Throat": [
        (62,-25,-16),(23,-9,-16),(56, 9,-16),(35,25,-16),
        (12,-25,  0),(45,-9,  0),(33, 9,  0),( 8,25,  0),
        (31,-17, 16),(20, 0, 16),(16,17, 16),
    ],
    # G diamond (8 gates, 3 rows: 3+3+2)
    "G": [
        ( 7,-18,-18),(1, 0,-18),(13,18,-18),
        (10,-18,  0),(25, 0,  0),(15,18,  0),
        (46, -9, 18),(2,  9, 18),
    ],
    # HEART triangle (4 gates, 2×2)
    "Heart": [
        (21,-14,-8),(40,14,-8),
        (26,-14, 8),(51,14, 8),
    ],
    # SOLAR PLEXUS triangle (7 gates: 3+2+2)
    "Solar Plexus": [
        (36,-18,-14),(22, 0,-14),(37,18,-14),
        ( 6,-9,   0),(49, 9,  0),
        (55,-9,  14),(30, 9, 14),
    ],
    # SACRAL — square 76×76, 9 gates: 3×3
    "Sacral": [
        (34,-22,-18),(5,  0,-18),(14,22,-18),
        (29,-22,  0),(59, 0,  0),( 9,22,  0),
        ( 3,-22, 18),(42, 0, 18),(27,22, 18),
    ],
    # SPLEEN triangle (7 gates: 3+2+2)
    "Spleen": [
        (48,-18,-14),(57, 0,-14),(44,18,-14),
        (50,-9,   0),(32, 9,  0),
        (28,-9,  14),(18, 9, 14),
    ],
    # ROOT — square 70×70, 9 gates: 3×3
    "Root": [
        (53,-22,-16),(60, 0,-16),(52,22,-16),
        (19,-22,  0),(39, 0,  0),(41,22,  0),
        (58,-22, 16),(38, 0, 16),(54,22, 16),
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
        sw     = "1.2" if active else "0.8"
        fw     = "700" if active else "400"
        fs     = "7"   if active else "6.5"
        sz     = 15    # gate square size

        elems.append(
            f'<rect x="{gx-sz/2:.1f}" y="{gy-sz/2:.1f}" width="{sz}" height="{sz}" '
            f'rx="3" fill="{fill}" stroke="{sc}" stroke-width="{sw}"/>'
            f'<text x="{gx:.1f}" y="{gy+3:.1f}" text-anchor="middle" '
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
        w   = "8"          if is_def else "2.5"
        op  = "1"          if is_def else "0.7"
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

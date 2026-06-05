"""
Body Graph SVG — Negócios com ALMA.
All 64 gates shown INSIDE their center shapes (no labels).
Defined channels = thick filled lines.
"""
from __future__ import annotations
from typing import Set, List, Tuple, Dict
from .hd_data import CHANNELS, GATE_TO_CENTER

# ── Brand colours ──────────────────────────────────────────────────────────────
C_DEF_FILL   = "#B2967D"   # defined center fill
C_DEF_STR    = "#7D5A44"   # defined stroke / channel
C_UNDEF_FILL = "#F5F1EA"   # undefined center
C_UNDEF_STR  = "#D4C4B0"
C_CHAN_DEF   = "#4A342A"   # thick defined channel
C_CHAN_UNDEF = "#EDE4D8"   # thin inactive channel
C_GATE_P     = "#B2967D"   # Personality gate
C_GATE_D     = "#7D5A44"   # Design gate
C_GATE_BOTH  = "#4A342A"   # Both
C_GATE_OFF   = "none"      # inactive gate (transparent fill)
C_ON_TXT     = "#FDFAF6"
C_OFF_TXT    = "#7D5A44"
C_BG         = "#FDFAF6"

# ── Center positions (visual centre for channel routing) ────────────────────────
CENTER_POS: Dict[str, Tuple[float, float]] = {
    "Head":         (220,  58),
    "Ajna":         (220, 138),
    "Throat":       (220, 210),
    "G":            (220, 300),
    "Heart":        (325, 260),
    "Solar Plexus": (328, 378),
    "Sacral":       (220, 395),
    "Spleen":       ( 90, 330),
    "Root":         (220, 482),
}

# ── Gate layout inside each center ────────────────────────────────────────────
# (gate, rel_x, rel_y) — relative to center position
_GATE_LAYOUT: Dict[str, List[Tuple[int,float,float]]] = {
    "Head": [
        (64, -18, 0), (61,  0, 0), (63, 18, 0),
    ],
    "Ajna": [
        (47,-18,-10),(24, 0,-10),(4, 18,-10),
        (17,-18, 10),(11, 0, 10),(43,18, 10),
    ],
    "Throat": [
        (62,-45,-10),(23,-27,-10),(56,-9,-10),(35, 9,-10),(12,27,-10),(45,45,-10),
        (33,-36, 10),(8,-18, 10),(31, 0, 10),(20,18, 10),(16,36, 10),
    ],
    "G": [
        ( 7,-18,-18),(1, 0,-18),(13,18,-18),
        (10,-18,  0),(25,0,  0),(15,18,  0),
        (46,-9,  18),(2, 9,  18),
    ],
    "Heart": [
        (21,-14,-8),(40,14,-8),
        (26,-14, 8),(51,14,  8),
    ],
    "Solar Plexus": [
        (36,-20,-14),(22, 0,-14),(37,20,-14),
        ( 6,-20,  0),(49, 0,  0),(55,20,  0),
        (30,  0, 14),
    ],
    "Sacral": [
        (34,-36,-14),(5,-18,-14),(14,0,-14),(29,18,-14),(59,36,-14),
        ( 9,-27,  6),(3,-9,   6),(42, 9,  6),(27,27,  6),
    ],
    "Spleen": [
        (48,-18,-16),(57, 0,-16),(44,18,-16),
        (50,-18,  2),(32, 0,  2),(28,18,  2),
        (18,  0, 18),
    ],
    "Root": [
        (53,-36,-14),(60,-18,-14),(52,0,-14),(19,18,-14),(39,36,-14),
        (41,-27,  4),(58,-9,  4),(38, 9,  4),(54,27,  4),
    ],
}

# ── Center shapes ──────────────────────────────────────────────────────────────
def _tri_pts(cx, cy, hw, hh, inv=False):
    if not inv:
        return f"{cx},{cy-hh} {cx-hw},{cy+hh*0.4} {cx+hw},{cy+hh*0.4}"
    return f"{cx-hw},{cy-hh*0.4} {cx+hw},{cy-hh*0.4} {cx},{cy+hh}"

def _diamond_pts(cx, cy, hw, hh):
    return f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"

def _center_shape(name: str, defined: bool) -> str:
    fill   = C_DEF_FILL   if defined else C_UNDEF_FILL
    stroke = C_DEF_STR    if defined else C_UNDEF_STR
    sw = 2.5 if defined else 1.5
    cx, cy = CENTER_POS[name]
    s = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'

    shapes = {
        "Head":  f'<polygon points="{_tri_pts(cx,cy,45,35)}" {s}/>',
        "Ajna":  f'<polygon points="{_tri_pts(cx,cy,42,32,inv=True)}" {s}/>',
        "Throat":f'<rect x="{cx-54}" y="{cy-22}" width="108" height="44" rx="4" {s}/>',
        "G":     f'<polygon points="{_diamond_pts(cx,cy,72,56)}" {s}/>',
        "Heart": f'<polygon points="{_tri_pts(cx,cy,34,28)}" {s}/>',
        "Solar Plexus": f'<polygon points="{_tri_pts(cx,cy,36,30)}" {s}/>',
        "Sacral":f'<rect x="{cx-54}" y="{cy-26}" width="108" height="52" rx="4" {s}/>',
        "Spleen":f'<polygon points="{_tri_pts(cx,cy,40,34)}" {s}/>',
        "Root":  f'<rect x="{cx-54}" y="{cy-22}" width="108" height="44" rx="4" {s}/>',
    }
    return shapes.get(name, "")

# ── Gates inside centers ───────────────────────────────────────────────────────
def _center_gates(name: str, p_gates: Set[int], d_gates: Set[int]) -> str:
    cx, cy = CENTER_POS[name]
    elems = []
    for gate, rx, ry in _GATE_LAYOUT.get(name, []):
        gx, gy = cx + rx, cy + ry
        in_p = gate in p_gates
        in_d = gate in d_gates

        if in_p and in_d:
            fill, tc, sw = C_GATE_BOTH, C_ON_TXT, "1"
        elif in_p:
            fill, tc, sw = C_GATE_P,    C_ON_TXT, "1"
        elif in_d:
            fill, tc, sw = C_GATE_D,    C_ON_TXT, "1"
        else:
            fill, tc, sw = C_GATE_OFF,  C_OFF_TXT, "0.8"

        sc = C_DEF_STR if (in_p or in_d) else C_UNDEF_STR
        r  = "8.5" if (in_p or in_d) else "8"
        fw = "700" if (in_p or in_d) else "400"
        fs = "7"   if (in_p or in_d) else "6.5"

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
    from collections import defaultdict
    pair_def: Set[Tuple[str,str]] = set()
    for g1, g2 in defined_channels:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        pair_def.add((min(c1,c2), max(c1,c2)))

    all_pairs: Set[Tuple[str,str]] = set()
    for g1, g2 in CHANNELS:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        all_pairs.add((min(c1,c2), max(c1,c2)))

    bg, top = [], []
    for pair in all_pairs:
        x1, y1 = CENTER_POS[pair[0]]
        x2, y2 = CENTER_POS[pair[1]]
        is_def  = pair in pair_def
        col = C_CHAN_DEF   if is_def else C_CHAN_UNDEF
        w   = "5"          if is_def else "1.5"
        op  = "1"          if is_def else "0.5"
        el  = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
               f'stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
        (top if is_def else bg).append(el)
    return "\n  ".join(bg + top)

# ── Legend ─────────────────────────────────────────────────────────────────────
def _legend(height: int) -> str:
    y = height - 58
    items = [(C_GATE_P,"Personalidade"),(C_GATE_D,"Design"),(C_GATE_BOTH,"Ambos")]
    rows = []
    for i,(c,lbl) in enumerate(items):
        ry = y + i*18
        rows.append(
            f'<circle cx="8" cy="{ry+5}" r="7" fill="{c}"/>'
            f'<text x="20" y="{ry+9}" font-family="sans-serif" font-size="9" fill="#7D5A44">{lbl}</text>'
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
        f'  <!-- channels -->\n  {channels}\n'
        f'  <!-- center shapes -->\n  {centers}\n'
        f'  <!-- gates inside centers -->\n  {gates}\n'
        f'  {legend}\n'
        f'</svg>'
    )

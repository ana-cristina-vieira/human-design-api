"""
Body Graph SVG — Negócios com ALMA.
Gates posicionados na BORDA de cada centro (nunca dentro das formas).
"""
from __future__ import annotations
from typing import Set, List, Tuple, Dict
from collections import defaultdict
from .hd_data import CHANNELS, GATE_TO_CENTER

# ── Brand colours ──────────────────────────────────────────────────────────────
C_DEF_FILL   = "#B2967D"
C_DEF_STR    = "#7D5A44"
C_UNDEF_FILL = "#F5F1EA"
C_UNDEF_STR  = "#D4C4B0"
C_CHAN_DEF   = "#7D5A44"
C_CHAN_UNDEF = "#EDE4D8"
C_GATE_P     = "#B2967D"
C_GATE_D     = "#7D5A44"
C_GATE_BOTH  = "#4A342A"
C_GATE_OFF   = "#FDFAF6"
C_OFF_STR    = "#D4C4B0"
C_ON_TXT     = "#FDFAF6"
C_OFF_TXT    = "#B2967D"
C_BG         = "#FDFAF6"

# ── Center visual positions (centre of each shape) ─────────────────────────────
CENTER_POS: Dict[str, Tuple[float, float]] = {
    "Head":         (210, 68),
    "Ajna":         (210, 142),
    "Throat":       (210, 205),
    "G":            (210, 285),
    "Heart":        (320, 252),
    "Solar Plexus": (322, 368),
    "Sacral":       (210, 378),
    "Spleen":       ( 88, 318),
    "Root":         (210, 462),
}

# Distance from center to edge of each shape (for gate placement)
CENTER_EDGE: Dict[str, float] = {
    "Head":         40,
    "Ajna":         38,
    "Throat":       18,
    "G":            58,
    "Heart":        34,
    "Solar Plexus": 40,
    "Sacral":       30,
    "Spleen":       44,
    "Root":         24,
}

# ── Gate positions (at center EDGE, toward partner center) ─────────────────────
def _build_gate_positions() -> Dict[int, Tuple[float, float]]:
    """
    Place each gate at the EDGE of its center shape, facing toward the
    partner center. Multiple channels between the same two centers are
    spread perpendicularly (offset by 10px each).
    """
    pair_chans: Dict[Tuple[str,str], List[Tuple[int,int]]] = defaultdict(list)
    for g1, g2 in CHANNELS:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        key = (min(c1,c2), max(c1,c2))
        pair_chans[key].append((g1, g2))

    raw: Dict[int, List[Tuple[float,float]]] = defaultdict(list)
    SPREAD = 10   # px between parallel channels

    for (cn1, cn2), chans in pair_chans.items():
        x1, y1 = CENTER_POS[cn1]
        x2, y2 = CENTER_POS[cn2]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            continue
        # unit vectors: along channel and perpendicular
        ux, uy   = dx / dist, dy / dist
        px, py   = -uy, ux

        n = len(chans)
        for i, (g1, g2) in enumerate(chans):
            offset = (i - (n - 1) / 2) * SPREAD
            ox, oy = offset * px, offset * py

            # Edge of center cn1 toward cn2
            r1 = CENTER_EDGE[cn1]
            gx1 = x1 + ux * r1 + ox
            gy1 = y1 + uy * r1 + oy

            # Edge of center cn2 toward cn1
            r2 = CENTER_EDGE[cn2]
            gx2 = x2 - ux * r2 + ox
            gy2 = y2 - uy * r2 + oy

            raw[g1].append((gx1, gy1))
            raw[g2].append((gx2, gy2))

    # Average positions for integration-circuit gates (appear in 3 channels)
    return {
        g: (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))
        for g, pts in raw.items()
    }


GATE_POSITIONS = _build_gate_positions()

# ── Helper: triangle & diamond point strings ───────────────────────────────────
def _tri(cx, cy, size, inv=False):
    if not inv:
        return f"{cx},{cy-size*0.7} {cx-size},{cy+size*0.3} {cx+size},{cy+size*0.3}"
    return f"{cx-size},{cy-size*0.35} {cx+size},{cy-size*0.35} {cx},{cy+size*0.65}"

def _diamond(cx, cy, hw, hh):
    return f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"

# ── Center shapes ──────────────────────────────────────────────────────────────
def _center_shape(name: str, defined: bool) -> str:
    fill   = C_DEF_FILL   if defined else C_UNDEF_FILL
    stroke = C_DEF_STR    if defined else C_UNDEF_STR
    sw     = 2.5 if defined else 1.5
    tc     = C_ON_TXT if defined else C_DEF_STR
    cx, cy = CENTER_POS[name]
    s = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'

    shapes = {
        "Head":  (f'<polygon points="{_tri(cx,cy,38)}" {s}/>',
                  cx, cy+8, "HEAD", 8),
        "Ajna":  (f'<polygon points="{_tri(cx,cy,36,inv=True)}" {s}/>',
                  cx, cy+5, "AJNA", 8),
        "Throat":(f'<rect x="{cx-37}" y="{cy-15}" width="74" height="30" rx="3" {s}/>',
                  cx, cy+5, "THROAT", 8),
        "G":     (f'<polygon points="{_diamond(cx,cy,58,50)}" {s}/>',
                  cx, cy+5, "G", 9),
        "Heart": (f'<polygon points="{_tri(cx,cy,32)}" {s}/>',
                  cx, cy+8, "HEART", 7),
        "Solar Plexus": (f'<polygon points="{_tri(cx,cy,38)}" {s}/>',
                         cx, cy+9, "SOL.PL.", 6),
        "Sacral":(f'<rect x="{cx-51}" y="{cy-26}" width="102" height="52" rx="3" {s}/>',
                  cx, cy+5, "SACRAL", 8),
        "Spleen":(f'<polygon points="{_tri(cx,cy,40)}" {s}/>',
                  cx, cy+10, "SPLEEN", 7),
        "Root":  (f'<rect x="{cx-51}" y="{cy-20}" width="102" height="40" rx="3" {s}/>',
                  cx, cy+5, "ROOT", 8),
    }
    if name not in shapes:
        return ""
    shape_svg, tx, ty, lbl, fs = shapes[name]
    label = (f'<text x="{tx}" y="{ty}" text-anchor="middle" font-family="sans-serif" '
             f'font-size="{fs}" fill="{tc}" font-weight="600" letter-spacing="0.5">'
             f'{lbl}</text>')
    return shape_svg + "\n  " + label

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
        x1,y1 = CENTER_POS[pair[0]]; x2,y2 = CENTER_POS[pair[1]]
        is_def = pair in def_pairs
        col = C_CHAN_DEF if is_def else C_CHAN_UNDEF
        w   = "3.5" if is_def else "1.2"
        op  = "1"   if is_def else "0.55"
        el  = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
               f'stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
        (top if is_def else bg).append(el)
    return "\n  ".join(bg + top)

# ── All 64 gate circles ────────────────────────────────────────────────────────
def _all_gate_circles(p_gates: Set[int], d_gates: Set[int]) -> str:
    elems = []
    for gate, (gx, gy) in sorted(GATE_POSITIONS.items()):
        in_p = gate in p_gates
        in_d = gate in d_gates
        active = in_p or in_d

        if in_p and in_d:
            fill, tc, sc = C_GATE_BOTH, C_ON_TXT,  C_DEF_STR
        elif in_p:
            fill, tc, sc = C_GATE_P,    C_ON_TXT,  C_DEF_STR
        elif in_d:
            fill, tc, sc = C_GATE_D,    C_ON_TXT,  C_DEF_STR
        else:
            fill, tc, sc = C_GATE_OFF,  C_OFF_TXT, C_OFF_STR

        r  = "8.5" if active else "7.5"
        sw = "1.5" if active else "0.7"
        fw = "700" if active else "400"
        fs = "7"   if active else "6.5"

        elems.append(
            f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{r}" '
            f'fill="{fill}" stroke="{sc}" stroke-width="{sw}"/>'
            f'<text x="{gx:.1f}" y="{gy+2.5:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{fs}" fill="{tc}" '
            f'font-weight="{fw}">{gate}</text>'
        )
    return "\n  ".join(elems)

# ── Legend ─────────────────────────────────────────────────────────────────────
def _legend(height: int) -> str:
    y = height - 52
    items = [
        (C_GATE_P,    "Personalidade"),
        (C_GATE_D,    "Design"),
        (C_GATE_BOTH, "Ambos"),
    ]
    rows = []
    for i, (c, lbl) in enumerate(items):
        ry = y + i * 16
        rows.append(
            f'<circle cx="8" cy="{ry+4}" r="6" fill="{c}"/>'
            f'<text x="18" y="{ry+8}" font-family="sans-serif" font-size="8" fill="#7D5A44">{lbl}</text>'
        )
    return f'<g>{"".join(rows)}</g>'

# ── Main entry point ───────────────────────────────────────────────────────────
def generate_body_graph_svg(
    defined_centers:   Set[str],
    defined_channels:  List[Tuple[int,int]],
    personality_gates: Set[int],
    design_gates:      Set[int],
    width:  int = 420,
    height: int = 560,
) -> str:
    channels_svg = _channel_lines(defined_channels)
    centers_svg  = "\n  ".join(
        _center_shape(name, name in defined_centers)
        for name in CENTER_POS
    )
    gates_svg = _all_gate_circles(personality_gates, design_gates)
    legend    = _legend(height)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        f'  <rect width="{width}" height="{height}" fill="{C_BG}"/>\n'
        f'  {channels_svg}\n'
        f'  {centers_svg}\n'
        f'  {gates_svg}\n'
        f'  {legend}\n'
        f'</svg>'
    )

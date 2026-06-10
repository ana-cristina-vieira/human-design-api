"""
Body Graph SVG — Negócios com ALMA.
Gates near the connecting edge of each center; channels drawn gate-to-gate.
"""
from __future__ import annotations
from typing import Set, List, Tuple, Dict
from .hd_data import CHANNELS, GATE_TO_CENTER

# ── Colours ────────────────────────────────────────────────────────────────────
C_CTR_DEF    = "#B2967D"
C_CTR_UNDEF  = "#FFFFFF"
C_CTR_STR    = "#7D5A44"
C_GATE_ON    = "#4A342A"
C_GATE_OFF   = "#FFFFFF"
C_GATE_ON_T  = "#FDFAF6"
C_GATE_OFF_T = "#7D5A44"
C_GATE_STR   = "#7D5A44"
C_GATE_OSTR  = "#D4C4B0"
C_CHAN_DEF   = "#1E1612"
C_CHAN_UNDEF = "#EDE4D8"
C_BG         = "#FDFAF6"

# ── Center positions (cx, cy) ──────────────────────────────────────────────────
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

# ── Gate positions relative to their center.
# Each gate is placed near the EDGE facing the center it connects to,
# so channel lines (drawn gate-to-gate) look like real bodygraph channels.
_GATE_LAYOUT: Dict[str, List[Tuple[int, float, float]]] = {
    # HEAD — all 3 gates connect DOWN to Ajna → near bottom of triangle
    "Head": [
        (64, -18, +8), (61,  0, +8), (63, +18, +8),
    ],
    # AJNA — top 3 connect UP to Head, bottom 3 connect DOWN to Throat
    "Ajna": [
        (47, -18, -12), (24,   0, -12), ( 4, +18, -12),
        (17, -12, +22), (11,   0, +26), (43, +12, +22),
    ],
    # THROAT — gates grouped by connecting direction
    # top  → Ajna,  left → Spleen,  right → Heart/SP,  bottom → G
    "Throat": [
        (62, -20, -25), (23,   0, -25), (56, +20, -25),   # top
        (16, -27,  +8),                                    # left
        (45, +27, -12), (35, +27,  +4), (12, +27, +16),   # right
        (20, -24, +25), ( 8,  -8, +25), (31,  +8, +25), (33, +24, +25),  # bottom
    ],
    # G — top → Throat, left → Spleen (integration), right → Heart, bottom → Sacral
    "G": [
        ( 7, -20, -18), ( 1,   0, -24), (13, +20, -18),
        (10, -24,   0),
        (25, +24,   0),
        (15, -20, +18), ( 2,   0, +24), (46, +20, +18),
    ],
    # HEART — gates face Throat (upper-left), Spleen (left), G (lower-left), SP (bottom)
    "Heart": [
        (21, -14,  -8),
        (26, -14,  +4),
        (51,  -4, +10),
        (40,  +8, +10),
    ],
    # SOLAR PLEXUS — top → Heart/Throat, left → Sacral, bottom → Root
    "Solar Plexus": [
        (37,  +8, -14), (36,  -4, -16), (22, -12, -10),
        ( 6, -16,  +4),
        (49, -10, +12), (55,   0, +12), (30, +10, +12),
    ],
    # SACRAL — top → G, right → SP, left → Spleen, bottom → Root
    "Sacral": [
        (34, -24, -24), ( 5,  -8, -28), (14,  +8, -28), (29, +24, -24),
        (59, +28,   0),
        (27, -28,  -8),
        ( 9, -18, +28), ( 3,   0, +28), (42, +18, +28),
    ],
    # SPLEEN — all gates connect RIGHT (all other centers are to the right)
    # sorted top→bottom by target center height
    "Spleen": [
        (48,  +6, -24),
        (44, +18, -12),
        (57, +22,  -2),
        (50, +22,  +8),
        (32, +18, +14),
        (28, +10, +12),
        (18, +14, +10),
    ],
    # ROOT — top → Sacral, left → Spleen, right → Solar Plexus
    "Root": [
        (53, -18, -25), (60,   0, -25), (52, +18, -25),
        (58, -25, -14), (38, -25,   0), (54, -25, +14),
        (19, +25, -14), (39, +25,   0), (41, +25, +14),
    ],
}

# Absolute gate positions built once at import time
_GATE_POS: Dict[int, Tuple[float, float]] = {}
for _cname, _gates in _GATE_LAYOUT.items():
    _cx, _cy = CENTER_POS[_cname]
    for _g, _rx, _ry in _gates:
        _GATE_POS[_g] = (_cx + _rx, _cy + _ry)


# ── Rounded triangle path ──────────────────────────────────────────────────────
def _rtri_path(verts: List[Tuple[float,float]], r: float = 12) -> str:
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
        sz = 68
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
        sz = 74
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    elif name == "Spleen":
        path = _rtri_path(_tri_verts(cx, cy, 38, 34), r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Root":
        sz = 68
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    return ""


# ── Gates as circles inside centers ───────────────────────────────────────────
def _center_gates(name: str, p_gates: Set[int], d_gates: Set[int]) -> str:
    cx, cy = CENTER_POS[name]
    elems = []
    for gate, rx, ry in _GATE_LAYOUT.get(name, []):
        gx, gy = cx + rx, cy + ry
        active = gate in p_gates or gate in d_gates
        fill   = C_GATE_ON   if active else C_GATE_OFF
        tc     = C_GATE_ON_T if active else C_GATE_OFF_T
        sc     = C_GATE_STR  if active else C_GATE_OSTR
        sw     = "1.5" if active else "0.8"
        fw     = "700" if active else "400"
        r      = "8"
        fs     = "6.5"
        elems.append(
            f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{r}" '
            f'fill="{fill}" stroke="{sc}" stroke-width="{sw}"/>'
            f'<text x="{gx:.1f}" y="{gy+2.5:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{fs}" fill="{tc}" '
            f'font-weight="{fw}">{gate}</text>'
        )
    return "\n  ".join(elems)


# ── Channel lines — drawn gate-to-gate ────────────────────────────────────────
def _channel_lines(defined_channels: List[Tuple[int,int]]) -> str:
    def_pairs: Set[Tuple[int,int]] = set()
    for g1, g2 in defined_channels:
        def_pairs.add((min(g1,g2), max(g1,g2)))

    bg, top = [], []
    for g1, g2 in CHANNELS:
        key = (min(g1,g2), max(g1,g2))
        x1, y1 = _GATE_POS[g1]
        x2, y2 = _GATE_POS[g2]
        is_def = key in def_pairs
        col = C_CHAN_DEF   if is_def else C_CHAN_UNDEF
        w   = "10"         if is_def else "2"
        op  = "1"          if is_def else "0.5"
        el  = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
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

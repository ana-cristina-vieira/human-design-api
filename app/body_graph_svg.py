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
    "Solar Plexus": (328, 360),
    "Sacral":       (220, 398),
    "Spleen":       ( 90, 360),
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
        (17, -12, +22), (43,   0, +26), (11, +12, +22),
    ],
    # THROAT — gates grouped by connecting direction
    # top  → Ajna,  left → Spleen/G,  right → SP/Heart,  bottom → G
    "Throat": [
        (62, -20, -25), (23,   0, -25), (56, +20, -25),   # top (topo → Ajna)
        (16, -27,  -6), (20, -27, +10),                   # left (esquerda → Baço/G)
        (35, +27, -12), (12, +27,  +4), (45, +27, +16),   # right (direita → PS/Ego)
        (31, -20, +25), ( 8,   0, +25), (33, +20, +25),   # bottom (base → G)
    ],
    # G — vértices: 1(topo), 10(esq), 25(dir), 2(base); diagonais: 7,13,15,46
    "G": [
        ( 1,   0, -46),  # vértice topo → Throat (1-8)
        ( 7, -24, -20),  # diagonal sup-esq → Throat (7-31)
        (13, +24, -20),  # diagonal sup-dir → Throat (13-33)
        (10, -58,   0),  # vértice esquerdo → Throat (10-20)
        (25, +58,   0),  # vértice direito → Heart (25-51)
        (15, -24, +20),  # diagonal inf-esq → Sacral (5-15)
        ( 2,   0, +46),  # vértice base → Sacral (2-14)
        (46, +24, +20),  # diagonal inf-dir → Sacral (29-46)
    ],
    # HEART — gates face Throat (upper-left), Spleen (left), G (lower-left), SP (bottom)
    # Larger triangle (hw=36,hh=32) gives room to spread 4 gates
    "Heart": [
        (21, -10, -16),   # upper → Throat (21-45)
        (26, -20,  +2),   # left  → Spleen (26-44)
        (51,  -6, +14),   # lower-left → G (25-51)
        (40, +14, +14),   # lower-right → Solar Plexus (37-40)
    ],
    # SOLAR PLEXUS — left-pointing triangle: 3 gates on upper diagonal, 1 at left tip, 3 on lower diagonal
    "Solar Plexus": [
        # Upper diagonal (upper-right base → left tip): connects to Throat/Heart above-left
        (36,  +8, -27),  # near base → Throat 35
        (22,  -7, -17),  # mid → Throat 12
        (37, -22,  -7),  # near tip → Heart 40
        # Left tip → Sacral (directly left)
        ( 6, -36,   0),  # tip → Sacral 59
        # Lower diagonal (left tip → lower-right base): connects to Root below-left
        (49, -22,  +7),  # near tip → Root 19
        (55,  -7, +17),  # mid → Root 39
        (30,  +8, +27),  # near base → Root 41
    ],
    # SACRAL — top (5,14,29) | right (59) | left top→bot (34,27) | bottom (42,3,9)
    "Sacral": [
        # Top row (left → right): connects to G bottom
        ( 5, -18, -28),  # → G 15
        (14,   0, -28),  # → G 2
        (29, +18, -28),  # → G 46
        # Right: connects to Solar Plexus
        (59, +28,   0),
        # Left (top → bottom): integration circuit + Spleen
        (34, -28, -12),  # → Throat 20 / Spleen 57
        (27, -28, +10),  # → Spleen 50
        # Bottom row (left → right): connects to Root top
        (42, -18, +28),  # → Root 53
        ( 3,   0, +28),  # → Root 60
        ( 9, +18, +28),  # → Root 52
    ],
    # SPLEEN — right-pointing triangle: 3 gates on upper diagonal, 1 at tip, 3 on lower diagonal
    "Spleen": [
        # Upper diagonal (upper-left → right tip): connects to Throat/G/Heart above-right
        (48,  -8, -27),  # top  → Throat 16
        (57,  +7, -17),  # mid  → Throat 20 / G 10
        (44, +22,  -7),  # near tip → Heart 26
        # Right tip → Sacral
        (50, +36,   0),
        # Lower diagonal (right tip → lower-left): connects to Root below-right
        (32, +22,  +7),  # near tip → Root 54
        (28,  +7, +17),  # mid  → Root 38
        (18,  -8, +27),  # bottom → Root 58
    ],
    # ROOT — top: 53,60,52 | left (top→bottom): 54,38,58 | right (top→bottom): 19,39,41
    "Root": [
        (53, -18, -25), (60,   0, -25), (52, +18, -25),
        (54, -25, -14), (38, -25,   0), (58, -25, +14),
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
        path = _rtri_path(_tri_verts(cx, cy, 36, 32), r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Solar Plexus":
        # Left-pointing triangle: vertical base on right, tip pointing left
        verts = [(cx+24, cy-40), (cx+24, cy+40), (cx-38, cy)]
        path = _rtri_path(verts, r=10)
        return f'<path d="{path}" {s}/>'
    elif name == "Sacral":
        sz = 74
        return f'<rect x="{cx-sz/2}" y="{cy-sz/2}" width="{sz}" height="{sz}" rx="6" {s}/>'
    elif name == "Spleen":
        # Right-pointing triangle: vertical base on left, tip pointing right
        verts = [(cx-24, cy-40), (cx-24, cy+40), (cx+38, cy)]
        path = _rtri_path(verts, r=10)
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
def _channel_lines(defined_channels: List[Tuple[int,int]],
                   active_gates: Set[int]) -> str:
    def_pairs: Set[Tuple[int,int]] = set()
    for g1, g2 in defined_channels:
        def_pairs.add((min(g1,g2), max(g1,g2)))

    def line(x1, y1, x2, y2, col, w, op):
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')

    bg, mid, top = [], [], []
    for g1, g2 in CHANNELS:
        key = (min(g1,g2), max(g1,g2))
        x1, y1 = _GATE_POS[g1]
        x2, y2 = _GATE_POS[g2]
        mx, my = (x1+x2)/2, (y1+y2)/2
        is_def  = key in def_pairs
        g1_on   = g1 in active_gates
        g2_on   = g2 in active_gates

        if is_def:
            top.append(line(x1, y1, x2, y2, C_CHAN_DEF, "10", "1"))
        elif g1_on or g2_on:
            # Undeclared background
            bg.append(line(x1, y1, x2, y2, C_CHAN_UNDEF, "2", "0.5"))
            # Half-channel stub from active gate to midpoint
            if g1_on:
                mid.append(line(x1, y1, mx, my, C_CHAN_DEF, "6", "0.75"))
            if g2_on:
                mid.append(line(mx, my, x2, y2, C_CHAN_DEF, "6", "0.75"))
        else:
            bg.append(line(x1, y1, x2, y2, C_CHAN_UNDEF, "2", "0.5"))

    return "\n  ".join(bg + mid + top)


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
    active_gates = personality_gates | design_gates
    channels = _channel_lines(defined_channels, active_gates)
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

"""
Body Graph SVG generator — Negócios com ALMA.
Shows ALL 64 gates (activated = filled, inactive = outline).
Brand palette: cremes, terracota, espresso.
"""

from __future__ import annotations
from typing import Set, List, Tuple, Dict
from collections import defaultdict
from .hd_data import CENTERS, CHANNELS, GATE_TO_CENTER

# ── Brand colours ─────────────────────────────────────────────────────────────
C_DEF_FILL    = "#B2967D"   # Terracota — defined center fill
C_DEF_STROKE  = "#7D5A44"   # Castanho Médio
C_UNDEF_FILL  = "#F5F1EA"   # Creme Suave — undefined center
C_UNDEF_STR   = "#D4C4B0"   # Bege Cálido
C_CHAN_DEF    = "#7D5A44"   # defined channel line
C_CHAN_UNDEF  = "#EDE4D8"   # inactive channel line

C_GATE_P      = "#B2967D"   # Personality gate (conscious)
C_GATE_D      = "#7D5A44"   # Design gate (unconscious)
C_GATE_BOTH   = "#4A342A"   # Both
C_GATE_OFF    = "#F5F1EA"   # inactive gate fill
C_GATE_OFF_TX = "#B2967D"   # inactive gate text
C_GATE_ON_TX  = "#FDFAF6"   # active gate text
C_BG          = "#FDFAF6"

# ── Center visual positions ────────────────────────────────────────────────────
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

# ── Gate positions (computed from channel layout) ──────────────────────────────
def _build_gate_positions() -> Dict[int, Tuple[float, float]]:
    """
    Place each gate ~25% along the channel line from its center.
    For multiple channels between the same pair of centers, spread
    the gates perpendicularly to avoid overlap.
    """
    # Group channels by center pair
    pair_chans: Dict[Tuple[str,str], List[Tuple[int,int]]] = defaultdict(list)
    for g1, g2 in CHANNELS:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        key = (min(c1,c2), max(c1,c2))
        pair_chans[key].append((g1, g2))

    raw: Dict[int, List[Tuple[float,float]]] = defaultdict(list)

    FRAC   = 0.24   # how far along the line to place each gate
    SPREAD = 9      # px between parallel channels

    for (cn1, cn2), chans in pair_chans.items():
        x1, y1 = CENTER_POS[cn1]
        x2, y2 = CENTER_POS[cn2]
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2) ** 0.5
        # perpendicular unit vector
        px, py = (-dy / length, dx / length) if length else (1, 0)

        n = len(chans)
        for i, (g1, g2) in enumerate(chans):
            offset = (i - (n - 1) / 2) * SPREAD
            ox, oy = offset * px, offset * py
            # gate g1 near center cn1, gate g2 near center cn2
            raw[g1].append((x1 + FRAC*(x2-x1) + ox, y1 + FRAC*(y2-y1) + oy))
            raw[g2].append((x2 + FRAC*(x1-x2) + ox, y2 + FRAC*(y1-y2) + oy))

    return {
        g: (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))
        for g, pts in raw.items()
    }


GATE_POSITIONS = _build_gate_positions()

# ── Center shapes ─────────────────────────────────────────────────────────────
def _tri(cx, cy, size, inv=False):
    if not inv:
        return f"{cx},{cy-size*0.7} {cx-size},{cy+size*0.3} {cx+size},{cy+size*0.3}"
    return f"{cx-size},{cy-size*0.3} {cx+size},{cy-size*0.3} {cx},{cy+size*0.7}"

def _diamond(cx, cy, hw, hh):
    return f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"

def _center_shape(name: str, defined: bool) -> str:
    fill   = C_DEF_FILL   if defined else C_UNDEF_FILL
    stroke = C_DEF_STROKE if defined else C_UNDEF_STR
    sw     = 2.5 if defined else 1.5
    tc     = C_GATE_ON_TX if defined else C_DEF_STROKE
    lbl    = name if name != "Solar Plexus" else "SOL.PLEX."
    cx, cy = CENTER_POS[name]
    s = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'

    if name == "Head":
        return (f'<polygon points="{_tri(cx,cy,36)}" {s}/>'
                f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="8" fill="{tc}" font-weight="600" letter-spacing="0.5">HEAD</text>')
    elif name == "Ajna":
        return (f'<polygon points="{_tri(cx,cy,34,inv=True)}" {s}/>'
                f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="8" fill="{tc}" font-weight="600" letter-spacing="0.5">AJNA</text>')
    elif name in ("Throat", "Sacral", "Root"):
        w, h = (74,30) if name=="Throat" else (102,52) if name=="Sacral" else (102,40)
        x,y = cx-w/2, cy-h/2
        lbl_y = cy+5
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" {s}/>'
                f'<text x="{cx}" y="{lbl_y}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="8" fill="{tc}" font-weight="600" letter-spacing="0.5">'
                f'{name.upper()}</text>')
    elif name == "G":
        return (f'<polygon points="{_diamond(cx,cy,60,52)}" {s}/>'
                f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="8" fill="{tc}" font-weight="600">G</text>')
    elif name == "Heart":
        return (f'<polygon points="{_tri(cx,cy,32)}" {s}/>'
                f'<text x="{cx}" y="{cy+8}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="7" fill="{tc}" font-weight="600">HEART</text>')
    elif name == "Solar Plexus":
        return (f'<polygon points="{_tri(cx,cy,36)}" {s}/>'
                f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="6" fill="{tc}" font-weight="600">SOL.PLEX.</text>')
    elif name == "Spleen":
        return (f'<polygon points="{_tri(cx,cy,38)}" {s}/>'
                f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-family="sans-serif" '
                f'font-size="7" fill="{tc}" font-weight="600">SPLEEN</text>')
    return ""

# ── Channel lines ─────────────────────────────────────────────────────────────
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
        col  = C_CHAN_DEF  if is_def else C_CHAN_UNDEF
        w    = "3" if is_def else "1.2"
        op   = "1" if is_def else "0.6"
        el   = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
        (top if is_def else bg).append(el)
    return "\n  ".join(bg + top)

# ── Gate circles (ALL 64) ─────────────────────────────────────────────────────
def _all_gate_circles(p_gates: Set[int], d_gates: Set[int]) -> str:
    elements = []
    for gate, (gx, gy) in sorted(GATE_POSITIONS.items()):
        in_p = gate in p_gates
        in_d = gate in d_gates
        active = in_p or in_d

        if in_p and in_d:
            fill, tc, sc = C_GATE_BOTH, C_GATE_ON_TX, C_DEF_STROKE
        elif in_p:
            fill, tc, sc = C_GATE_P, C_GATE_ON_TX, C_DEF_STROKE
        elif in_d:
            fill, tc, sc = C_GATE_D, C_GATE_ON_TX, C_DEF_STROKE
        else:
            fill, tc, sc = C_GATE_OFF, C_GATE_OFF_TX, C_UNDEF_STR

        r   = "8"   if active else "7"
        sw  = "1.2" if active else "0.7"
        fw  = "700" if active else "500"
        fs  = "7"   if active else "6.5"

        elements.append(
            f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{r}" '
            f'fill="{fill}" stroke="{sc}" stroke-width="{sw}"/>'
            f'<text x="{gx:.1f}" y="{gy+2.5:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="{fs}" fill="{tc}" '
            f'font-weight="{fw}">{gate}</text>'
        )
    return "\n  ".join(elements)

# ── Legend ────────────────────────────────────────────────────────────────────
def _legend(height: int) -> str:
    y = height - 52
    return f"""
  <g transform="translate(8,{y})">
    <circle cx="8" cy="8" r="6" fill="{C_GATE_P}"/>
    <text x="18" y="12" font-family="sans-serif" font-size="8" fill="#7D5A44">Personalidade</text>
    <circle cx="8" cy="24" r="6" fill="{C_GATE_D}"/>
    <text x="18" y="28" font-family="sans-serif" font-size="8" fill="#7D5A44">Design</text>
    <circle cx="8" cy="40" r="6" fill="{C_GATE_BOTH}"/>
    <text x="18" y="44" font-family="sans-serif" font-size="8" fill="#7D5A44">Ambos</text>
  </g>"""

# ── Main entry point ──────────────────────────────────────────────────────────
def generate_body_graph_svg(
    defined_centers:   Set[str],
    defined_channels:  List[Tuple[int,int]],
    personality_gates: Set[int],
    design_gates:      Set[int],
    width: int = 420,
    height: int = 560,
) -> str:
    channels_svg = _channel_lines(defined_channels)
    centers_svg  = "\n  ".join(
        _center_shape(name, name in defined_centers)
        for name in CENTER_POS
    )
    gates_svg = _all_gate_circles(personality_gates, design_gates)
    legend    = _legend(height)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
            f'  <rect width="{width}" height="{height}" fill="{C_BG}"/>\n'
            f'  <!-- Channel lines -->\n  {channels_svg}\n'
            f'  <!-- Centers -->\n  {centers_svg}\n'
            f'  <!-- All 64 gates -->\n  {gates_svg}\n'
            f'  {legend}\n'
            f'</svg>')

"""
Human Design calculation engine using Swiss Ephemeris (Moshier mode — no external files needed).
"""

from __future__ import annotations
import swisseph as swe
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Any

# The HD gate wheel starts at 3.5° tropical Aries (not 0°).
# Verified empirically: gives Profile 1/3 for Jun 14 1983 Portimão and
# Profile 5/1 for May 8 1982 Santarém (reference chart).
GATE_OFFSET = -1.75  # degrees; verified against 3 charts (PT, MZ, PT-PM)

from .hd_data import (
    GATE_SEQUENCE, DEGREES_PER_GATE, DEGREES_PER_LINE,
    CHANNELS, CENTERS, GATE_TO_CENTER, CHANNEL_TO_CENTERS,
    PLANET_ORDER, TYPE_META, CROSS_TYPE_BY_PROFILE, AUTHORITY_ORDER,
)

# Use Moshier analytical ephemeris (no external files, accurate within ~1 arcsec)
_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED


@dataclass
class PlanetPosition:
    key: str
    name: str
    symbol: str
    gate: int
    line: int
    longitude: float


@dataclass
class ChartResult:
    name: str
    birth_dt_utc: datetime
    birth_place: str
    design_dt_utc: datetime

    personality: List[PlanetPosition]
    design: List[PlanetPosition]

    all_personality_gates: Set[int]
    all_design_gates: Set[int]
    all_active_gates: Set[int]

    defined_channels: List[Tuple[int, int]]
    defined_centers: Set[str]

    hd_type: str
    strategy: str
    authority: str
    signature: str
    not_self_theme: str
    profile: str
    definition: str
    incarnation_cross: str

    connected_components: List[Set[str]]


# ---------------------------------------------------------------------------
# Core conversion helpers
# ---------------------------------------------------------------------------

def degree_to_gate_line(longitude: float) -> Tuple[int, int]:
    """Return (gate, line) for a tropical ecliptic longitude (0–360°)."""
    lon = (longitude - GATE_OFFSET) % 360
    index = int(lon / DEGREES_PER_GATE)
    gate = GATE_SEQUENCE[index]
    position_in_gate = lon - index * DEGREES_PER_GATE
    line = int(position_in_gate / DEGREES_PER_LINE) + 1
    line = min(line, 6)
    return gate, line


def _calc_planet(jd: float, planet_id: int) -> float:
    """Return tropical longitude for a planet at Julian Day jd."""
    result = swe.calc_ut(jd, planet_id, _FLAGS)
    # pyswisseph returns (xx_tuple, retflags) in recent versions
    if isinstance(result[0], (list, tuple)):
        return result[0][0]
    return result[0]


def get_planet_positions(jd: float) -> Dict[str, float]:
    """Return {key: longitude} for all 11 computed bodies + Earth + South Node."""
    raw = {
        "sun":        _calc_planet(jd, swe.SUN),
        "moon":       _calc_planet(jd, swe.MOON),
        "mercury":    _calc_planet(jd, swe.MERCURY),
        "venus":      _calc_planet(jd, swe.VENUS),
        "mars":       _calc_planet(jd, swe.MARS),
        "jupiter":    _calc_planet(jd, swe.JUPITER),
        "saturn":     _calc_planet(jd, swe.SATURN),
        "uranus":     _calc_planet(jd, swe.URANUS),
        "neptune":    _calc_planet(jd, swe.NEPTUNE),
        "pluto":      _calc_planet(jd, swe.PLUTO),
        "north_node": _calc_planet(jd, swe.TRUE_NODE),
    }
    raw["earth"]      = (raw["sun"]        + 180) % 360
    raw["south_node"] = (raw["north_node"] + 180) % 360
    return raw


def find_design_jd(birth_jd: float, birth_sun_lon: float) -> float:
    """Find the Julian Day when the sun was exactly 88° before birth sun position."""
    target = (birth_sun_lon - 88.0) % 360

    # Initial estimate (~88 days back)
    jd = birth_jd - 88.0

    for _ in range(20):
        result = swe.calc_ut(jd, swe.SUN, _FLAGS)
        xx = result[0] if isinstance(result[0], (list, tuple)) else result
        current = xx[0] % 360
        speed   = xx[3] if len(xx) > 3 else 1.0

        diff = (target - current + 180) % 360 - 180
        if abs(diff) < 0.00001:
            break
        jd += diff / speed

    return jd


# ---------------------------------------------------------------------------
# Body graph logic
# ---------------------------------------------------------------------------

def _build_positions(longitudes: Dict[str, float]) -> List[PlanetPosition]:
    positions = []
    for key, name, symbol in PLANET_ORDER:
        lon = longitudes[key]
        gate, line = degree_to_gate_line(lon)
        positions.append(PlanetPosition(key=key, name=name, symbol=symbol,
                                        gate=gate, line=line, longitude=lon))
    return positions


def _find_defined_channels(active_gates: Set[int]) -> List[Tuple[int, int]]:
    return [(g1, g2) for g1, g2 in CHANNELS
            if g1 in active_gates and g2 in active_gates]


def _find_defined_centers(defined_channels: List[Tuple[int, int]]) -> Set[str]:
    centers: Set[str] = set()
    for g1, g2 in defined_channels:
        centers.add(GATE_TO_CENTER[g1])
        centers.add(GATE_TO_CENTER[g2])
    return centers


def _connected_components(
    defined_centers: Set[str],
    defined_channels: List[Tuple[int, int]]
) -> List[Set[str]]:
    """Find groups of centers connected by defined channels."""
    adjacency: Dict[str, Set[str]] = {c: set() for c in defined_centers}
    for g1, g2 in defined_channels:
        c1, c2 = GATE_TO_CENTER[g1], GATE_TO_CENTER[g2]
        if c1 in adjacency and c2 in adjacency:
            adjacency[c1].add(c2)
            adjacency[c2].add(c1)

    visited: Set[str] = set()
    components: List[Set[str]] = []

    def bfs(start: str) -> Set[str]:
        group: Set[str] = set()
        queue = [start]
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            group.add(node)
            queue.extend(adjacency[node] - visited)
        return group

    for center in defined_centers:
        if center not in visited:
            components.append(bfs(center))

    return components


def _is_motor_connected_to_throat(
    defined_centers: Set[str],
    components: List[Set[str]],
) -> Tuple[bool, bool]:
    """Return (sacral_to_throat, other_motor_to_throat)."""
    throat_component: Set[str] = set()
    for comp in components:
        if "Throat" in comp:
            throat_component = comp
            break

    sacral_connected   = "Sacral" in throat_component
    other_motor_connected = any(
        c in throat_component for c in ("Heart", "Solar Plexus", "Root")
    )
    return sacral_connected, other_motor_connected


def _determine_type(
    defined_centers: Set[str],
    components: List[Set[str]],
) -> str:
    if not defined_centers:
        return "Reflector"

    sacral_defined = "Sacral" in defined_centers
    sacral_to_throat, other_motor_to_throat = _is_motor_connected_to_throat(
        defined_centers, components
    )

    if sacral_defined and (sacral_to_throat or other_motor_to_throat):
        return "Manifesting Generator"
    if sacral_defined:
        return "Generator"
    if other_motor_to_throat:
        return "Manifestor"
    return "Projector"


def _determine_authority(defined_centers: Set[str]) -> str:
    for center, label in AUTHORITY_ORDER:
        if center in defined_centers:
            return label
    return "None (Mental)"


def _definition_label(n: int) -> str:
    return {1: "Single Definition", 2: "Split Definition",
            3: "Triple Split", 4: "Quadruple Split"}.get(n, f"{n}-way Split")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_chart(
    name: str,
    birth_dt_utc: datetime,
    birth_place: str,
) -> ChartResult:
    """Full Human Design chart calculation from a UTC datetime."""
    swe.set_ephe_path("")  # force Moshier mode

    jd_birth = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0
    )

    # Personality positions (at birth)
    pers_lons = get_planet_positions(jd_birth)
    personality = _build_positions(pers_lons)

    # Design date: sun was 88° behind birth sun
    jd_design = find_design_jd(jd_birth, pers_lons["sun"])
    design_lons = get_planet_positions(jd_design)
    design = _build_positions(design_lons)

    # Design datetime (UTC) from Julian Day
    year, month, day, hour_frac = swe.revjul(jd_design)
    h = int(hour_frac)
    m = int((hour_frac - h) * 60)
    s = int(((hour_frac - h) * 60 - m) * 60)
    design_dt_utc = datetime(year, month, day, h, m, s, tzinfo=timezone.utc)

    # Active gates
    p_gates = {pos.gate for pos in personality}
    d_gates = {pos.gate for pos in design}
    all_gates = p_gates | d_gates

    # Body graph
    defined_channels = _find_defined_channels(all_gates)
    defined_centers  = _find_defined_centers(defined_channels)
    components       = _connected_components(defined_centers, defined_channels)

    hd_type   = _determine_type(defined_centers, components)
    authority = _determine_authority(defined_centers)

    meta = TYPE_META.get(hd_type, {})

    # Profile: Personality Sun line / Design Sun line
    p_sun_line = next(p.line for p in personality if p.key == "sun")
    d_sun_line = next(p.line for p in design      if p.key == "sun")
    profile = f"{p_sun_line}/{d_sun_line}"

    # Incarnation Cross
    p_sun_gate   = next(p.gate for p in personality if p.key == "sun")
    p_earth_gate = next(p.gate for p in personality if p.key == "earth")
    d_sun_gate   = next(p.gate for p in design      if p.key == "sun")
    d_earth_gate = next(p.gate for p in design      if p.key == "earth")
    cross_type   = CROSS_TYPE_BY_PROFILE.get(profile, "Cross")
    incarnation_cross = (
        f"{cross_type} ({p_sun_gate}/{p_earth_gate} | {d_sun_gate}/{d_earth_gate})"
    )

    definition = _definition_label(len(components)) if components else "No Definition"

    return ChartResult(
        name=name,
        birth_dt_utc=birth_dt_utc,
        birth_place=birth_place,
        design_dt_utc=design_dt_utc,
        personality=personality,
        design=design,
        all_personality_gates=p_gates,
        all_design_gates=d_gates,
        all_active_gates=all_gates,
        defined_channels=defined_channels,
        defined_centers=defined_centers,
        hd_type=hd_type,
        strategy=meta.get("strategy", ""),
        authority=authority,
        signature=meta.get("signature", ""),
        not_self_theme=meta.get("not_self_theme", ""),
        profile=profile,
        definition=definition,
        incarnation_cross=incarnation_cross,
        connected_components=components,
    )

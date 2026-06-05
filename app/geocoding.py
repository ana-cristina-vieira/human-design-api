"""
City name → (lat, lon, timezone_str, display_name) using Nominatim + timezonefinder.
"""

from __future__ import annotations
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime

_geolocator = Nominatim(user_agent="negocioscomalma-human-design-v1", timeout=10)
_tf = TimezoneFinder()


def geocode(place: str) -> tuple[float, float, str, str]:
    """Return (lat, lon, timezone_str, display_name). Raises ValueError if not found."""
    location = _geolocator.geocode(place)
    if not location:
        raise ValueError(f"Local não encontrado: '{place}'. Tenta com o país incluído (ex: 'Lisboa, Portugal').")

    lat = location.latitude
    lon = location.longitude
    tz_str = _tf.timezone_at(lat=lat, lng=lon)
    if not tz_str:
        tz_str = "UTC"

    return lat, lon, tz_str, location.address


def local_to_utc(year: int, month: int, day: int,
                 hour: int, minute: int, tz_str: str) -> datetime:
    """Convert local datetime to UTC-aware datetime."""
    tz = pytz.timezone(tz_str)
    local_dt = tz.localize(datetime(year, month, day, hour, minute))
    return local_dt.astimezone(pytz.UTC)

"""
FastAPI application — Human Design Chart Generator
Negócios com ALMA © Ana Vieira
"""

from __future__ import annotations
import os
import httpx
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from .geocoding import geocode, local_to_utc
from .calculation import calculate_chart, ChartResult
from .body_graph_svg import generate_body_graph_svg

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Human Design API — Negócios com ALMA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")  # set in .env


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChartRequest(BaseModel):
    name:        str = Field(..., min_length=1,  example="Maria Silva")
    email:       str = Field(..., example="maria@email.com")
    birth_year:  int = Field(..., ge=1900, le=2025, example=1990)
    birth_month: int = Field(..., ge=1,   le=12,   example=5)
    birth_day:   int = Field(..., ge=1,   le=31,   example=8)
    birth_hour:  int = Field(..., ge=0,   le=23,   example=14)
    birth_minute:int = Field(..., ge=0,   le=59,   example=30)
    birth_place: str = Field(..., min_length=2,  example="Lisboa, Portugal")


class PlanetData(BaseModel):
    key: str
    name: str
    symbol: str
    gate: int
    line: int


class ChartResponse(BaseModel):
    name:             str
    email:            str
    birth_place:      str
    birth_date_label: str
    design_date_label:str

    hd_type:          str
    strategy:         str
    authority:        str
    profile:          str
    definition:       str
    incarnation_cross:str
    signature:        str
    not_self_theme:   str

    personality:      list[PlanetData]
    design:           list[PlanetData]

    defined_channels: list[str]    # e.g. ["17-62", "34-57"]
    active_gates:     list[int]    # sorted list of all active gates

    body_graph_svg:   str          # inline SVG string


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_dt(dt: datetime) -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    suffix = {1:"st", 2:"nd", 3:"rd"}.get(dt.day % 10
              if dt.day not in (11, 12, 13) else 0, "th")
    return (f"{dt.day}{suffix} {months[dt.month-1]} {dt.year} "
            f"@ {dt.hour:02d}:{dt.minute:02d}")

def _fmt_local(year: int, month: int, day: int, hour: int, minute: int) -> str:
    """Format birth time using the user's LOCAL input (not UTC)."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    suffix = {1:"st", 2:"nd", 3:"rd"}.get(day % 10
              if day not in (11, 12, 13) else 0, "th")
    return f"{day}{suffix} {months[month-1]} {year} @ {hour:02d}:{minute:02d}"


async def _send_to_n8n(payload: dict) -> None:
    """Fire-and-forget webhook to n8n."""
    if not N8N_WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(N8N_WEBHOOK_URL, json=payload)
    except Exception:
        pass  # non-blocking — never fail the response because of this


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    html_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "human-design-api"}


@app.post("/calculate", response_model=ChartResponse)
async def calculate(req: ChartRequest):
    # 1. Geocode birth location
    try:
        lat, lon, tz_str, place_display = geocode(req.birth_place)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Convert to UTC
    try:
        birth_utc = local_to_utc(
            req.birth_year, req.birth_month, req.birth_day,
            req.birth_hour, req.birth_minute, tz_str
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data/hora inválida: {e}")

    # 3. Calculate chart
    try:
        chart: ChartResult = calculate_chart(req.name, birth_utc, req.birth_place)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no cálculo: {e}")

    # 4. Generate SVG
    svg = generate_body_graph_svg(
        defined_centers=chart.defined_centers,
        defined_channels=chart.defined_channels,
        personality_gates=chart.all_personality_gates,
        design_gates=chart.all_design_gates,
    )

    # 5. Send lead to n8n (async, non-blocking)
    import asyncio
    asyncio.create_task(_send_to_n8n({
        "name":         req.name,
        "email":        req.email,
        "birth_place":  req.birth_place,
        "birth_date":   f"{req.birth_year}-{req.birth_month:02d}-{req.birth_day:02d}",
        "hd_type":      chart.hd_type,
        "profile":      chart.profile,
        "authority":    chart.authority,
        "source":       "human-design-gratuito",
    }))

    # 6. Build response
    return ChartResponse(
        name=req.name,
        email=req.email,
        birth_place=place_display,
        birth_date_label=_fmt_local(req.birth_year, req.birth_month, req.birth_day,
                                    req.birth_hour, req.birth_minute),
        design_date_label=_fmt_dt(chart.design_dt_utc),

        hd_type=chart.hd_type,
        strategy=chart.strategy,
        authority=chart.authority,
        profile=chart.profile,
        definition=chart.definition,
        incarnation_cross=chart.incarnation_cross,
        signature=chart.signature,
        not_self_theme=chart.not_self_theme,

        personality=[PlanetData(key=p.key, name=p.name, symbol=p.symbol,
                                gate=p.gate, line=p.line)
                     for p in chart.personality],
        design=[PlanetData(key=p.key, name=p.name, symbol=p.symbol,
                           gate=p.gate, line=p.line)
                for p in chart.design],

        defined_channels=[f"{g1}-{g2}" for g1, g2 in sorted(chart.defined_channels)],
        active_gates=sorted(chart.all_active_gates),
        body_graph_svg=svg,
    )

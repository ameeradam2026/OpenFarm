"""NASA POWER daily point service. Results are reported in API-native units."""
from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import requests

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = ["PRECTOTCORR", "T2M_MAX", "T2M_MIN", "T2M", "RH2M", "WS10M", "ALLSKY_SFC_SW_DWN"]
UNITS = {
    "PRECTOTCORR": "mm/day", "T2M_MAX": "°C", "T2M_MIN": "°C", "T2M": "°C",
    "RH2M": "%", "WS10M": "m/s", "ALLSKY_SFC_SW_DWN": "kWh/m²/day",
}


def fetch_daily(lat: float, lon: float, start: date, end: date, timeout: int = 30) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fetch daily Agroclimatology observations and validate missing/sentinel values."""
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Latitude/longitude are outside valid ranges")
    if end < start:
        raise ValueError("End date precedes start date")
    params = {
        "parameters": ",".join(PARAMETERS), "community": "AG", "longitude": lon,
        "latitude": lat, "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    response = requests.get(POWER_URL, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    properties = payload.get("properties", {})
    raw = properties.get("parameter", {})
    if not raw:
        raise ValueError("NASA POWER response contains no parameter observations")
    frame = pd.DataFrame(raw)
    frame.index = pd.to_datetime(frame.index, format="%Y%m%d", errors="coerce")
    frame.index.name = "date"
    frame = frame.apply(pd.to_numeric, errors="coerce").replace([-999, -999.0], float("nan"))
    frame = frame.sort_index().dropna(how="all")
    metadata = {
        "source": "NASA POWER Daily API, Agroclimatology (AG)", "url": response.url,
        "retrieved_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "requested_start": start.isoformat(), "requested_end": end.isoformat(),
        "units": UNITS, "missing_values": {c: int(frame[c].isna().sum()) for c in frame.columns},
        "api_metadata": properties.get("parameter_information", {}),
    }
    return frame, metadata

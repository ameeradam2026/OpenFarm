"""Reproducible calculations from NASA POWER daily data; never imputes missing values."""
from __future__ import annotations
import pandas as pd


def summarize(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"monthly": pd.DataFrame(), "annual_precip_mm": None, "mean_temp_c": None,
                "max_temp_c": None, "heat_days_35c": None, "consecutive_dry_days": None}
    data = frame.copy().sort_index()
    monthly = pd.DataFrame(index=data.resample("MS").size().index)
    if "PRECTOTCORR" in data:
        monthly["precip_mm"] = data["PRECTOTCORR"].resample("MS").sum(min_count=1)
    if "T2M" in data:
        monthly["mean_temp_c"] = data["T2M"].resample("MS").mean()
    if "T2M_MAX" in data:
        monthly["max_temp_c"] = data["T2M_MAX"].resample("MS").max()
    dry_streak = max_streak = streak = 0
    if "PRECTOTCORR" in data:
        for value in data["PRECTOTCORR"].dropna():
            streak = streak + 1 if value < 1.0 else 0
            max_streak = max(max_streak, streak)
    result = {
        "monthly": monthly,
        "annual_precip_mm": float(data["PRECTOTCORR"].sum(min_count=1)) if "PRECTOTCORR" in data else None,
        "mean_temp_c": float(data["T2M"].mean()) if "T2M" in data else None,
        "max_temp_c": float(data["T2M_MAX"].max()) if "T2M_MAX" in data else None,
        "heat_days_35c": int((data["T2M_MAX"] >= 35).sum()) if "T2M_MAX" in data else None,
        "consecutive_dry_days": max_streak if "PRECTOTCORR" in data else None,
        "heavy_rain_days_20mm": int((data["PRECTOTCORR"] >= 20).sum()) if "PRECTOTCORR" in data else None,
        "period_start": data.index.min().date().isoformat(), "period_end": data.index.max().date().isoformat(),
    }
    return result

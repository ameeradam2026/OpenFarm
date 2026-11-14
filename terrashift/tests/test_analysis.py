import pandas as pd
from terrashift.analysis.climate_analysis import summarize
from terrashift.intelligence.crop_rotation import compare

def test_climate_summary_uses_units_and_thresholds():
    dates = pd.date_range("2025-01-01", periods=3)
    frame = pd.DataFrame({"PRECTOTCORR":[0.0, 21.0, 0.5], "T2M":[20, 21, 22], "T2M_MAX":[34, 36, 35]}, index=dates)
    result = summarize(frame)
    assert result["annual_precip_mm"] == 21.5
    assert result["heat_days_35c"] == 2
    assert result["heavy_rain_days_20mm"] == 1
    assert result["consecutive_dry_days"] == 1

def test_rotation_has_three_options_and_explains_heuristic():
    strategies, selected, caveat = compare({"annual_precip_mm":700,"heat_days_35c":5}, "Rebuild Soil Nitrogen and Prevent Erosion", "Loamy", "No")
    assert len(strategies) == 3
    assert selected == "regen"
    assert any(s["is_recommended"] for s in strategies)
    assert "not a validated" in caveat

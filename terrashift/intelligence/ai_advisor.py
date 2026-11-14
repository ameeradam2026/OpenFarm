"""Contextual, rule-based advisor. Not a generative AI model."""
def advise(climate: dict, strategy: dict, farm: dict) -> str:
    parts = [f"For {farm.get('location', 'this farm')}, the evidence currently supports considering {strategy['name']} ({strategy['sequence']})."]
    rain = climate.get("annual_precip_mm")
    heat = climate.get("heat_days_35c")
    if rain is not None:
        parts.append(f"NASA POWER Agroclimatology reports {rain:.0f} mm precipitation in the selected retrieval period; this is a regional grid estimate, not a field rain gauge.")
    if heat is not None:
        parts.append(f"There were {heat} days with daily maximum temperature at or above 35°C in the retrieved period; this threshold is a screening indicator, not a crop-specific damage model.")
    parts.append("Consider planting after effective local rainfall and confirm soil moisture in the field. Root-zone moisture, field soil fertility, crop duration and planting-window forecasts are not established by this dashboard.")
    parts.append("Recommendation source: transparent rule-based decision support; no generative AI or trained ML model is used. Consult local extension advice and soil testing.")
    return " ".join(parts)

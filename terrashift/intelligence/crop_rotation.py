"""Transparent rule-based rotation comparison; no yields or invented soil gains."""
from __future__ import annotations

STRATEGIES = [
    {"id":"baseline", "name":"A · Traditional baseline", "sequence":"Current crop → bare fallow",
     "soil":"No planned legume phase; nutrient outcomes depend on crop removal and inputs.",
     "water":"Fallow reduces crop water use during fallow, but exposed soil may lose moisture to evaporation.",
     "protection":"Bare periods leave soil exposed; erosion risk depends on slope, storms, residue and tillage.",
     "limitations":"Baseline comparison only; effects cannot be quantified from point climate data."},
    {"id":"regen", "name":"B · Soil regeneration", "sequence":"Current cereal → locally suitable cowpea/legume → cover crop",
     "soil":"Legumes can fix atmospheric nitrogen when compatible with rhizobia and well managed; no amount estimated.",
     "water":"Adds a crop phase and its water demand; select a locally adapted short-duration legume and manage planting timing.",
     "protection":"Maintained cover/residue can protect soil; benefit depends on cover establishment and management.",
     "limitations":"Legume suitability, nitrogen fixation and cover establishment require local soil and extension advice."},
    {"id":"diversify", "name":"C · Water & climate diversification", "sequence":"Sorghum → sesame → chickpea (only where locally suitable)",
     "soil":"Diverse crop families may support rotation diversity; fertility effects depend on residue and nutrient management.",
     "water":"Crop water needs vary by variety and season; drought-adapted crops do not eliminate water risk.",
     "protection":"Residue/cover management determines protection; avoid bare-soil gaps where feasible.",
     "limitations":"The listed sequence is not universally suitable. Confirm crop calendars and markets locally."},
]


def compare(climate: dict, objective: str, soil: str, irrigation: str) -> tuple[list[dict], str, str]:
    """Rank with explicit evidence-based heuristic; confidence is intentionally conservative."""
    rain = climate.get("annual_precip_mm")
    heatdays = climate.get("heat_days_35c")
    # Ranking is a transparent objective rule, not a crop model or yield prediction.
    preferred = "regen" if "Nitrogen" in objective else "diversify" if "Diversify" in objective else "diversify"
    if rain is not None and rain < 500 and irrigation == "No":
        preferred = "diversify" if "Diversify" in objective else "baseline"
    results = []
    for item in STRATEGIES:
        row = dict(item)
        row["climate_context"] = (
            f"POWER period precipitation {rain:.0f} mm; {heatdays} days with daily maximum ≥35°C."
            if rain is not None and heatdays is not None else "Climate observations are incomplete; suitability cannot be ranked from missing data."
        )
        row["is_recommended"] = row["id"] == preferred
        row["confidence"] = "Low — heuristic; local crop calendars and field data not integrated."
        results.append(row)
    return results, preferred, "Recommendation is a transparent objective-and-climate heuristic, not a validated yield, soil nitrogen, erosion or crop-suitability model. Verify locally."

"""NASA Earthdata CMR granule discovery (metadata only, not raster measurements)."""
from __future__ import annotations

from datetime import date
from typing import Any

import requests

CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
PRODUCTS = {
    "SMAP": {"short_name": "SPL3SMP_E", "title": "SMAP L3 Radiometer Global Daily 9 km EASE-Grid Soil Moisture"},
    "GPM IMERG": {"short_name": "GPM_3IMERGDF", "title": "GPM IMERG Final Run Daily precipitation"},
    "MODIS NDVI/EVI": {"short_name": "MOD13Q1", "title": "Terra MODIS Vegetation Indices 16-Day L3 Global 250 m"},
    "ECOSTRESS": {"short_name": "ECO_L2T_LSTE", "title": "ECOSTRESS Tiled Land Surface Temperature and Emissivity"},
}


def search_granules(product: str, lat: float, lon: float, start: date, end: date, timeout: int = 20) -> dict[str, Any]:
    """Search public NASA CMR metadata; this does not download or derive data values."""
    if product not in PRODUCTS:
        raise ValueError(f"Unsupported NASA product: {product}")
    params = {
        "short_name": PRODUCTS[product]["short_name"],
        "bounding_box": f"{lon - 0.05},{lat - 0.05},{lon + 0.05},{lat + 0.05}",
        "temporal": f"{start.isoformat()}T00:00:00Z,{end.isoformat()}T23:59:59Z",
        "page_size": 10, " sort_key[]": "-start_date",
    }
    params.pop(" sort_key[]")
    response = requests.get(CMR_URL, params=params, headers={"Accept": "application/json"}, timeout=timeout)
    response.raise_for_status()
    body = response.json()
    items = body.get("feed", {}).get("entry", [])
    return {
        "product": product, "title": PRODUCTS[product]["title"],
        "short_name": PRODUCTS[product]["short_name"], "granules": items,
        "count": int(body.get("feed", {}).get("hits", len(items))),
        "retrieved_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "source": "NASA Earthdata Common Metadata Repository (CMR)",
        "note": "CMR provides granule metadata only. Pixel values are not downloaded or interpreted by this application.",
    }

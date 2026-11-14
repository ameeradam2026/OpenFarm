"""Dataset-specific CMR entry points; currently discover metadata, not science values."""
from .earthdata_cmr import search_granules

def fetch_smap(lat, lon, start, end):
    return search_granules("SMAP", lat, lon, start, end)

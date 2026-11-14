from .earthdata_cmr import search_granules

def fetch_ecostress(lat, lon, start, end):
    return search_granules("ECOSTRESS", lat, lon, start, end)

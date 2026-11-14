from .earthdata_cmr import search_granules

def fetch_gpm(lat, lon, start, end):
    return search_granules("GPM IMERG", lat, lon, start, end)

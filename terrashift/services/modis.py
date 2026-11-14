from .earthdata_cmr import search_granules

def fetch_modis(lat, lon, start, end):
    return search_granules("MODIS NDVI/EVI", lat, lon, start, end)

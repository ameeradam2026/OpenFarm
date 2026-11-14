# TerraShift — NASA-informed agricultural decision support

TerraShift is a standalone Streamlit demonstration added under `terrashift/`. It adds a new application without replacing the existing OpenFarm web application in this repository. It includes a real NASA POWER daily Agroclimatology data connector, NASA Earthdata CMR metadata discovery for SMAP/GPM/MODIS/ECOSTRESS, climate summaries, transparent rotation comparisons, English/Hausa message templates, a SQLite field log, and CSV/PDF exports.

## Run locally

```bash
cd terrashift
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Choose Kano Sudan Savanna, enter farm details, select Maize and an objective, then press **Retrieve NASA POWER data**. The app requests daily POWER values and labels their source/time range. Internet access is required for NASA services. Errors are displayed without silently generating substitute data.

## Data and science scope

NASA POWER retrieval is implemented for PRECTOTCORR, T2M_MAX, T2M_MIN, T2M, RH2M, WS10M and ALLSKY_SFC_SW_DWN with community `AG`. SMAP, GPM IMERG, MODIS and ECOSTRESS currently have separate CMR catalog lookup adapters; those lookups return granule metadata only. **They do not download or process observation pixels**, so the dashboard explicitly marks soil moisture and vegetation metrics unavailable. Some data downloads require a NASA Earthdata Login. Do not treat regional gridded estimates as field measurements.

The rotation engine is a low-confidence transparent heuristic, not a validated crop model. No yield, nitrogen amount, erosion reduction, or trained-ML result is claimed. Verify crop calendars and agronomic decisions with local extension services and soil tests.

## Sources

- [NASA POWER API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [NASA Earthdata CMR Search API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
- [SMAP](https://smap.jpl.nasa.gov/), [GPM IMERG](https://gpm.nasa.gov/data/imerg), [MODIS MOD13](https://modis.gsfc.nasa.gov/data/dataprod/mod13.php), [ECOSTRESS](https://ecostress.jpl.nasa.gov/)

## Tests

Run `pytest terrashift/tests` from repository root.

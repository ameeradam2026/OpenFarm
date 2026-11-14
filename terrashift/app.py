"""TerraShift Streamlit application — additive standalone app within OpenFarm."""
from __future__ import annotations
from datetime import date, timedelta
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from terrashift.analysis.climate_analysis import summarize
from terrashift.intelligence.ai_advisor import advise
from terrashift.intelligence.crop_rotation import compare
from terrashift.localization.messages import MESSAGES
from terrashift.reports.report_generator import make_pdf
from terrashift.services.earthdata_cmr import PRODUCTS, search_granules
from terrashift.services.farm_store import add_observation, list_observations
from terrashift.services.nasa_power import fetch_daily, UNITS

st.set_page_config(page_title="TerraShift | NASA-informed agriculture", page_icon="🌱", layout="wide")
st.markdown("""<style>
.stApp{background:#071426;color:#e8f1fb}.block-container{padding-top:1.5rem;max-width:1450px}
[data-testid=stMetric]{background:#10243a;padding:16px;border:1px solid #1e3e5b;border-radius:14px}
div[data-testid=stVerticalBlockBorderWrapper]{border-color:#1e3e5b!important;border-radius:14px}
.terra-sub{color:#8fb1ce}.stButton>button{border-radius:10px}
</style>""", unsafe_allow_html=True)

FARMS = {
    "Kano Sudan Savanna, Nigeria": (12.0022, 8.5920), "Iowa Corn Belt, USA": (41.8780, -93.0977),
    "Punjab Indo-Gangetic Plain, India": (30.9010, 75.8573), "Minas Gerais Cerrado, Brazil": (-18.5122, -44.5550),
    "Custom Coordinates": (12.0022, 8.5920),
}
OBJECTIVES = ["Conserve Soil Moisture and Water", "Rebuild Soil Nitrogen and Prevent Erosion", "Diversify Market Income and Improve Heat Resilience"]
PAGES = ["Overview", "Farm Configuration", "NASA Data Explorer", "Climate Intelligence", "Crop Rotation Lab", "AI Agricultural Advisor", "My Farm", "Reports", "Scientific Methodology"]

st.sidebar.markdown("# 🌱 TerraShift")
st.sidebar.caption("Turning NASA Data into Smarter Agricultural Decisions")
page = st.sidebar.radio("Navigation", PAGES)
st.sidebar.divider()
location = st.sidebar.selectbox("Farm location", list(FARMS))
lat0, lon0 = FARMS[location]
if location == "Custom Coordinates":
    lat = st.sidebar.number_input("Latitude", -90.0, 90.0, lat0, format="%.4f")
    lon = st.sidebar.number_input("Longitude", -180.0, 180.0, lon0, format="%.4f")
else:
    lat, lon = lat0, lon0
farm_size = st.sidebar.number_input("Farm size (hectares)", 0.1, 100000.0, 2.0, step=0.5)
soil = st.sidebar.selectbox("Soil type", ["Unknown", "Sandy", "Loamy", "Clay", "Silty", "Lateritic"])
irrigation = st.sidebar.selectbox("Irrigation available?", ["No", "Yes", "Partial"])
crop = st.sidebar.selectbox("Current crop", ["Maize", "Sorghum", "Rice", "Wheat", "Cowpea", "Sesame", "Other locally supported crop"])
season = st.sidebar.selectbox("Planting season", ["Main season", "Second season", "Not specified"])
objective = st.sidebar.selectbox("Farming objective", OBJECTIVES)
start = st.sidebar.date_input("Analysis start", value=date.today() - timedelta(days=365))
end = st.sidebar.date_input("Analysis end", value=date.today() - timedelta(days=3))

if "power_frame" not in st.session_state: st.session_state.power_frame = None
if "power_meta" not in st.session_state: st.session_state.power_meta = None
if st.sidebar.button("⬇ Retrieve NASA POWER data", type="primary", use_container_width=True):
    try:
        with st.spinner("Requesting NASA POWER daily Agroclimatology data…"):
            frame, meta = fetch_daily(lat, lon, start, end)
        st.session_state.power_frame, st.session_state.power_meta = frame, meta
        st.sidebar.success(f"Retrieved {len(frame)} valid daily records")
    except Exception as exc:
        st.sidebar.error(f"NASA POWER unavailable: {exc}. No simulated replacement was used.")

frame = st.session_state.power_frame
meta = st.session_state.power_meta
summary = summarize(frame) if frame is not None else summarize(pd.DataFrame())
farm = {"location": location, "latitude": lat, "longitude": lon, "size_ha": farm_size, "soil": soil, "irrigation": irrigation, "crop": crop, "season": season, "objective": objective}
strategies, recommended_id, caveat = compare(summary, objective, soil, irrigation)
recommended = next(s for s in strategies if s["id"] == recommended_id)

st.title("🌱 TerraShift")
st.markdown('<p class="terra-sub">Adapting Farms with NASA Earth Observation Data · Scientific decision support, not field-level measurement</p>', unsafe_allow_html=True)

def telemetry():
    a,b,c,d = st.columns(4)
    a.metric("Root-zone moisture", "Unavailable", help="No SMAP measurement is currently ingested. CMR catalog search is metadata only.")
    b.metric("Rainfall · retrieved period", f"{summary['annual_precip_mm']:.0f} mm" if summary.get("annual_precip_mm") is not None else "—")
    c.metric("Maximum air temperature", f"{summary['max_temp_c']:.1f} °C" if summary.get("max_temp_c") is not None else "—")
    d.metric("Vegetation indices", "Unavailable", help="MODIS CMR granules are discoverable; NDVI/EVI pixels are not downloaded.")

def chart_climate():
    if frame is None or frame.empty:
        st.info("Retrieve NASA POWER data to view charts. There is no silent demo-data substitution.")
        return
    monthly = summary["monthly"].reset_index(names="month")
    if "precip_mm" in monthly:
        st.plotly_chart(px.bar(monthly, x="month", y="precip_mm", title="Monthly precipitation · mm/month", template="plotly_dark"), use_container_width=True)
    cols = [c for c in ["mean_temp_c", "max_temp_c"] if c in monthly]
    if cols:
        st.plotly_chart(px.line(monthly, x="month", y=cols, markers=True, title="Monthly air temperature · °C", template="plotly_dark"), use_container_width=True)
    if "PRECTOTCORR" in frame and "T2M" in frame:
        st.plotly_chart(px.scatter(frame.reset_index(), x="T2M", y="PRECTOTCORR", color="RH2M" if "RH2M" in frame else None, title="Daily rainfall and mean temperature", labels={"T2M":"Mean air temperature (°C)","PRECTOTCORR":"Precipitation (mm/day)"}, template="plotly_dark"), use_container_width=True)

if page == "Overview":
    st.subheader(f"Farm climate overview · {location}")
    telemetry()
    if meta: st.caption(f"NASA POWER · {summary.get('period_start')} to {summary.get('period_end')} · Retrieved {meta['retrieved_at_utc']} · source: {meta['source']}")
    chart_climate()
    st.subheader("Three crop-rotation strategies")
    cards = st.columns(3)
    for col, strategy in zip(cards, strategies):
        with col:
            with st.container(border=True):
                st.markdown(f"### {strategy['name']}")
                st.write(strategy["sequence"])
                st.caption("Recommended by current transparent heuristic" if strategy["is_recommended"] else "Comparison option")
                st.write(strategy["climate_context"])
                st.caption(strategy["confidence"])
    st.warning(caveat)
    st.caption("Scientific transparency: regional NASA grid products are not direct farm-field observations. Root-zone moisture, NDVI/EVI, GPM rainfall and ECOSTRESS temperature are not presented as measured unless their pixel data have actually been ingested.")
elif page == "Farm Configuration":
    st.header("Farm configuration")
    st.write(f"**Location:** {location} · **Coordinates:** {lat:.4f}, {lon:.4f} · **Area:** {farm_size:g} ha")
    st.write(f"**Soil:** {soil} · **Irrigation:** {irrigation} · **Current crop:** {crop} · **Season:** {season} · **Objective:** {objective}")
    st.info("Farm inputs are held in this browser session for analysis. Use My Farm to record observations locally in SQLite.")
elif page == "NASA Data Explorer":
    st.header("NASA Earth Observation Explorer")
    st.write("POWER daily values are retrieved independently. CMR results below are NASA Earthdata granule metadata only—not downloaded satellite measurements.")
    if meta:
        st.success(f"POWER retrieval: {meta['retrieved_at_utc']} · parameters and units: {UNITS}")
        st.json({"start":meta["requested_start"],"end":meta["requested_end"],"missing_values":meta["missing_values"]})
    for product, info in PRODUCTS.items():
        with st.expander(f"{product} · {info['title']}"):
            if st.button(f"Search NASA CMR for {product} metadata", key=f"cmr_{product}"):
                try:
                    result = search_granules(product, lat, lon, start, end)
                    st.write(f"Granules found: {result['count']} · retrieved {result['retrieved_at_utc']}")
                    st.caption(result["note"])
                    if result["granules"]:
                        st.dataframe(pd.DataFrame([{"title":g.get("title"),"start":g.get(" time_start",g.get("time_start")),"id":g.get("id")} for g in result["granules"]]), use_container_width=True)
                except Exception as exc: st.error(f"NASA CMR lookup failed: {exc}")
elif page == "Climate Intelligence":
    st.header("Climate Intelligence")
    telemetry(); chart_climate()
    if summary.get("consecutive_dry_days") is not None:
        st.write(f"Longest sequence of retrieved daily precipitation <1 mm: **{summary['consecutive_dry_days']} days** (simple threshold indicator).")
        st.write(f"Days with precipitation ≥20 mm: **{summary['heavy_rain_days_20mm']}**. This is a threshold count, not an intensity/distribution product analysis.")
        st.write(f"Days with maximum air temperature ≥35°C: **{summary['heat_days_35c']}** (screening threshold, not crop-specific heat damage).")
    st.warning("POWER values are gridded estimates; historical baseline anomalies, SMAP root-zone moisture and satellite vegetation trends are unavailable in this version.")
elif page == "Crop Rotation Lab":
    st.header("Crop Rotation Laboratory")
    st.caption(f"Baseline crop selected: {crop} · objective: {objective} · soil: {soil} · irrigation: {irrigation}")
    for strategy in strategies:
        with st.container(border=True):
            st.subheader(strategy["name"] + (" ★ Suggested" if strategy["is_recommended"] else ""))
            st.write(f"**Sequence:** {strategy['sequence']}")
            st.write(f"**Climate context:** {strategy['climate_context']}")
            st.write(f"**Water demand:** {strategy['water']}")
            st.write(f"**Soil fertility:** {strategy['soil']}")
            st.write(f"**Heat/drought vulnerability:** {strategy['limitations']}")
            st.write(f"**Erosion management:** {strategy['protection']}")
            st.write(f"**Confidence:** {strategy['confidence']}")
            st.caption("Evidence: NASA POWER daily Agroclimatology values where retrieved; qualitative agronomic principles are not locally validated. No yield, nitrogen gain or erosion reduction is calculated.")
    st.info(caveat)
elif page == "AI Agricultural Advisor":
    st.header("Agricultural Advisor")
    st.caption("Context-aware rule-based advisory (not a generative AI model or trained ML predictor).")
    question = st.selectbox("What would you like help with?", ["Which rotation is preferable?", "How can I conserve water?", "What is the climate risk?", "How can I improve soil fertility?", "What are possible planting windows?"])
    if st.button("Generate farm advisory", type="primary"):
        st.write(advise(summary, recommended, farm))
        st.write(f"**Question:** {question}")
        st.caption("Planting dates and crop suitability need locally validated crop calendars, forecast data and extension input; this app does not infer a precise planting date.")
elif page == "My Farm":
    st.header("My Farm · field records")
    with st.form("observation_form"):
        record_crop = st.text_input("Crop", crop)
        planting = st.date_input("Planting date", value=date.today())
        obs = st.text_area("Farm observation")
        e1,e2,e3 = st.columns(3)
        expenses = e1.number_input("Expenses", min_value=0.0, value=0.0)
        harvest = e2.number_input("Harvest (kg)", min_value=0.0, value=0.0)
        sales = e3.number_input("Sales", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Save farm record")
    if submitted:
        add_observation((location, record_crop, planting.isoformat(), soil, obs, expenses, harvest, sales))
        st.success("Saved locally to TerraShift SQLite database.")
    records = list_observations()
    st.dataframe(pd.DataFrame(records, columns=["Recorded","Location","Crop","Planting date","Soil","Observation","Expenses","Harvest kg","Sales"]), use_container_width=True)
elif page == "Reports":
    st.header("Reports and Exports")
    if frame is None:
        st.info("Retrieve NASA POWER data first. Reports will not invent absent observations.")
    else:
        st.download_button("Download daily climate CSV", frame.to_csv().encode("utf-8"), "terrashift_nasa_power_daily.csv", "text/csv")
        st.download_button("Download monthly summary CSV", summary["monthly"].to_csv().encode("utf-8"), "terrashift_monthly_summary.csv", "text/csv")
        report_lines = [f"Location: {location} ({lat:.4f}, {lon:.4f})", f"Farm area: {farm_size} ha; soil: {soil}; irrigation: {irrigation}; current crop: {crop}", f"NASA POWER source: {meta['source']}; retrieved: {meta['retrieved_at_utc']}", f"Period: {summary['period_start']} to {summary['period_end']}", f"Precipitation total (mm): {summary['annual_precip_mm']}", f"Mean air temperature (C): {summary['mean_temp_c']}", f"Maximum air temperature (C): {summary['max_temp_c']}", f"Recommended strategy: {recommended['name']} — {recommended['sequence']}", caveat, advise(summary, recommended, farm), "Limitations: grid observations are not field measurements; soil moisture and vegetation values unavailable unless separately ingested."]
        st.download_button("Download PDF farm report", make_pdf("TerraShift climate and rotation report", report_lines), "terrashift_report.pdf", "application/pdf")
elif page == "Scientific Methodology":
    st.header("Scientific methodology and limitations")
    st.markdown("""
- **NASA POWER:** Daily point endpoint, Agroclimatology community (`AG`). PRECTOTCORR in mm/day; T2M/T2M_MAX/T2M_MIN in °C; RH2M in percent; WS10M in m/s; ALLSKY_SFC_SW_DWN in kWh/m²/day. Monthly precipitation is the sum of daily values; temperature monthly values are means. Retrieved-period rainfall is a total, not necessarily a calendar-year climatology.
- **SMAP, GPM, MODIS, ECOSTRESS:** This release searches the public NASA Earthdata CMR catalog for product granule metadata. It does not retrieve pixel files or report soil-moisture/NDVI/EVI/land-surface-temperature measurements. Product granules may require Earthdata authentication and product-specific processing.
- **Missing data:** NASA POWER sentinel values are converted to missing and counted. Failed requests are surfaced; there is no silent synthetic fallback. Unavailable satellite metrics remain unavailable.
- **Derived indicators:** Dry days use daily precipitation <1 mm; heavy-rain days use ≥20 mm; heat days use daily maximum ≥35°C. These are simple screening thresholds, not validated local hazard definitions.
- **Recommendations:** Three qualitative rotations are compared with transparent objective/climate heuristics. Confidence is low. No yield, nitrogen gain, erosion reduction or resilience score is invented. There is no trained machine-learning model.
- **Spatial/temporal limits:** Satellite/grid cells represent regional conditions and can differ from a farm field. Product resolution and revisit period vary; consult each dataset's NASA metadata and documentation.
- **Use with care:** Verify planting calendars, varieties, irrigation and crop suitability with local extension officers. Field soil tests and on-farm measurements are needed for soil fertility and root-zone conditions.
""")
    st.markdown("Sources: [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), [NASA Earthdata CMR](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html), [SMAP](https://smap.jpl.nasa.gov/), [GPM](https://gpm.nasa.gov/data/imerg), [MODIS vegetation indices](https://modis.gsfc.nasa.gov/data/dataprod/mod13.php), [ECOSTRESS](https://ecostress.jpl.nasa.gov/).")

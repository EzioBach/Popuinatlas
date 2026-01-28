import streamlit as st
import pandas as pd
import plotly.express as px

from utils import inject_global_css, render_hero


st.set_page_config(page_title="City Analytics + City Map — Popuinatlas", page_icon="🏙️", layout="wide")

inject_global_css()
render_hero(
    "🏙️",
    "City Analytics + City Map",
    "Lat/lon map - population analytics",
    pill="Cities",
)


required = {"countries", "cities", "languages", "worldcities"}
missing = [k for k in required if k not in st.session_state]
if missing:
    st.error(f"Missing in session_state: {missing}. Open **Home (main.py)** once to load data.")
    st.stop()

countries = st.session_state["countries"].copy()
cities_mysql = st.session_state["cities"].copy()
worldcities = st.session_state["worldcities"]  

tab_map, tab_analytics = st.tabs(["🗺️ City Map (Lat/Lon)", "📈 City Analytics (Population)"])



with tab_map:
    if worldcities is None or (isinstance(worldcities, pd.DataFrame) and worldcities.empty):
        st.error("worldcities.csv is missing or empty. Put it at `data/worldcities.csv` and redeploy/restart.")
        st.stop()

    wc = worldcities.copy()

    wc.columns = [str(c).strip() for c in wc.columns]

    lat_col = None
    lon_col = None

    for cand in ["lat", "latitude", "LAT", "Latitude"]:
        if cand in wc.columns:
            lat_col = cand
            break

    for cand in ["lon", "lng", "longitude", "LON", "LNG", "Longitude"]:
        if cand in wc.columns:
            lon_col = cand
            break

    if not lat_col or not lon_col:
        st.error(
            f"worldcities.csv must contain latitude/longitude columns. "
            f"Expected 'lat' + ('lon' or 'lng'). Found: {wc.columns.tolist()}"
        )
        st.stop()

    iso3_col = "iso3" if "iso3" in wc.columns else None
    pop_col = "population" if "population" in wc.columns else None

    city_col = None
    for cand in ["city", "city_ascii", "name", "Name"]:
        if cand in wc.columns:
            city_col = cand
            break

    admin_col = "admin_name" if "admin_name" in wc.columns else None
    country_col = "country" if "country" in wc.columns else None

    c1, c2, c3 = st.columns([1.1, 1, 1])
    with c1:
        min_pop = st.number_input("Minimum population", value=200000, step=50000)
    with c2:
        max_points = st.slider("Max points (performance)", 2000, 50000, 15000, 1000)
    with c3:
        projection = st.selectbox("Projection", ["natural earth", "equirectangular", "orthographic"], index=0)

    chosen_iso3 = None
    if "Code" in countries.columns and "Name" in countries.columns and iso3_col:
        cdf = countries.dropna(subset=["Code", "Name"]).copy()
        cdf["Code"] = cdf["Code"].astype(str).str.strip()
        cdf["Name"] = cdf["Name"].astype(str).str.strip()
        cdf["_label"] = cdf["Name"] + " (" + cdf["Code"] + ")"
        cdf = cdf.sort_values("_label")
        pick = st.selectbox("Country filter (optional)", ["All"] + cdf["_label"].tolist())
        if pick != "All":
            chosen_iso3 = pick.split("(")[-1].replace(")", "").strip()
    else:
        st.caption("Country filter is disabled (missing countries Code/Name or worldcities iso3 column).")

    df = wc.dropna(subset=[lat_col, lon_col]).copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])

    if pop_col:
        df[pop_col] = pd.to_numeric(df[pop_col], errors="coerce")
        df = df[df[pop_col].fillna(0) >= min_pop]

    if chosen_iso3 and iso3_col:
        df[iso3_col] = df[iso3_col].astype(str).str.strip()
        df = df[df[iso3_col] == chosen_iso3]

    if pop_col and df[pop_col].notna().any():
        df = df.sort_values(pop_col, ascending=False).head(max_points)
    else:
        df = df.head(max_points)

    st.write(f"Showing **{len(df):,}** cities")

    hover_cols = []
    for col in [country_col, admin_col, pop_col]:
        if col and col in df.columns:
            hover_cols.append(col)

    fig = px.scatter_geo(
        df,
        lat=lat_col,
        lon=lon_col,
        hover_name=city_col if city_col else None,
        hover_data=hover_cols if hover_cols else None,
        size=pop_col if pop_col else None,
        projection=projection,
        template="plotly_dark",
        title="Cities (zoom / pan / hover)",
    )

    fig.update_layout(
        height=720,
        margin=dict(l=0, r=0, t=60, b=0),
        geo=dict(
            showocean=True,
            oceancolor="rgb(12,16,25)",
            showland=True,
            landcolor="rgb(20,25,35)",
            showcountries=True,
            countrycolor="rgba(255,255,255,0.22)",
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)



with tab_analytics:
    st.subheader("📈 Urban concentration patterns (city.csv)")
    st.caption("Analytics use the MySQL world dataset's city table (population, rankings, concentration).")

    cities = cities_mysql.copy()
    ctry = countries.copy()

    needed_cols = {"CountryCode", "Population"}
    if not needed_cols.issubset(set(cities.columns)):
        st.error(
            f"`cities` table is missing required columns {needed_cols}. "
            f"Found: {cities.columns.tolist()}"
        )
        st.stop()

    cities["CountryCode"] = cities["CountryCode"].astype(str).str.strip()
    cities["Population"] = pd.to_numeric(cities["Population"], errors="coerce")

    if "Continent" not in ctry.columns:
        st.warning("Countries table has no 'Continent' column — continent filter disabled.")
        conts = ["All"]
    else:
        conts = ["All"] + sorted(ctry["Continent"].dropna().astype(str).unique().tolist())

    sel_cont = st.selectbox("Continent", conts)

    filtered_countries = ctry.copy()
    if sel_cont != "All" and "Continent" in filtered_countries.columns:
        filtered_countries = filtered_countries[filtered_countries["Continent"] == sel_cont]

    if not {"Code", "Name"}.issubset(set(filtered_countries.columns)):
        st.error("Countries table must include 'Code' and 'Name'.")
        st.stop()

    filtered_countries = filtered_countries.dropna(subset=["Code", "Name"]).copy()
    filtered_countries["Code"] = filtered_countries["Code"].astype(str).str.strip()
    filtered_countries["Name"] = filtered_countries["Name"].astype(str).str.strip()
    filtered_countries["_label"] = filtered_countries["Name"] + " (" + filtered_countries["Code"] + ")"
    filtered_countries = filtered_countries.sort_values("_label")

    options = filtered_countries["_label"].tolist()
    default = options[:3] if len(options) >= 3 else options

    sel_labels = st.multiselect("Compare countries", options=options, default=default)
    if not sel_labels:
        st.info("Select at least one country.")
        st.stop()

    sel_codes = [x.split("(")[-1].replace(")", "").strip() for x in sel_labels]
    subset = cities[cities["CountryCode"].isin(sel_codes)].copy()

    st.divider()
    top_n = st.slider("Top N cities per country", 5, 30, 10, 5)

    rows = []
    for code in sel_codes:
        g = subset[subset["CountryCode"] == code].dropna(subset=["Population"]).sort_values("Population", ascending=False)
        top = g.head(top_n).copy()
        top["ISO3"] = code
        rows.append(top)

    top_all = pd.concat(rows, ignore_index=True) if rows else subset.head(0)

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### Top cities (table)")
        cols = ["ISO3"]
        if "Name" in top_all.columns:
            cols.append("Name")
        if "District" in top_all.columns:
            cols.append("District")
        cols.append("Population")

        out = top_all[cols].copy()
        out["Population"] = out["Population"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        st.dataframe(out.sort_values(["ISO3"], ascending=True), use_container_width=True)

    with right:
        st.markdown("### Urban concentration (Top-10 share)")
        conc = []
        for code in sel_codes:
            g = subset[subset["CountryCode"] == code].dropna(subset=["Population"]).sort_values("Population", ascending=False)
            if g.empty:
                continue
            total = g["Population"].sum()
            top10 = g["Population"].head(10).sum()
            conc.append({"ISO3": code, "Top10_share": (top10 / total) if total else None})

        conc_df = pd.DataFrame(conc)
        if conc_df.empty:
            st.write("—")
        else:
            figc = px.bar(
                conc_df,
                x="ISO3",
                y="Top10_share",
                template="plotly_dark",
                title="Top-10 population share",
            )
            figc.update_layout(margin=dict(l=0, r=0, t=60, b=0))
            st.plotly_chart(figc, use_container_width=True)

    st.divider()
    st.markdown("### Rank–size curve (population distribution)")

    rank_df = subset.dropna(subset=["Population"]).copy()
    rank_df = rank_df.sort_values(["CountryCode", "Population"], ascending=[True, False])
    rank_df["rank"] = rank_df.groupby("CountryCode").cumcount() + 1

    fig2 = px.scatter(
        rank_df,
        x="rank",
        y="Population",
        color="CountryCode",
        template="plotly_dark",
        title="Rank vs population (compare distributions)",
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0))
    st.plotly_chart(fig2, use_container_width=True)

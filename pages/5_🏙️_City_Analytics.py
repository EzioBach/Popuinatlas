import streamlit as st
import pandas as pd
import plotly.express as px

from utils import inject_global_css, render_hero, get_data

st.set_page_config(page_title="City Analytics — Popuinatlas", page_icon="🏙️", layout="wide")
inject_global_css()
render_hero("🏙️", "City Analytics + City Map", "Lat/lon map (worldcities.csv) + population analytics (MySQL city.csv).", pill="Cities")

countries_cities, countries, langs, worldcities = get_data()
cities_mysql = countries_cities.copy()
countries = countries.copy()

tab_map, tab_analytics = st.tabs(["🗺️ City Map (Lat/Lon)", "📈 City Analytics (Population)"])

# -------------------------
# TAB 1: City Map
# -------------------------
with tab_map:
    if worldcities is None:
        st.warning("No `data/worldcities.csv` found. Add it to enable the lat/lon city map.")
        st.stop()

    wc = worldcities.copy()

    # Find expected columns
    lat_col = "lat" if "lat" in wc.columns else None
    lon_col = "lon" if "lon" in wc.columns else None
    if not lat_col or not lon_col:
        st.error(f"worldcities.csv must contain 'lat' and 'lon'. Found: {wc.columns.tolist()}")
        st.stop()

    iso3_col = next((c for c in ["iso3", "ISO3", "code3"] if c in wc.columns), None)
    pop_col = next((c for c in ["population", "pop", "Population"] if c in wc.columns), None)
    city_col = next((c for c in ["city", "City", "name", "Name"] if c in wc.columns), None)

    c1, c2, c3 = st.columns([1.1, 1, 1])
    with c1:
        min_pop = st.number_input("Minimum population", value=200000, step=50000)
    with c2:
        max_points = st.slider("Max points (performance)", 2000, 50000, 15000, 1000)
    with c3:
        projection = st.selectbox("Projection", ["natural earth", "equirectangular", "orthographic"], index=0)

    chosen_iso3 = None
    if iso3_col and "Name" in countries.columns and "Code" in countries.columns:
        countries2 = countries.dropna(subset=["Code", "Name"]).copy()
        countries2["_label"] = countries2["Name"].astype(str) + " (" + countries2["Code"].astype(str) + ")"
        pick = st.selectbox("Country filter (optional)", ["All"] + sorted(countries2["_label"].tolist()))
        if pick != "All":
            chosen_iso3 = pick.split("(")[-1].replace(")", "").strip()

    df = wc.dropna(subset=[lat_col, lon_col]).copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])

    if pop_col:
        df[pop_col] = pd.to_numeric(df[pop_col], errors="coerce")
        df = df[df[pop_col] >= min_pop]

    if chosen_iso3 and iso3_col:
        df = df[df[iso3_col].astype(str) == str(chosen_iso3)]

    if pop_col and df[pop_col].notna().any():
        df = df.sort_values(pop_col, ascending=False).head(max_points)
    else:
        df = df.head(max_points)

    st.write(f"Showing **{len(df):,}** cities")

    hover_cols = [c for c in [city_col, "country", "admin_name", pop_col] if c and c in df.columns]

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

# -------------------------
# TAB 2: City Analytics
# -------------------------
with tab_analytics:
    st.subheader("Urban concentration patterns (MySQL city.csv)")
    if "Population" in cities_mysql.columns:
        cities_mysql["Population"] = pd.to_numeric(cities_mysql["Population"], errors="coerce")

    conts = ["All"] + sorted(countries["Continent"].dropna().unique().tolist()) if "Continent" in countries.columns else ["All"]
    sel_cont = st.selectbox("Continent", conts)

    filtered_countries = countries if sel_cont == "All" else countries[countries["Continent"] == sel_cont]
    filtered_countries = filtered_countries.dropna(subset=["Code", "Name"]).copy()
    filtered_countries["_label"] = filtered_countries["Name"].astype(str) + " (" + filtered_countries["Code"].astype(str) + ")"
    options = sorted(filtered_countries["_label"].tolist())

    default = options[:3] if len(options) >= 3 else options
    sel_labels = st.multiselect("Compare countries", options=options, default=default)

    if not sel_labels:
        st.info("Select at least one country.")
        st.stop()

    sel_codes = [x.split("(")[-1].replace(")", "").strip() for x in sel_labels]
    subset = cities_mysql[cities_mysql["CountryCode"].astype(str).isin(sel_codes)].copy()

    top_n = st.slider("Top N cities per country", 5, 30, 10, 5)

    rows = []
    for code in sel_codes:
        g = subset[subset["CountryCode"].astype(str) == str(code)].dropna(subset=["Population"])
        g = g.sort_values("Population", ascending=False).head(top_n).copy()
        g["ISO3"] = str(code)
        rows.append(g)

    top_all = pd.concat(rows, ignore_index=True) if rows else subset.head(0)

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### Top cities")
        cols = [c for c in ["ISO3", "Name", "District", "Population"] if c in top_all.columns]
        out = top_all[cols].copy()
        if "Population" in out.columns:
            out["Population"] = out["Population"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        st.dataframe(out, use_container_width=True)

    with right:
        st.markdown("### Urban concentration (Top-10 share)")
        conc = []
        for code in sel_codes:
            g = subset[subset["CountryCode"].astype(str) == str(code)].dropna(subset=["Population"]).sort_values("Population", ascending=False)
            if g.empty:
                continue
            total = g["Population"].sum()
            top10 = g["Population"].head(10).sum()
            conc.append({"ISO3": str(code), "Top10_share": (top10 / total) if total else None})

        conc_df = pd.DataFrame(conc)
        if conc_df.empty:
            st.write("—")
        else:
            figc = px.bar(conc_df, x="ISO3", y="Top10_share", template="plotly_dark", title="Top-10 population share")
            figc.update_layout(margin=dict(l=0, r=0, t=60, b=0))
            st.plotly_chart(figc, use_container_width=True)

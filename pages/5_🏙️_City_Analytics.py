import streamlit as st
import pandas as pd
import plotly.express as px
from utils import inject_global_css, render_hero
inject_global_css()
render_hero("🧩", "This Page Title", "One-line description of what the user can do here.")


st.set_page_config(page_title="City Analytics + Map", layout="wide")
st.title("🏙️ City Analytics + City Map")
st.caption("Map uses real lat/lon (worldcities.csv). Analytics use the MySQL world city table (city.csv).")

# -------------------------
# Safety
# -------------------------
required = {"countries", "cities", "languages", "worldcities"}
if not required.issubset(st.session_state.keys()):
    st.error("Open Home first (main.py).")
    st.stop()

countries = st.session_state["countries"].copy()
cities_mysql = st.session_state["cities"].copy()
worldcities = st.session_state["worldcities"]  # may be None

# Normalize types
countries["Code"] = countries["Code"].astype(str)

# -------------------------
# Tabs
# -------------------------
tab_map, tab_analytics = st.tabs(["🗺️ City Map (Lat/Lon)", "📈 City Analytics (Population)"])

# =========================================================
# TAB 1: City Map (KEEP your favorite map style)
# =========================================================
with tab_map:
    if worldcities is None:
        st.error("worldcities.csv not found. Put it in data/worldcities.csv and restart the app.")
        st.stop()

    wc = worldcities.copy()

    # Ensure lat/lon exist
    for c in ["lat", "lon"]:
        if c not in wc.columns:
            st.error(f"worldcities.csv missing '{c}'. Found: {wc.columns.tolist()}")
            st.stop()

    # Detect iso3 column
    iso3_col = None
    for cand in ["iso3", "ISO3", "code3"]:
        if cand in wc.columns:
            iso3_col = cand
            break

    # Detect population column
    pop_col = None
    for cand in ["population", "pop", "Population"]:
        if cand in wc.columns:
            pop_col = cand
            break

    # Detect city name column
    city_col = None
    for cand in ["city", "City", "name", "Name"]:
        if cand in wc.columns:
            city_col = cand
            break

    # Sidebar controls for the map (inside tab)
    c1, c2, c3 = st.columns([1.1, 1, 1])
    with c1:
        min_pop = st.number_input("Minimum population", value=200000, step=50000, key="citymap_minpop_merged")
    with c2:
        max_points = st.slider("Max points (performance)", 2000, 50000, 15000, 1000, key="citymap_maxpoints_merged")
    with c3:
        projection = st.selectbox("Projection", ["natural earth", "equirectangular", "orthographic"], index=0, key="citymap_proj_merged")

    chosen_iso3 = None
    if iso3_col and "Name" in countries.columns and "Code" in countries.columns:
        countries2 = countries.dropna(subset=["Code", "Name"]).copy()
        countries2["Name"] = countries2["Name"].astype(str)
        countries2["_label"] = countries2["Name"] + " (" + countries2["Code"] + ")"
        countries2 = countries2.sort_values("_label")

        pick = st.selectbox("Country filter (optional)", ["All"] + countries2["_label"].tolist(), key="citymap_country_merged")
        if pick != "All":
            chosen_iso3 = pick.split("(")[-1].replace(")", "").strip()
    else:
        st.caption("Country filter disabled (worldcities.csv has no ISO-3 column).")

    df = wc.copy()

    # Clean
    df = df.dropna(subset=["lat", "lon"])
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])

    if pop_col:
        df[pop_col] = pd.to_numeric(df[pop_col], errors="coerce")
        df = df[df[pop_col] >= min_pop]

    if chosen_iso3 and iso3_col:
        df[iso3_col] = df[iso3_col].astype(str)
        df = df[df[iso3_col] == chosen_iso3]

    # Performance: cap points (largest first)
    if pop_col and df[pop_col].notna().any():
        df = df.sort_values(pop_col, ascending=False).head(max_points)
    else:
        df = df.head(max_points)

    st.write(f"Showing **{len(df):,}** cities")

    hover_cols = []
    for col in [city_col, "country", "admin_name", pop_col]:
        if col and col in df.columns and col not in hover_cols:
            hover_cols.append(col)

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name=city_col if city_col else None,
        hover_data=hover_cols if hover_cols else None,
        size=pop_col if pop_col else None,
        projection=projection,
        template="plotly_dark",
        title="Cities (zoom/pan/hover)",
    )

    # KEEP your nice dark map look
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

# =========================================================
# TAB 2: City Analytics (your previous analytics)
# =========================================================
with tab_analytics:
    st.subheader("📈 Urban concentration patterns (city.csv)")
    st.caption("These analytics use the MySQL world dataset's city table (not lat/lon).")

    countries3 = countries.copy()
    cities = cities_mysql.copy()

    # Defensive conversions
    if "Population" in cities.columns:
        cities["Population"] = pd.to_numeric(cities["Population"], errors="coerce")

    conts = ["All"] + sorted(countries3["Continent"].dropna().unique().tolist())
    sel_cont = st.selectbox("Continent", conts, key="city_analytics_continent_merged")

    filtered_countries = countries3 if sel_cont == "All" else countries3[countries3["Continent"] == sel_cont]
    filtered_countries = filtered_countries.dropna(subset=["Code", "Name"]).copy()
    filtered_countries["Code"] = filtered_countries["Code"].astype(str)
    filtered_countries["Name"] = filtered_countries["Name"].astype(str)
    filtered_countries["_label"] = filtered_countries["Name"] + " (" + filtered_countries["Code"] + ")"
    filtered_countries = filtered_countries.sort_values("_label")

    options = filtered_countries["_label"].tolist()
    default = options[:3] if len(options) >= 3 else options

    sel_labels = st.multiselect("Compare countries", options=options, default=default, key="city_analytics_countries_merged")
    if not sel_labels:
        st.info("Select at least one country.")
        st.stop()

    sel_codes = [x.split("(")[-1].replace(")", "").strip() for x in sel_labels]

    subset = cities[cities["CountryCode"].astype(str).isin(sel_codes)].copy()

    st.divider()
    top_n = st.slider("Top N cities per country", 5, 30, 10, 5, key="city_analytics_topn_merged")

    rows = []
    for code in sel_codes:
        g = subset[subset["CountryCode"].astype(str) == str(code)].dropna(subset=["Population"]).sort_values("Population", ascending=False)
        top = g.head(top_n).copy()
        top["ISO3"] = str(code)
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
        if "Population" in top_all.columns:
            cols.append("Population")

        out = top_all[cols].copy()
        if "Population" in out.columns:
            out["Population"] = out["Population"].map(lambda x: f"{int(x):,}" if pd.notna(x) else "—")

        st.dataframe(out.sort_values(["ISO3"], ascending=True), use_container_width=True)

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

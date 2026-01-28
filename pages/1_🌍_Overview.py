import streamlit as st
import pandas as pd
import plotly.express as px

# MUST be first Streamlit command in this file
st.set_page_config(page_title="Overview — Popuinatlas", page_icon="🌍", layout="wide")

from utils import (
    inject_global_css,
    render_hero,
    get_data,
    normalize_columns,
    build_country_language_stats,
    build_global_language_stats,
)

inject_global_css()
render_hero("🌍", "Overview", "Global KPIs + the highest-signal maps from the dataset.")

# --- Load data safely (works even if user lands directly on this page) ---
cities, countries, langs = get_data()
cities = normalize_columns(cities)
countries = normalize_columns(countries)
langs = normalize_columns(langs)

# --- Build stats (NOTE: correct function calls) ---
stats = build_country_language_stats(langs)                 # per-country language stats
global_lang = build_global_language_stats(langs, countries) # per-language global stats

# --- Merge stats with countries for map/scatter fields ---
# stats has: CountryCode, n_languages, n_official, top_language, top_pct
# countries has: Code, Name, Continent, Region, Population, ...
merged = stats.merge(
    countries,
    left_on="CountryCode",
    right_on="Code",
    how="left",
)

# ---------------------------
# KPI row
# ---------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries", f"{countries.shape[0]:,}")
c2.metric("Unique languages", f"{langs['Language'].nunique():,}")
c3.metric("Cities", f"{cities.shape[0]:,}")

avg_langs = merged["n_languages"].mean()
c4.metric("Avg languages / country", f"{avg_langs:.2f}" if pd.notna(avg_langs) else "—")

st.divider()

# ---------------------------
# Row 1: map + bar
# ---------------------------
left, right = st.columns([1.25, 1])

with left:
    st.subheader("🗺️ Languages per country")

    map_df = merged.dropna(subset=["Code", "Name"]).copy()
    fig = px.choropleth(
        map_df,
        locations="Code",
        locationmode="ISO-3",
        color="n_languages",
        hover_name="Name",
        hover_data={
            "n_official": True,
            "Population": True,
            "Continent": True,
            "Region": True,
            "Code": False,
        },
        template="plotly_dark",
        title="Language diversity (count of listed languages per country)",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 Top languages (by #countries where listed)")

    top = global_lang.head(20).copy()
    fig2 = px.bar(
        top,
        x="countries_spoken",
        y="Language",
        orientation="h",
        template="plotly_dark",
        title="Top 20 languages by country coverage",
    )
    fig2.update_layout(
        margin=dict(l=0, r=0, t=60, b=0),
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------
# Row 2: scatter
# ---------------------------
st.subheader("🔎 Population vs language count")

scatter_df = merged.dropna(subset=["Population", "n_languages", "Name"]).copy()
scatter_df["Population"] = pd.to_numeric(scatter_df["Population"], errors="coerce")

fig3 = px.scatter(
    scatter_df,
    x="Population",
    y="n_languages",
    hover_name="Name",
    color="Continent" if "Continent" in scatter_df.columns else None,
    template="plotly_dark",
    title="Do larger populations correlate with more listed languages?",
)
fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
st.plotly_chart(fig3, use_container_width=True)

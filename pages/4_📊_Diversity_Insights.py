import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# MUST be first Streamlit command
st.set_page_config(page_title="Diversity Insights — Popuinatlas", page_icon="📊", layout="wide")

from utils import (
    inject_global_css,
    render_hero,
    get_data,
    normalize_columns,
    build_country_language_stats,
)

inject_global_css()
render_hero("📊", "Diversity Insights", "Compare language richness and (when possible) distribution entropy across countries.")

# ---------------------------
# Load data safely from any page
# ---------------------------
cities, countries, langs = get_data()
countries = normalize_columns(countries)
langs = normalize_columns(langs)

# ---------------------------
# Core stats (correct call)
# ---------------------------
stats = build_country_language_stats(langs)  # returns CountryCode, n_languages, n_official, top_language, top_pct

# Merge with countries to get Code/Name/Continent/Population/Region for maps + scatter
stats = stats.merge(
    countries,
    left_on="CountryCode",
    right_on="Code",
    how="left",
)

# ---------------------------
# Optional: Shannon entropy (only if Percentage exists)
# ---------------------------
entropy_available = "Percentage" in langs.columns

if entropy_available:
    tmp = langs.copy()
    tmp["CountryCode"] = tmp["CountryCode"].astype(str)
    tmp["Percentage"] = pd.to_numeric(tmp["Percentage"], errors="coerce")

    tmp = tmp.dropna(subset=["CountryCode", "Percentage"])
    tmp = tmp[tmp["Percentage"] > 0].copy()

    # Convert percent to probability
    tmp["p"] = tmp["Percentage"] / 100.0

    # Shannon entropy H = -sum(p log2 p)
    entropy = (
        tmp.groupby("CountryCode")["p"]
        .apply(lambda s: float(-(s * np.log2(s)).sum()) if len(s) else np.nan)
        .rename("entropy")
        .reset_index()
    )

    stats = stats.merge(entropy, on="CountryCode", how="left")
else:
    stats["entropy"] = np.nan

# ---------------------------
# KPIs row
# ---------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Countries (dataset)", f"{countries.shape[0]:,}")
k2.metric("Language rows", f"{langs.shape[0]:,}")
k3.metric("Avg languages / country", f"{stats['n_languages'].mean():.2f}" if stats["n_languages"].notna().any() else "—")
k4.metric("Entropy available?", "Yes" if stats["entropy"].notna().any() else "No")

st.divider()

tab1, tab2 = st.tabs(["🗺️ Maps", "🔗 Relationships"])

# ---------------------------
# TAB 1 — MAPS
# ---------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Languages per country")
        map_df = stats.dropna(subset=["Code", "Name", "n_languages"]).copy()

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
            title="Number of listed languages per country",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Shannon entropy (distribution spread)")
        if stats["entropy"].notna().any():
            ent_df = stats.dropna(subset=["Code", "Name", "entropy"]).copy()

            fig2 = px.choropleth(
                ent_df,
                locations="Code",
                locationmode="ISO-3",
                color="entropy",
                hover_name="Name",
                hover_data={
                    "n_languages": True,
                    "n_official": True,
                    "Population": True,
                    "Continent": True,
                    "Region": True,
                    "Code": False,
                },
                template="plotly_dark",
                title="Entropy from language percentages (higher = more evenly distributed)",
            )
            fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Entropy is unavailable because the language table has no usable 'Percentage' values.")

# ---------------------------
# TAB 2 — RELATIONSHIPS
# ---------------------------
with tab2:
    st.subheader("Population vs number of languages")

    rel = stats.dropna(subset=["Population", "n_languages", "Name"]).copy()
    rel["Population"] = pd.to_numeric(rel["Population"], errors="coerce")
    rel = rel.dropna(subset=["Population"])

    color_col = "Continent" if "Continent" in rel.columns else None

    fig3 = px.scatter(
        rel,
        x="Population",
        y="n_languages",
        color=color_col,
        hover_name="Name",
        template="plotly_dark",
        title="Population vs number of listed languages",
    )
    fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
    st.plotly_chart(fig3, use_container_width=True)

    if stats["entropy"].notna().any():
        st.subheader("Languages vs entropy")
        rel2 = stats.dropna(subset=["n_languages", "entropy", "Name"]).copy()

        fig4 = px.scatter(
            rel2,
            x="n_languages",
            y="entropy",
            color="Continent" if "Continent" in rel2.columns else None,
            hover_name="Name",
            template="plotly_dark",
            title="Does having more languages imply a more even distribution?",
        )
        fig4.update_layout(margin=dict(l=0, r=0, t=60, b=0))
        st.plotly_chart(fig4, use_container_width=True)

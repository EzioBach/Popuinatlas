import streamlit as st
import plotly.express as px

from utils import inject_global_css, render_hero, get_data, build_country_language_stats

st.set_page_config(page_title="Diversity Insights — Popuinatlas", page_icon="📊", layout="wide")
inject_global_css()
render_hero("📊", "Diversity Insights", "Compare language richness and (when possible) distribution entropy across countries.", pill="Derived metrics")

_, countries, langs, _ = get_data()
stats = build_country_language_stats(countries, langs)

tab1, tab2 = st.tabs(["🗺️ Maps", "🔎 Relationships"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.choropleth(
            stats,
            locations="Code",
            locationmode="ISO-3",
            color="n_languages",
            hover_name="Name" if "Name" in stats.columns else None,
            template="plotly_dark",
            title="Number of languages per country",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "entropy" in stats.columns and stats["entropy"].notna().any():
            fig2 = px.choropleth(
                stats,
                locations="Code",
                locationmode="ISO-3",
                color="entropy",
                hover_name="Name" if "Name" in stats.columns else None,
                template="plotly_dark",
                title="Shannon entropy (only if Percentage exists)",
            )
            fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Entropy is unavailable because Percentage is missing/empty in the language table.")

with tab2:
    if "Population" in stats.columns:
        df = stats.dropna(subset=["Population", "n_languages"]).copy()
        fig3 = px.scatter(
            df,
            x="Population",
            y="n_languages",
            color="Continent" if "Continent" in df.columns else None,
            hover_name="Name" if "Name" in df.columns else None,
            template="plotly_dark",
            title="Population vs number of languages",
        )
        fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Population column not available in your country table.")

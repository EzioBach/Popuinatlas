import streamlit as st
import plotly.express as px

from utils import inject_global_css, render_hero, get_data, build_country_language_stats, build_global_language_stats

st.set_page_config(page_title="Overview — Popuinatlas", page_icon="🌍", layout="wide")
inject_global_css()
render_hero("🌍", "Overview", "Global KPIs and the highest-signal maps from the dataset.", pill="Global view")

cities, countries, langs, _ = get_data()

stats = build_country_language_stats(countries, langs)
global_lang = build_global_language_stats(langs, countries)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries", f"{countries.shape[0]:,}")
c2.metric("Unique languages", f"{langs['Language'].nunique():,}" if "Language" in langs.columns else "—")
c3.metric("Cities", f"{cities.shape[0]:,}")
c4.metric("Avg languages/country", f"{stats['n_languages'].mean():.2f}" if "n_languages" in stats.columns else "—")

st.divider()

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Languages per country")
    fig = px.choropleth(
        stats,
        locations="Code",
        locationmode="ISO-3",
        color="n_languages",
        hover_name="Name" if "Name" in stats.columns else None,
        hover_data={k: True for k in ["n_official", "Population"] if k in stats.columns},
        template="plotly_dark",
        title="Language diversity (count of listed languages)",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top languages (by number of countries where listed)")
    top = global_lang.head(20).copy()
    fig2 = px.bar(
        top,
        x="countries_spoken",
        y="Language",
        orientation="h",
        template="plotly_dark",
        title="Top 20 languages",
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0), yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Population vs language count")
if "Population" in stats.columns:
    df = stats.dropna(subset=["Population", "n_languages"]).copy()
    fig3 = px.scatter(
        df,
        x="Population",
        y="n_languages",
        hover_name="Name" if "Name" in df.columns else None,
        color="Continent" if "Continent" in df.columns else None,
        template="plotly_dark",
        title="Do larger populations correlate with more listed languages?",
    )
    fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Population column not available in your country table.")

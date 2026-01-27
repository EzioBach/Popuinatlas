import streamlit as st
import plotly.express as px
from utils import build_country_language_stats, build_global_language_stats

st.set_page_config(page_title="Overview", layout="wide")
st.title("🌍 Overview")
st.caption("Global KPIs and the best high-signal maps from the dataset.")

if not {"countries", "cities", "languages"}.issubset(st.session_state.keys()):
    st.error("Open Home first (main.py).")
    st.stop()

countries = st.session_state["countries"]
cities = st.session_state["cities"]
langs = st.session_state["languages"]

stats = build_country_language_stats(countries, langs)
global_lang = build_global_language_stats(langs, countries)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries", f"{countries.shape[0]:,}")
c2.metric("Unique languages", f"{langs['Language'].nunique():,}")
c3.metric("Cities", f"{cities.shape[0]:,}")
c4.metric("Avg languages/country", f"{stats['n_languages'].mean():.2f}")

st.divider()

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Languages per country")
    fig = px.choropleth(
        stats,
        locations="Code",
        locationmode="ISO-3",
        color="n_languages",
        hover_name="Name",
        hover_data={"n_official": True, "Population": True},
        template="plotly_dark",
        title="Language diversity (count)",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top languages (by countries where listed)")
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
df = stats.dropna(subset=["Population", "n_languages"]).copy()
fig3 = px.scatter(
    df,
    x="Population",
    y="n_languages",
    hover_name="Name",
    color="Continent",
    template="plotly_dark",
    title="Do larger populations correlate with more listed languages?",
)
fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
st.plotly_chart(fig3, use_container_width=True)

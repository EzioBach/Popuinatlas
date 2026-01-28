import streamlit as st
import plotly.express as px
from utils import build_country_language_stats
from utils import inject_global_css, render_hero
inject_global_css()
render_hero("🧩", "This Page Title", "One-line description of what the user can do here.")


st.set_page_config(page_title="Diversity Insights", layout="wide")
st.title("📊 Diversity Insights")
st.caption("Derived indicators: language counts + entropy index (if % exists) + relationships.")

if not {"countries", "languages"}.issubset(st.session_state.keys()):
    st.error("Open Home first (main.py).")
    st.stop()

countries = st.session_state["countries"]
langs = st.session_state["languages"]

stats = build_country_language_stats(countries, langs)

tab1, tab2 = st.tabs(["Maps", "Relationships"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.choropleth(
            stats,
            locations="Code",
            locationmode="ISO-3",
            color="n_languages",
            hover_name="Name",
            template="plotly_dark",
            title="Number of languages per country",
        )
        fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if stats["entropy"].notna().any():
            fig2 = px.choropleth(
                stats,
                locations="Code",
                locationmode="ISO-3",
                color="entropy",
                hover_name="Name",
                template="plotly_dark",
                title="Shannon entropy (from percentages)",
            )
            fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Entropy is unavailable because Percentage is missing/empty in the language table.")

with tab2:
    df = stats.dropna(subset=["Population", "n_languages"]).copy()
    fig3 = px.scatter(
        df,
        x="Population",
        y="n_languages",
        color="Continent",
        hover_name="Name",
        template="plotly_dark",
        title="Population vs number of languages",
    )
    fig3.update_layout(margin=dict(l=0, r=0, t=60, b=0))
    st.plotly_chart(fig3, use_container_width=True)

import streamlit as st
import pandas as pd

from utils import inject_global_css, render_hero, card
from utils import get_data
cities, countries, langs = get_data()


# IMPORTANT: set_page_config should be the first Streamlit command on the page
st.set_page_config(
    page_title="Popuinatlas — Geo-Linguistic Atlas",
    page_icon="🧭",
    layout="wide",
)

inject_global_css()

# -------------------------
# Identity (your seminar info)
# -------------------------
STUDENT_NAME = "Ezzat Bachour"
MAJOR = "B.Sc. Psychology"
UNIVERSITY = "Leuphana University Lüneburg"
MATRICULATION_NUMBER = "3045988"

SEMINAR_NAME = "Mastering Data Visualization with Python (S)"
LECTURER_NAME = "Jorge Gustavo Rodríguez Aboytes"

# -------------------------
# Data
# -------------------------
@st.cache_data
def load_data():
    cities = pd.read_csv("data/city.csv")
    countries = pd.read_csv("data/country.csv")
    languages = pd.read_csv("data/countrylanguage.csv")
    return cities, countries, languages

cities, countries, languages = load_data()

st.session_state["cities"] = cities
st.session_state["countries"] = countries
st.session_state["languages"] = languages

# -------------------------
# Hero header
# -------------------------
render_hero(
    "🧭",
    "World Geo-Linguistic Dashboard",
    "Explore countries, cities, and language distributions through interactive maps + relational analytics.",
)

# -------------------------
# Intro + Identity
# -------------------------
left, right = st.columns([1.3, 1])

with left:
    card(
        "What this app is",
        """
        <ul>
          <li><b>Geo layer:</b> country drill-downs and region context</li>
          <li><b>Language layer:</b> official vs. non-official languages + prevalence (when available)</li>
          <li><b>City layer:</b> population-driven exploration of urban centers</li>
        </ul>
        """,
    )

    card(
        "How to use it",
        """
        <ul>
          <li>Use the <b>sidebar</b> to navigate pages.</li>
          <li>On <b>Country Explorer</b>, click a country to update details instantly.</li>
          <li>On <b>Language Explorer</b>, choose a language to see where it’s spoken.</li>
        </ul>
        """,
    )

with right:
    st.markdown("### 📌 Project metadata")
    st.markdown(
        f"""
        **Author:** {STUDENT_NAME}  
        **Program:** {MAJOR} · {UNIVERSITY}  
        **Matriculation No.:** `{MATRICULATION_NUMBER}`  
        **Seminar:** *{SEMINAR_NAME}*  
        **Lecturer:** *{LECTURER_NAME}*
        """
    )

    st.markdown("### 📊 Dataset snapshot")
    k1, k2, k3 = st.columns(3)
    k1.metric("Countries", f"{countries.shape[0]:,}")
    k2.metric("Cities", f"{cities.shape[0]:,}")
    k3.metric("Language rows", f"{languages.shape[0]:,}")

st.divider()

# -------------------------
# Preview area (cleaner than 3 stacked tables)
# -------------------------
st.markdown("## 🔍 Quick previews")
tab1, tab2, tab3 = st.tabs(["🌍 Countries", "🗣️ Languages", "🏙️ Cities"])

with tab1:
    st.caption("Country table preview (top rows).")
    st.dataframe(countries.head(20), use_container_width=True)

with tab2:
    st.caption("Country-language table preview (top rows).")
    st.dataframe(languages.head(20), use_container_width=True)

with tab3:
    st.caption("City table preview (top rows).")
    st.dataframe(cities.head(20), use_container_width=True)

st.divider()

# -------------------------
# Footer guidance
# -------------------------
st.info("✅ Use the sidebar to navigate between pages 👈 (Country Explorer • Language Explorer • etc.)")

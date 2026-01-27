import streamlit as st
import pandas as pd
import plotly.express as px
from utils import (
    APP_NAME, APP_TAGLINE, APP_ICON,
    STUDENT_NAME, MAJOR, UNIVERSITY, MATRICULATION_NUMBER,
    SEMINAR_NAME, LECTURER_NAME,
    ensure_data_in_session, sidebar_brand
)

st.set_page_config(
    page_title=f"{APP_NAME} — Overview",
    page_icon=APP_ICON,
    layout="wide",
)

ensure_data_in_session()
sidebar_brand()

countries = st.session_state["countries"].copy()
cities = st.session_state["cities"].copy()
langs = st.session_state["languages"].copy()

st.title(f"{APP_ICON} {APP_NAME}")
st.subheader(APP_TAGLINE)
st.caption("Explore the world’s linguistic landscape through interactive maps, drilldowns, and city-level analytics.")

st.markdown(
    f"""
**Author:** {STUDENT_NAME}  
**Program:** {MAJOR} · {UNIVERSITY}  
**Matriculation No.:** `{MATRICULATION_NUMBER}`  
**Seminar:** *{SEMINAR_NAME}*  
**Lecturer:** *{LECTURER_NAME}*
"""
)

st.divider()

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Countries", f"{countries.shape[0]:,}")
k2.metric("Cities", f"{cities.shape[0]:,}")
k3.metric("Language rows", f"{langs.shape[0]:,}")
k4.metric("Unique languages", f"{langs['Language'].nunique():,}" if "Language" in langs.columns else "—")

st.divider()

# What to do (clean cards)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 🧭 Country Explorer")
    st.write("Click a country on the map and inspect languages + top cities.")
with c2:
    st.markdown("### 🔎 Language Explorer")
    st.write("Pick a language and see where it’s spoken and how official it is.")
with c3:
    st.markdown("### 🌐 Insights")
    st.write("Quick diversity indicators and city population patterns.")

st.divider()

# Previews in tabs (much nicer UX)
tab1, tab2, tab3 = st.tabs(["🌍 Countries", "🗣️ Languages", "🏙️ Cities"])  # official tabs API :contentReference[oaicite:3]{index=3}

with tab1:
    st.caption("Sample from country.csv")
    st.dataframe(countries.head(20), use_container_width=True)

with tab2:
    st.caption("Sample from countrylanguage.csv")
    st.dataframe(langs.head(20), use_container_width=True)

with tab3:
    st.caption("Sample from city.csv")
    st.dataframe(cities.head(20), use_container_width=True)

st.info("Use the sidebar navigation to open the other pages 👈")

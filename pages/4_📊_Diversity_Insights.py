import streamlit as st
import pandas as pd
import plotly.express as px
from utils import APP_NAME, APP_ICON, ensure_data_in_session, sidebar_brand, normalize_columns

st.set_page_config(
    page_title=f"{APP_NAME} — Diversity Insights",
    page_icon=APP_ICON,
    layout="wide",
)

ensure_data_in_session()
sidebar_brand()

langs = normalize_columns(st.session_state["languages"].copy())
countries = normalize_columns(st.session_state["countries"].copy())

st.title("🌐 Diversity Insights")
st.caption("Derived indicators from the country-language table (quick comparative view).")

langs["CountryCode"] = langs["CountryCode"].astype(str)
langs["Language"] = langs["Language"].astype(str)
if "IsOfficial" in langs.columns:
    langs["IsOfficial"] = langs["IsOfficial"].astype(str).str.upper()
else:
    langs["IsOfficial"] = "?"

# Count languages per country
counts = (
    langs.groupby("CountryCode")["Language"]
    .nunique()
    .reset_index(name="num_languages")
)

# Count official languages per country
official_counts = (
    langs[langs["IsOfficial"] == "T"]
    .groupby("CountryCode")["Language"]
    .nunique()
    .reset_index(name="num_official_languages")
)

df = counts.merge(official_counts, on="CountryCode", how="left").fillna({"num_official_languages": 0})
df = df.merge(countries, left_on="CountryCode", right_on="Code", how="left")

k1, k2, k3 = st.columns(3)
k1.metric("Countries (with language rows)", f"{df['CountryCode'].nunique():,}")
k2.metric("Median languages/country", f"{df['num_languages'].median():.0f}")
k3.metric("Max languages/country", f"{df['num_languages'].max():.0f}")

st.divider()

tab1, tab2 = st.tabs(["🏆 Top countries", "📊 Distribution"])

with tab1:
    top = df.sort_values("num_languages", ascending=False).head(25)
    show_cols = [c for c in ["Name", "Continent", "Region", "num_languages", "num_official_languages"] if c in top.columns]
    st.dataframe(top[show_cols].reset_index(drop=True), use_container_width=True)

with tab2:
    fig = px.histogram(df, x="num_languages", nbins=30, title="Distribution: number of languages per country", template="plotly_dark")
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import APP_NAME, APP_ICON, ensure_data_in_session, sidebar_brand, normalize_columns

st.set_page_config(
    page_title=f"{APP_NAME} — Language Explorer",
    page_icon=APP_ICON,
    layout="wide",
)

ensure_data_in_session()
sidebar_brand()

langs = normalize_columns(st.session_state["languages"].copy())
countries = normalize_columns(st.session_state["countries"].copy())

st.title("🔎 Language Explorer")
st.caption("Pick a language and see where it is spoken, whether it is official, and prevalence when available.")

if "Language" not in langs.columns:
    st.error(f"Missing 'Language' column. Found: {langs.columns.tolist()}")
    st.stop()

langs["Language"] = langs["Language"].astype(str)
langs["CountryCode"] = langs["CountryCode"].astype(str)
countries["Code"] = countries["Code"].astype(str)

if "IsOfficial" in langs.columns:
    langs["IsOfficial"] = langs["IsOfficial"].astype(str).str.upper()
else:
    langs["IsOfficial"] = "?"

if "Percentage" in langs.columns:
    langs["Percentage"] = pd.to_numeric(langs["Percentage"], errors="coerce")

all_languages = sorted(langs["Language"].dropna().unique().tolist())

left, right = st.columns([1.2, 1])

with left:
    q = st.text_input("Search language (optional)", value="")
    candidates = [x for x in all_languages if q.lower() in x.lower()] if q else all_languages
    selected_language = st.selectbox("Choose a language", candidates, key="lang_select")

with right:
    only_official = st.toggle("Show only official occurrences", value=False)

df = langs[langs["Language"] == selected_language].copy()
if only_official:
    df = df[df["IsOfficial"] == "T"].copy()

merged = df.merge(countries, left_on="CountryCode", right_on="Code", how="left")

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric("Selected language", selected_language)
k2.metric("Countries where found", f"{merged['Name'].nunique():,}" if "Name" in merged.columns else "—")
k3.metric("Official entries", f"{(merged.get('IsOfficial','') == 'T').sum():,}")

st.divider()

# Table + chart
tabA, tabB = st.tabs(["📄 Table", "📊 Top prevalence"])  # official tabs :contentReference[oaicite:5]{index=5}

with tabA:
    cols = []
    for c in ["Name", "Continent", "Region", "IsOfficial", "Percentage"]:
        if c in merged.columns:
            cols.append(c)

    out = merged[cols].copy() if cols else merged.copy()
    if "Percentage" in out.columns:
        out = out.sort_values("Percentage", ascending=False)
    st.dataframe(out.reset_index(drop=True), use_container_width=True)

with tabB:
    if "Percentage" in merged.columns and merged["Percentage"].notna().any() and "Name" in merged.columns:
        top = merged.sort_values("Percentage", ascending=False).head(20)
        fig = px.bar(top, x="Name", y="Percentage", title=f"Top prevalence for: {selected_language}", template="plotly_dark")
        fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No prevalence (% column) available for this selection in the dataset.")

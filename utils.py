import streamlit as st
import pandas as pd

APP_NAME = "Popuinatlas"
APP_TAGLINE = "A Geo-Linguistic Atlas of Countries, Cities & Languages"
APP_ICON = "🧭"

STUDENT_NAME = "Ezzat Bachour"
MAJOR = "B.Sc. Psychology"
UNIVERSITY = "Leuphana University Lüneburg"
MATRICULATION_NUMBER = "3045988"

SEMINAR_NAME = "Mastering Data Visualization with Python (S)"
LECTURER_NAME = "Jorge Gustavo Rodríguez Aboytes"

@st.cache_data
def load_data():
    cities = pd.read_csv("data/city.csv")
    countries = pd.read_csv("data/country.csv")
    languages = pd.read_csv("data/countrylanguage.csv")
    return cities, countries, languages

def ensure_data_in_session():
    """Load into st.session_state once, used by every page."""
    if not {"cities", "countries", "languages"}.issubset(st.session_state.keys()):
        cities, countries, languages = load_data()
        st.session_state["cities"] = cities
        st.session_state["countries"] = countries
        st.session_state["languages"] = languages

def sidebar_brand():
    with st.sidebar:
        st.markdown(f"## {APP_ICON} {APP_NAME}")
        st.caption(APP_TAGLINE)
        st.divider()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Fix common Kaggle merge artifacts like Name_x / Name_y."""
    rename_map = {
        "Name_x": "Name",
        "Name_y": "Name",
        "Code_x": "Code",
        "Code_y": "Code",
        "CountryCode_x": "CountryCode",
        "CountryCode_y": "CountryCode",
    }
    for old, new in rename_map.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    return df

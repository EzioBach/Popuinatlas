import streamlit as st
from utils import load_data, prep_tables, prep_worldcities

st.set_page_config(page_title="Popuinatlas - A Geo-Linguistic Atlas of Countries, Cities & Languages", layout="wide")

# --- Personalization ---
STUDENT_NAME = "Ezzat Bachour"
MAJOR = "B.Sc. Psychology"
UNIVERSITY = "Leuphana University Lüneburg"
MATRICULATION_NUMBER = "3045988"
SEMINAR_NAME = "Mastering Data Visualization with Python (S)"
LECTURER_NAME = "Jorge Gustavo Rodríguez Aboytes"

cities, countries, langs, worldcities = load_data()
cities, countries, langs = prep_tables(cities, countries, langs)
worldcities = prep_worldcities(worldcities)

st.session_state["cities"] = cities
st.session_state["countries"] = countries
st.session_state["languages"] = langs
st.session_state["worldcities"] = worldcities  # may be None if file not present

st.markdown(
f"""
# 🌍 World Languages Dashboard

**Author:** {STUDENT_NAME}  
**Program:** {MAJOR} · {UNIVERSITY}  
**Matriculation No.:** `{MATRICULATION_NUMBER}`  
**Seminar:** *{SEMINAR_NAME}*  
**Lecturer:** *{LECTURER_NAME}*

---
"""
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries", f"{countries.shape[0]:,}")
c2.metric("Cities (MySQL World)", f"{cities.shape[0]:,}")
c3.metric("Language rows", f"{langs.shape[0]:,}")
c4.metric("Lat/Lon cities loaded", "Yes" if worldcities is not None else "No")

st.markdown(
"""
### What you can do
- **Overview:** global choropleths + top languages
- **Country Explorer:** click a country on a clean map to drill down
- **Language Explorer:** pick a language → see where it’s listed
- **Diversity Insights:** language count + entropy-based diversity index
- **City Analytics:** urban concentration patterns (no fake geo)
- **City Map:** real lat/lon city mapping (if you added worldcities.csv)
"""
)

st.divider()
st.subheader("Data preview")
tab1, tab2, tab3 = st.tabs(["Countries", "Languages", "Cities"])
with tab1: st.dataframe(countries.head(10), use_container_width=True)
with tab2: st.dataframe(langs.head(10), use_container_width=True)
with tab3: st.dataframe(cities.head(10), use_container_width=True)

if worldcities is not None:
    st.subheader("Preview: Lat/Lon Cities (worldcities.csv)")
    st.dataframe(worldcities.head(10), use_container_width=True)

st.info("Use the sidebar to navigate between pages.")

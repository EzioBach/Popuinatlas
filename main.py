import streamlit as st
from utils import inject_global_css, render_hero, get_data, format_int

st.set_page_config(
    page_title="Popuinatlas — A Geo-Linguistic Atlas",
    page_icon="🧭",
    layout="wide",
)

inject_global_css()
render_hero(
    "🧭",
    "Popuinatlas — A Geo-Linguistic Atlas",
    "Explore countries, cities, and language distributions through interactive maps + relational analytics.",
    pill="World Geo-Linguistic Dashboard",
)

# Load once (cached) and store in session_state for all pages
cities, countries, langs, worldcities = get_data()

# ---- Metadata (edit freely) ----
STUDENT_NAME = "Ezzat Bachour"
MAJOR = "B.Sc. Psychology"
UNIVERSITY = "Leuphana University Lüneburg"
MATRICULATION_NUMBER = "3045988"
SEMINAR_NAME = "Mastering Data Visualization with Python (S)"
LECTURER_NAME = "Jorge Gustavo Rodríguez Aboytes"

left, right = st.columns([1.25, 1])

with left:
    st.subheader("What this app is")
    st.markdown(
        """
- **Country drill-downs**: borders, region context, population
- **Language structure**: official vs non-official, prevalence (when available)
- **City patterns**: urban concentration - lat/lon world city map
        """
    )

    st.subheader("How to use it")
    st.markdown(
        """
Use the **sidebar** pages:
- 🌍 Overview → global KPIs + best maps  
- 🧭 Country Explorer → pick a country and drill down  
- 🗣️ Language Explorer → pick a language and see where it appears  
- 📊 Diversity Insights → diversity metrics
- 🏙️ City Analytics → lat/lon city map + city population analytics  
        """
    )

with right:
    st.subheader("📌 Project metadata")
    st.markdown(
        f"""
**Author:** {STUDENT_NAME}  
**Program:** {MAJOR} · {UNIVERSITY}  
**Matriculation No.:** `{MATRICULATION_NUMBER}`  
**Seminar:** *{SEMINAR_NAME}*  
**Lecturer:** *{LECTURER_NAME}*
        """
    )

    st.subheader("📦 Dataset snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Countries", format_int(countries.shape[0]))
    c2.metric("Cities (MySQL)", format_int(cities.shape[0]))
    c3.metric("Language rows", format_int(langs.shape[0]))
    c4.metric("Worldcities (lat/lon)", format_int(worldcities.shape[0]) if worldcities is not None else "—")

st.divider()

with st.expander("Preview raw tables (first 10 rows)"):
    st.write("Countries")
    st.dataframe(countries.head(10), use_container_width=True)
    st.write("Languages")
    st.dataframe(langs.head(10), use_container_width=True)
    st.write("Cities")
    st.dataframe(cities.head(10), use_container_width=True)

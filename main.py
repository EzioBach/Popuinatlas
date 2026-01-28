import streamlit as st

from utils import inject_global_css, render_hero, get_data

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
    pill="Geo-Linguistic Dashboard",
)

# Load data (and populate session_state for all pages)
cities, countries, langs, worldcities = get_data()

# ---- Metadata ----
STUDENT_NAME = "Ezzat Bachour"
MAJOR = "B.Sc. Psychology"
UNIVERSITY = "Leuphana University Lüneburg"
MATRICULATION_NUMBER = "3045988"
SEMINAR_NAME = "Mastering Data Visualization with Python (S)"
LECTURER_NAME = "Jorge Gustavo Rodríguez Aboytes"

left, right = st.columns([1.2, 1])

with left:
    st.subheader("What this app is")
    st.markdown(
        """
- **Country drill-downs**: borders, region context, population, top cities  
- **Language structure**: official vs. non-official + prevalence (when available)  
- **Global views**: diversity maps, top languages, relationships with population  
- **Optional city map**: lat/lon visualization if `worldcities.csv` exists  
        """
    )

    st.subheader("How to use it")
    st.markdown(
        """
Use the **sidebar** to move between pages:
- 🌍 **Overview** → global KPIs + high-signal maps  
- 🧭 **Country Explorer** → click/select a country and drill down  
- 🗣️ **Language Explorer** → pick a language and see where it appears  
- 📊 **Diversity Insights** → diversity metrics (incl. entropy if % exists)  
- 🏙️ **City Analytics** → city map + population analytics  
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
    c1.metric("Countries", f"{countries.shape[0]:,}")
    c2.metric("Cities", f"{cities.shape[0]:,}")
    c3.metric("Language rows", f"{langs.shape[0]:,}")
    c4.metric("Worldcities", "✅" if worldcities is not None else "—")

st.divider()

with st.expander("Preview raw tables (first 10 rows each)"):
    st.write("Countries")
    st.dataframe(countries.head(10), use_container_width=True)
    st.write("Languages")
    st.dataframe(langs.head(10), use_container_width=True)
    st.write("Cities")
    st.dataframe(cities.head(10), use_container_width=True)

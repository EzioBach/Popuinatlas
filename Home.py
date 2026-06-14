import streamlit as st
from utils import set_theme, sidebar_header

set_theme()
user_id = sidebar_header()

st.title("🌊 Ocean Legacy Challenge")
st.caption("A psychology-based intervention for sustainable fashion behaviour")

st.markdown(
    """
    <div class="hero-box">
    <div style='display:flex;align-items:center;gap:18px;flex-wrap:wrap;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/9/93/Leuphana_Universität_Lüneburg_Logo_2020.svg' width='120' style='border-radius:14px;border:1px solid rgba(255,255,255,0.2);'>
            <div>
        <h2>What kind of ocean will future generations inherit?</h2>
        <p>
        This challenge helps university students reflect on fast-fashion behaviour,
        take practical sustainable actions, and build long-term habits that reduce
        harm to ocean ecosystems.
                <p style='margin:0;'>Leuphana University · Group 5 · Andrea Andriamalala· Ezzat Bachour · Leen Ghafar· Maha El kadiri</p>
        </p>
    </div>
   
    """,
    unsafe_allow_html=True
)

st.markdown("### Why this project matters")
col1, col2, col3 = st.columns(3)

with col1:
    st.error("Fast fashion creates waste")
    st.write("Huge amounts of clothing are produced, used briefly, and discarded.")

with col2:
    st.warning("Textiles affect oceans")
    st.write("Synthetic fibres and production systems contribute to marine pollution.")

with col3:
    st.info("Students are a key audience")
    st.write("Young adults are highly exposed to trends, but their habits are still flexible.")

st.markdown("### How the challenge works")
st.markdown(
    """
    1. **Week 1 — Awareness & Baseline:** reflect on current clothing habits and triggers.  
    2. **Week 2 — Sustainable Action:** complete practical alternatives to fast fashion.  
    3. **Week 3 — Legacy Plan:** create personal rules and write a message to the child.  
    4. **Dashboard:** track progress, reflections, and behaviour change over time.
    """
)

st.markdown("### Intervention logic")
st.markdown(
    """
    - A **child-based future-generation prompt** makes the issue feel concrete.
    - A **structured challenge** turns good intentions into action.
    - **Weekly-style action steps** support commitment and self-regulation.
    - A **final message** reinforces responsibility and identity change.
    """
)

st.markdown("### Start here")
if user_id:
    st.success("Open the left sidebar and begin with **Day 1 Awareness**.")
else:
    st.info("Enter a Participant ID in the sidebar to unlock the full journey.")
st.markdown("### Our team")
st.markdown(
    "<span class='team-pill'>Andrea . </span><span class='team-pill'> Ezzat . </span><span class='team-pill'>Leen . </span><span class='team-pill'>Maha .</span>",
    unsafe_allow_html=True,
)

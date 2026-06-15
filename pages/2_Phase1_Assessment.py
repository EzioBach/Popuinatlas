import streamlit as st
import plotly.graph_objects as go
from utils import set_theme, sidebar_header, load_user, save_user, today, send_report_to_email

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

# Load user data to check condition
data = load_user(user_id) if user_id else None

st.title("📋 T1 Baseline Assessment")
st.caption("Phase 1: Understanding current behaviours and psychological drivers")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

# --- INTERVENTION-ONLY TASK INSTRUCTION ---
if data and data.get("condition") == "full_intervention":
    st.markdown("---")
    st.markdown("### 👗 Challenge Task: The 7-Outfit Audit")
    st.info(
        "**Your Task for Week 2:** \n"
        "To help you realize the abundance in your current wardrobe, please curate 7 different "
        "outfit combinations from your existing clothes before our next session. \n\n"
        "**How to prepare:** You don't need to list them here. Just experiment in your closet "
        "this week, take photos if you like, and be ready to discuss your combinations "
        "and any 'fashion freedom' you discovered when we meet next!"
    )
    st.checkbox("I acknowledge this task and will prepare my 7 outfits for the next session.")
    st.markdown("---")

# --- PSYCHOLOGICAL ASSESSMENT ---
st.markdown("### Section A: Psychological Assessment")
st.write("Indicate your agreement (1 = Strongly Disagree, 7 = Strongly Agree).")

col1, col2 = st.columns(2)
with col1:
    nature_conn = st.slider("1. I feel a deep emotional connection to marine ecosystems.", 1, 7, 4)
    future_gen = st.slider("2. I feel a moral obligation to protect the oceans for future generations.", 1, 7, 4)
    resp_feel = st.slider("3. My personal clothing choices directly impact ocean health.", 1, 7, 4)

with col2:
    autonomy = st.slider("4. I want to change my habits because it aligns with my personal values.", 1, 7, 4)
    competence = st.slider("5. I am confident I know how to find sustainable fashion alternatives.", 1, 7, 4)
    social_norm = st.slider("6. Most people my age care about sustainable fashion.", 1, 7, 4)

# --- BEHAVIOURAL AUDIT ---
st.markdown("### Section B: Behavioural Audit")
fast_fashion_items = st.number_input("How many newly produced garments did you purchase in the last 30 days?", min_value=0, max_value=50, value=2)
main_triggers = st.multiselect("Primary triggers for fast-fashion consumption:", ["Social media trends", "Sales/Discounts", "Need for novelty", "Peer pressure", "Stress/Boredom buying"])

# --- VISUAL PROFILE ---
st.markdown("### Your Psychological Profile")
if st.button("📊 Generate My Profile Visual"):
    categories = ['Nature Connection', 'Future Gen Obligation', 'Responsibility', 'Autonomy', 'Competence', 'Social Norms']
    values = [nature_conn, future_gen, resp_feel, autonomy, competence, social_norm]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', line_color='#5ea8c0', fillcolor='rgba(94, 168, 192, 0.4)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 7])), showlegend=False, template="plotly_white")
    st.plotly_chart(fig)

# --- SAVE & EMAIL ---
if st.button("💾 Save T1 Baseline & Lock Data", type="primary"):
    data = load_user(user_id)
    data["progress"] = max(data["progress"], 1)

    data["baseline"].update({
        "nature_conn": nature_conn, "future_gen": future_gen, "resp_feel": resp_feel,
        "autonomy": autonomy, "competence": competence, "social_norm": social_norm,
        "fast_fashion_items": fast_fashion_items, "main_triggers": main_triggers
    })

    data["logs"].append({"date": today(), "phase": "T1_baseline_complete"})
    save_user(user_id, data)
    
    st.success("T1 Baseline successfully saved. Your psychological profile is locked.")
    
    with st.spinner("Transmitting data to research team..."):
        try:
            send_report_to_email(user_id, data)
            st.success("📧 Data emailed to the research team!")
        except Exception as e:
            st.error(f"Email failed to send. Error: {e}")

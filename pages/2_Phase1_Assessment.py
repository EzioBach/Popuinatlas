import streamlit as st
import plotly.graph_objects as go
from utils import set_theme, sidebar_header, load_user, save_user, today, send_report_to_email

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

data = load_user(user_id) if user_id else None

st.title("📋 T1 Baseline Assessment")
st.caption("Phase 1: Understanding current behaviours and psychological drivers")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

outfit_audit = {}
if data and data.get("condition") == "full_intervention":
    st.markdown("---")
    st.markdown("### 👗 Challenge Task: The 7-Outfit Audit")
    st.write("Since you are in the full challenge, let's start by auditing your existing abundance. Please describe 7 different outfits you can create from what you already own.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        outfit_audit["Outfit 1"] = st.text_input("Outfit 1 description", placeholder="e.g., Blue jeans + white shirt")
        outfit_audit["Outfit 2"] = st.text_input("Outfit 2 description")
        outfit_audit["Outfit 3"] = st.text_input("Outfit 3 description")
        outfit_audit["Outfit 4"] = st.text_input("Outfit 4 description")
    with col_b:
        outfit_audit["Outfit 5"] = st.text_input("Outfit 5 description")
        outfit_audit["Outfit 6"] = st.text_input("Outfit 6 description")
        outfit_audit["Outfit 7"] = st.text_input("Outfit 7 description")
    st.markdown("---")

st.markdown("### Section A: Psychological Assessment")
st.write("Indicate your agreement (1 = Strongly Disagree, 7 = Strongly Agree).")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Emotional & Nature Connection**")
    nature_conn = st.slider("1. I feel a deep emotional connection to marine ecosystems.", 1, 7, 4)
    future_gen = st.slider("2. I feel a moral obligation to protect the oceans for future generations.", 1, 7, 4)
    resp_feel = st.slider("3. My personal clothing choices directly impact ocean health.", 1, 7, 4)

with col2:
    st.markdown("**Motivation & Competence (SDT)**")
    autonomy = st.slider("4. I want to change my habits because it aligns with my personal values.", 1, 7, 4)
    competence = st.slider("5. I am confident I know how to find sustainable fashion alternatives.", 1, 7, 4)
    social_norm = st.slider("6. Most people my age care about sustainable fashion.", 1, 7, 4)

st.markdown("### Section B: Behavioural Audit")
fast_fashion_items = st.number_input(
    "How many newly produced garments did you purchase in the last 30 days?",
    min_value=0, max_value=50, value=2
)

main_triggers = st.multiselect(
    "Primary triggers for fast-fashion consumption (Select all that apply):",
    ["Social media trends", "Sales/Discounts", "Need for novelty", "Peer pressure", "Stress/Boredom buying"]
)

st.markdown("### Your Psychological Profile")
if st.button("📊 Generate My Profile Visual"):
    categories = [
        'Nature Connection', 'Future Gen Obligation', 
        'Responsibility', 'Autonomy', 
        'Competence', 'Social Norms'
    ]
    values = [nature_conn, future_gen, resp_feel, autonomy, competence, social_norm]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        line_color='#5ea8c0',
        fillcolor='rgba(94, 168, 192, 0.4)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig)

if st.button("💾 Save T1 Baseline & Lock Data", type="primary"):
    data = load_user(user_id)
    data["progress"] = max(data["progress"], 1)

    data["baseline"] = {
        "nature_conn": nature_conn,
        "future_gen": future_gen,
        "resp_feel": resp_feel,
        "autonomy": autonomy,
        "competence": competence,
        "social_norm": social_norm,
        "fast_fashion_items": fast_fashion_items,
        "main_triggers": main_triggers
    }

    data["logs"].append({"date": today(), "phase": "T1_baseline_complete"})
    save_user(user_id, data)
    
    st.success("T1 Baseline successfully saved. Your psychological profile is locked.")
    st.balloons()
    
    # --- EMAIL TRIGGER BLOCK ---
    with st.spinner("Transmitting encrypted baseline data to research team..."):
        try:
            send_report_to_email(user_id, data)
            st.success("📧 T1 Baseline successfully emailed to the research team!")
        except Exception as e:
            st.error(f"Email failed to send. Please check your secrets.toml file and Gmail App Passwords. Error: {e}")

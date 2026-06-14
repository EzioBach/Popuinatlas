import streamlit as st
import plotly.graph_objects as go
from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("🌍 Week 1 — Awareness & Baseline")
st.caption("Understand your current fashion habits and how they connect to ocean health")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

with st.expander("📖 Read: Why are we measuring this?", expanded=False):
    st.write(
        "To create lasting behavioral change, we look at **Self-Determination Theory**. "
        "By understanding your autonomy (your personal values), competence (your confidence), "
        "and relatedness (your connection to nature and others), we can tailor this 30-day "
        "journey to be much more effective."
    )

st.markdown("### Psychological Baseline Assessment")
st.write("Indicate how strongly you agree with the following (1 = Strongly Disagree, 7 = Strongly Agree).")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Nature Relatedness & Responsibility**")
    nature_connection = st.slider("I feel a deep, personal connection to marine ecosystems.", 1, 7, 4)
    responsibility_feeling = st.slider("My daily consumer choices directly impact future oceans.", 1, 7, 4)

with col_b:
    st.markdown("**Autonomy & Competence**")
    autonomy_scale = st.slider("I want to reduce fast-fashion because it aligns with my personal values.", 1, 7, 4)
    competence_scale = st.slider("I feel confident in my ability to utilize sustainable fashion alternatives.", 1, 7, 4)

st.markdown("### Behavioral Audit")
fast_fashion_items = st.number_input(
    "How many newly produced garments did you purchase in the last 30 days?",
    min_value=0, max_value=50, value=2
)

# Extended to multiselect for more options
main_triggers = st.multiselect(
    "Identify your primary behavioral triggers for fast-fashion consumption (Select all that apply):",
    [
        "Algorithmic social media trends",
        "Scarcity marketing (Sales/Discounts)",
        "Psychological need for novelty",
        "Social conformity / Peer pressure",
        "Emotional regulation (Stress/Boredom buying)",
        "Special events / One-time occasions"
    ],
    default=["Psychological need for novelty"]
)

goal = st.text_input(
    "Implementation Goal",
    placeholder="Example: I will unsubscribed from 3 fast-fashion email lists today."
)

st.markdown("### Your Psychological Profile")
if st.button("📊 Generate My Profile Visual", use_container_width=True):
    categories = ['Nature Connection', 'Responsibility', 'Autonomy', 'Competence']
    values = [nature_connection, responsibility_feeling, autonomy_scale, competence_scale]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], # Close the loop
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
    st.plotly_chart(fig, use_container_width=True)

if st.button("Save Week 1 Baseline", type="primary", use_container_width=True):
    if not goal.strip():
        st.error("Please write a personal goal before saving.")
        st.stop()

    data = load_user(user_id)[cite: 3]
    data["progress"] = max(data["progress"], 1)[cite: 3]

    data["baseline"] = {
        "nature_connection": nature_connection,
        "responsibility_feeling": responsibility_feeling,
        "autonomy_scale": autonomy_scale,
        "competence_scale": competence_scale,
        "fast_fashion_items": fast_fashion_items,
        "main_triggers": main_triggers,
        "goal": goal
    }[cite: 3]

    data["logs"].append({
        "date": today(),
        "phase": "week1_awareness",
        "goal": goal
    })[cite: 3]

    save_user(user_id, data)[cite: 3]
    st.success("Week 1 saved. You have completed the awareness stage.")

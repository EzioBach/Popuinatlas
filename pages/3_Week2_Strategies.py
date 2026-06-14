import streamlit as st
from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("♻️ Week 2 — Action Strategies")
st.caption("Turn intention into concrete behavior through active implementation.")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)

if data["condition"] in ["control", "video_only"]:
    st.warning("🔒 **Access Restricted**")
    st.info(
        "Based on your assigned study cohort, you do not require access to the daily tracking modules. "
        "Thank you for completing your T1 Baseline Assessment. Please return at the end of the 30-day period "
        "to complete your final T2 Post-Test."
    )
    st.stop()

if data["progress"] < 1:
    st.warning("Complete Week 1 first.")
    st.stop()

st.markdown("### Select Your Actions for Today")
st.write("Browse the categories below and check off the interventions you successfully implemented.")

completed = []

with st.expander("🛑 Strategy A: Refuse & Reduce", expanded=True):
    if st.checkbox("Paused for 24 hours before a possible fast-fashion purchase"): completed.append("Reflected before buying")
    if st.checkbox("Unsubscribed from a fast-fashion newsletter or unfollowed a brand"): completed.append("Digital boundary setting")

with st.expander("🔄 Strategy B: Reuse & Reimagine", expanded=False):
    if st.checkbox("Created a completely new outfit from clothes I already own"): completed.append("Reused existing outfit")
    if st.checkbox("Borrowed, swapped, or arranged a clothing swap with friends"): completed.append("Borrowed/swapped clothing")

with st.expander("🧵 Strategy C: Repair & Second-Hand", expanded=False):
    if st.checkbox("Repaired, tailored, or customized one clothing item"): completed.append("Repaired clothing")
    if st.checkbox("Purchased or searched exclusively for a second-hand alternative"): completed.append("Searched second-hand")

st.markdown("### Daily Reflection")
temptation_today = st.radio(
    "Did you experience psychological friction (temptation) to buy fast fashion today?",
    ["No temptation", "Mild temptation", "Strong temptation", "Overwhelming urge"],
    horizontal=True
)

if_trigger = st.text_input("Implementation Intention: IF I want to buy something new tomorrow, THEN I will...")

if st.button("💾 Log Daily Actions", type="primary", use_container_width=True):
    if len(completed) < 1:
        st.error("Please select at least 1 sustainable action to log today's progress.")
        st.stop()

    data["progress"] = max(data["progress"], 2)

    for action_name in completed:
        data["actions"].append({
            "date": today(),
            "action": action_name,
            "completed": True
        })

    save_user(user_id, data)
    st.success(f"Successfully logged {len(completed)} actions for today!")
    st.balloons()

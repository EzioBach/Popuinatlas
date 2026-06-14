import streamlit as st

from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("♻️ Day 2 — Sustainable Action Strategies")
st.caption("Turn intention into concrete behaviour")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)

if data["progress"] < 1:
    st.warning("Complete Day 1 first.")
    st.stop()

st.markdown(
    """
    **Today's challenge**
    Choose sustainable alternatives to fast fashion and record what you actually did.
    """
)

st.markdown("### Action checklist")
c1, c2 = st.columns(2)

with c1:
    act1 = st.checkbox("Created a new outfit from clothes I already own")
    act2 = st.checkbox("Repaired or customised one clothing item")
    act3 = st.checkbox("Shared or photographed an outfit I reused")

with c2:
    act4 = st.checkbox("Borrowed, swapped, or discussed swapping clothes")
    act5 = st.checkbox("Looked for a second-hand alternative instead of buying new")
    act6 = st.checkbox("Paused and reflected before a possible fast-fashion purchase")

temptation_today = st.selectbox(
    "Did you feel tempted to buy fast fashion today?",
    ["No", "A little", "Yes", "Very much"]
)

if_trigger = st.text_input(
    "If-then plan: IF I want to buy something new, THEN I will..."
)

best_action = st.selectbox(
    "Which action had the biggest impact today?",
    [
        "Rewearing",
        "Repairing",
        "Swapping",
        "Second-hand search",
        "Reflection before buying"
    ]
)

day2_reflection = st.text_area(
    "What helped you most to act sustainably today?"
)

if st.button("Save Day 2", use_container_width=True):
    completed = [
        ("Reused existing outfit", act1),
        ("Repaired/customised clothing", act2),
        ("Shared reused outfit", act3),
        ("Borrowed/swapped clothing", act4),
        ("Searched second-hand first", act5),
        ("Reflected before buying", act6),
    ]

    completed_count = sum(1 for _, done in completed if done)

    if completed_count < 2:
        st.error("Please complete at least 2 sustainable actions before saving Day 2.")
        st.stop()

    data = load_user(user_id)
    data["progress"] = max(data["progress"], 2)

    for action_name, done in completed:
        if done:
            data["actions"].append({
                "date": today(),
                "action": action_name,
                "completed": True
            })

    data["logs"].append({
        "date": today(),
        "phase": "day2_action",
        "completed_actions": completed_count,
        "temptation_today": temptation_today,
        "if_then_plan": if_trigger,
        "best_action": best_action,
        "reflection": day2_reflection
    })

    save_user(user_id, data)
    st.success("Day 2 saved. Sustainable action phase completed.")

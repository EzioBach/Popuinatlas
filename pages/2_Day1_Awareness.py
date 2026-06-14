import streamlit as st

from utils import set_theme, sidebar_header, load_user, save_user, today

set_theme()
user_id = sidebar_header()

st.title("🌍 Day 1 — Awareness & Baseline")
st.caption("Understand your current fashion habits and how they connect to ocean health")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

st.markdown(
    """
    **Objectives**
    - Establish a baseline of current clothing behaviour
    - Identify fast-fashion triggers
    - Reflect on the environmental impact of personal choices
    - Set a first commitment for the Ocean Legacy Challenge
    """
)

st.markdown("### The opening prompt")
st.info("“When I am your age, what kind of ocean will I inherit?”")

col1, col2 = st.columns(2)

with col1:
    fast_fashion_items = st.number_input(
        "How many fast-fashion items did you buy in the last 30 days?",
        min_value=0, max_value=50, value=2
    )
    second_hand_items = st.number_input(
        "How many second-hand items did you buy in the last 30 days?",
        min_value=0, max_value=50, value=0
    )
    reuse_frequency = st.slider(
        "How often do you rewear or restyle clothes you already own?",
        1, 10, 5
    )
    ocean_concern = st.slider(
        "How concerned are you about fashion's impact on oceans?",
        1, 10, 6
    )

with col2:
    main_trigger = st.selectbox(
        "What most often triggers fast-fashion buying?",
        [
            "Social media trends",
            "Sales and discounts",
            "Need for novelty",
            "Peer pressure",
            "Convenience",
            "Special occasions"
        ]
    )
    buying_feeling = st.selectbox(
        "How do you usually feel before buying?",
        ["Excited", "Pressured", "Bored", "Curious", "Insecure", "Neutral"]
    )
    post_buy_feeling = st.selectbox(
        "How do you usually feel after buying?",
        ["Satisfied", "Guilty", "Neutral", "Regretful", "Excited"]
    )
    commitment = st.slider(
        "How committed are you to reducing fast fashion for 30 days?",
        1, 10, 7
    )

reflection = st.text_area(
    "What did you realize about your clothing habits today?"
)

goal = st.text_input(
    "Write one personal goal for this challenge",
    placeholder="Example: I will avoid buying any new fast-fashion item for 30 days."
)

if st.button("Save Day 1", use_container_width=True):
    if not goal.strip():
        st.error("Please write a personal goal before saving.")
        st.stop()

    data = load_user(user_id)
    data["progress"] = max(data["progress"], 1)

    data["baseline"] = {
        "fast_fashion_items": fast_fashion_items,
        "second_hand_items": second_hand_items,
        "reuse_frequency": reuse_frequency,
        "ocean_concern": ocean_concern,
        "main_trigger": main_trigger,
        "buying_feeling": buying_feeling,
        "post_buy_feeling": post_buy_feeling,
        "commitment": commitment,
        "goal": goal
    }

    data["logs"].append({
        "date": today(),
        "phase": "day1_awareness",
        "fast_fashion_items": fast_fashion_items,
        "second_hand_items": second_hand_items,
        "reuse_frequency": reuse_frequency,
        "ocean_concern": ocean_concern,
        "main_trigger": main_trigger,
        "buying_feeling": buying_feeling,
        "post_buy_feeling": post_buy_feeling,
        "reflection": reflection,
        "goal": goal
    })

    save_user(user_id, data)
    st.success("Day 1 saved. You have completed the awareness stage.")

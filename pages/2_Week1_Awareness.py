import streamlit as st

from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

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

st.markdown("### Psychological Baseline Assessment")
st.write("Please indicate how strongly you agree or disagree with the following statements (1 = Strongly Disagree, 7 = Strongly Agree).")

# Construct 1: Nature Relatedness (Emotional Connection)
st.markdown("**Part 1: Connection to the Ocean Ecosystem**")
nature_connection = st.slider(
    "I feel a deep, personal connection to the natural environment and marine ecosystems.",
    1, 7, 4
)
responsibility_feeling = st.slider(
    "I believe my daily consumer choices directly impact the health of future oceans.",
    1, 7, 4
)

# Construct 2: Autonomous Motivation (SDT - Autonomy)
st.markdown("**Part 2: Personal Values and Motivation**")
autonomy_scale = st.slider(
    "I want to reduce my fast-fashion consumption because it aligns with my core personal values, not just because others expect me to.",
    1, 7, 4
)

# Construct 3: Perceived Competence (SDT - Competence)
st.markdown("**Part 3: Behavioral Confidence**")
competence_scale = st.slider(
    "I feel confident in my ability to find and utilize sustainable fashion alternatives over the next 30 days.",
    1, 7, 4
)

st.markdown("### Behavioral Audit")
fast_fashion_items = st.number_input(
    "Quantify your fast-fashion acquisitions: How many newly produced garments did you purchase in the last 30 days?",
    min_value=0, max_value=50, value=2
)

main_trigger = st.selectbox(
    "Identify your primary behavioral trigger for fast-fashion consumption:",
    [
        "Algorithmic social media trends",
        "Scarcity marketing (Sales/Discounts)",
        "Psychological need for novelty",
        "Social conformity / Peer pressure",
        "Emotional regulation (Stress/Boredom buying)"
    ]
)

goal = st.text_input(
    "Implementation Goal",
    placeholder="Define a specific, measurable objective for the next 30 days..."
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

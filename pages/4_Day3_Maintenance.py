import pandas as pd
import plotly.express as px
import streamlit as st

from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("💙 Day 3 — Legacy Plan & Final Message")
st.caption("Build long-term rules and close the challenge with responsibility")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)

if data["progress"] < 2:
    st.warning("Complete Day 2 first.")
    st.stop()

st.markdown("### Reflection")
what_changed = st.text_area("What changed in how you think about clothing during this challenge?")
what_worked = st.text_area("What worked best for you?")
what_hardest = st.text_area("What was hardest to change?")

st.markdown("### Personal clothing rules")
rules = st.text_area(
    "Write 3–5 personal rules for future clothing decisions",
    placeholder="Example: I will wait 48 hours before any non-essential clothing purchase."
)

warning_signs = st.text_input(
    "What are your early warning signs that you are slipping back into fast-fashion habits?"
)

recovery_plan = st.text_area(
    "If you feel pressure to buy fast fashion again, what will you do instead?"
)

support_person = st.text_input(
    "Who could support or remind you of your goal?"
)

st.markdown("### Post-challenge self-rating")
post_fast_fashion_intent = st.slider(
    "How likely are you now to buy fast fashion impulsively?",
    1, 10, 4
)
post_responsibility = st.slider(
    "How responsible do you feel now for fashion's impact on the ocean?",
    1, 10, 8
)
post_commitment = st.slider(
    "How committed are you to continuing these habits?",
    1, 10, 8
)

final_message = st.text_area(
    "Write your final message to the child",
    placeholder="Example: I cannot fix everything alone, but I can choose differently and protect your future ocean through my habits."
)

if st.button("Complete Program", use_container_width=True):
    if not rules.strip() or not warning_signs.strip() or not final_message.strip():
        st.error("Please complete your rules, warning signs, and final message.")
        st.stop()

    data = load_user(user_id)
    data["progress"] = 3
    data["maintenance"] = {
        "what_changed": what_changed,
        "what_worked": what_worked,
        "what_hardest": what_hardest,
        "rules": rules,
        "warning_signs": warning_signs,
        "recovery_plan": recovery_plan,
        "support_person": support_person,
        "post_fast_fashion_intent": post_fast_fashion_intent,
        "post_responsibility": post_responsibility,
        "post_commitment": post_commitment
    }
    data["final_message"] = final_message

    data["logs"].append({
        "date": today(),
        "phase": "day3_legacy",
        "post_fast_fashion_intent": post_fast_fashion_intent,
        "post_responsibility": post_responsibility,
        "post_commitment": post_commitment,
        "final_message": final_message
    })

    save_user(user_id, data)
    st.success("Program completed. Your Ocean Legacy has been recorded.")
    st.balloons()

baseline = data.get("baseline", {})
if baseline:
    st.markdown("### Before vs after")
    compare_df = pd.DataFrame({
        "Metric": ["Ocean concern", "Commitment"],
        "Before": [
            baseline.get("ocean_concern", 0),
            baseline.get("commitment", 0)
        ],
        "After": [
            post_responsibility,
            post_commitment
        ]
    })

    fig = px.bar(
        compare_df,
        x="Metric",
        y=["Before", "After"],
        barmode="group",
        title="Pre/Post Comparison"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
   

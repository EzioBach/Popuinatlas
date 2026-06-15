import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils import set_theme, sidebar_header, load_user, save_user, today, build_report

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("📝 T2 Post-Test & Program Completion")
st.caption("Final evaluation of psychological shifts and behavioural changes.")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)

# --- DEVELOPER TIME TRAVEL BYPASS ---
with st.expander("🛠️ Evaluator / Professor Bypass"):
    st.info("In a live RCT, this page unlocks 30 days after T1. Click below to bypass for grading purposes.")
    if st.button("Unlock T2 Assessment"):
        data["progress"] = 2
        save_user(user_id, data)
        st.rerun()

if data["progress"] < 3:
    st.warning("⏳ Access Denied: The 30-day intervention period is still ongoing. Please return at the end of the study.")
    st.stop()

st.markdown("### Section A: T2 Re-Assessment")
st.write("Please answer these questions again based on how you feel *right now*.")

col1, col2 = st.columns(2)
with col1:
    t2_nature_conn = st.slider("1. I feel a deep emotional connection to marine ecosystems. (T2)", 1, 7, 4)
    t2_future_gen = st.slider("2. I feel a moral obligation to protect the oceans for future generations. (T2)", 1, 7, 4)
    t2_resp_feel = st.slider("3. My personal clothing choices directly impact ocean health. (T2)", 1, 7, 4)

with col2:
    t2_autonomy = st.slider("4. I want to change my habits because it aligns with my personal values. (T2)", 1, 7, 4)
    t2_competence = st.slider("5. I am confident I know how to find sustainable fashion alternatives. (T2)", 1, 7, 4)
    t2_social_norm = st.slider("6. Most people my age care about sustainable fashion. (T2)", 1, 7, 4)

st.markdown("### Section B: Final Behavioural Audit")
t2_fast_fashion = st.number_input(
    "How many newly produced garments did you purchase during this 30-day period?",
    min_value=0, max_value=50, value=0
)

final_message = st.text_area(
    "Final Legacy Message",
    placeholder="Write a brief message to the next generation regarding the ocean..."
)

if st.button("🏁 Submit T2 & Generate Report", type="primary"):
    if not final_message.strip():
        st.error("Please complete your final message.")
        st.stop()

    data["progress"] = 4
    data["final_message"] = final_message
    
    # Save T2 Data
    data["maintenance"] = {
        "t2_nature_conn": t2_nature_conn, "t2_future_gen": t2_future_gen,
        "t2_resp_feel": t2_resp_feel, "t2_autonomy": t2_autonomy,
        "t2_competence": t2_competence, "t2_social_norm": t2_social_norm,
        "t2_fast_fashion": t2_fast_fashion
    }
    save_user(user_id, data)
    st.success("Study Completed! Your data has been recorded.")
    st.balloons()
    
# --- EMAIL TRIGGER BLOCK ---
    with st.spinner("Transmitting data to research team..."):
        try:
            send_report_to_email(user_id, data)
            st.success("📧 Progress successfully emailed to the research team!")
        except Exception as e:
            st.error(f"Email failed to send. Please check your secrets. Error: {e}")

    # --- PRE/POST COMPARISON GENERATION ---
    baseline = data.get("baseline", {})
    if baseline:
        st.markdown("---")
        st.markdown("### 📊 Your Psychological Shift (T1 vs T2)")
        
        compare_df = pd.DataFrame({
            "Metric": ["Nature Conn.", "Future Gen Obligation", "Responsibility", "Competence"],
            "T1 (Baseline)": [
                baseline.get("nature_conn", 0), baseline.get("future_gen", 0),
                baseline.get("resp_feel", 0), baseline.get("competence", 0)
            ],
            "T2 (Post-Test)": [
                t2_nature_conn, t2_future_gen, t2_resp_feel, t2_competence
            ]
        })

        fig = go.Figure(data=[
            go.Bar(name='T1 (Baseline)', x=compare_df['Metric'], y=compare_df['T1 (Baseline)'], marker_color='#78b7cb'),
            go.Bar(name='T2 (Post-Test)', x=compare_df['Metric'], y=compare_df['T2 (Post-Test)'], marker_color='#173042')
        ])
        fig.update_layout(barmode='group', template="plotly_white", title="Pre and Post Intervention Comparison")
        st.plotly_chart(fig)


import pandas as pd
import plotly.express as px
import streamlit as st

from utils import set_theme, sidebar_header, load_user, progress_label

set_theme()
user_id = sidebar_header()

st.title("📊 Participant Dashboard")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)

logs_df = pd.DataFrame(data["logs"]) if data["logs"] else pd.DataFrame()
actions_df = pd.DataFrame(data["actions"]) if data["actions"] else pd.DataFrame()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Progress stage", data["progress"])
col2.metric("Status", progress_label(data["progress"]))
col3.metric("Entries logged", len(logs_df))
col4.metric("Actions completed", len(actions_df))

st.markdown("### Snapshot")
baseline = data.get("baseline", {})

c1, c2, c3 = st.columns(3)
c1.metric("Fast-fashion items (last 30d)", baseline.get("fast_fashion_items", 0))
c2.metric("Ocean concern", baseline.get("ocean_concern", 0))
c3.metric("Commitment level", baseline.get("commitment", 0))

st.markdown("### Behaviour log")
if not logs_df.empty:
    if "fast_fashion_items" in logs_df.columns:
        fig = px.line(
            logs_df,
            x="date",
            y="fast_fashion_items",
            markers=True,
            title="Logged Fast-Fashion Purchases Over Time"
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(logs_df, use_container_width=True)
else:
    st.info("No logs yet. Start with Day 1.")

st.markdown("### Sustainable actions")
if not actions_df.empty:
    fig2 = px.histogram(
        actions_df,
        x="action",
        color="completed",
        barmode="group",
        title="Completed Sustainable Actions"
    )
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(actions_df, use_container_width=True)
else:
    st.info("No action records yet. Complete Day 2 to populate this section.")

st.markdown("### Final message")
if data.get("final_message"):
    st.success("A final legacy message has been saved.")
    st.write(data["final_message"])
else:
    st.info("The final message to the child will appear here after Day 3.")

st.download_button(
    "Download participant JSON",
    data=str(data),
    file_name=f"{user_id}_ocean_legacy_data.txt"
)

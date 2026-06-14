import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import set_theme, sidebar_header, load_user, progress_label[cite: 4]

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

st.title("📊 Participant Dashboard")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

data = load_user(user_id)[cite: 4]
logs_df = pd.DataFrame(data["logs"]) if data["logs"] else pd.DataFrame()[cite: 4]
actions_df = pd.DataFrame(data["actions"]) if data["actions"] else pd.DataFrame()[cite: 4]

# Overall Progress Bar
st.markdown("### 30-Day Journey Progress")
progress_val = (data["progress"] / 3)
st.progress(progress_val)
st.caption(f"Current Status: **{progress_label(data['progress'])}**")

# Interactive Tabs
tab1, tab2, tab3 = st.tabs(["🌍 My Tangible Impact", "🤝 Cohort Comparison", "📝 Behavioral Log"])

with tab1:
    st.markdown("### Impact Metrics")
    items_saved = len(actions_df) * 1.5  
    water_saved = items_saved * 2700  
    co2_saved = items_saved * 10  
    
    impact_col1, impact_col2, impact_col3 = st.columns(3)
    impact_col1.metric("Items Diverted", f"{items_saved:.1f}", help="Estimated garments kept from landfills")
    impact_col2.metric("Freshwater Preserved", f"{water_saved:,.0f} L", delta="Marine health critical", delta_color="normal")
    impact_col3.metric("CO2 Prevented", f"{co2_saved:.1f} kg", delta="Reduced acidification", delta_color="normal")
    
    if not actions_df.empty:
        fig2 = px.histogram(actions_df, x="action", color="completed", title="Action Distribution", color_discrete_sequence=['#5ea8c0'])
        fig2.update_layout(template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Leuphana Cohort Alignment")
    baseline = data.get("baseline", {})[cite: 4]
    user_concern = baseline.get("responsibility_feeling", 0)
    user_competence = baseline.get("competence_scale", 0)
    
    avg_concern = 5.2
    avg_competence = 4.8
    
    compare_df = pd.DataFrame({
        "Metric": ["Responsibility", "Competence"],
        "You": [user_concern, user_competence],
        "Cohort Average": [avg_concern, avg_competence]
    })
    
    fig3 = go.Figure(data=[
        go.Bar(name='You', x=compare_df['Metric'], y=compare_df['You'], marker_color='#173042'),
        go.Bar(name='Cohort Average', x=compare_df['Metric'], y=compare_df['Cohort Average'], marker_color='#78b7cb')
    ])
    fig3.update_layout(barmode='group', template="plotly_white", title="Psychological Alignment")
    st.plotly_chart(fig3, use_container_width=True)
    
    if len(actions_df) >= 3.5:
        st.success("🌟 You are leading by example! Your logged actions exceed the cohort average.")
    else:
        st.info("🤝 Every small action you log brings our collective Leuphana cohort closer to our environmental goals.")

with tab3:
    st.markdown("### Challenge Records")
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)[cite: 4]
    else:
        st.info("No logs yet. Complete Week 1 to populate this section.")[cite: 4]

    st.download_button("📥 Download My Raw Data (JSON)", data=str(data), file_name=f"{user_id}_ocean_legacy.txt")[cite: 4]    co2_saved = items_saved * 10  
    
    impact_col1, impact_col2, impact_col3 = st.columns(3)
    impact_col1.metric("Items Diverted", f"{items_saved:.1f}", help="Estimated garments kept from landfills")
    impact_col2.metric("Freshwater Preserved", f"{water_saved:,.0f} L", delta="Marine health critical", delta_color="normal")
    impact_col3.metric("CO2 Prevented", f"{co2_saved:.1f} kg", delta="Reduced acidification", delta_color="normal")
    
    if not actions_df.empty:
        fig2 = px.histogram(actions_df, x="action", color="completed", title="Action Distribution", color_discrete_sequence=['#5ea8c0'])
        fig2.update_layout(template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Leuphana Cohort Alignment")
    baseline = data.get("baseline", {})[cite: 4]
    user_concern = baseline.get("responsibility_feeling", 0)
    user_competence = baseline.get("competence_scale", 0)
    
    avg_concern = 5.2
    avg_competence = 4.8
    
    compare_df = pd.DataFrame({
        "Metric": ["Responsibility", "Competence"],
        "You": [user_concern, user_competence],
        "Cohort Average": [avg_concern, avg_competence]
    })
    
    fig3 = go.Figure(data=[
        go.Bar(name='You', x=compare_df['Metric'], y=compare_df['You'], marker_color='#173042'),
        go.Bar(name='Cohort Average', x=compare_df['Metric'], y=compare_df['Cohort Average'], marker_color='#78b7cb')
    ])
    fig3.update_layout(barmode='group', template="plotly_white", title="Psychological Alignment")
    st.plotly_chart(fig3, use_container_width=True)
    
    if len(actions_df) >= 3.5:
        st.success("🌟 You are leading by example! Your logged actions exceed the cohort average.")
    else:
        st.info("🤝 Every small action you log brings our collective Leuphana cohort closer to our environmental goals.")

with tab3:
    st.markdown("### Challenge Records")
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)[cite: 4]
    else:
        st.info("No logs yet. Complete Week 1 to populate this section.")[cite: 4]

    st.download_button("📥 Download My Raw Data (JSON)", data=str(data), file_name=f"{user_id}_ocean_legacy.txt")[cite: 4]

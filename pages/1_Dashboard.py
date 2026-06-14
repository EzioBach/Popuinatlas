import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import base64

from utils import set_theme, sidebar_header, load_user, progress_label

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

# The Gatekeeper: Block non-challenge groups
data = load_user(user_id) if user_id else None
if data and data.get("condition") in ["control", "video_only"]:
    st.warning("🔒 **Access Restricted**")
    st.info(
        "Based on your assigned study cohort, you do not require access to the daily tracking modules. "
        "Thank you for completing your T1 Baseline Assessment. Please return at the end of the 30-day period "
        "to complete your final T2 Post-Test."
    )
    st.stop()

st.title("📊 Participant Dashboard")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

logs_df = pd.DataFrame(data.get("logs", []))
actions_df = pd.DataFrame(data.get("actions", []))

# Overall Progress Bar
st.markdown("### 30-Day Journey Progress")
progress_val = (data["progress"] / 3)
st.progress(progress_val)
st.caption(f"Current Status: **{progress_label(data['progress'])}**")

# Interactive Tabs (Now with Gallery)
tab1, tab2, tab3, tab4 = st.tabs(["🌍 My Tangible Impact", "🤝 Cohort Comparison", "📝 Behavioural Log", "📸 Wardrobe Gallery"])

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
        st.plotly_chart(fig2)

with tab2:
    st.markdown("### Leuphana Cohort Alignment")
    baseline = data.get("baseline", {})
    user_concern = baseline.get("resp_feel", 0)
    user_competence = baseline.get("competence", 0)
    
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
    st.plotly_chart(fig3)
    
    if len(actions_df) >= 3.5:
        st.success("🌟 You are leading by example! Your logged actions exceed the cohort average.")
    else:
        st.info("🤝 Every small action you log brings our collective Leuphana cohort closer to our environmental goals.")

with tab3:
    st.markdown("### Challenge Records")
    if not logs_df.empty:
        # Hide the base64 image strings from the data table so it doesn't crash the browser
        display_df = actions_df.drop(columns=['image']) if 'image' in actions_df.columns else actions_df
        st.dataframe(display_df)
    else:
        st.info("No logs yet. Complete Week 1 to populate this section.")

    st.download_button("📥 Download My Raw Data (JSON)", data=str(data), file_name=f"{user_id}_ocean_legacy.txt")

with tab4:
    st.markdown("### My Sustainable Wardrobe")
    st.write("A visual record of the clothing you've saved, repaired, or restyled during the challenge.")
    
    # Extract only the actions that have an image attached
    gallery_items = [action for action in data.get("actions", []) if action.get("image") is not None]
    
    if gallery_items:
        cols = st.columns(3)
        for idx, item in enumerate(gallery_items):
            try:
                # Decode the base64 string back into bytes for Streamlit to render
                img_bytes = base64.b64decode(item["image"])
                action_date = item.get("date", "Unknown date")
                cols[idx % 3].image(img_bytes, caption=f"Logged: {action_date}")
            except Exception:
                pass # Skip if image decoding fails
    else:
        st.info("No photos uploaded yet. Head to Week 2 to upload your first sustainable outfit!")

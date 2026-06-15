import streamlit as st
import base64
from utils import set_theme, sidebar_header, load_user, save_user, today

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

# The Gatekeeper: Block non-challenge groups from RCT
data = load_user(user_id) if user_id else None
if data and data.get("condition") in ["control", "video_only"]:
    st.warning("🔒 **Access Restricted**")
    st.info(
        "Based on your assigned study cohort, you do not require access to the daily tracking modules. "
        "Thank you for completing your T1 Baseline Assessment. Please return at the end of the 30-day period "
        "to complete your final T2 Post-Test."
    )
    st.stop()

st.title("♻️ Week 2 — Action Strategies")
st.caption("Overcoming the intention-behaviour gap through concrete, high-impact interventions.")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

if data["progress"] < 1:
    st.warning("Complete Week 1 first.")
    st.stop()

st.markdown("### Select Your Interventions for Today")
st.write("Browse the categories below and check off the behavioural interventions you successfully implemented.")

completed = []

with st.expander("🛑 Strategy A: Behavioural Friction (Refuse & Reduce)", expanded=True):
    if st.checkbox("Cognitive Pause: Mandated a 48-hour waiting period before a fast-fashion purchase"): completed.append("Reflected before buying")
    if st.checkbox("Digital Cleansing: Unsubscribed from a fast-fashion newsletter or unfollowed a brand"): completed.append("Digital boundary setting")

with st.expander("🔄 Strategy B: Identity & Circularity (Reuse & Reimagine)", expanded=False):
    if st.checkbox("Resource Optimization: Created a completely new outfit combination from existing wardrobe"): completed.append("Reused existing outfit")
    if st.checkbox("Social Exchange: Borrowed, swapped, or arranged a clothing swap with friends"): completed.append("Borrowed/swapped clothing")

with st.expander("🧵 Strategy C: Skill Acquisition (Repair & Upcycle)", expanded=False):
    if st.checkbox("Material Longevity: Repaired, tailored, or customized one clothing item"): completed.append("Repaired clothing")
    if st.checkbox("Market Substitution: Purchased or searched exclusively for a second-hand alternative"): completed.append("Searched second-hand")

st.markdown("---")
st.markdown("### 📸 Proof of Action (Photo Gallery Upload)")
st.write("Visual accountability strengthens habit formation. Upload a photo of your re-styled outfit, your mended clothing, or a second-hand find!")

uploaded_file = st.file_uploader("Upload a photo (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

st.markdown("### Daily Reflection")
temptation_today = st.radio(
    "Did you experience psychological friction (temptation) to buy fast fashion today?",
    ["No temptation", "Mild temptation", "Strong temptation", "Overwhelming urge"],
    horizontal=True
)

if_trigger = st.text_input("Implementation Intention: IF I am triggered to buy something new tomorrow, THEN I will...")

if st.button("💾 Log Daily Actions & Upload", type="primary"):
    if len(completed) < 1 and uploaded_file is None:
        st.error("Please select at least 1 sustainable action or upload a photo to log today's progress.")
        st.stop()

    data["progress"] = max(data["progress"], 2)

    # Convert uploaded image to base64 string for database storage
    image_b64 = None
    if uploaded_file is not None:
        image_b64 = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

    # Save each action. If an image was uploaded, attach it to the first action logged today.
    for idx, action_name in enumerate(completed):
        action_data = {
            "date": today(),
            "action": action_name,
            "completed": True,
            "image": image_b64 if idx == 0 else None  # Attach image only once per day to save space
        }
        data["actions"].append(action_data)
        
    # If they ONLY uploaded a photo without checking a box
    if len(completed) == 0 and uploaded_file is not None:
         data["actions"].append({
            "date": today(),
            "action": "Uploaded photo of sustainable action",
            "completed": True,
            "image": image_b64
        })

    save_user(user_id, data)
    st.success(f"Successfully logged your progress for today!")
    st.balloons()

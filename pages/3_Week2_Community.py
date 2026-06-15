import streamlit as st
from utils import set_theme, sidebar_header, load_user, save_user, today, build_report

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

set_theme()
user_id = sidebar_header()

# The Gatekeeper: Block non-challenge groups from RCT
data = load_user(user_id) if user_id else None
if data and data.get("condition") in ["control", "video_only"]:
    st.warning("🔒 **Access Restricted**")
    st.info(
        "Based on your assigned study cohort, you do not require access to the community modules. "
        "Please return at the end of the 30-day period to complete your final T2 Post-Test."
    )
    st.stop()

st.title("🤝 Week 2 — Community & Goal Setting")
st.caption("Fostering belonging and setting concrete intentions for sustainable action.")

if not user_id:
    st.warning("Enter your Participant ID in the sidebar first.")
    st.stop()

if data["progress"] < 1:
    st.warning("Please complete Week 1 (Baseline) first.")
    st.stop()

# --- WHATSAPP & COMMUNITY ---
st.markdown("### 💬 Join the Leuphana Cohort")
st.write(
    "Behavior change is easier when we do it together. Join our private WhatsApp group "
    "to share ideas, ask for repair tips, and connect with fellow students taking the challenge."
)
# Placeholder for the actual WhatsApp invite link
st.link_button("📱 Join the Week 2 WhatsApp Group", "https://chat.whatsapp.com/placeholder_link", type="primary")

st.markdown("---")

# --- EDUCATION & IDEAS ---
st.markdown("### 🛠️ Concept Intro: The Art of Repair & Reuse")
st.write("Before taking action next week, let's explore what is possible. Here are some popular ideas from your peers:")

c1, c2, c3 = st.columns(3)
with c1:
    st.info("**Visible Mending**\n\nUse bright, contrasting threads to embroider over holes in denim or sweaters, turning damage into a design statement.")
with c2:
    st.success("**The Clothing Swap**\n\nGather 3 friends. Everyone brings 3 items they no longer wear. Trade items to refresh your wardrobe for free.")
with c3:
    st.warning("**Creative Upcycling**\n\nCut old jeans into shorts, dye stained t-shirts, or turn unwearable fabrics into tote bags or cleaning cloths.")

st.markdown("---")

# --- GOAL SETTING ---
st.markdown("### 🎯 Set Your Week 2 Pledge")
st.write("Commit to one specific action you will attempt to execute by next week's check-in.")

community_goal = st.text_area(
    "What is your repair, reuse, or refuse goal for the upcoming days?",
    placeholder="Example: I am going to attempt to sew the hole in my black jacket, or I will arrange a swap with Sarah."
)

if st.button("💾 Lock in My Goal & Share with Cohort", type="primary"):
    if not community_goal.strip():
        st.error("Please write a goal before saving.")
        st.stop()

    # Progress becomes 2 (Community Completed)
    data["progress"] = max(data["progress"], 2)
    data["community_goal"] = community_goal
    
    data["logs"].append({
        "date": today(),
        "phase": "week2_community",
        "goal": community_goal
    })

    save_user(user_id, data)
    st.success("Your goal is set! Check back in Week 3 to log your actual progress.")
    st.balloons()

    with st.spinner("Transmitting goal to research team..."):
        try:
            send_report_to_email(user_id, data)
        except Exception:
            pass # Fails silently for the user but keeps the app moving

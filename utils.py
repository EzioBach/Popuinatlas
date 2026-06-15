import json
import sqlite3
import random
from datetime import date
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st


DB_DIR = Path("data")
DB_PATH = DB_DIR / "users.db"

DEFAULT_USER = {
    "condition": None, 
    "progress": 0,
    "baseline": {},
    "logs": [],
    "actions": [],
    "maintenance": {},
    "final_message": ""
}
TEAM = ["Andrea Andriamalala", "Ezzat Bachour", "Leen Ghafar", "Maha El kadiri"]


def ensure_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, data TEXT)"
    )
    conn.commit()
    return conn


def load_user(user_id: str):
    conn = ensure_db()
    cur = conn.cursor()
    cur.execute("SELECT data FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    
    if row:
        data = json.loads(row[0])
        merged = DEFAULT_USER.copy()
        merged.update(data)
        return merged
    else:
        # THE RANDOMIZER: If the user doesn't exist, assign them a condition immediately
        new_user = DEFAULT_USER.copy()
        conditions = ["control", "challenge_only", "video_only", "full_intervention"]
        new_user["condition"] = random.choice(conditions)
        
        # Save it immediately so their condition is locked in forever
        save_user(user_id, new_user)
        return new_user


def save_user(user_id: str, data: dict):
    conn = ensure_db()
    conn.execute(
        "REPLACE INTO users (id, data) VALUES (?, ?)",
        (user_id, json.dumps(data))
    )
    conn.commit()


def today():
    return str(date.today())


def set_theme():
    st.set_page_config(
        page_title="Ocean Legacy Challenge",
        page_icon="🌊",
        layout="wide"
    )
    st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4fbff 0%, #eaf6fb 40%, #dff1f6 100%);
        color: #173042;
    }

    header[data-testid="stHeader"] {
        background: rgba(244, 251, 255, 0.98);
    }

    .stApp > header {
        background-color: rgba(244, 251, 255, 0.98);
    }

    [data-testid="stToolbar"] {
        background: rgba(244, 251, 255, 0.98);
    }

    .main {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(180deg, #f4fbff 0%, #eaf6fb 40%, #dff1f6 100%);
        color: #173042;
    }

    .main {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #173042;
    }

    p, li, label, span, div {
        color: #2d465a;
    }

    .hero-box {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(118, 168, 187, 0.22);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 10px 24px rgba(32, 70, 88, 0.08);
        backdrop-filter: blur(6px);
    }

    .ocean-card {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(118, 168, 187, 0.18);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 18px rgba(32, 70, 88, 0.06);
    }

    .team-pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(225, 242, 247, 0.95);
        border: 1px solid rgba(118, 168, 187, 0.18);
        font-size: 0.85rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        color: #173042;
    }

    .stSidebar {
        background: linear-gradient(180deg, #f8fcfe 0%, #edf8fb 100%);
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(118, 168, 187, 0.16);
        border-radius: 16px;
        padding: 0.6rem 0.8rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #78b7cb, #5ea8c0);
        color: white;
        border: none;
        border-radius: 12px;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #6aaac0, #4f9db7);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def sidebar_header():
    st.sidebar.title("🌊 Ocean Legacy")
    st.sidebar.caption("Fashion choices, future oceans")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Project:** Ocean Legacy Challenge")
    st.sidebar.markdown("**Team:**")
    st.sidebar.markdown(
        " ".join([f"<span class='team-pill'>{name}</span>" for name in TEAM]),
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = ""

    entered_id = st.sidebar.text_input("Participant ID", key="participant_id_input")

    # Correctly indented validation check
    if not entered_id:
        st.sidebar.warning("Please enter a valid ID to save progress.")
    else:
        st.session_state["user_id"] = entered_id

    return st.session_state["user_id"]

def progress_label(progress):
    labels = {
        0: "Not started", 
        1: "Week 1 (Baseline) completed", 
        2: "Week 2 (Community) completed", 
        3: "Week 3 (Action Phase) completed",
        4: "Week 4 (Legacy Phase) completed"
    }
    return labels.get(progress, "In progress")
    
def build_report(user_id, data):
    lines = []
    lines.append("Ocean Legacy Challenge Report")
    lines.append(f"Participant ID: {user_id}")
    lines.append("")
    lines.append("BASELINE")
    lines.append(str(data.get("baseline", {})))
    lines.append("")
    lines.append("LOGS")
    for item in data.get("logs", []):
        lines.append(str(item))
    lines.append("")
    lines.append("ACTIONS")
    for item in data.get("actions", []):
        lines.append(str(item))
    lines.append("")
    lines.append("MAINTENANCE")
    lines.append(str(data.get("maintenance", {})))
    lines.append("")
    lines.append("FINAL MESSAGE")
    lines.append(str(data.get("final_message", "")))
    return "\n".join(lines)


def build_report(user_id, data):
    lines = []
    lines.append("🌊 OCEAN LEGACY CHALLENGE - DYNAMIC REPORT 🌊")
    lines.append(f"Participant ID: {user_id}")
    lines.append(f"Current Progress Stage: {data.get('progress', 0)} / 4")
    lines.append(f"Assigned RCT Condition: {data.get('condition', 'Unknown')}")
    lines.append("-" * 50)
    
    # --- STAGE 1: BASELINE ---
    lines.append("\n[1] WEEK 1: BASELINE (T1)")
    baseline = data.get("baseline", {})
    if baseline:
        for k, v in baseline.items():
            lines.append(f"    • {k}: {v}")
    else:
        lines.append("    (Not completed yet)")
    
    # --- STAGE 2: COMMUNITY ---
    lines.append("\n[2] WEEK 2: COMMUNITY & GOAL SETTING")
    goal = data.get("community_goal", "")
    if goal:
        lines.append(f"    • Pledge: {goal}")
    else:
        lines.append("    (Not completed yet)")
    
    # --- STAGE 3: ACTIONS ---
    lines.append("\n[3] WEEK 3: ACTION LOGS")
    actions = data.get("actions", [])
    if actions:
        for a in actions:
            # We exclude the 'image' key here so we don't flood the email with base64 text
            action_name = a.get('action', 'Unknown action')
            action_date = a.get('date', 'Unknown date')
            lines.append(f"    • {action_date}: {action_name}")
    else:
        lines.append("    (No actions logged yet)")
    
    # --- STAGE 4: POST-TEST ---
    lines.append("\n[4] WEEK 4: POST-TEST (T2) & LEGACY")
    maintenance = data.get("maintenance", {})
    if maintenance:
        for k, v in maintenance.items():
            lines.append(f"    • {k}: {v}")
        lines.append(f"    • Final Legacy Message: {data.get('final_message', '')}")
    else:
        lines.append("    (Not completed yet)")
    
    # ==========================================
    # DATA ANALYSIS (Only runs if T2 is done)
    # ==========================================
    if data.get("progress", 0) >= 4 and baseline and maintenance:
        lines.append("\n" + "=" * 50)
        lines.append("📊 AUTOMATED DATA ANALYSIS (T1 vs T2 SHIFTS)")
        lines.append("=" * 50)
        
        # 1. Behavioral Shift
        ff_t1 = baseline.get("fast_fashion_items", 0)
        ff_t2 = maintenance.get("t2_fast_fashion", 0)
        ff_diff = ff_t2 - ff_t1
        trend = "Decrease 📉" if ff_diff < 0 else "Increase 📈" if ff_diff > 0 else "No Change ➖"
        
        lines.append("\nBEHAVIOURAL IMPACT:")
        lines.append(f"    • Fast Fashion Purchases: {ff_t1} -> {ff_t2} ({trend}: {ff_diff})")
        lines.append(f"    • Total Sustainable Interventions Executed: {len(actions)}")
        
        # 2. Psychological Shift
        lines.append("\nPSYCHOLOGICAL SHIFTS (Scale 1-7):")
        metrics = [
            ("Nature Connection", "nature_conn", "t2_nature_conn"),
            ("Future Gen Obligation", "future_gen", "t2_future_gen"),
            ("Personal Responsibility", "resp_feel", "t2_resp_feel"),
            ("Autonomous Motivation", "autonomy", "t2_autonomy"),
            ("Perceived Competence", "competence", "t2_competence"),
            ("Social Norms", "social_norm", "t2_social_norm")
        ]
        
        for label, k1, k2 in metrics:
            v1 = baseline.get(k1, 0)
            v2 = maintenance.get(k2, 0)
            shift = v2 - v1
            shift_symbol = "(+)" if shift > 0 else "(-)" if shift < 0 else "(=)"
            lines.append(f"    • {label}: {v1} -> {v2}  {shift_symbol} Shift: {shift}")

    return "\n".join(lines)
    
    def send_report_to_email(user_id, data):
    # Fetch credentials from Streamlit Secrets
    sender = st.secrets["EMAIL_ADDRESS"]
    password = st.secrets["EMAIL_PASSWORD"]
    
    # The email address where you want to RECEIVE the data
    receiver = "Ezzat.bashour96@gmail.com" 

    # Generate the text body using our new build_report function
    body = build_report(user_id, data)

    # Construct the email
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"Ocean Legacy Challenge Data: Participant {user_id}"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Connect to Gmail server and send
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()

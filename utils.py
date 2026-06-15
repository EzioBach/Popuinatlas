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
    "community_goal": "",
    "final_message": ""
}
TEAM = ["Andrea Andriamalala", "Ezzat Bachour", "Leen Ghafar", "Maha El kadiri"]

def ensure_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, data TEXT)")
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
        new_user = DEFAULT_USER.copy()
        conditions = ["control", "challenge_only", "video_only", "full_intervention"]
        new_user["condition"] = random.choice(conditions)
        save_user(user_id, new_user)
        return new_user

def save_user(user_id: str, data: dict):
    conn = ensure_db()
    conn.execute("REPLACE INTO users (id, data) VALUES (?, ?)", (user_id, json.dumps(data)))
    conn.commit()

def today():
    return date.today().isoformat()

def set_theme():
    st.set_page_config(page_title="Ocean Legacy Challenge", page_icon="🌊", layout="wide")
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(180deg, #f4fbff 0%, #eaf6fb 40%, #dff1f6 100%); color: #173042; }
        h1, h2, h3 { color: #173042; }
        .hero-box { background: rgba(255, 255, 255, 0.72); border-radius: 24px; padding: 28px; box-shadow: 0 10px 24px rgba(32, 70, 88, 0.08); }
        .stButton > button { background: linear-gradient(90deg, #78b7cb, #5ea8c0); color: white; border-radius: 12px; }
        </style>
    """, unsafe_allow_html=True)

def sidebar_header():
    st.sidebar.title("🌊 Ocean Legacy")
    entered_id = st.sidebar.text_input("Participant ID")
    if entered_id: st.session_state["user_id"] = entered_id
    return st.session_state.get("user_id", "")

def progress_label(progress):
    labels = {0: "Not started", 1: "Week 1 (Baseline)", 2: "Week 2 (Community)", 3: "Week 3 (Action)", 4: "Week 4 (Legacy)"}
    return labels.get(progress, "In progress")

def build_report(user_id, data):
    lines = [f"🌊 REPORT: {user_id}", f"Stage: {data.get('progress')}/4", "-"*20]
    # Add your logic for baseline, logs, etc. here as you had it...
    return "\n".join(lines)

def send_report_to_email(user_id, data):
    sender = st.secrets["EMAIL_ADDRESS"]
    password = st.secrets["EMAIL_PASSWORD"]
    receiver = "Ezzat.bashour96@gmail.com"
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = sender, receiver, f"Report: {user_id}"
    msg.attach(MIMEText(build_report(user_id, data), 'plain', 'utf-8'))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

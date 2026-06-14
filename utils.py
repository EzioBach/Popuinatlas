import json
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st

DB_DIR = Path("data")
DB_PATH = DB_DIR / "users.db"

DEFAULT_USER = {
    "progress": 0,
    "baseline": {},
    "logs": [],
    "actions": [],
    "maintenance": {},
    "final_message": ""
}
TEAM = ["Leen", "Andrea", "Ezzat", "Maha"]


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
    return DEFAULT_USER.copy()


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
            background: linear-gradient(180deg, #03111f 0%, #08243b 45%, #0d3853 100%);
            color: #f3fbff;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(144,224,239,0.18);
            padding: 12px;
            border-radius: 16px;
        }
        .ocean-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(144,224,239,0.18);
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 14px;
        }
        .hero-box {
            background: linear-gradient(135deg, rgba(0,180,216,0.20), rgba(0,119,182,0.18));
            border: 1px solid rgba(144,224,239,0.25);
            border-radius: 24px;
            padding: 28px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def sidebar_header():
    st.sidebar.title("🌊 Ocean Legacy")
    st.sidebar.caption("Fashion choices, future oceans")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Leuphana University**")
    st.sidebar.markdown("**Project:** Ocean Legacy Challenge")
    st.sidebar.markdown("**Target group:** University students (18–30)")
    st.sidebar.markdown("**Goal:** Reduce fast-fashion consumption")
    st.sidebar.markdown("**Team:** Andrea, Ezzat, Leen, Maha.")
    st.sidebar.markdown("---")
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/93/Leuphana_Universität_Lüneburg_Logo_2020.svg", width=140)
    user_id = st.sidebar.text_input("Participant ID")
    if user_id:
        st.sidebar.success(f"Logged in as: {user_id}")
    else:
        st.sidebar.info("Enter your Participant ID to begin.")
    return user_id


def progress_label(progress: int):
    labels = {
        0: "Not started",
        1: "Awareness completed",
        2: "Action phase completed",
        3: "Legacy plan completed"
    }
    return labels.get(progress, "In progress")

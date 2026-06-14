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

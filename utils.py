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
            radial-gradient(circle at top, rgba(35, 68, 102, 0.28), transparent 35%),
            linear-gradient(180deg, #07111f 0%, #091a2d 45%, #0b2338 100%);
        color: #edf4f8;
    }

    .main {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f4f8fb;
    }

    p, li, label, span, div {
        color: #d9e5ec;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(13, 40, 67, 0.88), rgba(19, 58, 88, 0.78));
        border: 1px solid rgba(157, 196, 214, 0.16);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
    }

    .ocean-card {
        background: rgba(15, 36, 57, 0.80);
        border: 1px solid rgba(157, 196, 214, 0.14);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .team-pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.85rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        color: #edf4f8;
    }

    .stSidebar {
        background: linear-gradient(180deg, #081224 0%, #0a1b2f 100%);
    }

    [data-testid="stMetric"] {
        background: rgba(14, 34, 53, 0.80);
        border: 1px solid rgba(157, 196, 214, 0.12);
        border-radius: 16px;
        padding: 0.6rem 0.8rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2b5d7d, #3e7f96);
        color: white;
        border: none;
        border-radius: 12px;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #356b8e, #4a8aa2);
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

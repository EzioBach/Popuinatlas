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
    st.sidebar.markdown("**Project:** Ocean Legacy Challenge")
    st.sidebar.markdown("**Target group:** University students (18–30)")
    st.sidebar.markdown("**Goal:** Reduce fast-fashion consumption")
    st.sidebar.markdown("---")
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
    return labels.get(progress, "In progress")  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 0.85rem;
  opacity: 0.9;
}
</style>
        """,
        unsafe_allow_html=True,
    )

def render_hero(icon: str, title: str, subtitle: str, pill: str | None = None) -> None:
    pill_html = f'<span class="pop-pill">{pill}</span>' if pill else ""
    st.markdown(
        f"""
<div class="pop-hero">
  <div class="pop-hero-top">
    <div style="font-size:1.6rem">{icon}</div>
    <div class="pop-hero-title">{title}</div>
    {pill_html}
  </div>
  <div class="pop-hero-sub">{subtitle}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

def format_int(x) -> str:
    try:
        if pd.isna(x):
            return "—"
        return f"{int(float(x)):,}"
    except Exception:
        return "—"


@st.cache_data(show_spinner=False)
def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df

def _coerce_bool_official(series: pd.Series) -> pd.Series:
    s = series.copy()
    if s.dtype == object:
        s = s.astype(str).str.strip().str.upper().replace({"TRUE":"T","FALSE":"F","YES":"T","NO":"F"})
        return s.isin(["T", "1", "Y"])
    return s.astype(bool)

def get_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    """
    Returns: (cities, countries, languages, worldcities_or_None)

    Also ensures st.session_state has:
      - "cities", "countries", "languages", "worldcities"
    so pages can be opened directly (Streamlit Cloud users often do).
    """
    keys = {"cities", "countries", "languages", "worldcities"}
    if keys.issubset(st.session_state.keys()):
        return (
            st.session_state["cities"],
            st.session_state["countries"],
            st.session_state["languages"],
            st.session_state["worldcities"],
        )

    cities = _read_csv(DATA_DIR / "city.csv")
    countries = _read_csv(DATA_DIR / "country.csv")
    langs = _read_csv(DATA_DIR / "countrylanguage.csv")

    worldcities = _read_csv(DATA_DIR / "worldcities.csv")

    if cities is None or countries is None or langs is None:
        missing = []
        if cities is None: missing.append("data/city.csv")
        if countries is None: missing.append("data/country.csv")
        if langs is None: missing.append("data/countrylanguage.csv")
        raise FileNotFoundError(f"Missing required dataset file(s): {', '.join(missing)}")

    cities = normalize_columns(cities)
    countries = normalize_columns(countries)
    langs = normalize_columns(langs)
    if worldcities is not None:
        worldcities = normalize_columns(worldcities)

    st.session_state["cities"] = cities
    st.session_state["countries"] = countries
    st.session_state["languages"] = langs
    st.session_state["worldcities"] = worldcities

    return cities, countries, langs, worldcities


def build_country_language_stats(countries: pd.DataFrame, langs: pd.DataFrame) -> pd.DataFrame:
    c = countries.copy()
    l = langs.copy()

    if "CountryCode" not in l.columns and "Code" in l.columns:
        l = l.rename(columns={"Code": "CountryCode"})
    if "Language" not in l.columns:
        cand = [x for x in l.columns if x.lower() in ("language", "lang")]
        if cand:
            l = l.rename(columns={cand[0]: "Language"})

    grp = l.groupby("CountryCode", dropna=False)
    out = pd.DataFrame({
        "Code": grp["Language"].nunique(),
    }).rename(columns={"Code": "n_languages"})
    out.index.name = "Code"
    out = out.reset_index()

    if "IsOfficial" in l.columns:
        is_off = _coerce_bool_official(l["IsOfficial"])
        tmp = l.assign(_is_off=is_off).groupby("CountryCode")["_is_off"].sum().reset_index()
        tmp.columns = ["Code", "n_official"]
        out = out.merge(tmp, on="Code", how="left")
    else:
        out["n_official"] = np.nan

    if "Percentage" in l.columns:
        perc = pd.to_numeric(l["Percentage"], errors="coerce")
        l2 = l.assign(_p=perc).dropna(subset=["_p"])
        if not l2.empty:
            l2["_p"] = l2["_p"] / 100.0
            def _entropy(p):
                p = p[p > 0]
                return float(-(p * np.log(p)).sum()) if len(p) else np.nan
            ent = l2.groupby("CountryCode")["_p"].apply(_entropy).reset_index()
            ent.columns = ["Code", "entropy"]
            out = out.merge(ent, on="Code", how="left")
        else:
            out["entropy"] = np.nan
    else:
        out["entropy"] = np.nan

    if "Code" not in c.columns and "CountryCode" in c.columns:
        c = c.rename(columns={"CountryCode": "Code"})
    keep = [x for x in ["Code", "Name", "Continent", "Region", "Population"] if x in c.columns]
    out = out.merge(c[keep], on="Code", how="left")

    for col in ["n_languages", "n_official"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    if "Population" in out.columns:
        out["Population"] = pd.to_numeric(out["Population"], errors="coerce")

    return out

def build_global_language_stats(langs: pd.DataFrame, countries: pd.DataFrame | None = None) -> pd.DataFrame:
    l = langs.copy()
    if "Language" not in l.columns:
        return pd.DataFrame(columns=["Language", "countries_spoken", "official_countries"])

    by_lang = l.groupby("Language")["CountryCode"].nunique().reset_index()
    by_lang.columns = ["Language", "countries_spoken"]

    if "IsOfficial" in l.columns:
        is_off = _coerce_bool_official(l["IsOfficial"])
        l2 = l.assign(_is_off=is_off)
        off = l2[l2["_is_off"]].groupby("Language")["CountryCode"].nunique().reset_index()
        off.columns = ["Language", "official_countries"]
        by_lang = by_lang.merge(off, on="Language", how="left")
    else:
        by_lang["official_countries"] = np.nan

    by_lang["official_countries"] = pd.to_numeric(by_lang["official_countries"], errors="coerce").fillna(0).astype(int)
    by_lang = by_lang.sort_values("countries_spoken", ascending=False)

    return by_lang

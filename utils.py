import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# Branding
# =========================
APP_NAME = "Popuinatlas"
APP_SUBTITLE = "A Geo-Linguistic Atlas"
APP_LINE = "Popuinatlas - A Geo linguistic app World Languages Dashboard"


# =========================
# UI helpers (banner + CSS)
# =========================
def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px; }
        h1, h2, h3 { letter-spacing: -0.02em; }
        p, li { line-height: 1.55; }

        .hero {
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(17,26,46,0.80));
            border-radius: 18px;
            padding: 18px 18px 14px 18px;
            margin: 0.25rem 0 1.0rem 0;
        }
        .hero-title {
            font-size: 2.0rem;
            font-weight: 800;
            margin: 0;
        }
        .hero-sub {
            opacity: 0.92;
            font-size: 1.05rem;
            margin: 0.35rem 0 0 0;
        }
        .hero-line {
            opacity: 0.75;
            font-size: 0.95rem;
            margin-top: 0.6rem;
        }
        .badge {
            display: inline-block;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.06);
            font-size: 0.85rem;
            margin-right: 0.35rem;
            margin-bottom: 0.25rem;
        }
        .card {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(17,26,46,0.60);
            border-radius: 16px;
            padding: 14px 14px 10px 14px;
            margin: 0.5rem 0;
        }
        .card h4 { margin: 0 0 0.4rem 0; }
        .muted { opacity: 0.75; }

        div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(page_emoji: str, page_title: str, page_desc: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-title">{page_emoji} {APP_NAME} <span class="muted">— {APP_SUBTITLE}</span></div>
          <div class="hero-sub"><span class="badge">{page_title}</span> {page_desc}</div>
          <div class="hero-line">{APP_LINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body_html: str) -> None:
    st.markdown(
        f"""
        <div class="card">
          <h4>{title}</h4>
          <div class="muted">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Data loading (works from ANY page)
# =========================
@st.cache_data
def _load_csvs(data_dir: str = "data"):
    data_path = Path(data_dir)
    cities = pd.read_csv(data_path / "city.csv")
    countries = pd.read_csv(data_path / "country.csv")
    languages = pd.read_csv(data_path / "countrylanguage.csv")
    return cities, countries, languages


def get_data():
    """Load and store data in session_state so any page works even if user lands directly there."""
    if not {"cities", "countries", "languages"}.issubset(st.session_state.keys()):
        cities, countries, languages = _load_csvs()
        st.session_state["cities"] = cities
        st.session_state["countries"] = countries
        st.session_state["languages"] = languages
    return (
        st.session_state["cities"].copy(),
        st.session_state["countries"].copy(),
        st.session_state["languages"].copy(),
    )


# =========================
# Cleaning + formatting helpers (your pages expect these!)
# =========================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Name_x": "Name",
        "Name_y": "Name",
        "Code_x": "Code",
        "Code_y": "Code",
        "CountryCode_x": "CountryCode",
        "CountryCode_y": "CountryCode",
    }
    for old, new in rename_map.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    return df


def require_cols(df: pd.DataFrame, needed: list[str], name: str) -> None:
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"'{name}' missing columns: {missing}. Found: {df.columns.tolist()}")


def format_int(x) -> str:
    try:
        if pd.isna(x):
            return "—"
        return f"{int(float(x)):,}"
    except Exception:
        return "—"


# =========================
# Stats builders (your Overview/Diversity pages import these)
# =========================
def build_country_language_stats(languages: pd.DataFrame) -> pd.DataFrame:
    """Per-country language diversity stats from countrylanguage.csv."""
    df = languages.copy()
    df = normalize_columns(df)

    require_cols(df, ["CountryCode", "Language"], "languages")

    df["CountryCode"] = df["CountryCode"].astype(str)
    df["Language"] = df["Language"].astype(str)

    if "IsOfficial" in df.columns:
        df["IsOfficial"] = df["IsOfficial"].astype(str).str.upper()
    else:
        df["IsOfficial"] = "?"

    if "Percentage" in df.columns:
        df["Percentage"] = pd.to_numeric(df["Percentage"], errors="coerce")

    # number of languages per country
    lang_count = df.groupby("CountryCode")["Language"].nunique().rename("n_languages")

    # official count
    off_count = (
        df[df["IsOfficial"] == "T"]
        .groupby("CountryCode")["Language"]
        .nunique()
        .rename("n_official")
    )

    # top language by percentage (if available)
    if "Percentage" in df.columns:
        top = (
            df.sort_values(["CountryCode", "Percentage"], ascending=[True, False])
            .groupby("CountryCode")
            .head(1)[["CountryCode", "Language", "Percentage"]]
            .rename(columns={"Language": "top_language", "Percentage": "top_pct"})
            .set_index("CountryCode")
        )
    else:
        top = pd.DataFrame(index=lang_count.index, columns=["top_language", "top_pct"])

    out = pd.concat([lang_count, off_count, top], axis=1).fillna({"n_official": 0})
    out["n_official"] = out["n_official"].astype(int)
    return out.reset_index()


def build_global_language_stats(languages: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    """Per-language global stats: in how many countries it appears, official counts, avg percentage."""
    df = languages.copy()
    df = normalize_columns(df)
    require_cols(df, ["CountryCode", "Language"], "languages")

    df["CountryCode"] = df["CountryCode"].astype(str)
    df["Language"] = df["Language"].astype(str)

    if "IsOfficial" in df.columns:
        df["IsOfficial"] = df["IsOfficial"].astype(str).str.upper()
    else:
        df["IsOfficial"] = "?"

    if "Percentage" in df.columns:
        df["Percentage"] = pd.to_numeric(df["Percentage"], errors="coerce")

    countries = normalize_columns(countries.copy())
    if "Code" in countries.columns:
        code_to_name = dict(zip(countries["Code"].astype(str), countries.get("Name", countries["Code"]).astype(str)))
    else:
        code_to_name = {}

    g = df.groupby("Language")
    out = pd.DataFrame({
        "Language": g.size().index,
        "country_rows": g.size().values,
        "countries_spoken": g["CountryCode"].nunique().values,
        "countries_official": g.apply(lambda x: x.loc[x["IsOfficial"] == "T", "CountryCode"].nunique()).values,
    })

    if "Percentage" in df.columns:
        out["avg_pct"] = g["Percentage"].mean().values
        out["max_pct"] = g["Percentage"].max().values
    else:
        out["avg_pct"] = pd.NA
        out["max_pct"] = pd.NA

    out = out.sort_values(["countries_spoken", "countries_official"], ascending=False).reset_index(drop=True)
    return out

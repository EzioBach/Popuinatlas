from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import streamlit as st


# ----------------------------
# Paths
# ----------------------------
DATA_DIR = Path(__file__).parent / "data"
CITY_CSV = DATA_DIR / "city.csv"
COUNTRY_CSV = DATA_DIR / "country.csv"
LANG_CSV = DATA_DIR / "countrylanguage.csv"
WORLDCITIES_CSV = DATA_DIR / "worldcities.csv"  # optional


# ----------------------------
# Styling
# ----------------------------
def inject_global_css() -> None:
    st.markdown(
        """
<style>
/* Reduce top padding a bit */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Make charts/cards feel cleaner */
[data-testid="stMetric"] { 
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  padding: 14px 14px;
  border-radius: 16px;
}

/* Dataframes */
[data-testid="stDataFrame"] {
  border-radius: 16px;
  overflow: hidden;
}

/* Hero container */
.pop-hero {
  border-radius: 22px;
  padding: 22px 22px;
  border: 1px solid rgba(255,255,255,0.08);
  background: radial-gradient(1200px 500px at 15% 10%, rgba(120,90,255,0.35), transparent 60%),
              radial-gradient(900px 500px at 85% 0%, rgba(0,200,255,0.20), transparent 55%),
              rgba(255,255,255,0.03);
  box-shadow: 0 12px 45px rgba(0,0,0,0.35);
}

.pop-hero .appname {
  font-size: 18px;
  opacity: 0.9;
  letter-spacing: 0.2px;
  margin-bottom: 6px;
}

.pop-hero .pagetitle {
  font-size: 44px;
  font-weight: 800;
  margin: 4px 0 4px 0;
  line-height: 1.05;
}

.pop-hero .subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin-top: 6px;
}

.pop-pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  font-size: 13px;
  opacity: 0.95;
  margin-right: 10px;
}

.pop-muted { opacity: 0.75; }
</style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(icon: str, page_title: str, subtitle: str, pill: str = "World Geo-Linguistic Dashboard") -> None:
    st.markdown(
        f"""
<div class="pop-hero">
  <div class="appname">🧭 <b>Popuinatlas</b> — <span class="pop-muted">A Geo-Linguistic Atlas</span></div>
  <div>
    <span class="pop-pill">{pill}</span>
  </div>
  <div class="pagetitle">{icon} {page_title}</div>
  <div class="subtitle">{subtitle}</div>
  <div class="pop-muted" style="margin-top:10px;">Popuinatlas — A Geo-linguistic app • World languages, countries, and cities in one interactive atlas.</div>
</div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Data loading
# ----------------------------
@st.cache_data(show_spinner=False)
def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Fix common merge artifacts like Name_x/Name_y etc."""
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
        st.error(f"'{name}' is missing columns: {missing}. Found: {df.columns.tolist()}")
        st.stop()


def get_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Always returns (cities, countries, langs, worldcities_optional).

    Key idea: pages do NOT depend on 'Open Home first'.
    We load into session_state if missing.
    """
    if "cities" not in st.session_state:
        st.session_state["cities"] = normalize_columns(_read_csv(CITY_CSV))
    if "countries" not in st.session_state:
        st.session_state["countries"] = normalize_columns(_read_csv(COUNTRY_CSV))
    if "languages" not in st.session_state:
        st.session_state["languages"] = normalize_columns(_read_csv(LANG_CSV))

    # Optional worldcities
    if "worldcities" not in st.session_state:
        if WORLDCITIES_CSV.exists():
            st.session_state["worldcities"] = _read_csv(WORLDCITIES_CSV)
        else:
            st.session_state["worldcities"] = None

    cities = st.session_state["cities"].copy()
    countries = st.session_state["countries"].copy()
    langs = st.session_state["languages"].copy()
    worldcities = st.session_state["worldcities"]
    worldcities = worldcities.copy() if isinstance(worldcities, pd.DataFrame) else None

    # Basic schema checks
    require_cols(countries, ["Code", "Name"], "countries")
    require_cols(cities, ["CountryCode"], "cities")
    require_cols(langs, ["CountryCode", "Language"], "languages")

    countries["Code"] = countries["Code"].astype(str)
    cities["CountryCode"] = cities["CountryCode"].astype(str)
    langs["CountryCode"] = langs["CountryCode"].astype(str)

    return cities, countries, langs, worldcities


# ----------------------------
# Formatting helpers
# ----------------------------
def format_int(x) -> str:
    try:
        if pd.isna(x):
            return "—"
        return f"{int(x):,}"
    except Exception:
        return "—"


# ----------------------------
# Stats builders (THIS is what your pages import)
# ----------------------------
def build_country_language_stats(countries: pd.DataFrame, langs: pd.DataFrame) -> pd.DataFrame:
    """
    Per-country:
      - n_languages
      - n_official
      - entropy (if Percentage exists)
    """
    c = countries[["Code", "Name"]].copy()
    for col in ["Continent", "Region", "Population"]:
        if col in countries.columns:
            c[col] = countries[col]

    l = langs.copy()
    l["IsOfficial"] = l["IsOfficial"].astype(str).str.upper() if "IsOfficial" in l.columns else "?"
    has_pct = "Percentage" in l.columns

    if has_pct:
        l["Percentage"] = pd.to_numeric(l["Percentage"], errors="coerce")

    g = (
        l.groupby("CountryCode")
        .agg(
            n_languages=("Language", "nunique"),
            n_official=("IsOfficial", lambda s: int((s == "T").sum())),
        )
        .reset_index()
        .rename(columns={"CountryCode": "Code"})
    )

    out = c.merge(g, on="Code", how="left")
    out["n_languages"] = out["n_languages"].fillna(0).astype(int)
    out["n_official"] = out["n_official"].fillna(0).astype(int)

    # Entropy if Percentage exists and has data
    out["entropy"] = None
    if has_pct and l["Percentage"].notna().any():
        def entropy_for_country(df: pd.DataFrame) -> float:
            p = df["Percentage"].dropna().values
            if len(p) == 0:
                return float("nan")
            # convert percent to probability, normalize to sum=1 (dataset may not sum exactly)
            probs = (p / 100.0)
            s = probs.sum()
            if s <= 0:
                return float("nan")
            probs = probs / s
            return float(-sum(pi * math.log(pi) for pi in probs if pi > 0))

        ent = l.groupby("CountryCode").apply(entropy_for_country).reset_index(name="entropy")
        ent = ent.rename(columns={"CountryCode": "Code"})
        out = out.merge(ent, on="Code", how="left")

    return out


def build_global_language_stats(langs: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    """
    Global language table:
      - countries_spoken: number of countries where language appears
      - official_countries: number of countries where it is official (if IsOfficial exists)
    """
    l = langs.copy()
    l["IsOfficial"] = l["IsOfficial"].astype(str).str.upper() if "IsOfficial" in l.columns else "?"

    g = (
        l.groupby("Language")
        .agg(
            countries_spoken=("CountryCode", "nunique"),
            official_countries=("IsOfficial", lambda s: int((s == "T").sum())),
        )
        .reset_index()
        .sort_values(["countries_spoken", "official_countries"], ascending=False)
        .reset_index(drop=True)
    )
    return g

from __future__ import annotations

import math
from typing import Optional, Tuple

import pandas as pd
import streamlit as st


# -----------------------------
# Styling helpers
# -----------------------------
def inject_global_css() -> None:
    st.markdown(
        """
<style>
/* Slightly nicer spacing + typography */
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px; }

/* Hero card */
.pui-hero {
  background: radial-gradient(1200px 500px at 20% 0%, rgba(120,90,255,.25), rgba(0,0,0,0)) ,
              radial-gradient(900px 400px at 80% 10%, rgba(0,180,255,.18), rgba(0,0,0,0));
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 18px;
}
.pui-hero-title {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: .2px;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.pui-hero-sub {
  margin: 0;
  opacity: .85;
  font-size: 1.02rem;
  line-height: 1.35;
}
.pui-pill {
  display: inline-block;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: .9rem;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.04);
  opacity: .95;
}

/* Make metric labels wrap instead of truncating */
div[data-testid="stMetricLabel"] > div { white-space: normal !important; }

/* Sidebar spacing */
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
</style>
""",
        unsafe_allow_html=True,
    )


def render_hero(icon: str, title: str, subtitle: str, pill: Optional[str] = None) -> None:
    pill_html = f'<div class="pui-pill">{pill}</div>' if pill else ""
    st.markdown(
        f"""
<div class="pui-hero">
  <div class="pui-hero-title">{icon} {title}</div>
  <p class="pui-hero-sub">{subtitle}</p>
  {pill_html}
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# Data loading (works on every page)
# -----------------------------
@st.cache_data(show_spinner=False)
def _load_csvs() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    cities = pd.read_csv("data/city.csv")
    countries = pd.read_csv("data/country.csv")
    langs = pd.read_csv("data/countrylanguage.csv")

    worldcities = None
    try:
        worldcities = pd.read_csv("data/worldcities.csv")
    except Exception:
        worldcities = None

    return cities, countries, langs, worldcities


def get_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Loads CSVs and ALWAYS ensures session_state contains:
    - countries, cities, languages, worldcities (optional)
    This removes the need for "Open Home first".
    """
    cities, countries, langs, worldcities = _load_csvs()

    st.session_state["cities"] = cities
    st.session_state["countries"] = countries
    st.session_state["languages"] = langs
    st.session_state["worldcities"] = worldcities

    return cities, countries, langs, worldcities


# -----------------------------
# Robust dataframe utilities
# -----------------------------
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
        st.error(f"'{name}' is missing columns: {missing}. Found: {df.columns.tolist()}")
        st.stop()


def format_int(x) -> str:
    try:
        if pd.isna(x):
            return "—"
        return f"{int(x):,}"
    except Exception:
        return "—"


# -----------------------------
# Stats builders (used by Overview / Diversity)
# -----------------------------
def build_country_language_stats(countries: pd.DataFrame, langs: pd.DataFrame) -> pd.DataFrame:
    countries = normalize_columns(countries).copy()
    langs = normalize_columns(langs).copy()

    require_cols(countries, ["Code", "Name"], "countries")
    require_cols(langs, ["CountryCode", "Language"], "languages")

    countries["Code"] = countries["Code"].astype(str)
    langs["CountryCode"] = langs["CountryCode"].astype(str)

    # language counts per country
    n_lang = langs.groupby("CountryCode")["Language"].nunique().rename("n_languages")

    # official count
    if "IsOfficial" in langs.columns:
        tmp = langs.copy()
        tmp["IsOfficial"] = tmp["IsOfficial"].astype(str).str.upper()
        n_off = tmp[tmp["IsOfficial"] == "T"].groupby("CountryCode")["Language"].nunique().rename("n_official")
    else:
        n_off = pd.Series(dtype="float64", name="n_official")

    out = countries.merge(n_lang, left_on="Code", right_index=True, how="left")
    out = out.merge(n_off, left_on="Code", right_index=True, how="left")

    out["n_languages"] = out["n_languages"].fillna(0).astype(int)
    out["n_official"] = out["n_official"].fillna(0).astype(int)

    # entropy if percentages exist
    entropy = pd.Series(index=out["Code"], dtype="float64", name="entropy")

    if "Percentage" in langs.columns:
        tmp = langs[["CountryCode", "Language", "Percentage"]].copy()
        tmp["Percentage"] = pd.to_numeric(tmp["Percentage"], errors="coerce")
        tmp = tmp.dropna(subset=["Percentage"])
        # convert to proportions (0..1)
        tmp["p"] = tmp["Percentage"] / 100.0
        tmp = tmp[(tmp["p"] > 0) & (tmp["p"] <= 1)]

        def shannon(group: pd.DataFrame) -> float:
            ps = group["p"].values
            # normalize if sums are weird
            s = ps.sum()
            if s <= 0:
                return float("nan")
            ps = ps / s
            return float(-sum(p * math.log(p, 2) for p in ps if p > 0))

        H = tmp.groupby("CountryCode").apply(shannon)
        entropy.update(H)

    out["entropy"] = out["Code"].map(entropy)

    # keep standard columns if present
    for col in ["Continent", "Region", "Population"]:
        if col in out.columns:
            out[col] = out[col]

    return out


def build_global_language_stats(langs: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    langs = normalize_columns(langs).copy()
    countries = normalize_columns(countries).copy()

    require_cols(langs, ["CountryCode", "Language"], "languages")
    require_cols(countries, ["Code", "Name"], "countries")

    langs["CountryCode"] = langs["CountryCode"].astype(str)
    countries["Code"] = countries["Code"].astype(str)

    # count how many countries each language appears in
    g = langs.groupby("Language")["CountryCode"].nunique().rename("countries_spoken").reset_index()
    g = g.sort_values("countries_spoken", ascending=False).reset_index(drop=True)
    return g

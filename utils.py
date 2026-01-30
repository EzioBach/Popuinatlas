from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

def inject_global_css() -> None:
    st.markdown(
        """
<style>
/* Page padding */
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px; }

/* Make Plotly charts blend in */
[data-testid="stPlotlyChart"] > div { border-radius: 18px; overflow: hidden; }

/* Slightly nicer sidebar */
section[data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.06); }

/* Hero card */
.pop-hero {
  background: radial-gradient(1200px 600px at 20% 0%, rgba(120,70,255,0.28), rgba(0,0,0,0)) ,
              linear-gradient(135deg, rgba(30,40,70,0.75), rgba(10,14,22,0.6));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 22px;
  padding: 18px 18px;
  margin: 6px 0 18px 0;
}
.pop-hero-top { display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.pop-hero-title { font-size: 1.15rem; font-weight: 800; letter-spacing: 0.2px; opacity: 0.98; }
.pop-hero-sub { margin-top: 6px; opacity: 0.86; font-size: 0.98rem; line-height: 1.35; }
.pop-pill {
  display:inline-block; padding: 4px 10px;
  border-radius: 999px;
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

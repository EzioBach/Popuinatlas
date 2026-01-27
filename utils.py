import math
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_data():
    cities = pd.read_csv("data/city.csv")
    countries = pd.read_csv("data/country.csv")
    languages = pd.read_csv("data/countrylanguage.csv")

    # Optional: only if you added it
    try:
        worldcities = pd.read_csv("data/worldcities.csv")
    except Exception:
        worldcities = None

    return cities, countries, languages, worldcities

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

def prep_tables(cities: pd.DataFrame, countries: pd.DataFrame, langs: pd.DataFrame):
    cities = normalize_columns(cities).copy()
    countries = normalize_columns(countries).copy()
    langs = normalize_columns(langs).copy()

    require_cols(countries, ["Code", "Name"], "countries")
    require_cols(cities, ["CountryCode"], "cities")
    require_cols(langs, ["CountryCode", "Language"], "languages")

    countries["Code"] = countries["Code"].astype(str)
    countries["Name"] = countries["Name"].astype(str)

    langs["CountryCode"] = langs["CountryCode"].astype(str)
    langs["Language"] = langs["Language"].astype(str)

    if "IsOfficial" in langs.columns:
        langs["IsOfficial"] = langs["IsOfficial"].astype(str).str.upper()
    else:
        langs["IsOfficial"] = "?"

    if "Percentage" in langs.columns:
        langs["Percentage"] = pd.to_numeric(langs["Percentage"], errors="coerce")

    if "Population" in countries.columns:
        countries["Population"] = pd.to_numeric(countries["Population"], errors="coerce")

    if "Population" in cities.columns:
        cities["Population"] = pd.to_numeric(cities["Population"], errors="coerce")

    # Normalize cities name column if needed
    if "Name" not in cities.columns and "Name_x" in cities.columns:
        cities = cities.rename(columns={"Name_x": "Name"})

    return cities, countries, langs

def prep_worldcities(worldcities: pd.DataFrame | None) -> pd.DataFrame | None:
    if worldcities is None:
        return None

    wc = worldcities.copy()

    # Normalize common lat/lon names
    if "lng" in wc.columns and "lon" not in wc.columns:
        wc = wc.rename(columns={"lng": "lon"})
    if "longitude" in wc.columns and "lon" not in wc.columns:
        wc = wc.rename(columns={"longitude": "lon"})
    if "latitude" in wc.columns and "lat" not in wc.columns:
        wc = wc.rename(columns={"latitude": "lat"})
    if "Latitude" in wc.columns and "lat" not in wc.columns:
        wc = wc.rename(columns={"Latitude": "lat"})
    if "Longitude" in wc.columns and "lon" not in wc.columns:
        wc = wc.rename(columns={"Longitude": "lon"})

    # Coerce numeric
    if "lat" in wc.columns:
        wc["lat"] = pd.to_numeric(wc["lat"], errors="coerce")
    if "lon" in wc.columns:
        wc["lon"] = pd.to_numeric(wc["lon"], errors="coerce")

    # Population normalization
    for popcand in ["population", "pop", "Population"]:
        if popcand in wc.columns:
            wc[popcand] = pd.to_numeric(wc[popcand], errors="coerce")

    return wc

@st.cache_data(show_spinner=False)
def build_country_language_stats(countries: pd.DataFrame, langs: pd.DataFrame) -> pd.DataFrame:
    df = langs.copy()

    counts = df.groupby("CountryCode").agg(
        n_languages=("Language", "nunique"),
        n_official=("IsOfficial", lambda s: int((s == "T").sum()))
    ).reset_index()

    # Entropy only when percentages exist
    if "Percentage" in df.columns:
        ent_list = []
        for code, g in df.groupby("CountryCode"):
            g = g.dropna(subset=["Percentage"])
            if g.empty:
                ent_list.append((code, None))
                continue
            p = (g["Percentage"] / 100.0).clip(lower=0)
            p = p[p > 0]
            if p.empty:
                ent_list.append((code, None))
                continue
            entropy = float(-(p * p.apply(math.log)).sum())
            ent_list.append((code, entropy))
        entropy_df = pd.DataFrame(ent_list, columns=["CountryCode", "entropy"])
        out = counts.merge(entropy_df, on="CountryCode", how="left")
    else:
        out = counts.copy()
        out["entropy"] = None

    out = out.merge(
        countries[["Code", "Name", "Continent", "Region", "Population"]],
        left_on="CountryCode",
        right_on="Code",
        how="left"
    )
    out["Population"] = pd.to_numeric(out["Population"], errors="coerce")
    return out

@st.cache_data(show_spinner=False)
def build_global_language_stats(langs: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    merged = langs.merge(
        countries[["Code", "Continent", "Region", "Name"]],
        left_on="CountryCode",
        right_on="Code",
        how="left"
    )

    agg = merged.groupby("Language").agg(
        countries_spoken=("CountryCode", "nunique"),
        official_count=("IsOfficial", lambda s: int((s == "T").sum())),
        continents_count=("Continent", "nunique"),
    ).reset_index()

    if "Percentage" in merged.columns:
        agg["avg_percentage"] = merged.groupby("Language")["Percentage"].mean().values
    else:
        agg["avg_percentage"] = None

    return agg.sort_values("countries_spoken", ascending=False)

def format_int(x):
    try:
        if pd.isna(x):
            return "—"
        return f"{int(x):,}"
    except Exception:
        return "—"

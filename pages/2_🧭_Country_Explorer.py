import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

from utils import (
    APP_NAME, APP_ICON,
    ensure_data_in_session, sidebar_brand, normalize_columns
)

st.set_page_config(
    page_title=f"{APP_NAME} — Country Explorer",
    page_icon=APP_ICON,
    layout="wide",
)

ensure_data_in_session()
sidebar_brand()

countries = normalize_columns(st.session_state["countries"].copy())
cities = normalize_columns(st.session_state["cities"].copy())
langs = normalize_columns(st.session_state["languages"].copy())

# Basic schema checks
for col in ["Code", "Name"]:
    if col not in countries.columns:
        st.error(f"countries missing '{col}'. Found: {countries.columns.tolist()}")
        st.stop()
for col in ["CountryCode"]:
    if col not in cities.columns:
        st.error(f"cities missing '{col}'. Found: {cities.columns.tolist()}")
        st.stop()
for col in ["CountryCode", "Language"]:
    if col not in langs.columns:
        st.error(f"languages missing '{col}'. Found: {langs.columns.tolist()}")
        st.stop()

# Types
countries = countries.dropna(subset=["Code", "Name"]).copy()
countries["Code"] = countries["Code"].astype(str)
countries["Name"] = countries["Name"].astype(str)

cities["CountryCode"] = cities["CountryCode"].astype(str)
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

# Title
st.title("🧭 Country Explorer")
st.caption("Pick a country from the sidebar or click it on the map (single-click).")

# Labels
countries["_label"] = countries["Name"] + " (" + countries["Code"] + ")"
countries = countries.sort_values("_label").reset_index(drop=True)
label_to_iso3 = dict(zip(countries["_label"], countries["Code"]))
iso3_to_label = dict(zip(countries["Code"], countries["_label"]))

# Session selection
if "selected_iso3" not in st.session_state:
    st.session_state["selected_iso3"] = countries["Code"].iloc[0]

SELECTBOX_KEY = "country_selectbox_country_explorer"

def sidebar_changed():
    label = st.session_state[SELECTBOX_KEY]
    st.session_state["selected_iso3"] = label_to_iso3[label]

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    cur_iso = str(st.session_state["selected_iso3"])
    default_label = iso3_to_label.get(cur_iso, countries["_label"].iloc[0])

    if SELECTBOX_KEY not in st.session_state:
        st.session_state[SELECTBOX_KEY] = default_label
    else:
        if st.session_state[SELECTBOX_KEY] != default_label:
            st.session_state[SELECTBOX_KEY] = default_label

    st.selectbox(
        "Select a country",
        options=countries["_label"].tolist(),
        key=SELECTBOX_KEY,
        on_change=sidebar_changed,
    )

    st.divider()
    debug = st.toggle("Debug mode", value=False)

# Layout (more map space)
left, right = st.columns([1.7, 1])

# --- Map ---
with left:
    selected_iso3 = str(st.session_state["selected_iso3"])

    base_df = countries.copy()
    base_df["_base"] = 1

    fig = px.choropleth(
        base_df,
        locations="Code",
        locationmode="ISO-3",
        color="_base",
        hover_name="Name",
        title="World map (click a country)",
        template="plotly_dark",
        range_color=(0, 1),
    )
    fig.update_traces(
        marker_line_width=0.6,
        marker_line_color="rgba(255,255,255,0.28)",
        hovertemplate="<b>%{hovertext}</b><extra></extra>",
    )
    fig.update_layout(
        coloraxis_showscale=False,
        height=560,
        margin=dict(l=0, r=0, t=60, b=0),
        geo=dict(
            projection_type="natural earth",
            showframe=False,
            showcountries=True,
            countrycolor="rgba(255,255,255,0.20)",
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.15)",
            showocean=True,
            oceancolor="rgb(12,16,25)",
            showland=True,
            landcolor="rgb(20,25,35)",
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    # Overlay highlight
    sel_df = countries[countries["Code"] == selected_iso3].copy()
    if not sel_df.empty:
        sel_df["_sel"] = 1
        overlay = px.choropleth(
            sel_df,
            locations="Code",
            locationmode="ISO-3",
            color="_sel",
            hover_name="Name",
            template="plotly_dark",
            range_color=(0, 1),
        )
        overlay.update_traces(
            marker_line_width=1.2,
            marker_line_color="rgba(255,255,255,0.75)",
            hovertemplate="<b>%{hovertext}</b><extra></extra>",
        )
        for tr in overlay.data:
            fig.add_trace(tr)

    clicked = plotly_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        override_height=560,
        key="country_map_click_events",
    )

    if debug:
        st.write("clicked payload:", clicked)

    # Decode click
    if clicked and len(clicked) > 0:
        d = clicked[0]
        iso = None
        if d.get("location"):
            iso = str(d["location"])
        elif d.get("pointNumber") is not None:
            idx = int(d["pointNumber"])
            if 0 <= idx < len(countries):
                iso = str(countries.iloc[idx]["Code"])

        if iso and iso in iso3_to_label and iso != st.session_state["selected_iso3"]:
            st.session_state["selected_iso3"] = iso
            st.session_state[SELECTBOX_KEY] = iso3_to_label[iso]
            st.rerun()

# --- Right details (stacked, no truncation) ---
with right:
    selected_iso3 = str(st.session_state["selected_iso3"])
    row = countries.loc[countries["Code"] == selected_iso3].head(1)

    name = row["Name"].iloc[0] if not row.empty else selected_iso3
    st.subheader(name)
    st.caption(f"ISO-3: {selected_iso3}")

    continent = row["Continent"].iloc[0] if "Continent" in row.columns and not row.empty else "—"
    region = row["Region"].iloc[0] if "Region" in row.columns and not row.empty else "—"
    population = row["Population"].iloc[0] if "Population" in row.columns and not row.empty else None

    st.markdown("#### Continent")
    st.write(continent if str(continent).strip() else "—")

    st.markdown("#### Region")
    st.write(region if str(region).strip() else "—")

    st.markdown("#### Population")
    st.write(f"{int(population):,}" if pd.notna(population) else "—")

st.divider()

# --- Tabs for content (better UX) ---
tab_lang, tab_city = st.tabs(["🗣️ Languages", "🏙️ Cities"])  # tabs are official :contentReference[oaicite:4]{index=4}

with tab_lang:
    st.subheader("🗣️ Languages")
    selected_iso3 = str(st.session_state["selected_iso3"])
    df = langs.loc[langs["CountryCode"] == selected_iso3].copy()

    if df.empty:
        st.warning("No language rows found for this country.")
    else:
        official = df[df["IsOfficial"] == "T"].copy()
        other = df[df["IsOfficial"] != "T"].copy()

        c1, c2 = st.columns(2)

        def render_lang(dfx, title):
            st.markdown(f"### {title}")
            if dfx.empty:
                st.write("—")
                return
            if "Percentage" in dfx.columns and dfx["Percentage"].notna().any():
                dfx = dfx.sort_values("Percentage", ascending=False)
                out = dfx[["Language", "Percentage"]].copy()
                out["Percentage"] = out["Percentage"].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
            else:
                out = dfx[["Language"]].copy()
            st.dataframe(out.reset_index(drop=True), use_container_width=True)

        with c1:
            render_lang(official, "🏛️ Official")

        with c2:
            render_lang(other, "🗨️ Other")

with tab_city:
    st.subheader("🏙️ Cities (top by population)")
    selected_iso3 = str(st.session_state["selected_iso3"])
    df = cities.loc[cities["CountryCode"] == selected_iso3].copy()

    if df.empty:
        st.write("No cities found for this country.")
    else:
        top_n = st.slider("How many cities?", 5, 30, 10, 5, key="topn_country_cities")
        if "Population" in df.columns:
            df["Population"] = pd.to_numeric(df["Population"], errors="coerce")

        name_col = "Name" if "Name" in df.columns else None
        if not name_col:
            st.error("City name column not found (expected 'Name').")
            st.stop()

        top = df.sort_values("Population", ascending=False).head(top_n)
        cols = [name_col]
        if "District" in top.columns:
            cols.append("District")
        if "Population" in top.columns:
            cols.append("Population")

        st.dataframe(top[cols].reset_index(drop=True), use_container_width=True)

        if "Population" in top.columns and top["Population"].notna().any():
            fig_bar = px.bar(top, x=name_col, y="Population", title=f"Top {top_n} cities by population", template="plotly_dark")
            fig_bar.update_layout(margin=dict(l=0, r=0, t=50, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)

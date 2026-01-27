import streamlit as st
import pandas as pd
import plotly.express as px
from utils import format_int

st.set_page_config(page_title="Country Explorer", layout="wide")
st.title("🧭 Country Explorer")
st.caption("Select from the sidebar or click a country on the map. The sidebar stays synced.")

# -------------------------
# Safety
# -------------------------
required = {"countries", "cities", "languages"}
if not required.issubset(st.session_state.keys()):
    st.error("Open Home first (main.py).")
    st.stop()

countries = st.session_state["countries"].copy()
cities = st.session_state["cities"].copy()
langs = st.session_state["languages"].copy()

# -------------------------
# Prep / labels
# -------------------------
countries = countries.dropna(subset=["Code", "Name"]).copy()
countries["Code"] = countries["Code"].astype(str)
countries["Name"] = countries["Name"].astype(str)

countries["_label"] = countries["Name"] + " (" + countries["Code"] + ")"
countries = countries.sort_values("_label").reset_index(drop=True)

label_to_iso3 = dict(zip(countries["_label"], countries["Code"]))
iso3_to_label = dict(zip(countries["Code"], countries["_label"]))

# Single source of truth for current country
if "selected_iso3" not in st.session_state:
    st.session_state["selected_iso3"] = countries["Code"].iloc[0]

SELECTBOX_KEY = "country_selectbox_country_explorer"

def set_country(iso3: str):
    """Update country selection everywhere (session + selectbox)."""
    iso3 = str(iso3)
    if iso3 not in iso3_to_label:
        return
    st.session_state["selected_iso3"] = iso3
    st.session_state[SELECTBOX_KEY] = iso3_to_label[iso3]

def get_clicked_iso3(selection_obj):
    """
    Streamlit versions can return selection data in different shapes.
    This function extracts the first clicked country ISO3 robustly.
    """
    if not selection_obj:
        return None

    pts = None

    # Case A: selection_obj is a dict
    if isinstance(selection_obj, dict):
        pts = selection_obj.get("points")
        if not pts:
            pts = (selection_obj.get("selection") or {}).get("points")

    # Case B: selection_obj is a "dict-like" object with .selection
    if pts is None and hasattr(selection_obj, "selection"):
        sel = getattr(selection_obj, "selection")
        if isinstance(sel, dict):
            pts = sel.get("points")

    if not pts:
        return None

    p0 = pts[0] if isinstance(pts, list) else None
    if not p0 or not isinstance(p0, dict):
        return None

    # Best: Plotly choropleth returns ISO3 in "location"
    iso = p0.get("location")

    # Fallback: use customdata if present
    if not iso:
        cd = p0.get("customdata")
        if isinstance(cd, (list, tuple)) and len(cd) > 0:
            iso = cd[0]

    return str(iso) if iso else None

# -------------------------
# Sidebar (synced to selected_iso3)
# -------------------------
with st.sidebar:
    st.header("Controls")

    # Force selectbox to reflect current selected_iso3 (important)
    current_iso3 = str(st.session_state["selected_iso3"])
    st.session_state[SELECTBOX_KEY] = iso3_to_label.get(current_iso3, countries["_label"].iloc[0])

    selected_label = st.selectbox(
        "Select a country",
        options=countries["_label"].tolist(),
        key=SELECTBOX_KEY,
    )

    dropdown_iso3 = label_to_iso3[selected_label]
    if dropdown_iso3 != st.session_state["selected_iso3"]:
        set_country(dropdown_iso3)
        st.rerun()

    st.divider()
    debug = st.toggle("Debug mode", value=False)

# -------------------------
# Layout
# -------------------------
left, right = st.columns([1.6, 1])

# -------------------------
# Map (click → update selected_iso3)
# -------------------------
with left:
    selected_iso3 = str(st.session_state["selected_iso3"])

    # highlight column
    countries["_highlight"] = (countries["Code"] == selected_iso3).astype(int)

    fig = px.choropleth(
        countries,
        locations="Code",
        locationmode="ISO-3",
        color="_highlight",
        hover_name="Name",
        custom_data=["Code"],  # reliable fallback
        template="plotly_dark",
        title="World map (click a country to select it)",
        range_color=(0, 1),
    )

    fig.update_traces(
        marker_line_width=0.6,
        marker_line_color="rgba(255,255,255,0.30)",
        hovertemplate="<b>%{hovertext}</b><extra></extra>",
    )

    fig.update_layout(
        coloraxis_showscale=False,
        height=560,
        margin=dict(l=0, r=0, t=60, b=0),
        clickmode="event+select",  # makes click behave like a “selection”
        geo=dict(
            projection_type="natural earth",
            showframe=False,
            showcountries=True,
            countrycolor="rgba(255,255,255,0.22)",
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.15)",
            showocean=True,
            oceancolor="rgb(12,16,25)",
            showland=True,
            landcolor="rgb(20,25,35)",
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    selection = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key="country_map_native",
    )

    if debug:
        st.write("raw selection:", selection)

    clicked_iso3 = get_clicked_iso3(selection)
    if clicked_iso3 and clicked_iso3 != st.session_state["selected_iso3"]:
        set_country(clicked_iso3)
        st.rerun()

# -------------------------
# Details panel
# -------------------------
with right:
    selected_iso3 = str(st.session_state["selected_iso3"])
    row = countries[countries["Code"] == selected_iso3].head(1)

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
    st.write(format_int(population))

st.divider()

# -------------------------
# Languages
# -------------------------
st.subheader("🗣️ Languages")
selected_iso3 = str(st.session_state["selected_iso3"])
country_langs = langs[langs["CountryCode"].astype(str) == selected_iso3].copy()

if country_langs.empty:
    st.warning("No language rows found for this country.")
else:
    if "IsOfficial" in country_langs.columns:
        country_langs["IsOfficial"] = country_langs["IsOfficial"].astype(str).str.upper()
    else:
        country_langs["IsOfficial"] = "?"

    if "Percentage" in country_langs.columns:
        country_langs["Percentage"] = pd.to_numeric(country_langs["Percentage"], errors="coerce")

    official = country_langs[country_langs["IsOfficial"] == "T"].copy()
    other = country_langs[country_langs["IsOfficial"] != "T"].copy()

    c1, c2 = st.columns(2)

    def render_lang(df: pd.DataFrame, title: str):
        st.markdown(f"### {title}")
        if df.empty:
            st.write("—")
            return
        if "Percentage" in df.columns and df["Percentage"].notna().any():
            df = df.sort_values("Percentage", ascending=False)
            out = df[["Language", "Percentage"]].copy()
            out["Percentage"] = out["Percentage"].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
        else:
            out = df[["Language"]].copy()
        st.dataframe(out.reset_index(drop=True), use_container_width=True)

    with c1:
        render_lang(official, "🏛️ Official")
    with c2:
        render_lang(other, "🗨️ Other")

st.divider()

# -------------------------
# Cities
# -------------------------
st.subheader("🏙️ Cities (top by population)")
country_cities = cities[cities["CountryCode"].astype(str) == selected_iso3].copy()

if country_cities.empty:
    st.write("No cities found for this country.")
else:
    top_n = st.slider("How many cities?", 5, 30, 10, 5, key="top_n_country_explorer")

    if "Population" in country_cities.columns:
        country_cities["Population"] = pd.to_numeric(country_cities["Population"], errors="coerce")

    city_name_col = "Name" if "Name" in country_cities.columns else "Name"
    top = country_cities.sort_values("Population", ascending=False).head(top_n)

    cols = [city_name_col]
    if "District" in top.columns:
        cols.append("District")
    if "Population" in top.columns:
        cols.append("Population")

    st.dataframe(top[cols].reset_index(drop=True), use_container_width=True)

    if "Population" in top.columns and top["Population"].notna().any():
        figb = px.bar(top, x=city_name_col, y="Population", title=f"Top {top_n} cities by population", template="plotly_dark")
        figb.update_layout(margin=dict(l=0, r=0, t=60, b=0))
        st.plotly_chart(figb, use_container_width=True)

import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Language Explorer", layout="wide")
st.title("🗣️ Language Explorer")
st.caption("Pick a language → see where it is listed, official status, and prevalence (if available).")

if not {"countries", "languages"}.issubset(st.session_state.keys()):
    st.error("Open Home first (main.py).")
    st.stop()

countries = st.session_state["countries"]
langs = st.session_state["languages"]

all_langs = sorted(langs["Language"].dropna().unique().tolist())
selected = st.selectbox("Choose a language", all_langs, key="language_selectbox")

filtered = langs[langs["Language"] == selected].copy()
merged = filtered.merge(
    countries[["Code", "Name", "Continent", "Region", "Population"]],
    left_on="CountryCode",
    right_on="Code",
    how="left",
)

k1, k2, k3 = st.columns(3)
k1.metric("Countries where listed", f"{merged['Name'].nunique():,}")
k2.metric("Official rows", f"{int((merged.get('IsOfficial','')=='T').sum()):,}")
k3.metric("Avg % (if available)", f"{merged['Percentage'].mean():.2f}%" if "Percentage" in merged.columns and merged["Percentage"].notna().any() else "—")

st.divider()

left, right = st.columns([1.25, 1])

with left:
    if "Percentage" in merged.columns and merged["Percentage"].notna().any():
        fig = px.choropleth(
            merged,
            locations="Code",
            locationmode="ISO-3",
            color="Percentage",
            hover_name="Name",
            hover_data={"IsOfficial": True, "Percentage": True},
            template="plotly_dark",
            title=f"{selected} prevalence by country (%)",
        )
    else:
        merged["_spoken"] = 1
        fig = px.choropleth(
            merged,
            locations="Code",
            locationmode="ISO-3",
            color="_spoken",
            hover_name="Name",
            template="plotly_dark",
            title=f"Countries where {selected} is listed",
            range_color=(0, 1),
        )
        fig.update_layout(coloraxis_showscale=False)

    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0), height=520)
    st.plotly_chart(fig, use_container_width=True)

with right:
    by_cont = merged.groupby("Continent").agg(
        countries=("Code", "nunique"),
        official=("IsOfficial", lambda s: int((s == "T").sum())),
    ).reset_index().sort_values("countries", ascending=False)

    fig2 = px.bar(by_cont, x="countries", y="Continent", orientation="h",
                  template="plotly_dark", title="Countries by continent")
    fig2.update_layout(margin=dict(l=0, r=0, t=60, b=0), yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Country list")

cols = ["Name", "Continent", "Region", "IsOfficial"]
if "Percentage" in merged.columns:
    cols.append("Percentage")

st.dataframe(
    merged[cols].sort_values("Percentage", ascending=False) if "Percentage" in merged.columns else merged[cols],
    use_container_width=True
)

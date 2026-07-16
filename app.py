import math
import os

import altair as alt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

DATA_FILE = "neo_data_scored.csv"
GROQ_MODEL = "llama-3.3-70b-versatile"

RISK_COLORS = {
    "Low": "#0B3D91",
    "Moderate": "#2563EB",
    "High": "#FC3D21",
    "Critical": "#B91C1C",
}

CATEGORY_ORDER = ["Low", "Moderate", "High", "Critical"]


def inject_space_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap');

            .stApp {
                background-color: #F5F6F8;
                color: #111827;
            }

            body {
                background-color: #F5F6F8;
            }

            .top-nav {
                background: linear-gradient(180deg, #0B3D91 0%, #0A2A6D 100%);
                padding: 2rem 1.5rem;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
            }

            .top-nav::before {
                content: '';
                position: absolute;
                top: -12px;
                right: -12px;
                width: 180px;
                height: 180px;
                background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.12), transparent 48%);
                opacity: 0.35;
            }

            .top-nav::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 120px;
                background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08), transparent 40%);
                opacity: 0.4;
            }

            .top-nav-title {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: 0.16em;
                color: #FFFFFF;
                margin: 0 0 0.5rem 0;
                position: relative;
                z-index: 1;
            }

            .hero-subtitle {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 1rem;
                font-weight: 400;
                letter-spacing: 0.08em;
                line-height: 1.7;
                color: #D1D5DB;
                margin: 0;
                max-width: 900px;
                position: relative;
                z-index: 1;
            }

            [data-testid="stSidebar"] {
                background: #F5F6F8;
                border-right: 1px solid #D1D5DB;
            }

            [data-testid="stSidebar"] * {
                color: #111827 !important;
            }

            .mission-title {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: 0.16em;
                margin: 0;
                color: #0B3D91;
            }

            .mission-subtitle {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                text-align: left;
                color: #374151;
                letter-spacing: 0.06em;
                font-size: 0.95rem;
                margin-top: 0.5rem;
                margin-bottom: 1.5rem;
                max-width: 900px;
            }

            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .neo-card,
            .briefing-box,
            .metric-card,
            .panel-card {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 1.25rem;
                margin-bottom: 0;
            }

            .neo-card {
                padding: 1rem 1.1rem;
            }

            .neo-name {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 1rem;
                font-weight: 700;
                color: #111827;
                margin-bottom: 0.55rem;
            }

            .risk-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.3rem 0.75rem;
                border-radius: 3px;
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
                color: #FFFFFF;
            }

            .risk-badge.low,
            .risk-badge.moderate {
                background: #0B3D91;
            }

            .risk-badge.high,
            .risk-badge.critical {
                background: #FC3D21;
            }

            .neo-detail {
                font-family: 'Roboto Mono', 'Courier New', monospace;
                font-size: 0.85rem;
                color: #374151;
                line-height: 1.75;
            }

            .neo-detail span {
                color: #0B3D91;
            }

            .section-header {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 1rem;
                letter-spacing: 0.18em;
                color: #0B3D91;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.25rem;
                border-bottom: 1px solid #D1D5DB;
            }

            div[data-testid="stMetric"] {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0.75rem 1rem;
                color: #111827;
            }

            div[data-testid="stMetric"] label {
                color: #6B7280 !important;
            }

            div[data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #111827 !important;
                font-family: 'Roboto Mono', 'Courier New', monospace !important;
            }

            .briefing-box {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 1.3rem 1.4rem;
                margin: 1rem 0 1.5rem 0;
            }

            .briefing-label {
                font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 0.75rem;
                letter-spacing: 0.18em;
                color: #6B7280;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }

            .briefing-target {
                font-family: 'Roboto Mono', 'Courier New', monospace;
                font-size: 0.82rem;
                color: #111827;
                margin-bottom: 0.75rem;
            }

            .briefing-text {
                font-family: 'Roboto Mono', 'Courier New', monospace;
                font-size: 0.95rem;
                color: #374151;
                line-height: 1.75;
            }

            .space-panel {
                background: #0A0E17;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 1.25rem;
                color: #FFFFFF;
            }

            .space-panel h2,
            .space-panel p {
                color: #FFFFFF;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_miss_distance(km: float) -> str:
    if pd.isna(km):
        return "N/A"
    if km >= 1_000_000:
        return f"{km / 1_000_000:,.2f} million km"
    if km >= 1_000:
        return f"{km / 1_000:,.1f} thousand km"
    return f"{km:,.1f} km"


def render_asteroid_card(row: pd.Series) -> None:
    risk_class = row["risk_category"].lower()
    st.markdown(
        f"""
        <div class="neo-card">
            <div class="neo-name">{row["name"]}</div>
            <div class="risk-badge {risk_class}">
                {row["risk_category"]}
            </div>
            <div class="neo-detail">
                <span>Scale:</span> {row["scale_comparison"]}<br>
                <span>Approach:</span> {row["close_approach_date"]}<br>
                <span>Miss distance:</span> {format_miss_distance(row["miss_distance_km"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


def generate_briefing(asteroid: pd.Series, api_key: str) -> str:
    client = Groq(api_key=api_key)
    prompt = f"""You are a NASA JPL mission control analyst delivering a near-Earth object tracking briefing.

Write a calm, professional 2-3 sentence briefing about this asteroid. Use precise, measured language — informative but not alarmist. Do not use exclamation marks or sensational phrasing.

Asteroid data:
- Name: {asteroid["name"]}
- Risk category: {asteroid["risk_category"]} (score: {asteroid["risk_score"]:.1f}/100)
- Size comparison: {asteroid["scale_comparison"]}
- Estimated max diameter: {asteroid["estimated_diameter_max_km"]:.3f} km
- Relative velocity: {float(asteroid["velocity_kmh"]):,.0f} km/h
- Miss distance: {format_miss_distance(asteroid["miss_distance_km"])}
- Close approach date: {asteroid["close_approach_date"]}
- Potentially hazardous: {asteroid["is_potentially_hazardous"]}

Respond with only the briefing text, no labels or preamble."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def render_briefing_box(asteroid_name: str, briefing_text: str) -> None:
    st.markdown(
        f"""
        <div class="briefing-box">
            <div class="briefing-label">Mission Analyst Briefing</div>
            <div class="briefing-target">Subject: {asteroid_name}</div>
            <div class="briefing-text">{briefing_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_orbit_visualization(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        return

    distances = filtered["miss_distance_km"].fillna(0).astype(float)
    scale_factor = 1e5
    radii = (distances / scale_factor).tolist()
    n = len(radii)
    angles = [i * 2 * math.pi / max(n, 1) for i in range(n)]
    elevations = [((i / max(n - 1, 1)) - 0.5) * (math.pi / 6) for i in range(n)]

    asteroid_x = [r * math.cos(a) * math.cos(e) for r, a, e in zip(radii, angles, elevations)]
    asteroid_y = [r * math.sin(a) * math.cos(e) for r, a, e in zip(radii, angles, elevations)]
    asteroid_z = [r * math.sin(e) for r, e in zip(radii, elevations)]

    sizes = (
        filtered["estimated_diameter_max_km"].fillna(0).astype(float) * 16
    ).clip(lower=6, upper=28)
    colors = [RISK_COLORS.get(cat, "#0B3D91") for cat in filtered["risk_category"]]

    hover_text = [
        f"{row['name']}<br>Risk: {row['risk_category']}<br>Diameter: {row['estimated_diameter_max_km']:.3f} km<br>Miss distance: {format_miss_distance(row['miss_distance_km'])}"
        for _, row in filtered.iterrows()
    ]

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=[0],
                y=[0],
                z=[0],
                mode="markers+text",
                marker=dict(size=10, color="#FFFFFF", symbol="circle"),
                text=["Earth"],
                textposition="top center",
                name="Earth",
                hoverinfo="text",
                hovertext=["Earth - reference origin"],
            ),
            go.Scatter3d(
                x=asteroid_x,
                y=asteroid_y,
                z=asteroid_z,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=colors,
                    opacity=0.9,
                    line=dict(width=0),
                ),
                hovertemplate="%{text}<extra></extra>",
                text=hover_text,
                name="Asteroids",
            ),
        ]
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0A1830",
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False),
            bgcolor="#0A1830",
            camera=dict(
                eye=dict(x=1.5, y=1.3, z=0.8),
            ),
            aspectmode='auto',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="#D1D5DB",
            borderwidth=1,
            font=dict(color="#FFFFFF"),
        ),
    )

    st.markdown('<p class="section-header">ORBITAL VISUALIZATION</p>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="NEO Mission Control",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_space_theme()
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

    df = load_data()

    st.markdown('<div class="top-nav"><p class="top-nav-title">NEO MISSION CONTROL</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="mission-title">Mission Control Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="mission-subtitle">Near-Earth object tracking and risk monitoring aligned to NASA mission data standards</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### 🎛️ Filters")
        selected_categories = st.multiselect(
            "Risk category",
            options=CATEGORY_ORDER,
            default=CATEGORY_ORDER,
        )
        sort_by = st.selectbox(
            "Sort cards by",
            options=["Risk score (high → low)", "Approach date", "Name"],
        )

    filtered = df[df["risk_category"].isin(selected_categories)].copy()

    if sort_by == "Risk score (high → low)":
        filtered = filtered.sort_values("risk_score", ascending=False)
    elif sort_by == "Approach date":
        filtered = filtered.sort_values("close_approach_date")
    else:
        filtered = filtered.sort_values("name")

    col_metrics = st.columns(4)
    col_metrics[0].metric("Tracked objects", len(filtered))
    col_metrics[1].metric("Critical", int((filtered["risk_category"] == "Critical").sum()))
    col_metrics[2].metric("High risk", int((filtered["risk_category"] == "High").sum()))
    col_metrics[3].metric("Avg risk score", f"{filtered['risk_score'].mean():.1f}" if len(filtered) else "—")

    if "briefing_text" not in st.session_state:
        st.session_state.briefing_text = None
    if "briefing_asteroid" not in st.session_state:
        st.session_state.briefing_asteroid = None

    if not filtered.empty:
        asteroid_names = filtered["name"].tolist()
        default_index = 0

        briefing_header, briefing_controls = st.columns([3, 1])
        with briefing_header:
            st.markdown(
                '<p class="section-header">MISSION ANALYST BRIEFING</p>',
                unsafe_allow_html=True,
            )
        with briefing_controls:
            selected_name = st.selectbox(
                "Briefing target",
                options=asteroid_names,
                index=default_index,
                label_visibility="collapsed",
            )
            generate_clicked = st.button("Generate Briefing", use_container_width=True)

        selected_asteroid = filtered[filtered["name"] == selected_name].iloc[0]

        if generate_clicked:
            if not groq_api_key:
                st.error("GROQ_API_KEY not found in .env")
            else:
                with st.spinner("Consulting mission analyst..."):
                    try:
                        st.session_state.briefing_text = generate_briefing(
                            selected_asteroid, groq_api_key
                        )
                        st.session_state.briefing_asteroid = selected_name
                    except Exception as exc:
                        st.error(f"Briefing generation failed: {exc}")

        if (
            st.session_state.briefing_text
            and st.session_state.briefing_asteroid == selected_name
        ):
            render_briefing_box(selected_name, st.session_state.briefing_text)

        render_orbit_visualization(filtered)

    chart_col, cards_col = st.columns([1, 1])

    with chart_col:
        st.markdown('<p class="section-header">RISK SCORE DISTRIBUTION</p>', unsafe_allow_html=True)
        chart_df = filtered.sort_values("risk_score", ascending=False).reset_index(drop=True)
        chart_df["rank"] = chart_df.index + 1

        scatter = (
            alt.Chart(chart_df)
            .mark_circle(size=70, opacity=0.85)
            .encode(
                x=alt.X("rank:Q", title="Asteroid (sorted by risk score)"),
                y=alt.Y("risk_score:Q", title="Risk score", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color(
                    "risk_category:N",
                    title="Risk category",
                    scale=alt.Scale(
                        domain=CATEGORY_ORDER,
                        range=[RISK_COLORS[c] for c in CATEGORY_ORDER],
                    ),
                ),
                tooltip=["name", "risk_score", "risk_category", "close_approach_date"],
            )
            .properties(height=420)
            .configure_axis(labelColor="#9aabd4", titleColor="#c8d6ff", gridColor="rgba(0,229,255,0.08)")
            .configure_view(strokeWidth=0)
            .configure_legend(labelColor="#c8d6ff", titleColor="#c8d6ff")
        )
        st.altair_chart(scatter, use_container_width=True)

    with cards_col:
        st.markdown('<p class="section-header">ASTEROID TRACKING CARDS</p>', unsafe_allow_html=True)
        if filtered.empty:
            st.info("No asteroids match the selected filters.")
        else:
            rows = [filtered.iloc[i : i + 3] for i in range(0, len(filtered), 3)]
            for chunk in rows:
                cols = st.columns(3)
                for idx, (_, row) in enumerate(chunk.iterrows()):
                    with cols[idx]:
                        render_asteroid_card(row)


if __name__ == "__main__":
    main()

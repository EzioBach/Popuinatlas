import streamlit as st

APP_NAME = "Popuinatlas"
APP_SUBTITLE = "A Geo-Linguistic Atlas"
APP_LINE = "Popuinatlas - A Geo linguistic app World Languages Dashboard"

def inject_global_css() -> None:
    """Global styling (lightweight, readable, 'app-like' layout)."""
    st.markdown(
        """
        <style>
        /* Slightly tighter layout + better typography */
        .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px; }
        h1, h2, h3 { letter-spacing: -0.02em; }
        p, li { line-height: 1.55; }

        /* Hero card */
        .hero {
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(17,26,46,0.80));
            border-radius: 18px;
            padding: 18px 18px 14px 18px;
            margin: 0.25rem 0 1.0rem 0;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0;
        }
        .hero-sub {
            opacity: 0.90;
            font-size: 1.05rem;
            margin: 0.35rem 0 0 0;
        }
        .hero-line {
            opacity: 0.75;
            font-size: 0.95rem;
            margin-top: 0.6rem;
        }

        /* Cards */
        .card {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(17,26,46,0.60);
            border-radius: 16px;
            padding: 14px 14px 10px 14px;
            margin: 0.5rem 0;
        }
        .card h4 { margin: 0 0 0.4rem 0; }
        .muted { opacity: 0.75; }
        .badge {
            display: inline-block;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.06);
            font-size: 0.85rem;
            margin-right: 0.35rem;
        }

        /* Better dataframe spacing */
        div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

        </style>
        """,
        unsafe_allow_html=True,
    )

def render_hero(page_emoji: str, page_title: str, page_desc: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <p class="hero-title">{page_emoji} {APP_NAME} <span class="muted">— {APP_SUBTITLE}</span></p>
          <p class="hero-sub"><span class="badge">{page_title}</span> {page_desc}</p>
          <p class="hero-line">{APP_LINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def card(title: str, body_md: str) -> None:
    st.markdown(
        f"""
        <div class="card">
          <h4>{title}</h4>
          <div class="muted">{body_md}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

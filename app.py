"""
Estancia San Eduardo — Selección de Vaquillonas
Bragado, Buenos Aires · Análisis de Inteligencia Ganadera

Run: python3 -m streamlit run app.py
"""
from __future__ import annotations

import base64
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image

# ── page config ────────────────────────────────────────────────────────────────
_favicon = Image.open(Path(__file__).parent / "assets" / "favicon.png")
st.set_page_config(
    page_title="San Eduardo · Selección de Vaquillonas",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).parent
DATA   = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"
FIGS   = ROOT / "outputs" / "figures"
ASSETS = ROOT / "assets"

# ── image helper ───────────────────────────────────────────────────────────────
def _b64(path: Path, mime: str = "image/jpeg") -> str:
    if not path.exists():
        return ""
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

HERO_B64   = _b64(ASSETS / "hero.jpg")
FARM_B64   = _b64(ASSETS / "farm_calves.jpg")
AUTHOR_B64 = _b64(ASSETS / "author_pro.jpg", "image/png")

# ── design tokens ──────────────────────────────────────────────────────────────
FOREST   = "#0D2B1F"
PRIMARY  = "#1B4332"
MID      = "#2D6A4F"
LIGHT    = "#95D5B2"
TERRA    = "#C4622D"
TERRA_DK = "#9A4620"
AMBER    = "#D4A017"
AMBER_L  = "#FEF3C7"
RED      = "#991B1B"
RED_L    = "#FEE2E2"
GOLD     = "#D4A017"
ESPRESSO = "#2C1A0E"
TAUPE    = "#8B7355"
SAGE     = "#6B7C5C"
G900     = "#2C1A0E"
G700     = "#5C4535"
G500     = "#8B7355"
G300     = "#E0D5C5"
G100     = "#F5EFE4"
BG       = "#F0E8D8"
CREAM    = "#FBF7F0"
WHITE    = "#FFFFFF"

# ── SVG icons ─────────────────────────────────────────────────────────────────
ICO_CHART = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="3" y="10" width="4" height="11"/><rect x="10" y="6" width="4" height="15"/><rect x="17" y="3" width="4" height="18"/></svg>'
ICO_CHECK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>'
ICO_BRAIN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg>'
ICO_DB    = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3S3 13.66 3 12"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>'
ICO_COMP  = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polygon points="16.24,7.76 14.12,14.12 7.76,16.24 9.88,9.88" fill="currentColor" stroke="none"/></svg>'
ICO_LINK  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
ICO_STAR  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
ICO_WARN  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
ICO_X     = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'

# ── global CSS ─────────────────────────────────────────────────────────────────
_hero_bg = f"url('{HERO_B64}')" if HERO_B64 else f"linear-gradient(135deg, {FOREST}, {PRIMARY})"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400;1,700&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600&display=swap');

html, body {{ overflow-x: hidden; }}
html, body, [class*="css"], .stMarkdown, button, label, input, select,
[data-testid="stDataFrame"], [data-baseweb="tab"] {{
  font-family: 'Source Sans 3', 'DM Sans', sans-serif !important;
}}
.stApp, [data-testid="stAppViewContainer"] {{
  background-color: {BG} !important;
}}
[data-testid="stHeader"] {{ display: none !important; height: 0 !important; min-height: 0 !important; }}
[data-testid="stToolbar"] {{ visibility: hidden !important; }}
[data-testid="stDecoration"] {{ display: none !important; height: 0 !important; }}
[data-testid="stMain"] {{ padding-top: 0 !important; margin-top: 0 !important; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 0 !important; }}
section.main {{ padding-top: 0 !important; }}
section.main > div {{ padding-top: 0 !important; }}
.stApp > section {{ padding-top: 0 !important; }}
[data-testid="block-container"] {{
  padding-top: 0 !important;
  padding-bottom: 3rem !important;
}}
[data-testid="stVerticalBlock"] {{ gap: 1rem !important; }}
[data-testid="stVerticalBlock"] > [data-testid="element-container"]:first-child {{
  margin-top: 0 !important; padding-top: 0 !important;
}}

/* ── Hero — full-bleed ── */
.hero-wrap {{
  min-height: 480px;
  background-image: {_hero_bg};
  background-size: cover;
  background-position: center 38%;
  border-radius: 0;
  overflow: hidden;
  position: relative;
  /* escape Streamlit container padding to reach viewport edges */
  width: 100vw;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  margin-top: calc(-1rem - 2px);
  margin-bottom: 0;
}}
.hero-overlay {{
  min-height: 480px;
  background: linear-gradient(125deg,
    rgba(13,43,31,0.95) 0%,
    rgba(13,43,31,0.82) 45%,
    rgba(13,43,31,0.42) 100%);
  display: flex;
  align-items: center;
  padding: 64px 68px 88px;
  position: relative;
}}
.hero-wave {{
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  line-height: 0;
  pointer-events: none;
}}
.hero-wave svg {{ display: block; width: 100%; }}
.hero-eyebrow {{
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.60);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
.hero-eyebrow::before {{
  content: '';
  width: 30px;
  height: 2px;
  background: {AMBER};
  display: inline-block;
  border-radius: 2px;
  opacity: 0.85;
}}
.hero-title {{
  font-family: 'Libre Baskerville', Georgia, serif !important;
  font-size: 4.4rem !important;
  font-weight: 700 !important;
  font-style: normal !important;
  color: {WHITE} !important;
  line-height: 1.05 !important;
  margin: 0 0 16px 0 !important;
  letter-spacing: -0.01em;
}}
.hero-sub {{
  font-size: 1.06rem;
  color: rgba(255,255,255,0.74);
  margin: 0 0 46px 0;
  font-weight: 300;
  max-width: 520px;
  line-height: 1.68;
}}
.hero-stats {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}}
.stat-badge {{
  background: rgba(255,248,235,0.09);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(212,160,23,0.28);
  border-radius: 18px;
  padding: 16px 22px;
  min-width: 108px;
  text-align: center;
  opacity: 0;
  animation: fadeUp 0.7s ease forwards;
  transition: background 0.28s, border-color 0.28s, transform 0.22s;
  cursor: default;
}}
.stat-badge:hover {{
  background: rgba(255,248,235,0.16);
  border-color: rgba(212,160,23,0.55);
  transform: translateY(-3px);
}}
.stat-badge:nth-child(1) {{ animation-delay: 0.10s; }}
.stat-badge:nth-child(2) {{ animation-delay: 0.22s; }}
.stat-badge:nth-child(3) {{ animation-delay: 0.34s; }}
.stat-badge:nth-child(4) {{ animation-delay: 0.46s; }}
.stat-num {{
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 1.9rem;
  font-weight: 700;
  font-style: italic;
  color: {AMBER};
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 5px;
}}
.stat-lbl {{
  font-size: 0.57rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.52);
  line-height: 1.45;
}}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to   {{ opacity: 1; transform: translateY(0);    }}
}}
@keyframes amberGlow {{
  0%,100% {{ box-shadow: 0 4px 14px rgba(45,106,79,0.30), 0 0 0 3px rgba(212,160,23,0); }}
  50%      {{ box-shadow: 0 4px 14px rgba(45,106,79,0.30), 0 0 0 5px rgba(212,160,23,0.30); }}
}}
@keyframes revealUp {{
  from {{ opacity: 0; transform: translateY(22px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* wave spacer after hero */
.hero-bottom-wave {{
  margin-bottom: 44px;
  line-height: 0;
  overflow: hidden;
}}
.hero-bottom-wave svg {{ display: block; width: 100%; }}

/* ── Farm intro ── */
.farm-intro {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 52px;
  align-items: center;
  margin-bottom: 52px;
  padding-bottom: 52px;
  border-bottom: 1px solid {G300};
}}
.farm-intro-text .overline {{
  font-size: 0.63rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: {MID};
  margin-bottom: 10px;
}}
.farm-intro-text h2 {{
  font-family: 'Libre Baskerville', Georgia, serif !important;
  font-size: 2.3rem;
  font-weight: 700;
  color: {ESPRESSO};
  margin: 0 0 22px 0;
  line-height: 1.18;
}}
.farm-intro-text p {{
  font-size: 0.94rem;
  color: {G700};
  line-height: 1.82;
  margin-bottom: 14px;
}}
.farm-intro-text strong {{ color: {ESPRESSO}; }}
.farm-intro-image img {{
  width: 100%;
  height: 320px;
  border-radius: 20px;
  box-shadow: 0 16px 48px rgba(44,26,14,0.18);
  object-fit: cover;
  object-position: center 30%;
  display: block;
}}

/* ── Overline ── */
.overline {{
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: {MID};
  margin-top: 25px;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.overline::before {{
  content: '●';
  font-size: 0.38rem;
  color: {MID};
}}

/* ── Section headings ── */
.sec-h2 {{
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 2.0rem;
  font-weight: 700;
  color: {ESPRESSO};
  margin: 4px 0 22px 0;
  line-height: 1.22;
}}
.sec-h3 {{
  font-size: 1.0rem;
  font-weight: 700;
  color: {G900};
  margin: 0 0 8px 0;
  line-height: 1.4;
}}
.sec-lead {{
  font-size: 0.94rem;
  color: {G700};
  line-height: 1.78;
  margin-bottom: 28px;
  max-width: 760px;
}}

/* ── Icon label ── */
.icon-label {{
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  color: {G500};
  margin-bottom: 6px;
}}
.icon-label svg {{ flex-shrink: 0; color: {MID}; }}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
  background: {CREAM};
  border-radius: 18px;
  padding: 20px 24px;
  border: 1px solid {G300};
  border-left: 4px solid {MID};
  box-shadow: 0 4px 18px rgba(44,26,14,0.08);
  transition: transform 0.22s ease, box-shadow 0.22s ease, outline 0.15s ease;
  cursor: pointer;
}}
[data-testid="stMetric"]:hover {{
  transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(44,26,14,0.14);
  outline: 2px solid rgba(212,160,23,0.42);
  outline-offset: 2px;
}}
[data-testid="stMetricValue"] {{
  font-family: 'Libre Baskerville', Georgia, serif !important;
  font-size: 2.4rem !important;
  font-weight: 700 !important;
  font-style: italic !important;
  color: {ESPRESSO} !important;
  letter-spacing: -0.03em;
}}
[data-testid="stMetricLabel"] {{
  font-size: 0.65rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.09em !important;
  text-transform: uppercase !important;
  color: {G500} !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 0.8rem !important; }}

/* ── Custom metric cards (HTML) ── */
.mc-grid {{
  display: grid;
  gap: 16px;
  margin-bottom: 32px;
}}
.mc-grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
.mc-grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
.mc-card {{
  background: {CREAM};
  border: 1px solid rgba(196,98,45,0.15);
  border-left: 5px solid {MID};
  border-radius: 20px;
  padding: 22px 20px;
  box-shadow: 0 4px 18px rgba(44,26,14,0.10);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, outline 0.15s ease;
}}
.mc-card:hover {{
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(44,26,14,0.14);
  outline: 2px solid rgba(212,160,23,0.38);
  outline-offset: 2px;
}}
.mc-label {{
  font-size: 0.60rem;
  font-weight: 700;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: {G500};
  margin-bottom: 10px;
}}
.mc-val {{
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 2.7rem;
  font-weight: 700;
  font-style: italic;
  color: {ESPRESSO};
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 6px;
}}
.mc-sub {{
  font-size: 0.74rem;
  color: {G500};
  line-height: 1.45;
}}

/* ── Tab bar — full-bleed nav rectangle ── */
[data-baseweb="tab-list"] {{
  background: {CREAM} !important;
  border: none !important;
  border-bottom: 1px solid {G300} !important;
  border-radius: 0 !important;
  gap: 6px !important;
  /* vertical padding */
  padding-top: 10px !important;
  padding-bottom: 10px !important;
  /* full-bleed: extend background to viewport edges */
  width: 100vw !important;
  position: relative !important;
  left: 50% !important;
  margin-left: -50vw !important;
  margin-right: -50vw !important;
  /* horizontal padding keeps tabs aligned with content */
  padding-left: 48px !important;
  padding-right: 48px !important;
  /* spacing above nav (separation from hero) and below nav to first section */
  margin-top: 4px !important;
  margin-bottom: 36px !important;
  box-shadow: 0 4px 20px rgba(44,26,14,0.06) !important;
}}
button[data-baseweb="tab"] {{
  font-family: 'Source Sans 3', 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  color: {G700} !important;
  background: transparent !important;
  border: none !important;
  border-bottom: none !important;
  margin-bottom: 0 !important;
  padding: 10px 22px !important;
  border-radius: 50px !important;
  letter-spacing: 0.01em;
  transition: color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease !important;
}}
button[data-baseweb="tab"]:hover {{
  color: {MID} !important;
  background: rgba(45,106,79,0.06) !important;
}}
button[data-baseweb="tab"]:active {{
  transform: scale(0.97) !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
  color: {CREAM} !important;
  background: {MID} !important;
  border-bottom: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 14px rgba(45,106,79,0.28), 0 0 0 3px rgba(212,160,23,0.25) !important;
}}
button[data-baseweb="tab"][aria-selected="true"]:hover {{
  box-shadow: 0 4px 18px rgba(45,106,79,0.40), 0 0 0 4px rgba(212,160,23,0.40) !important;
}}
[data-baseweb="tab-border"] {{ display: none !important; }}
[data-baseweb="tab-panel"] {{ padding-top: 0 !important; }}

/* ── Callouts ── */
.callout {{
  padding: 17px 22px;
  border-radius: 18px;
  margin: 10px 0 18px 0;
  line-height: 1.74;
  font-size: 0.875rem;
  color: {G900};
}}
.c-green {{
  background: linear-gradient(135deg, rgba(45,106,79,0.09) 0%, rgba(45,106,79,0.04) 100%);
  border: 1px solid rgba(45,106,79,0.20);
  border-left: 4px solid {MID};
}}
.c-amber {{
  background: linear-gradient(135deg, {AMBER_L} 0%, rgba(254,243,199,0.55) 100%);
  border: 1px solid rgba(212,160,23,0.24);
  border-left: 4px solid {AMBER};
}}
.c-red {{
  background: linear-gradient(135deg, {RED_L} 0%, rgba(252,218,218,0.55) 100%);
  border: 1px solid rgba(153,27,27,0.18);
  border-left: 4px solid {RED};
}}
.callout-icon {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 0.8rem;
}}
.callout-icon.green {{ color: {MID}; }}
.callout-icon.amber {{ color: {AMBER}; }}
.callout-icon.red   {{ color: {RED};  }}

/* ── Roadmap cards ── */
.roadmap-card {{
  padding: 26px 28px;
  border-radius: 20px;
  height: 100%;
  line-height: 1.65;
  background: {CREAM};
  border: 1px solid {G300};
  box-shadow: 0 4px 18px rgba(44,26,14,0.08);
  transition: transform 0.22s ease, box-shadow 0.22s ease, outline 0.15s ease;
}}
.roadmap-card:hover {{
  transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(44,26,14,0.13);
  outline: 2px solid rgba(212,160,23,0.38);
  outline-offset: 2px;
}}
.roadmap-card-year {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 6px;
}}
.roadmap-card-name {{
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 1.02rem;
  font-weight: 700;
  font-style: italic;
  color: {ESPRESSO};
  margin-bottom: 14px;
  line-height: 1.3;
}}
.roadmap-card ul {{
  font-size: 0.84rem;
  padding-left: 0;
  list-style: none;
  color: {G700};
  margin: 0;
}}
.roadmap-card li {{
  margin-bottom: 7px;
  padding-left: 16px;
  position: relative;
}}
.roadmap-card li::before {{
  content: '●';
  position: absolute;
  left: 0;
  font-size: 0.38rem;
  color: {TERRA};
  top: 5px;
}}

/* ── Highlight box ── */
.highlight-box {{
  background: {CREAM};
  border: 1px solid {G300};
  border-radius: 18px;
  padding: 22px 26px;
  box-shadow: 0 4px 18px rgba(44,26,14,0.07);
  margin-bottom: 18px;
}}
.highlight-box-accent {{
  background: linear-gradient(135deg, rgba(45,106,79,0.09), rgba(45,106,79,0.04));
  border: 1px solid rgba(45,106,79,0.20);
  border-radius: 18px;
  padding: 22px 26px;
  margin-bottom: 18px;
}}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {{
  border: 1px solid {G300} !important;
  border-radius: 16px !important;
  overflow: hidden !important;
  box-shadow: 0 4px 14px rgba(44,26,14,0.07) !important;
}}

/* ── Dividers ── */
hr {{ border-color: {G300} !important; margin: 2.5rem 0 !important; }}

/* ── Captions ── */
[data-testid="stCaptionContainer"] p {{
  color: {G500} !important;
  font-size: 0.78rem !important;
}}

/* ── Selectbox ── */
[data-baseweb="select"] {{
  font-family: 'Source Sans 3', 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
}}
[data-baseweb="select"] > div {{
  border-radius: 50px !important;
  border-color: {G300} !important;
  background: {CREAM} !important;
  transition: box-shadow 0.2s ease !important;
}}
[data-baseweb="select"] > div:focus-within {{
  box-shadow: 0 0 0 2.5px rgba(212,160,23,0.40) !important;
}}

/* ── Author ── */
.author-section {{
  margin-top: 72px;
  padding: 52px 0 0;
  border-top: 1px solid {G300};
}}
.author-card {{
  display: flex;
  align-items: flex-start;
  gap: 26px;
  max-width: 620px;
}}
.author-photo {{
  width: 76px;
  height: 76px;
  border-radius: 50%;
  object-fit: cover;
  object-position: center top;
  border: 3px solid {AMBER};
  box-shadow: 0 6px 20px rgba(44,26,14,0.18), 0 0 0 4px rgba(212,160,23,0.18);
  flex-shrink: 0;
}}
.author-name {{
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 700;
  font-style: italic;
  color: {ESPRESSO};
  margin-bottom: 3px;
}}
.author-role {{
  font-size: 0.74rem;
  font-weight: 700;
  color: {G500};
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 12px;
}}
.author-bio {{
  font-size: 0.88rem;
  color: {G700};
  line-height: 1.72;
  margin-bottom: 14px;
  font-style: italic;
}}
.author-link {{
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 0.79rem;
  font-weight: 600;
  color: {MID};
  text-decoration: none;
  border-bottom: 1px solid rgba(149,213,178,0.55);
  padding-bottom: 1px;
  transition: color 0.18s, border-color 0.18s, box-shadow 0.18s;
  border-radius: 2px;
}}
.author-link:hover {{
  color: {PRIMARY};
  border-color: {MID};
  box-shadow: 0 0 0 3px rgba(212,160,23,0.28);
}}

/* ── Footer ── */
.footer-txt {{
  text-align: center;
  color: {G500};
  font-size: 0.72rem;
  padding: 28px 0 16px;
  border-top: 1px solid {G300};
  margin-top: 36px;
  letter-spacing: 0.02em;
}}
</style>
""", unsafe_allow_html=True)


# ── helpers ────────────────────────────────────────────────────────────────────
def callout(text: str, kind: str = "green") -> None:
    cls = {"green": "c-green", "amber": "c-amber", "red": "c-red"}.get(kind, "c-green")
    st.markdown(f'<div class="callout {cls}">{text}</div>', unsafe_allow_html=True)


def sec_header(eyebrow: str, title: str, lead: str = "") -> None:
    lead_html = f'<p class="sec-lead">{lead}</p>' if lead else ""
    st.markdown(f"""
    <div class="overline">{eyebrow}</div>
    <div class="sec-h2">{title}</div>
    {lead_html}
    """, unsafe_allow_html=True)


def icon_label(icon: str, text: str) -> None:
    st.markdown(f'<div class="icon-label">{icon} {text}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, sub: str = "", accent: str = "") -> str:
    acc = accent or MID
    sub_html = f'<div class="mc-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="mc-card" style="border-left-color:{acc}">'
        f'<div class="mc-label">{label}</div>'
        f'<div class="mc-val">{value}</div>'
        f'{sub_html}'
        f'</div>'
    )


def metric_row(*cards: str, cols: int = 4) -> None:
    html = f'<div class="mc-grid mc-grid-{cols}">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _chart(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CREAM,
        font=dict(family="Source Sans 3, DM Sans", size=11, color=G700),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, linecolor=G300, tickfont_size=11)
    fig.update_yaxes(gridcolor=G300, linecolor=G300, tickfont_size=11)
    return fig


# ── data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load() -> dict:
    return dict(
        registry = pd.read_csv(DATA / "cow_registry.csv"),
        ihm      = pd.read_csv(DATA / "ihm_history.csv"),
        sup      = pd.read_csv(DATA / "supervised_dataset.csv"),
        rule     = pd.read_csv(DATA / "rule_predictions_documented.csv"),
        models   = pd.read_csv(TABLES / "model_comparison.csv"),
        shap     = pd.read_csv(TABLES / "shap_feature_importance.csv"),
        holdout  = pd.read_csv(TABLES / "temporal_holdout_comparison.csv"),
        layer3   = pd.read_csv(TABLES / "layer3_rule_vs_model_2025.csv"),
        drift    = pd.read_csv(TABLES / "concept_drift.csv"),
        model2   = pd.read_csv(TABLES / "model2_predictions_2027.csv"),
    )

D = load()

# ── label maps ─────────────────────────────────────────────────────────────────
TIER_LABELS = {
    "verdes_3":                     "★★★ Categoría 3 — padre IATF, madre conocida, IHM ≥ 40%",
    "verdes_2":                     "★★  Categoría 2 — padre conocido, genealogía completa",
    "verdes_1":                     "★   Categoría 1 — retenida, otros criterios",
    "verdes_fm_venta":              "Vendida — futura madre a otro campo",
    "verdes_pesada_sin_genealogia": "Vendida — animal pesado, sin genealogía",
    "verdes_invernada":             "Invernada — por debajo del umbral de peso",
    "verdes_venta":                 "Vendida — comercial / engorde",
    "verdes_unknown":               "Sin clasificar — sin datos de peso",
}

FEATURE_LABELS = {
    "anio_nacimiento":        "Año de nacimiento / cohorte",
    "pelaje_colorado":        "Pelaje colorado",
    "madre_mean_ihm_pre":     "IHM promedio de la madre",
    "madre_max_ihm_pre":      "Mejor IHM histórico de la madre",
    "pelaje_negro":           "Pelaje negro",
    "madre_latest_ihm_pre":   "IHM más reciente de la madre",
    "madre_n_ihm_pre":        "Años de historial de la madre",
    "tipo_padre_iatf":        "Padre tipo IATF",
    "tipo_padre_repaso":      "Padre tipo repaso",
    "tipo_padre_desconocido": "Padre desconocido",
}

MODEL_LABELS = {
    "random_forest":  "Random Forest",
    "decision_tree":  "Árbol de Decisión",
    "gradient_boost": "Gradient Boost",
    "linear":         "Regresión Lineal",
    "ridge":          "Ridge",
    "baseline_mean":  "Línea de base",
}


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-overlay">
    <div>
      <div class="hero-eyebrow">San Eduardo &nbsp;·&nbsp; Bragado, Buenos Aires</div>
      <div class="hero-title">Selección de<br>Vaquillonas</div>
      <p class="hero-sub">
        Un análisis exploratorio para entender cómo decide hoy el campo:<br>
        dónde están los patrones, dónde falta información, y qué necesitaría
        la IA para ser realmente útil.
      </p>
      <div class="hero-stats">
        <div class="stat-badge">
          <div class="stat-num">{len(D['registry']):,}</div>
          <div class="stat-lbl">vacas<br>registradas</div>
        </div>
        <div class="stat-badge">
          <div class="stat-num">{len(D['ihm']):,}</div>
          <div class="stat-lbl">registros<br>de IHM</div>
        </div>
        <div class="stat-badge">
          <div class="stat-num">5</div>
          <div class="stat-lbl">años de<br>datos</div>
        </div>
        <div class="stat-badge">
          <div class="stat-num">49%</div>
          <div class="stat-lbl">consistencia<br>de la regla</div>
        </div>
      </div>
    </div>
  </div>
  <div class="hero-wave">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 60" preserveAspectRatio="none" style="display:block;width:100%;height:60px;">
      <path fill="{BG}" d="M0,30 C240,60 480,0 720,30 C960,60 1200,0 1440,30 L1440,60 L0,60 Z"/>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5, t6 = st.tabs([
    "≡  Tu Rodeo",
    "✓  Auditoría de Reglas",
    "⊙  Modelo 1",
    "⊟  Qué Está Faltando",
    "◈  La Visión",
    "◎  Modelo 2 — 2027",
])


# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — TU RODEO
# ──────────────────────────────────────────────────────────────────────────────
with t1:
    _farm_img_tag = (
        f'<img src="{FARM_B64}" alt="Herd at San Eduardo">'
        if FARM_B64 else
        f'<div style="width:100%;height:320px;border-radius:14px;background:{G300};"></div>'
    )
    st.markdown(f"""
<div class="farm-intro">
  <div class="farm-intro-text">
    <div class="overline">La Historia</div>
    <h2>Sobre San Eduardo</h2>
    <p>
      Estancia San Eduardo es un campo ganadero familiar ubicado en Bragado, provincia
      de Buenos Aires — corazón de la llanura pampeana argentina. Con décadas de
      historia, cría ganado Angus-cruza en uno de los ecosistemas bovinos más
      productivos del mundo.
    </p>
    <p>
      Cada año, el equipo toma una decisión que define la genética del campo por
      los próximos 5 a 10 años: qué vaquillonas se convierten en las próximas madres
      del rodeo.
    </p>
    <p>
      Este análisis nació de una pregunta simple: <strong>¿con cuánta consistencia
      estamos aplicando nuestras propias reglas de selección?</strong> La respuesta
      fue inesperada — y ese hallazgo es la base de este proyecto.
    </p>
  </div>
  <div class="farm-intro-image">
    {_farm_img_tag}
  </div>
</div>
""", unsafe_allow_html=True)
    st.divider()

    sec_header(
        "Análisis de datos",
        "Qué analizó este proyecto",
        "Procesamos cada registro del campo — planillas Excel, registros de inseminación "
        "y alarmas de WhatsApp — en un único dataset con cada vaca que perteneció al rodeo.",
    )

    metric_row(
        metric_card("Vacas identificadas",           f"{len(D['registry']):,}", "en el registro del campo",         MID),
        metric_card("Registros de IHM",              f"{len(D['ihm']):,}",      "mediciones de productividad",       TERRA),
        metric_card("Años de datos",                 "5",                        "2022–2026",                         AMBER),
        metric_card("En el modelo predictivo",       f"{len(D['sup']):,}",      "vacas con datos completos",         TAUPE),
        cols=4,
    )
    st.divider()

    col_a, col_b = st.columns([3, 2])
    with col_a:
        icon_label(ICO_CHART, "Productividad del rodeo en el tiempo")
        st.caption(
            "IHM (Índice de Habilidad Materna) = qué tan bien cría una vaca a su ternero. "
            "Escala 0–1; más alto es mejor. La banda sombreada es ±1 error estándar."
        )
        ihm_yr = (
            D["ihm"].groupby("year")["ihm"]
            .agg(mean="mean", count="count", std="std")
            .reset_index()
        )
        ihm_yr["se"]    = ihm_yr["std"] / np.sqrt(ihm_yr["count"])
        ihm_yr["upper"] = (ihm_yr["mean"] + ihm_yr["se"]).clip(upper=1.0)
        ihm_yr["lower"] = (ihm_yr["mean"] - ihm_yr["se"]).clip(lower=0.0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(ihm_yr["year"]) + list(ihm_yr["year"][::-1]),
            y=list(ihm_yr["upper"]) + list(ihm_yr["lower"][::-1]),
            fill="toself", fillcolor="rgba(196,98,45,0.12)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=ihm_yr["year"], y=ihm_yr["mean"],
            mode="lines+markers",
            line=dict(color=TERRA, width=2.5),
            marker=dict(size=9, color=CREAM, symbol="circle", line=dict(color=TERRA, width=2.2)),
            name="IHM promedio",
            hovertemplate="<b>%{x}</b><br>IHM promedio: %{y:.3f}<extra></extra>",
        ))
        _chart(fig, 300)
        fig.update_layout(
            yaxis=dict(title="IHM promedio", range=[0.35, 0.55]),
            xaxis=dict(title="Año", dtick=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        icon_label(ICO_CHART, "Registros por año")
        st.caption("Vacas con IHM registrado cada año")
        ihm_yr_total = (
            D["ihm"].groupby("year").size().reset_index(name="total")
        )
        ihm_yr_merged = ihm_yr.merge(ihm_yr_total, on="year", how="left")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=ihm_yr_merged["year"], y=ihm_yr_merged["total"],
            name="Total en BD",
            marker_color="rgba(139,115,85,0.25)",
            marker_line_width=0,
            marker_cornerradius=8,
            text=ihm_yr_merged["total"],
            textposition="outside",
            textfont=dict(family="Libre Baskerville, Georgia, serif", size=11,
                          color=TAUPE, style="italic"),
            hovertemplate="<b>%{x}</b><br>Total en BD: %{y}<extra></extra>",
        ))
        fig2.add_trace(go.Bar(
            x=ihm_yr_merged["year"], y=ihm_yr_merged["count"],
            name="Con IHM registrado",
            marker_color=TERRA,
            marker_line_width=0,
            marker_cornerradius=8,
            text=ihm_yr_merged["count"],
            textposition="inside",
            textfont=dict(family="Libre Baskerville, Georgia, serif", size=13,
                          color=CREAM, style="italic"),
            hovertemplate="<b>%{x}</b><br>Con IHM: %{y}<extra></extra>",
        ))
        fig2.update_layout(barmode="overlay")
        _chart(fig2, 300)
        fig2.update_layout(
            xaxis=dict(title="Año", dtick=1),
            yaxis=dict(title="Vacas registradas"),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(size=10),
            ),
        )
        st.plotly_chart(fig2, use_container_width=True)

    callout(
        "<b>¿Qué es el IHM?</b> Es el cociente entre el peso del ternero a 205 días (ajustado) "
        "y el peso vivo de la madre: IHM = peso ternero 205d / peso madre. "
        "Un puntaje de 0,42 significa que el ternero pesó el 42% de lo que pesa su madre al destete. "
        "El promedio del rodeo se ubica entre 0,40 y 0,48 en todos los años — típico "
        "de una operación Angus-cruza bien manejada en la Pampa.",
        "green",
    )

    st.divider()
    icon_label(ICO_CHART, "Vacas disponibles para el modelo predictivo")
    st.markdown(
        '<p class="sec-lead" style="margin-bottom:16px;">'
        "El modelo necesita vacas con <b>datos al nacimiento</b> y <b>resultados adultos de IHM</b>. "
        "Una vaquillona nacida en 2020 recién tiene resultados adultos desde 2024 (edad 4+), "
        "por lo que necesitamos cohortes lo suficientemente antiguas para haberse desarrollado antes de 2026."
        "</p>",
        unsafe_allow_html=True,
    )
    cohort_counts = (
        D["sup"]["anio_nacimiento"].dropna().astype(int)
        .value_counts().sort_index().reset_index()
    )
    cohort_counts.columns = ["Año de nacimiento", "Vacas con resultados"]

    fig3 = px.bar(cohort_counts, x="Año de nacimiento", y="Vacas con resultados",
                  text="Vacas con resultados", color_discrete_sequence=[AMBER])
    fig3.update_traces(
        marker_line_width=0,
        marker_cornerradius=8,
        textposition="outside",
        textfont=dict(family="Libre Baskerville, Georgia, serif", size=13,
                      color=ESPRESSO, style="italic"),
    )
    _chart(fig3, 260)
    fig3.update_layout(
        xaxis=dict(title="Año de nacimiento", dtick=1),
        yaxis=dict(title=""),
    )
    st.plotly_chart(fig3, use_container_width=True)

    callout(
        "Solo las vacas nacidas entre 2018 y 2022 tienen suficientes datos de IHM adulto "
        "para entrenar el modelo. Las cohortes más recientes (2023–2025) podrán utilizarse "
        "a medida que esos animales maduren en los próximos 2–4 años.",
        "amber",
    )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — AUDITORÍA DE REGLAS
# ──────────────────────────────────────────────────────────────────────────────
with t2:
    sec_header(
        "El hallazgo principal",
        "¿Con qué consistencia aplica el campo su propia regla?",
        "Este es el resultado más concreto y directo de todo el análisis — sin modelos, sin estimaciones. "
        "El campo tiene una regla documentada: retener vaquillonas por encima de un peso mínimo, "
        "con madre conocida de IHM ≥ 40%, preñadas por IATF. "
        "Aplicamos esa regla a la última cohorte y la comparamos con lo que se decidió realmente.",
    )

    rule_ev = D["rule"][D["rule"]["recorded_label"].notna()].copy()
    n_eval  = len(rule_ev)
    n_match = (rule_ev["predicted"] == rule_ev["recorded_label"]).sum()
    overall = n_match / n_eval

    ra = rule_ev[~rule_ev["recorded_label"].isin(
        ["verdes_venta", "verdes_invernada", "verdes_unknown"]
    )]
    n_ra       = len(ra)
    n_ra_match = (ra["predicted"] == ra["recorded_label"]).sum()
    ra_rate    = n_ra_match / n_ra

    metric_row(
        metric_card("Vaquillonas evaluadas",       f"{n_eval}",           "en la cohorte 2025",                         MID),
        metric_card("Consistencia general",        f"{overall:.0%}",      "regla documentada vs. decisiones reales",    TERRA),
        metric_card("Predicción clara",            f"{ra_rate:.0%}",      f"{n_ra} animales — excluye invernada/venta", AMBER),
        cols=3,
    )

    callout(
        f"<b>La regla documentada coincide con el {overall:.0%} de las decisiones.</b> "
        f"Para los {n_ra} animales donde la regla hace una predicción clara, la consistencia "
        f"sube al {ra_rate:.0%}. El {1 - ra_rate:.0%} restante son <b>excepciones del productor</b> — "
        "decisiones basadas en evaluación física, comportamiento materno y experiencia que la "
        "regla escrita no captura.",
        "amber",
    )

    st.divider()

    col_a, col_b = st.columns([3, 2])
    with col_a:
        icon_label(ICO_CHECK, "Acuerdo por categoría")
        st.caption("Para cada decisión real del campo, ¿con qué frecuencia coincide la regla documentada?")

        tier_order = [
            "verdes_3", "verdes_2", "verdes_1",
            "verdes_fm_venta", "verdes_pesada_sin_genealogia",
            "verdes_invernada", "verdes_venta",
        ]
        tier_stats = []
        for tier in tier_order:
            sub = rule_ev[rule_ev["recorded_label"] == tier]
            if len(sub) == 0:
                continue
            n_ok = (sub["predicted"] == tier).sum()
            tier_stats.append({
                "tier":     tier,
                "label":    TIER_LABELS.get(tier, tier),
                "agree":    int(n_ok),
                "disagree": len(sub) - int(n_ok),
            })
        ts = pd.DataFrame(tier_stats)

        _tier_colors = {
            "verdes_3":                     TERRA,
            "verdes_2":                     AMBER,
            "verdes_1":                     SAGE,
            "verdes_fm_venta":              TAUPE,
            "verdes_pesada_sin_genealogia": G500,
            "verdes_invernada":             G300,
            "verdes_venta":                 G300,
        }
        _short_labels = {
            "verdes_3":                     "Cat. 3",
            "verdes_2":                     "Cat. 2",
            "verdes_1":                     "Cat. 1",
            "verdes_fm_venta":              "Vta. Madre",
            "verdes_pesada_sin_genealogia": "Vta. S/G",
            "verdes_invernada":             "Invernada",
            "verdes_venta":                 "Vta. Com.",
        }
        ts["pct"]   = ts["agree"] / (ts["agree"] + ts["disagree"])
        ts["short"] = ts["tier"].map(_short_labels)
        ts["color"] = ts["tier"].map(_tier_colors)
        ts["lbl"]   = ts["pct"].map(lambda x: f"{x:.0%}")

        fig = go.Figure()
        # Background track
        fig.add_trace(go.Bar(
            x=[1.0] * len(ts), y=ts["short"][::-1],
            orientation="h",
            marker_color="rgba(196,98,45,0.08)",
            marker_cornerradius=12,
            showlegend=False, hoverinfo="skip",
        ))
        # Per-tier foreground bars
        for _, row in ts[::-1].iterrows():
            fig.add_trace(go.Bar(
                x=[row["pct"]], y=[row["short"]],
                orientation="h",
                marker_color=row["color"],
                marker_cornerradius=12,
                text=[row["lbl"]],
                textposition="outside",
                textfont=dict(family="Libre Baskerville, Georgia, serif", size=14,
                              color=ESPRESSO, style="italic"),
                showlegend=False,
                hovertemplate=f"<b>{row['short']}</b>: {row['lbl']}<extra></extra>",
            ))
        _chart(fig, 320)
        fig.update_layout(
            barmode="overlay",
            xaxis=dict(
                range=[0, 1.35],
                tickformat=".0%",
                title="Concordancia con la decisión real",
                showgrid=False,
            ),
            yaxis=dict(showgrid=False),
            annotations=[dict(
                text="● Concordancia regla documentada vs. etiquetas asignadas",
                xref="paper", yref="paper", x=0, y=-0.18,
                xanchor="left", showarrow=False,
                font=dict(size=10, color=G500),
            )],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="sec-h3">Conclusiones clave</div>', unsafe_allow_html=True)
        callout(
            f'<div class="callout-icon green">{ICO_CHECK} <b>Categoría 3: acuerdo perfecto</b></div>'
            "La regla identifica correctamente cada animal verdes_3. "
            "Los criterios — padre IATF, madre conocida, IHM ≥ 40% — se aplican "
            "exactamente como están documentados.",
            "green",
        )
        callout(
            f'<div class="callout-icon amber">{ICO_WARN} <b>Las categorías inferiores divergen</b></div>'
            "Para animales de nivel medio, el campo hace excepciones que la regla escrita "
            "no captura. Son decisiones basadas en evaluación física y experiencia.",
            "amber",
        )
        callout(
            f'<div class="callout-icon amber">{ICO_WARN} <b>~28% de decisiones fuera de la regla</b></div>'
            "Es la 'brecha de conocimiento tácito': ojos experimentados toman decisiones "
            "que ninguna planilla captura — exactamente lo que el modelo necesita aprender.",
            "amber",
        )

    callout(
        f'<div class="callout-icon green">{ICO_CHECK} <b>El umbral de peso se mantiene en 190 kg</b></div>'
        "El criterio documentado de 190 kg al destete es el vigente. "
        "Lo que sí evolucionó es el IHM de entrada: los archivos más nuevos usan peso "
        "ajustado a 205 días en lugar del peso bruto al destete.",
        "green",
    )

    if (FIGS / "03_rule_confusion.png").exists():
        st.divider()
        icon_label(ICO_CHECK, "Matriz de confusión completa")
        st.caption("Categoría predicha por la regla (columnas) vs. decisión real del campo (filas)")
        st.image(str(FIGS / "03_rule_confusion.png"))


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — LO QUE ENCONTRÓ EL MODELO
# ──────────────────────────────────────────────────────────────────────────────
with t3:
    sec_header(
        "Exploración del modelo",
        "¿Qué puede ver la IA con los datos actuales?",
        "Entrenamos un modelo con los datos existentes del campo no para predecir, sino para "
        "explorar: ¿qué señales contiene este dataset? ¿Dónde está la señal y dónde están "
        "los límites? Los resultados son honestos sobre lo que el modelo puede y no puede hacer hoy.",
    )

    callout(
        f'<div class="callout-icon amber">{ICO_WARN} <b>Esto es exploración de datos, no un sistema de predicción</b></div>'
        "El modelo se entrenó con datos de <b>un solo campo</b> (337 vacas) y tiene una limitación "
        "estructural importante: los datos de IHM del campo solo existen desde 2022, pero las "
        "cohortes de entrenamiento necesitarían historial de IHM de las madres desde antes de ese año. "
        "El resultado es que el <b>conjunto de entrenamiento no tiene prácticamente ningún dato de IHM</b> "
        "disponible para las cohortes anteriores a 2021. El modelo existe, funciona, "
        "pero sus limitaciones actuales son estructurales — y están documentadas aquí.",
        "amber",
    )

    st.divider()

    col_a, col_b = st.columns([2, 3])
    with col_a:
        icon_label(ICO_BRAIN, "¿Qué predice buenas hijas?")
        st.caption(
            "Importancia SHAP — cuánto influye cada variable en el puntaje del modelo "
            "(barra más larga = más influyente)"
        )
        shap_plot = D["shap"].copy()
        shap_plot["label"] = shap_plot["feature"].map(FEATURE_LABELS).fillna(shap_plot["feature"])
        shap_plot = shap_plot.sort_values("mean_abs_shap")

        fig = px.bar(shap_plot, x="mean_abs_shap", y="label",
                     orientation="h", color_discrete_sequence=[TERRA],
                     hover_data={"mean_abs_shap": ":.4f"})
        fig.update_traces(
            marker_line_width=0,
            marker_cornerradius=8,
            textfont=dict(family="Libre Baskerville, Georgia, serif", size=12,
                          color=ESPRESSO, style="italic"),
        )
        _chart(fig, 360)
        fig.update_layout(
            xaxis=dict(title="Impacto promedio en la predicción"),
            yaxis=dict(title="", showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="sec-h3">Qué significa en términos simples</div>', unsafe_allow_html=True)
        callout(
            f'<div class="callout-icon green">{ICO_STAR} <b>Predictor #1: Historial de productividad de la madre</b></div>'
            "El IHM promedio de la propia madre de la vaquillona — en todos los años con datos — "
            "es la señal más fuerte. <b>Las buenas madres producen buenas hijas.</b> "
            "Este es el hallazgo más accionable: llevar un registro cuidadoso del IHM de las "
            "madres genera retorno directo.",
            "green",
        )
        callout(
            f'<div class="callout-icon green">{ICO_STAR} <b>Predictor #2: Año de nacimiento / cohorte</b></div>'
            "El año en que nació una vaquillona importa — las variaciones interanuales de "
            "clima, pasturas y manejo afectan los puntajes IHM de todo el rodeo. "
            "El modelo lo captura como un factor de ruido, no como herramienta de decisión.",
            "green",
        )
        callout(
            f'<div class="callout-icon green">{ICO_STAR} <b>Predictor #3: Color de pelaje</b></div>'
            "El pelaje aparece como predictor, probablemente porque actúa como proxy de "
            "línea genética — los rodeos colorado y negro se manejan separados y pueden "
            "tener distintas bases genéticas. No es una causa directa.",
            "green",
        )
        callout(
            f'<div class="callout-icon amber">{ICO_STAR} <b>Predictor #4: Tipo de padre IATF</b></div>'
            "Las vaquillonas con padre IATF tienden a puntuar más alto. Los toros usados "
            "en programas de inseminación son seleccionados genéticamente, lo que se refleja "
            "en las hijas. Menos influyente de lo esperado — la calidad individual del toro "
            "varía más que el tipo de servicio solo.",
            "amber",
        )

    st.divider()
    icon_label(ICO_BRAIN, "¿Qué tan preciso es el modelo?")
    st.caption(
        "Dos formas de medir: validación cruzada (mezcla cohortes — resultado optimista) "
        "vs. holdout temporal (entrenado ≤2020, probado en 2021–2022 — resultado honesto)"
    )

    rf_cv = D["models"][D["models"]["model"] == "random_forest"].iloc[0]
    gb_ho = D["holdout"][D["holdout"]["model"] == "gradient_boost"].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            "Validación cruzada (optimista)",
            f"{rf_cv['precision_at_0.3']:.0%}",
            delta=f"+{rf_cv['precision_at_0.3'] - 0.30:.0%} vs. azar",
            help="Random Forest mezclando todas las cohortes. Parece mejor de lo que es: "
                 "las cohortes recientes (con datos de madre) informan el entrenamiento de "
                 "las cohortes anteriores, lo que infla el resultado.",
        )
    with c2:
        st.metric(
            "Holdout temporal (número honesto)",
            f"{gb_ho['precision_at_0.3']:.0%}",
            delta=f"{gb_ho['spearman']:+.2f} Spearman · R² negativo",
            help="Gradient Boost entrenado en ≤2020, evaluado en 2021–2022. "
                 "El set de entrenamiento no tiene datos de IHM de madres — "
                 "refleja las condiciones reales de uso. R² negativo significa que "
                 "el modelo puro supera al promedio solo en ranking, no en magnitud.",
        )
    with c3:
        st.metric(
            "Selección al azar",
            "30%",
            help="Si eligieras al azar, el 30% de tus elecciones estarían en el top 30% real por casualidad",
        )

    ho_lift = gb_ho["precision_at_0.3"] / 0.30
    callout(
        f'<div class="callout-icon amber">{ICO_WARN} <b>Señal real, pero débil: {ho_lift:.1f}× sobre el azar en la prueba honesta</b></div>'
        "El holdout temporal es el número que importa: el modelo elige el 35% correcto cuando selecciona el top 30% — "
        "frente al 30% de una selección al azar. Eso es una mejora de ~5 puntos porcentuales, no un sistema predictivo. "
        "El resultado de validación cruzada (44%) aparece mejor porque mezcla cohortes con y sin datos de madre en el mismo entrenamiento — "
        "una condición que no existe en la práctica real. "
        "<b>La señal confirma que hay algo que aprender de los datos; lo que falta es el dato correcto para aprenderlo.</b>",
        "amber",
    )

    col_a, col_b = st.columns([3, 2])
    with col_a:
        icon_label(ICO_BRAIN, "Comparación de modelos — precisión en el top 30%")
        st.caption(
            "Mayor valor = mayor superposición entre las elecciones del top 30% del modelo "
            "y las productoras reales del top 30%"
        )
        plot_m = D["models"][~D["models"]["model"].str.startswith("heuristic")].copy()
        plot_m["Modelo"] = plot_m["model"].map(MODEL_LABELS).fillna(plot_m["model"])
        plot_m = plot_m.sort_values("precision_at_0.3", ascending=False)
        _model_palette = {
            "random_forest":  TERRA,
            "gradient_boost": AMBER,
            "ridge":          SAGE,
            "linear":         TAUPE,
            "decision_tree":  G500,
            "baseline_mean":  G300,
        }
        plot_m["color"] = plot_m["model"].map(_model_palette).fillna(G300)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=plot_m["Modelo"], y=plot_m["precision_at_0.3"],
            marker_color=plot_m["color"].tolist(),
            marker_line_width=0,
            marker_cornerradius=8,
            text=plot_m["precision_at_0.3"].apply(lambda v: f"{v:.0%}"),
            textposition="outside",
            textfont=dict(family="Libre Baskerville, Georgia, serif", size=13,
                          color=ESPRESSO, style="italic"),
            hovertemplate="%{x}<br>Precisión @30%%: %{y:.1%}<extra></extra>",
        ))
        fig.add_hline(y=0.30, line_dash="dot", line_color=G500, line_width=1.5,
                      annotation_text="  Azar (30%)",
                      annotation_font=dict(size=10, color=G500),
                      annotation_position="right")
        _chart(fig, 320)
        fig.update_layout(
            yaxis=dict(title="Precisión @ top 30%", range=[0, 0.62]),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        icon_label(ICO_BRAIN, "SHAP Beeswarm")
        st.caption("Cada punto es una vaca — muestra dirección e intensidad del efecto de cada variable")
        if (FIGS / "10_shap_beeswarm.png").exists():
            st.image(str(FIGS / "10_shap_beeswarm.png"))

    if (FIGS / "14_learning_curves.png").exists():
        st.divider()
        icon_label(ICO_BRAIN, "Curvas de aprendizaje — ¿más datos mejoran el modelo?")
        st.caption(
            "Las curvas de aprendizaje muestran cómo cambia el rendimiento del modelo al agregar "
            "más ejemplos de entrenamiento. Una brecha entre entrenamiento y validación indica que "
            "el modelo se beneficiaría de más datos — exactamente lo que aportan campos adicionales."
        )
        st.image(str(FIGS / "14_learning_curves.png"))

    st.divider()
    icon_label(ICO_BRAIN, "Cohorte 2025 — Regla vs. Modelo, animal por animal")
    st.caption(
        "Para cada vaquillona de la cohorte 2025: ¿qué predijo la regla documentada? "
        "¿Qué puntaje dio el modelo? ¿Cuál fue la decisión real del campo?"
    )

    l3 = D["layer3"].copy()
    l3["Decisión del campo"]     = l3["recorded_label"].map(TIER_LABELS).fillna(l3["recorded_label"])
    l3["Predicción de la regla"] = l3["rule_predicted_label"].map(TIER_LABELS).fillna(l3["rule_predicted_label"])
    l3["Puntaje del modelo"]     = l3["model_predicted_ihm"].round(3)
    l3["Top 30% modelo"]         = l3["model_tier_30"].apply(
        lambda x: "Sí" if x == "model_top30" else "No"
    )
    l3["Regla coincide"]         = (l3["recorded_label"] == l3["rule_predicted_label"]).apply(
        lambda x: "Sí" if x else "No"
    )
    l3["IHM madre"] = l3["ihm_madre_rule_input"].round(3)

    tiers_filter = ["Todas"] + sorted(
        [t for t in l3["recorded_label"].dropna().unique() if t in TIER_LABELS]
    )
    selected = st.selectbox(
        "Filtrar por decisión real del campo:",
        options=tiers_filter,
        format_func=lambda x: "Todas las categorías" if x == "Todas" else TIER_LABELS.get(x, x),
    )

    view = l3 if selected == "Todas" else l3[l3["recorded_label"] == selected]

    _TIER_SHORT = {
        "verdes_3":                     "★★★ Cat. 3",
        "verdes_2":                     "★★ Cat. 2",
        "verdes_1":                     "★ Cat. 1",
        "verdes_fm_venta":              "Vta. Madre",
        "verdes_pesada_sin_genealogia": "Vta. Peso",
        "verdes_invernada":             "Invernada",
        "verdes_venta":                 "Venta",
        "verdes_unknown":               "Sin datos",
    }

    _va = view[["idv", "recorded_label", "rule_predicted_label",
                "Regla coincide", "model_predicted_ihm",
                "Top 30% modelo", "IHM madre"]].copy()
    _va["Campo"] = _va["recorded_label"].map(_TIER_SHORT).fillna(_va["recorded_label"])
    _va["Regla"] = _va["rule_predicted_label"].map(_TIER_SHORT).fillna(_va["rule_predicted_label"])
    _va["✓/✗"]  = _va["Regla coincide"].map({"Sí": "✓", "No": "✗"})
    _va = _va.rename(columns={"idv": "IDV", "model_predicted_ihm": "Score", "Top 30% modelo": "Top 30%"})
    st.dataframe(
        _va[["IDV", "Campo", "Regla", "✓/✗", "Score", "Top 30%", "IHM madre"]],
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score modelo",
                min_value=0.0,
                max_value=0.7,
                format="%.3f",
            ),
        },
        use_container_width=True, height=420, hide_index=True,
    )

    st.caption(f"Mostrando {len(view):,} de {len(l3):,} animales")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — DATOS FALTANTES
# ──────────────────────────────────────────────────────────────────────────────
with t4:
    sec_header(
        "Diagnóstico de datos",
        "Qué datos tiene el campo — y qué hace falta documentar",
        "El campo tiene cinco años de datos valiosos. Este diagnóstico muestra exactamente "
        "qué está registrado, qué tiene brechas estructurales, y qué nuevas variables "
        "mejorarían el análisis si se empiezan a documentar hoy.",
    )

    icon_label(ICO_DB, "Calidad actual de los datos")
    dq = pd.DataFrame([
        {
            "Variable":         "Identificadores únicos (IDV)",
            "Estado":           "Completo",
            "Cobertura":        "2.728 vacas",
            "Valor predictivo": "—",
            "Acción requerida": "Ninguna",
        },
        {
            "Variable":         "Registros de IHM (variable objetivo)",
            "Estado":           "Completo",
            "Cobertura":        "5.265 registros · 2022–2026",
            "Valor predictivo": "Crítico — es lo que predicemos",
            "Acción requerida": "Extender hasta 2018 para más datos de entrenamiento",
        },
        {
            "Variable":         "Historial de IHM de la madre",
            "Estado":           "Parcial",
            "Cobertura":        "71% ausente. 0% disponible para cohortes 2018–2020 (IHM registrado solo desde 2022)",
            "Valor predictivo": "Alta — predictor más fuerte cuando está disponible",
            "Acción requerida": "Registrar IHM por vaca cada año, sin excepciones — el beneficio acumula año a año",
        },
        {
            "Variable":         "Tipo de padre (IATF / repaso)",
            "Estado":           "Bueno",
            "Cobertura":        "Disponible para la mayoría de las vacas",
            "Valor predictivo": "Media",
            "Acción requerida": "Ninguna",
        },
        {
            "Variable":         "Peso real al nacimiento (por ternero)",
            "Estado":           "Faltante",
            "Cobertura":        "Todas las vacas muestran 30,0 kg como marcador",
            "Valor predictivo": "Alta — predice productividad adulta",
            "Acción requerida": "Registrar el peso real de cada ternero al nacer",
        },
        {
            "Variable":         "Dificultad al parto",
            "Estado":           "Faltante",
            "Cobertura":        "No registrado en ningún lugar",
            "Valor predictivo": "Media — la facilidad de parto es heredable",
            "Acción requerida": "Agregar un campo al registro de partos",
        },
        {
            "Variable":         "Edad de la madre al parto",
            "Estado":           "Parcialmente derivable",
            "Cobertura":        "~70% del registro tiene años de nacimiento completos",
            "Valor predictivo": "Media — las vaquillonas primíparas producen diferente",
            "Acción requerida": "Completar años de nacimiento faltantes en el registro",
        },
        {
            "Variable":         "Eventos de salud de la madre",
            "Estado":           "Solo informal",
            "Cobertura":        "Registro de alarmas WhatsApp — 79 eventos, sin estructura",
            "Valor predictivo": "Media — el historial de salud de la madre es predictivo",
            "Acción requerida": "Registro estructurado: fecha · tipo de evento · IDV",
        },
        {
            "Variable":         "Fecha y motivo de baja del rodeo",
            "Estado":           "Faltante",
            "Cobertura":        "Sin registros de baja en ningún lugar",
            "Valor predictivo": "Alta — longevidad es señal genética fuerte",
            "Acción requerida": "Registrar fecha + motivo de cada vaca que sale",
        },
        {
            "Variable":         "EPDs del padre (asociaciones raciales)",
            "Estado":           "No vinculado",
            "Cobertura":        "Nombres de padres disponibles pero no cruzados",
            "Valor predictivo": "Muy alta — los EPDs son el estándar genético",
            "Acción requerida": "Vincular a Angus Argentina o Hereford Argentina",
        },
    ])
    st.dataframe(dq, use_container_width=True, hide_index=True, height=420)

    callout(
        f'<div class="callout-icon amber">{ICO_WARN} <b>Por qué el IHM de la madre aparece como "Parcial" — y no es un error</b></div>'
        "Los datos de IHM del campo cubren 2022–2026. Las vaquillonas usadas en el modelo nacieron entre 2018 y 2022, "
        "y su 'año de corte' — el momento en que se seleccionan — ocurre dos años después del nacimiento. "
        "Eso significa que las cohortes 2018, 2019 y 2020 necesitarían historial de IHM de sus madres de <em>antes del 2022</em>, "
        "que simplemente no existe en los registros. <b>Para esas cohortes, el predictor más importante del modelo no está disponible.</b> "
        "Solo las vaquillonas nacidas en 2021–2022 tienen datos de madre usables. "
        "Este es el argumento más concreto para que el campo empiece a registrar IHM sistemáticamente desde ya.",
        "amber",
    )

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        callout(
            f'<div class="callout-icon red">{ICO_X} <b>Brecha #1: Pesos reales al nacimiento</b></div><br>'
            "Cada vaca en el modelo predictivo tiene un peso al nacimiento de exactamente "
            "<b>30,0 kg</b> — un valor de relleno del registro antiguo, no una medición real. "
            "Los pesos reales van de ~25 kg a ~45 kg y contienen señal genética significativa. "
            "Esta variable está completamente inutilizada.<br><br>"
            "<b>Solución:</b> Pedir a cada campo que incluya los pesos reales al nacimiento. "
            "La mayoría de los campos ya pesa los terneros al nacer — el dato existe, "
            "simplemente no fue compartido.",
            "red",
        )
    with col_b:
        callout(
            f'<div class="callout-icon red">{ICO_X} <b>Brecha #2: No sabemos cuándo salieron las vacas</b></div><br>'
            "Una madre que sigue pariendo productivamente a los 12 años es una señal "
            "genética muy distinta a una descartada a los 6 por baja producción. "
            "<b>La longevidad de las madres es uno de los predictores más fuertes</b> "
            "en genética bovina — y no tenemos ninguno de estos datos.<br><br>"
            "<b>Solución:</b> Una columna extra en el registro: fecha de baja + motivo "
            "(venta / descarte / muerte). Registrar para cada animal de ahora en adelante.",
            "red",
        )

    st.divider()
    icon_label(ICO_CHART, "Qué cambiaría con mejores datos — proyección por etapas")
    st.caption(
        "Estimaciones basadas en mejoras típicas observadas en regresión ganadera al agregar "
        "variables de calidad. Son rangos orientativos, no garantías — el valor real dependerá "
        "de cuán limpios y completos sean los nuevos datos."
    )

    proj = pd.DataFrame({
        "Escenario": [
            "Ahora — 1 campo, 4 variables reales",
            "Agregar: peso real al nacer + edad de la madre + historial de bajas",
            "Agregar: EPDs del padre desde la asociación de razas",
            "Agregar: datos estandarizados de 3 campos",
            "Agregar: 5 campos + todas las nuevas variables",
        ],
        "Spearman holdout estimado": [
            "0,13  (actual)",
            "~0,20–0,25",
            "~0,25–0,30",
            "~0,30–0,35",
            "~0,40–0,50",
        ],
        "Precisión @ top 30%": [
            f"{D['holdout'][D['holdout']['model']=='gradient_boost'].iloc[0]['precision_at_0.3']:.0%}  (actual)",
            "~40%",
            "~45%",
            "~50%",
            "~55–65%",
        ],
        "Significado práctico": [
            "~1,2× sobre el azar — señal real pero débil, no suficiente para decidir",
            "Señal clara; justifica probar en un segundo campo",
            "Acercándose a la calidad de las herramientas genómicas",
            "Generalización entre campos establecida",
            "Suficiente para cambiar decisiones reales del campo",
        ],
    })
    st.dataframe(proj, use_container_width=True, hide_index=True)

    callout(
        "<b>Referencia: herramientas genómicas norteamericanas.</b> Zoetis GeneMax — una de las "
        "herramientas genómicas líderes para selección de vaquillonas en rodeos Angus — cuesta "
        "~USD 28 por animal y está calibrada sobre poblaciones norteamericanas. Las correlaciones "
        "publicadas entre su puntaje y el desempeño real varían por rasgo; la precisión puede "
        "reducirse en poblaciones genéticamente distintas a su referencia, como el ganado "
        "Angus-cruza pampeano.",
        "green",
    )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — LA VISIÓN
# ──────────────────────────────────────────────────────────────────────────────
with t5:
    sec_header(
        "Hoja de ruta",
        "De exploración a herramienta real",
        "Este análisis es la Fase 1: entender los datos de un campo, documentar sus límites, "
        "y construir la base. Lo que sigue depende de cerrar las brechas de datos identificadas "
        "en la pestaña anterior. Esta es la trayectoria concreta si se hace ese trabajo.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="roadmap-card" style="border-top: 4px solid {PRIMARY};">
          <div class="roadmap-card-year" style="color:{PRIMARY};">Ahora — Año 1</div>
          <div class="roadmap-card-name">Auditoría de Reglas + Documentación</div>
          <ul>
            <li>Entregar el informe de auditoría al campo</li>
            <li>Empezar a registrar: peso al nacer, IHM anual, fecha de baja</li>
            <li>Conversar con 2–3 campos de la red sobre datos y decisiones</li>
            <li>Entender qué tan distintos son los formatos de otros campos</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="roadmap-card" style="border-top: 4px solid {AMBER};">
          <div class="roadmap-card-year" style="color:{AMBER};">Año 2</div>
          <div class="roadmap-card-name">Modelo Multifinca</div>
          <ul>
            <li>3 campos con 1+ año de datos estandarizados</li>
            <li>Reconstruir el modelo con nuevas variables</li>
            <li>Validación retrospectiva en campos externos</li>
            <li>Si Spearman &gt; 0,35: lanzar informes de predicción</li>
            <li>Benchmark: consistencia de tu campo vs. pares</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="roadmap-card" style="border-top: 4px solid {G700};">
          <div class="roadmap-card-year" style="color:{G700};">Año 3</div>
          <div class="roadmap-card-name">Plataforma Completa</div>
          <ul>
            <li>Plataforma web de autoservicio</li>
            <li>Subir datos → ranking + auditoría de reglas</li>
            <li>Vista retrospectiva: modelo vs. resultados reales</li>
            <li>5+ campos, base de datos pampeana en crecimiento</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    icon_label(ICO_COMP, "La vista retrospectiva — por qué sería útil")
    st.markdown(
        '<p class="sec-lead">'
        "Una vez que el modelo tenga datos suficientes, la función más clara sería mostrarle "
        "al productor <b>qué habría predicho el modelo para cohortes pasadas, antes de conocer "
        "los resultados</b>, y compararlo con lo que realmente ocurrió. "
        "La infraestructura de holdout temporal ya existe en el código; solo falta la señal."
        "</p>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)
    with col_a:
        callout(
            "<b>Ejemplo proyectado — cómo se vería con un modelo maduro</b><br><br>"
            "<span style='color:#2D6A4F;font-weight:600;'>●</span> Elecciones top 30% del modelo "
            "→ IHM real promedio a edad 4: <b>~0,47–0,49</b><br>"
            "<span style='color:#B45309;font-weight:600;'>●</span> Animales retenidos por la regla del campo "
            "→ IHM real promedio: <b>~0,43–0,45</b><br>"
            "<span style='color:#6B7280;font-weight:600;'>●</span> Selección al azar → IHM real promedio: <b>~0,41–0,43</b><br><br>"
            "Una ventaja de ~0,04 IHM sobre la regla equivale a "
            "<b>un ternero productivo adicional cada 25 vacas por año</b>, acumulado sobre toda la vida del rodeo. "
            "Esto es un escenario posible para el Año 2–3 — no el estado actual del modelo.",
            "green",
        )
    with col_b:
        callout(
            "<b>La metodología ya funciona — falta la señal</b><br><br>"
            "El holdout temporal ya está implementado: el modelo se entrena en cohortes anteriores "
            "y se evalúa en cohortes que nunca vio. La arquitectura es sólida.<br><br>"
            "Lo que hace que los números proyectados no sean reales hoy: el conjunto de entrenamiento "
            "no tiene datos de IHM de madres, que es el predictor más fuerte. "
            "Con dos años de registros sistemáticos de IHM, esa brecha desaparece.<br><br>"
            "<code>scripts/run_models.py</code> ya corre la evaluación automáticamente cada vez que "
            "se actualizan los datos.",
            "green",
        )

    st.divider()

    icon_label(ICO_DB, "Qué empezar a registrar — para uso propio y para el modelo")
    st.caption(
        "Estos datos tienen valor para el campo independientemente del modelo. "
        "Los marcados como NUEVO no están en los registros actuales — cada uno que empiece "
        "a registrarse hoy estará disponible para el análisis en 1–2 años."
    )

    schema = pd.DataFrame([
        {"Tabla": "Registro de Vacas",  "Campo": "IDV — número de caravana permanente",         "Req.": "Obligatorio",  "Notas": "Identificador único de la vaca en todos los registros"},
        {"Tabla": "Registro de Vacas",  "Campo": "Fecha de nacimiento (fecha completa)",         "Req.": "Obligatorio",  "Notas": "No solo el año — la fecha completa permite calcular la edad al parto"},
        {"Tabla": "Registro de Vacas",  "Campo": "IDV de la madre",                              "Req.": "Obligatorio",  "Notas": "Dejar en blanco si se desconoce — no adivinar"},
        {"Tabla": "Registro de Vacas",  "Campo": "Nombre del padre + número de registro racial", "Req.": "Obligatorio",  "Notas": "Permite consultar EPDs en Angus Argentina / Hereford Argentina"},
        {"Tabla": "Registro de Vacas",  "Campo": "Tipo de padre (IATF / repaso)",                "Req.": "Obligatorio",  "Notas": "Ya se registra — continuar"},
        {"Tabla": "Registro de Vacas",  "Campo": "Peso real al nacimiento (kg)",                 "Req.": "NUEVO",        "Notas": "Peso real de cada ternero. No usar valor por defecto."},
        {"Tabla": "Registro de Vacas",  "Campo": "Dificultad al parto",                          "Req.": "NUEVO",        "Notas": "Fácil / Asistido / Cesárea — un campo por ternero"},
        {"Tabla": "Registro de Vacas",  "Campo": "Fecha de baja + motivo",                       "Req.": "NUEVO",        "Notas": "Baja producción / Salud / Venta / Invernada / Muerte"},
        {"Tabla": "Registros de IHM",   "Campo": "IHM por vaca por año",                         "Req.": "Obligatorio",  "Notas": "Como proporción (0–1) o porcentaje (0–100) — ser consistente"},
        {"Tabla": "Registros de IHM",   "Campo": "¿La vaca tuvo ternero? (S/N)",                 "Req.": "Obligatorio",  "Notas": "IHM=0 significa ternero de bajo peso, NO es dato faltante"},
        {"Tabla": "Registros de IHM",   "Campo": "Peso ajustado del ternero a 205 días (kg)",    "Req.": "Opcional",     "Notas": "Si el campo lo calcula — valioso pero no bloqueante"},
        {"Tabla": "Reproductivo",       "Campo": "Eventos IATF + resultados",                    "Req.": "Obligatorio",  "Notas": "Fecha · toro · preñada / vacía / sin dato"},
        {"Tabla": "Eventos de salud",   "Campo": "Registro estructurado de eventos",             "Req.": "NUEVO",        "Notas": "Reemplazar WhatsApp: fecha · tipo de evento · IDV de la vaca"},
    ])
    st.dataframe(schema, use_container_width=True, hide_index=True)

    st.divider()

    icon_label(ICO_COMP, "La brecha competitiva")
    callout(
        "<b>No se identificó ningún software de selección de vaquillonas específico para Argentina.</b><br><br>"
        "<b>Norteamérica</b> — Zoetis GeneMax, Neogen Igenity: ~USD 28/muestra de ADN, "
        "calibradas para Angus norteamericano. La precisión se reduce en poblaciones genéticamente "
        "distintas a la referencia, como el ganado Angus-cruza pampeano.<br><br>"
        "<b>Brasil</b> — JetBov: plataforma de gestión ganadera amplia, no específica para "
        "selección de vaquillonas.<br><br>"
        "<b>Argentina</b> — El mercado de software de gestión bovina está en crecimiento en América "
        "Latina, con Argentina entre los mercados con mayor proyección de la región (Grand View "
        "Research, 2024). Un modelo entrenado en datos locales podría ofrecer una ventaja "
        "de contexto que las herramientas importadas no tienen.",
        "green",
    )


# ══════════════════════════════════════════════════════════════════════════════
# AUTHOR + FOOTER
# ══════════════════════════════════════════════════════════════════════════════
_author_photo = (
    f'<img class="author-photo" src="{AUTHOR_B64}" alt="Tatiana Quinn">'
    if AUTHOR_B64 else
    f'<div style="width:76px;height:76px;border-radius:50%;background:{G300};flex-shrink:0;"></div>'
)

st.markdown(f"""
<div class="author-section">
  <div class="author-card">
    {_author_photo}
    <div>
      <div class="author-name">Tatiana Quinn</div>
      <div class="author-role">Computer Science &amp; AI &nbsp;·&nbsp; IE University, Madrid</div>
      <a class="author-link" href="https://www.linkedin.com/in/tatianaquinn" target="_blank" rel="noopener">
        {ICO_LINK}
        linkedin.com/in/tatianaquinn
      </a>
    </div>
  </div>
</div>

<div class="footer-txt">
  San Eduardo &nbsp;·&nbsp; Bragado, Buenos Aires
  &nbsp;·&nbsp; IE University Machine Learning Foundations 2026
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 6 — MODELO 2: PREDICCIONES 2027
# ──────────────────────────────────────────────────────────────────────────────
with t6:
    sec_header(
        "Predicción en vivo",
        "Modelo 2 — Cohorte 2027",
        "El modelo predice qué vaquillonas nacidas en 2025 tendrán mayor IHM adulto. "
        "La selección real ocurrirá en 2027. Cuando llegue ese momento, compará estos rankings con las decisiones del campo."
    )

    # ── Diferencia entre Modelo 1 y Modelo 2 ──────────────────────────────────
    callout(
        f'<div class="callout-icon green">{ICO_CHECK} <b>Modelo 1 vs. Modelo 2 — ¿cuál es la diferencia?</b></div>'
        "<b>Modelo 1</b> se entrenó con vacas nacidas 2018–2022 (ya adultas, con IHM medido) "
        "y se aplicó a la cohorte 2025 — una cohorte que <em>ya fue seleccionada</em>, por lo que no podemos verificar las predicciones en tiempo real.<br><br>"
        "<b>Modelo 2</b> usa exactamente el mismo algoritmo entrenado, pero lo aplica a las 405 vaquillonas "
        "nacidas en 2025 que <em>todavía no fueron seleccionadas</em>. "
        "Su selección ocurrirá en 2027. Esta es la primera predicción genuinamente verificable del proyecto.",
        "green",
    )

    # ── Stats de cobertura ────────────────────────────────────────────────────
    m2 = D["model2"].copy()
    n_total = len(m2)
    n_top30 = int(m2["top_30pct"].sum())
    n_regla3 = int((m2["rule_prediction"] == "verdes_3").sum())
    n_both   = int((m2["top_30pct"] & (m2["rule_prediction"] == "verdes_3")).sum())
    n_madre_ihm = int(m2["madre_mean_ihm_pre"].notna().sum())

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    metric_row(
        metric_card("Vaquillonas evaluadas",    str(n_total),                   "nacidas 2025, selección 2027",       MID),
        metric_card("Con IHM de la madre",      f"{n_madre_ihm} ({n_madre_ihm/n_total:.0%})", "dato más predictivo disponible", TERRA),
        metric_card("Recomendadas por el modelo", str(n_top30),                  "top 30% por IHM predicho",           AMBER),
        metric_card("Regla predice verdes_3",    str(n_regla3),                  "cumplen todos los criterios escritos", TAUPE),
        cols=4,
    )

    callout(
        f'<div class="callout-icon amber">{ICO_WARN} <b>96% de las vaquillonas tienen madre conocida con IHM registrado</b></div>'
        f"Esta cohorte tiene cobertura de datos mucho mejor que la de 2025 (donde solo el 30% tenía IHM de la madre). "
        f"Las predicciones del Modelo 2 son más confiables que las del Modelo 1 por esta razón.",
        "amber",
    )

    # ── Distribución de la regla ──────────────────────────────────────────────
    st.divider()
    icon_label(ICO_CHART, "Lo que predice la regla documentada")

    rule_dist = m2["rule_prediction"].value_counts().reset_index()
    rule_dist.columns = ["Categoría", "N"]
    rule_labels_map = {
        "verdes_3":                    "★★★ Verdes 3 — cumple todos los criterios",
        "verdes_2":                    "★★  Verdes 2 — padre conocido, sin IATF",
        "verdes_fm_venta":             "★   Venta FM — madre con IHM bajo",
        "verdes_invernada":            "✗   Invernada — bajo peso al destete",
        "verdes_pesada_sin_genealogia":"?   Sin genealogía — madre desconocida",
    }
    rule_dist["Categoría"] = rule_dist["Categoría"].map(rule_labels_map).fillna(rule_dist["Categoría"])
    rule_colors = [TERRA if "★★★" in r else MID if "★★ " in r else AMBER if "★  " in r else G500
                   for r in rule_dist["Categoría"]]
    fig_rule = go.Figure(go.Bar(
        x=rule_dist["N"], y=rule_dist["Categoría"],
        orientation="h",
        marker_color=rule_colors,
        marker_line_width=0,
        text=rule_dist["N"],
        textposition="outside",
    ))
    _chart(fig_rule, 260)
    fig_rule.update_layout(
        xaxis=dict(title="N vaquillonas"),
        yaxis=dict(title=""),
        margin=dict(l=0, r=40, t=10, b=0),
    )
    st.plotly_chart(fig_rule, use_container_width=True)

    # ── Tabla rankeada ────────────────────────────────────────────────────────
    st.divider()
    icon_label(ICO_CHART, "Ranking completo — las 405 vaquillonas")
    st.caption(
        "Ordenadas por puntaje del modelo (IHM adulto predicho). "
        "Las columnas 'Top 30%' y 'Regla' son la recomendación del modelo y la regla documentada respectivamente."
    )

    display = m2.copy()
    display["Rank"]        = display["rank"]
    display["IDV"]         = display["idv"]
    display["Puntaje"]     = display["model_predicted_ihm"].round(3)
    display["Top 30%"]     = display["top_30pct"].map({True: "✓ Sí", False: "—"})
    display["Regla"]       = display["rule_prediction"].map({
        "verdes_3":                     "★★★ Verdes 3",
        "verdes_2":                     "★★  Verdes 2",
        "verdes_fm_venta":              "★   FM Venta",
        "verdes_invernada":             "✗   Invernada",
        "verdes_pesada_sin_genealogia": "?   Sin genealogía",
    }).fillna(display["rule_prediction"])
    display["IHM madre"]   = display["madre_mean_ihm_pre"].round(3)
    display["Peso destete"] = display["peso_destete"].round(0).astype("Int64")
    display["Padre IATF"]  = display["padre_iatf"].map({True: "Sí", False: "No"})

    # Filter by regla
    opciones_regla = ["Todas"] + sorted(display["Regla"].dropna().unique().tolist())
    sel_regla = st.selectbox("Filtrar por predicción de la regla:", opciones_regla, key="m2_filter")
    vista = display if sel_regla == "Todas" else display[display["Regla"] == sel_regla]

    st.dataframe(
        vista[["Rank", "IDV", "Puntaje", "Top 30%", "Regla", "IHM madre", "Peso destete", "Padre IATF"]],
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Rank":         st.column_config.NumberColumn("Rank", width="small"),
            "Puntaje":      st.column_config.NumberColumn("Puntaje modelo", format="%.3f"),
            "Top 30%":      st.column_config.TextColumn("Top 30%", width="small"),
            "IHM madre":    st.column_config.NumberColumn("IHM madre", format="%.3f"),
            "Peso destete": st.column_config.NumberColumn("Peso destete (kg)", width="medium"),
        }
    )
    st.caption(f"Mostrando {len(vista):,} de {n_total:,} vaquillonas")

    # ── Nota de verificación ──────────────────────────────────────────────────
    callout(
        f'<div class="callout-icon amber">{ICO_WARN} <b>Cómo verificar estas predicciones en 2027</b></div>'
        "Cuando el campo complete la selección de la cohorte 2027, compará la columna <b>Top 30%</b> "
        "con las vaquillonas que el campo retenga como verdes_3 o verdes_2. "
        "Si el modelo funciona, debería haber solapamiento significativo entre su top-30% y las retenciones reales. "
        "La columna <b>Regla</b> muestra qué haría la regla documentada — eso también es verificable.<br><br>"
        "El IHM adulto real de estas vaquillonas empezará a estar disponible en <b>2029</b> (cuando tengan 4 años). "
        "Esa será la validación definitiva del modelo.",
        "amber",
    )

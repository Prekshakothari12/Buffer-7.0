"""
SecureBank APT Detection Engine — Streamlit Dashboard
======================================================
Run:  streamlit run app.py
Deps: pip install streamlit plotly pandas
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import re
import json
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be FIRST streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecureBank APT Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — FIXED SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700;900&display=swap');
            
:root {
    --bg:        #0f1117;
    --surface:   #181c27;
    --surface2:  #1e2335;
    --border:    #2a3352;
    --accent:    #4fc3f7;
    --accent2:   #f06292;
    --accent3:   #66bb6a;
    --warn:      #ffa726;
    --text:      #cdd6f4;
    --text-dim:  #7986a8;
    --mono:      'Share Tech Mono', monospace;
    --sans:      'Exo 2', sans-serif;
}

/* ── Global background & text ── */
.stApp,
.main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

/* ── Remove Streamlit default top padding on the main content block ── */
.block-container,
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Fix all stray white text */
p, span, label, div, li, td, th {
    color: var(--text) !important;
}

/* Streamlit default overrides */
.stMarkdown, .stText, [data-testid="stMarkdownContainer"] {
    color: var(--text) !important;
}

/* Fix tab labels */
/* Fix tab labels */
[data-testid="stTabs"] button {
    color: var(--text-dim) !important;
    font-family: var(--mono) !important;
    font-size: .78rem !important;
    letter-spacing: .08em !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 18px !important;
    transition: all .2s !important;
}
[data-testid="stTabs"] button:hover {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--accent) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border: 1px solid var(--border) !important;
    border-bottom: 2px solid var(--accent) !important;
    border-radius: 6px 6px 0 0 !important;
    background: var(--surface2) !important;
    box-shadow: 0 0 8px rgba(79,195,247,0.15) !important;
}
[data-testid="stTabs"] [data-testid="stTabsBarContainer"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
}

/* Fix selectbox / multiselect text */
[data-testid="stSelectbox"] span,
[data-testid="stMultiSelect"] span {
    color: var(--text) !important;
}
/* ── Multiselect (Permitted Devices) — match dark theme ── */
[data-testid="stMultiSelect"] > div,
[data-testid="stMultiSelect"] > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}
[data-testid="stMultiSelect"] input {
    background: transparent !important;
    color: var(--text) !important;
}
[data-testid="stMultiSelect"] input::placeholder {
    color: var(--text-dim) !important;
}
/* Dropdown chevron */
[data-testid="stMultiSelect"] svg {
    fill: var(--text-dim) !important;
}
/* Dropdown options list */
[data-testid="stMultiSelect"] ul {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
[data-testid="stMultiSelect"] ul li {
    background: transparent !important;
    color: var(--text) !important;
}
[data-testid="stMultiSelect"] ul li:hover {
    background: var(--surface) !important;
    color: var(--accent) !important;
}
/* Selected tags/chips */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
}
            
/* Fix dataframe text */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th {
    color: var(--text) !important;
    background: var(--surface) !important;
}

/* Fix number input */
input[type="number"], input[type="text"] {
    color: var(--text) !important;
    background: var(--surface2) !important;
}

/* Fix checkbox */
[data-testid="stCheckbox"] label {
    color: var(--text) !important;
}

/* Fix expander text */
.streamlit-expanderContent {
    background: var(--surface) !important;
    color: var(--text) !important;
}

/* Fix warning/info/success boxes */
[data-testid="stAlert"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

/* ══════════════════════════════════════════════════
   SIDEBAR — FORCE VISIBLE, CORRECT WIDTH, STYLED
   ══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    min-width: 240px !important;
    max-width: 280px !important;
    width: 260px !important;
    background: linear-gradient(180deg, #12172a 0%, #0b0f1c 100%) !important;
    border-right: 1px solid #1e2d50 !important;
    transform: none !important;
    left: 0 !important;
    position: relative !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * {
    color: #c8d8f0 !important;
}

/* Force the sidebar collapse button to be visible */
[data-testid="collapsedControl"],
button[kind="header"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #00e5ff !important;
    background: #0d1428 !important;
    border: 1px solid #1e2d50 !important;
}

/* ── Hide default Streamlit chrome (but NOT sidebar toggle) ── */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }

/* ══════════════════════════════════════════════════
   RADIO NAV BUTTONS — fully working active state
   ══════════════════════════════════════════════════ */
/* Hide the group label "NAVIGATION" */
[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    display: none !important;
}
/* Flex column container */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    width: 100% !important;
}
/* Each nav item */
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label {
    display: flex !important;
    align-items: center !important;
    background: #0d1428 !important;
    border: 1px solid #1e2d50 !important;
    border-radius: 5px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    color: #c8d8f0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.07em !important;
    cursor: pointer !important;
    transition: background 0.15s, border-color 0.15s, color 0.15s !important;
    width: 100% !important;
    box-sizing: border-box !important;
    user-select: none !important;
    position: relative !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {
    background: #111d35 !important;
    border-color: #00e5ff !important;
    color: #00e5ff !important;
}
/* Hide the radio dot visually but keep it in DOM for :checked to work */
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label > div:first-child {
    position: absolute !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
}
/* SELECTED state */
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:has(input:checked) {
    background: #001e2e !important;
    border-color: #00e5ff !important;
    border-left: 3px solid #00e5ff !important;
    color: #00e5ff !important;
    font-weight: 700 !important;
    box-shadow: inset 0 0 12px rgba(0,229,255,0.08), 0 0 6px rgba(0,229,255,0.15) !important;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent);
}
.metric-card:hover { border-color: var(--accent); }
.metric-val {
    font-family: var(--mono);
    font-size: 2rem;
    color: var(--accent);
    margin: 0;
    line-height: 1;
}
.metric-label {
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 4px;
}

/* ── Section headers ── */
.sec-header {
    font-family: var(--mono);
    font-size: .75rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin: 24px 0 14px;
}

/* ── Verdict boxes ── */
.verdict-critical {
    background: linear-gradient(90deg,#2b0010,#1a000a);
    border: 1px solid var(--accent2);
    color: var(--accent2);
    font-family: var(--mono);
    font-size: 1.1rem;
    letter-spacing: .25em;
    padding: 14px 20px;
    border-radius: 6px;
    text-align: center;
    animation: flicker 3s infinite;
}
.verdict-suspicious {
    background: linear-gradient(90deg,#1a1000,#0f0a00);
    border: 1px solid var(--warn);
    color: var(--warn);
    font-family: var(--mono);
    font-size: 1.1rem;
    letter-spacing: .25em;
    padding: 14px 20px;
    border-radius: 6px;
    text-align: center;
}
.verdict-clear {
    background: linear-gradient(90deg,#001a08,#000f05);
    border: 1px solid var(--accent3);
    color: var(--accent3);
    font-family: var(--mono);
    font-size: 1.1rem;
    letter-spacing: .25em;
    padding: 14px 20px;
    border-radius: 6px;
    text-align: center;
}
@keyframes flicker {
    0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:.7} 94%{opacity:1} 96%{opacity:.85} 97%{opacity:1}
}

/* ── Event rows ── */
.event-row {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

/* ── Severity badges ── */
.badge-high   { background:#2b0010; color:#ff2d6b; border:1px solid #ff2d6b; border-radius:4px; padding:2px 8px; font-size:.72rem; font-family:var(--mono); }
.badge-medium { background:#1a1000; color:#ffb800; border:1px solid #ffb800; border-radius:4px; padding:2px 8px; font-size:.72rem; font-family:var(--mono); }
.badge-low    { background:#001a06; color:#39ff14; border:1px solid #39ff14; border-radius:4px; padding:2px 8px; font-size:.72rem; font-family:var(--mono); }

/* ── Raw output panel ── */
.raw-output {
    background: #181c27;
    border: 1px solid #2a3352;
    border-radius: 6px;
    padding: 16px;
    font-family: var(--mono);
    font-size: .78rem;
    color: #7986a8;
    white-space: pre-wrap;
    max-height: 420px;
    overflow-y: auto;
    line-height: 1.6;
}
/* ── Attack path ── */
.path-wrap { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:12px 0; }
.path-node {
    background: var(--surface2);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: var(--mono);
    font-size:.75rem;
    padding: 5px 12px;
    border-radius: 4px;
}
.path-arrow { color: var(--text-dim); font-size:1.1rem; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 6px !important; }

/* ── Form inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div,
.stDateInput > div > div,
.stTextInput > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
}

/* ── Multiselect deep override ── */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-baseweb="popover"] > div,
[data-baseweb="menu"] {
    background-color: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] input {
    background-color: transparent !important;
    color: var(--text) !important;
}
[data-baseweb="select"] input::placeholder {
    color: var(--text-dim) !important;
}
[data-baseweb="tag"] {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
}
[data-baseweb="menu"] li {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] li:hover {
    background-color: var(--surface) !important;
    color: var(--accent) !important;
}
/* ── Multiselect dropdown portal (floating list) ── */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] ul,
[data-baseweb="menu"],
[data-baseweb="menu"] > ul {
    background-color: #1e2335 !important;
    border: 1px solid #2a3352 !important;
    border-radius: 6px !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] li > div,
[data-baseweb="option"] {
    background-color: #1e2335 !important;
    color: #cdd6f4 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover {
    background-color: #0d1428 !important;
    color: #4fc3f7 !important;
}
/* Select all row + divider */
[data-baseweb="menu"] li:first-child {
    border-bottom: 1px solid #2a3352 !important;
    color: #7986a8 !important;
}
/* Checked item highlight */
[aria-selected="true"][data-baseweb="option"],
[data-baseweb="menu"] li[aria-selected="true"] {
    background-color: #0d1e38 !important;
    color: #4fc3f7 !important;
}
/* ── Regular buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    letter-spacing: .1em !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}


/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: .8rem !important;
    border: 1px solid var(--border) !important;
}

            /* Fix all dataframe/table whites */
[data-testid="stDataFrame"] * {
    background-color: #181c27 !important;
    color: #cdd6f4 !important;
}
[data-testid="stDataFrame"] th {
    background-color: #1e2335 !important;
    color: #7986a8 !important;
}

/* ── File uploader — match dark theme ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploader"] > div {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] p {
    color: var(--text-dim) !important;
}
[data-testid="stFileUploader"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    border-radius: 4px !important;
}
[data-testid="stFileUploader"] button:hover {
    border-color: var(--accent) !important;
    background: #1a2540 !important;
}

/* Fix form backgrounds */
[data-testid="stForm"] {
    background: #181c27 !important;
    border: 1px solid #2a3352 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

/* Expander header fix */
[data-testid="stExpander"] summary {
    background: #181c27 !important;
    color: #cdd6f4 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border: 1px solid #2a3352 !important;
}
[data-testid="stExpander"] > div {
    background: #181c27 !important;
    border: 1px solid #2a3352 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BACKEND INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
def init_engine():
    try:
        import apt_engine
        engine = apt_engine.APTEngine()
        loaded = engine.loadConfig("config.txt")
        return engine, loaded, None
    except ImportError:
        return None, False, "apt_engine module not found — please build the module first."
    except Exception as e:
        return None, False, str(e)

if "engine_obj" not in st.session_state:
    st.session_state.engine_obj, st.session_state.config_loaded, st.session_state.engine_error = init_engine()

engine_obj    = st.session_state.engine_obj
config_loaded = st.session_state.config_loaded
engine_error  = st.session_state.engine_error

# ─────────────────────────────────────────────────────────────────────────────
# CACHED DATA FETCHERS
# ─────────────────────────────────────────────────────────────────────────────
def get_users(_eng=None):
    eng = st.session_state.get("engine_obj")
    if eng is None: return []
    try: return eng.getUsers()
    except: return []

def get_devices(_eng=None):
    eng = st.session_state.get("engine_obj")
    if eng is None: return []
    try: return eng.getDevices()
    except: return []

def get_zones(_eng=None):
    eng = st.session_state.get("engine_obj")
    if eng is None: return []
    try: return eng.getZones()
    except: return []

def get_edges(_eng=None):
    eng = st.session_state.get("engine_obj")
    if eng is None: return []
    try:
        raw = eng.getEdges()
        return [(e["from"], e["to"]) for e in raw]
    except: return []

def get_report(_eng):
    if _eng is None: return []
    try: return _eng.getThreatReport()
    except: return []

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def parse_score(output: str) -> int:
    m = re.search(r'TOTAL RISK SCORE\s+(\d+)', output)
    return int(m.group(1)) if m else 0

def parse_verdict(output: str) -> str:
    m = re.search(r'VERDICT:\s*(.+)', output)
    return m.group(1).strip() if m else "UNKNOWN"

def parse_path(output: str):
    # Try BFS path first
    m = re.search(r'BFS shortest path\s*:\s*(.+)', output)
    if m:
        raw = m.group(1).strip()
        if '(unreachable)' not in raw:
            return [n.strip() for n in raw.split('-->')]
    # Fall back to visited path from event log device column
    devices = re.findall(r'^\s+\d+\s+\S+\s+\S+\s+(\S+)\s+', output, re.MULTILINE)
    return devices if devices else []

def verdict_html(verdict: str) -> str:
    v = verdict.upper()
    if "CRITICAL" in v:
        return f'<div class="verdict-critical">⚠ {verdict}</div>'
    if "SUSPICIOUS" in v:
        return f'<div class="verdict-suspicious">⚡ {verdict}</div>'
    return f'<div class="verdict-clear">✓ {verdict}</div>'

def zone_badge(level: str) -> str:
    cls = {"HIGH":"high","MEDIUM":"medium","LOW":"low"}.get(level.upper(),"low")
    return f'<span class="badge-{cls}">{level}</span>'

def score_color(score: int) -> str:
    if score >= 30: return "#ff2d6b"
    if score >= 10: return "#ffb800"
    return "#39ff14"

def path_html(nodes) -> str:
    parts = []
    for i, n in enumerate(nodes):
        parts.append(f'<span class="path-node">{n}</span>')
        if i < len(nodes) - 1:
            parts.append('<span class="path-arrow">→</span>')
    return f'<div class="path-wrap">{"".join(parts)}</div>'

def metric_card(label: str, value, icon="") -> str:
    return (
        f'<div style="'
        f'background:#181c27;'
        f'border:1px solid #2a3352;'
        f'border-radius:8px;'
        f'padding:18px 12px 16px 16px;'
        f'position:relative;'
        f'overflow:hidden;'
        f'flex:1 1 0;'
        f'min-width:0;'
        f'box-sizing:border-box;'
        f'height:90px;'
        f'display:flex;'
        f'flex-direction:column;'
        f'justify-content:center;'
        f'">'
        f'<div style="'
        f'position:absolute;top:0;left:0;'
        f'width:3px;height:100%;'
        f'background:#4fc3f7;'
        f'border-radius:8px 0 0 8px;'
        f'"></div>'
        f'<p style="'
        f'font-family:\'Share Tech Mono\',monospace;'
        f'font-size:1.6rem;'
        f'color:#4fc3f7;'
        f'margin:0 0 4px 0;'
        f'line-height:1;'
        f'white-space:nowrap;'
        f'overflow:hidden;'
        f'text-overflow:ellipsis;'
        f'">{icon} {value}</p>'
        f'<p style="'
        f'font-size:.68rem;'
        f'letter-spacing:.12em;'
        f'text-transform:uppercase;'
        f'color:#7986a8;'
        f'margin:0;'
        f'white-space:nowrap;'
        f'overflow:hidden;'
        f'text-overflow:ellipsis;'
        f'">{label}</p>'
        f'</div>'
    )

def sec_header(text: str) -> str:
    clean = text.lstrip("/ ").strip()
    return (
        f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:.72rem;'
        f'letter-spacing:.2em;text-transform:uppercase;color:#4fc3f7;'
        f'border-bottom:1px solid #2a3352;padding-bottom:5px;'
        f'margin:22px 0 10px 0;">{clean}</p>'
    )

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    "⚙️  Configuration",
    "🖥️  Network Topology",
    "👥  User Management",
    "🎯  Session Analysis",
    "📊  Threat Dashboard",
]
if "page" not in st.session_state:
    st.session_state.page = NAV_ITEMS[0]
if "events" not in st.session_state:
    st.session_state.events = [{"date": str(date.today()), "hour": 9, "minute": 0, "device": ""}]
if "history" not in st.session_state:
    st.session_state.history = []
if "last_output" not in st.session_state:
    st.session_state.last_output = ""
if "last_path" not in st.session_state:
    st.session_state.last_path = []
if "alert_sent" not in st.session_state:
    st.session_state.alert_sent = False
if "alert_status" not in st.session_state:
    st.session_state.alert_status = "Monitoring"
    # "Monitoring" | "Suspicious" | "Medium Alert" | "Strong Alert"
    # | "Email Sent" | "Email Failed" | "Config Loaded" | "Config Failed"
if "live_score" not in st.session_state:
    st.session_state.live_score = 0
if "session_fingerprint" not in st.session_state:
    st.session_state.session_fingerprint = ""
if "selected_user" not in st.session_state:
    st.session_state.selected_user = ""
if "last_alert_level" not in st.session_state:
    st.session_state.last_alert_level = ""

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

# Style nav buttons to look like a proper sidebar menu
st.markdown("""
<style>
/* Override Streamlit default button styling ONLY inside sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: #0d1428 !important;
    border: 1px solid #1e2d50 !important;
    border-left: 3px solid transparent !important;
    border-radius: 4px !important;
    color: #c8d8f0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.07em !important;
    padding: 10px 14px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.15s !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #111d35 !important;
    border-color: #00e5ff !important;
    color: #00e5ff !important;
}
/* Active nav button */
[data-testid="stSidebar"] .stButton > button[data-active="true"],
[data-testid="stSidebar"] .nav-active > button {
    background: #001e2e !important;
    border-left: 3px solid #00e5ff !important;
    border-color: #00e5ff !important;
    color: #00e5ff !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 20px">
      <div style="font-family:'Share Tech Mono',monospace;font-size:1.3rem;color:#00e5ff;
                  letter-spacing:.2em">🛡 SECUREBANK</div>
      <div style="font-size:.65rem;letter-spacing:.3em;color:#5a7099;margin-top:4px">
        APT DETECTION ENGINE v4.0
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
        'letter-spacing:.2em;color:#5a7099;margin:0 0 8px 4px">NAVIGATION</p>',
        unsafe_allow_html=True,
    )

    # ── Button-based navigation (always visible, no CSS :checked quirks) ──
    for item in NAV_ITEMS:
        is_active = st.session_state.page == item
        # Inject a wrapper class for active styling
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.page

    st.markdown("---")

    # Engine status
    if engine_obj and config_loaded:
        st.markdown(
            '<div style="color:#39ff14;font-family:\'Share Tech Mono\',monospace;'
            'font-size:.72rem;letter-spacing:.1em">● ENGINE ONLINE</div>',
            unsafe_allow_html=True,
        )
        try:
            summary = engine_obj.getConfigSummary()
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.68rem;'
                f'color:#5a7099;margin-top:6px;line-height:1.8">'
                f'Users: {summary.get("users",0)}<br>'
                f'Devices: {summary.get("devices",0)}<br>'
                f'APT Sigs: {summary.get("apt_signatures",0)}</div>',
                unsafe_allow_html=True,
            )
        except:
            pass
    else:
        st.markdown(
            '<div style="color:#ffb800;font-family:\'Share Tech Mono\',monospace;'
            'font-size:.72rem;letter-spacing:.1em">◌ ENGINE OFFLINE</div>',
            unsafe_allow_html=True,
        )
        if engine_error:
            st.caption(engine_error)

    st.markdown(
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.63rem;'
        f'color:#3a5070;margin-top:16px">◷ {datetime.now():%Y-%m-%d %H:%M:%S}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SESSION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
import subprocess, os

# Critical reason keywords that force immediate email regardless of score
# Critical reason keywords that force immediate email regardless of score
_CRITICAL_REASONS = {"phantom edge", "apt signature", "unknown device"}

def _alert_level(score: int, reasons: list) -> str:
    """Return alert level string based on score and critical reasons."""
    reason_text = " ".join(r.lower() for r in reasons)
    has_critical = any(k in reason_text for k in _CRITICAL_REASONS)
    if has_critical or score >= 40:
        return "Strong Alert"
    if score >= 30:
        return "Medium Alert"
    if score >= 10:
        return "Suspicious"
    return "Monitoring"

def _should_send_email(alert_level: str) -> bool:
    return alert_level in ("Strong Alert", "Medium Alert")

def _build_email(user: str, score: int, threshold: int,
                 alert_level: str, score_lines: list,
                 authorized_but_anomalous: bool) -> tuple:
    """Build subject + body dynamically from triggered reasons."""
    subject = f"[APT ALERT] Suspicious session detected for {user}"

    reason_block = ""
    for reason, pts in score_lines:
        reason_block += f"  * {reason}: +{pts}\n"
    if not reason_block:
        reason_block = "  (No specific reasons extracted)\n"

    body = (
        f"Suspicious session detected for user {user}.\n\n"
        f"Reasons:\n{reason_block}\n"
        f"Total risk score: {score}\n"
        f"Threshold crossed: {threshold}\n\n"
        f"Alert level: {alert_level}\n"
        f"\nGenerated: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"SecureBank APT Detection Engine"
    )
    return subject, body

def _send_email_alert(user: str, score: int, threshold: int,
                      alert_level: str, score_lines: list,
                      authorized_but_anomalous: bool = False) -> bool:
    """Fire the PowerShell alert script with rich email content. Returns True on success."""
    ps_path = os.path.join(os.path.dirname(__file__), "send_alert.ps1")
    if not os.path.exists(ps_path):
        return False
    subject, body = _build_email(user, score, threshold, alert_level,
                                 score_lines, authorized_but_anomalous)
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path,
             "-To", "preksha.kothari@cumminscollege.in",
             "-Subject", subject, "-Body", body],
            capture_output=True, timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False

def render_session_path_graph(path_nodes, score, output):
    if not path_nodes or len(path_nodes) < 1:
        return

    import plotly.graph_objects as go
    import math

    # ── Pull full topology data ──
    all_devices = get_devices(engine_obj)
    all_edges   = get_edges(engine_obj)

    if not all_devices:
        return

    is_threat     = score >= 30
    is_suspicious = score >= 10

    # ── Parse flagged nodes/edges from analysis output ──
    phantom_pairs      = set()
    unauthorized_nodes = set()

    for i in range(len(path_nodes) - 1):
        block = f"{path_nodes[i]}.*?{path_nodes[i+1]}"
        if re.search(r'PHANTOM EDGE', output, re.IGNORECASE):
            phantom_pairs.add((path_nodes[i], path_nodes[i+1]))

    for line in output.splitlines():
        if "UNAUTHORIZED" in line:
            m = re.search(r'\d+\s+\S+\s+\S+\s+(\S+)\s+', line)
            if m:
                unauthorized_nodes.add(m.group(1).strip())

    visited_set   = set(path_nodes)
    visited_edges = set(zip(path_nodes[:-1], path_nodes[1:]))

    # ── Layout: place nodes by zone tier with spread ──
    zone_tier = {}
    for d in all_devices:
        z = d.get("zone", "BRANCH")
        sl = d.get("security_level", "LOW")
        tier = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}.get(sl, 0)
        zone_tier[d["id"]] = tier

    tier_counts  = {0: 0, 1: 0, 2: 0}
    positions    = {}
    for d in all_devices:
        nid  = d["id"]
        tier = zone_tier.get(nid, 0)
        slot = tier_counts[tier]
        tier_counts[tier] += 1
        x = tier * 3.5
        y = slot * 2.2
        positions[nid] = (x, y)

    # Center each tier vertically
    for tier in range(3):
        nodes_in_tier = [nid for nid, t in zone_tier.items() if t == tier]
        if not nodes_in_tier:
            continue
        ys    = [positions[nid][1] for nid in nodes_in_tier]
        mid_y = (max(ys) + min(ys)) / 2
        for nid in nodes_in_tier:
            x, y = positions[nid]
            positions[nid] = (x, y - mid_y)

    # ── Color helpers ──
    def node_fill(nid, idx_in_path):
        if nid in unauthorized_nodes:            return "#ff2d6b"
        if idx_in_path == 0:                     return "#00e5ff"
        if idx_in_path == len(path_nodes) - 1:
            return "#ff2d6b" if is_threat else "#4fc3f7"
        if nid in visited_set and is_threat:     return "#ff8c00"
        if nid in visited_set and is_suspicious: return "#ffa726"
        if nid in visited_set:                   return "#4fc3f7"
        return "#1e2d50"   # background node

    def node_border(nid):
        if nid in unauthorized_nodes:  return "#ff2d6b"
        if nid in visited_set:
            return "#ff2d6b" if is_threat else "#ffa726" if is_suspicious else "#4fc3f7"
        return "#2a3352"

    def node_size(nid, idx_in_path):
        if idx_in_path in (0, len(path_nodes) - 1): return 32
        if nid in visited_set:                       return 26
        return 18

    def edge_style(f, t):
        """Returns (color, width, is_active)"""
        if (f, t) in visited_edges or (t, f) in visited_edges:
            if is_threat:     return ("#ff2d6b", 4, True)
            if is_suspicious: return ("#ffa726", 3, True)
            return ("#4fc3f7", 3, True)
        return ("#1e2d50", 1, False)

    # ── Build edge traces ──
    edge_traces = []

    for f, t in all_edges:
        if f not in positions or t not in positions:
            continue
        x0, y0 = positions[f]
        x1, y1 = positions[t]
        ec, ew, is_active = edge_style(f, t)

        # Glow layer for active edges
        # Glow layer for active edges
        if is_active:
            glow_color = {
                "#ff2d6b": "rgba(255,45,107,0.15)",
                "#ffa726": "rgba(255,167,38,0.15)",
                "#4fc3f7": "rgba(79,195,247,0.15)",
            }.get(ec, "rgba(79,195,247,0.15)")
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(color=glow_color, width=14),
                hoverinfo="none", showlegend=False,
            ))

        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(color=ec, width=ew, dash="solid"),
            hoverinfo="none", showlegend=False,
        ))

        # Clean arrowhead at 75% along active edges only
        if is_active:
            ax = x0 + (x1 - x0) * 0.75
            ay = y0 + (y1 - y0) * 0.75
            angle = math.degrees(math.atan2(y1 - y0, x1 - x0))
            edge_traces.append(go.Scatter(
                x=[ax], y=[ay],
                mode="markers",
                marker=dict(
                    symbol="arrow",
                    size=12,
                    color=ec,
                    angle=angle,
                    line=dict(width=0),
                ),
                hoverinfo="none", showlegend=False,
            ))

    # ── Build node trace ──
    path_index = {nid: i for i, nid in enumerate(path_nodes)}

    nx_l, ny_l, nc_l, nb_l, ns_l, nt_l, nh_l, nopacity = [], [], [], [], [], [], [], []

    for d in all_devices:
        nid = d["id"]
        if nid not in positions:
            continue
        x, y    = positions[nid]
        idx     = path_index.get(nid, -1)
        fill    = node_fill(nid, idx)
        border  = node_border(nid)
        size    = node_size(nid, idx)
        opacity = 1.0 if nid in visited_set else 0.45

        label_suffix = ""
        if idx == 0:                         label_suffix = "\n▶ START"
        elif idx == len(path_nodes) - 1:     label_suffix = "\n■ END"
        elif nid in unauthorized_nodes:      label_suffix = "\n⚠ UNAUTH"

        hover = (
            f"<b>{nid}</b><br>"
            f"Zone: {d.get('zone','?')}  |  Security: {d.get('security_level','?')}<br>"
            f"Required Role: {d.get('required_role','?')}<br>"
            + ("⚠ UNAUTHORIZED ACCESS<br>" if nid in unauthorized_nodes else "")
            + ("🔴 THREAT DESTINATION" if idx == len(path_nodes)-1 and is_threat
               else "🟢 SESSION START" if idx == 0
               else f"Step {idx+1} in path" if idx >= 0
               else "Background node")
        )

        nx_l.append(x);      ny_l.append(y)
        nc_l.append(fill);   nb_l.append(border)
        ns_l.append(size);   nt_l.append(nid + label_suffix)
        nh_l.append(hover);  nopacity.append(opacity)

    node_trace = go.Scatter(
        x=nx_l, y=ny_l,
        mode="markers+text",
        marker=dict(
            size=ns_l, color=nc_l, opacity=nopacity,
            line=dict(color=nb_l, width=2),
        ),
        text=nt_l,
        textposition="top center",
        textfont=dict(family="Share Tech Mono", size=9, color="#c8d8f0"),
        hovertext=nh_l,
        hoverinfo="text",
        showlegend=False,
    )

    # ── Glow rings for critical/unauthorized nodes ──
    glow_traces = []
    for nid in visited_set:
        if nid not in positions:
            continue
        idx = path_index.get(nid, -1)
        if nid in unauthorized_nodes or (idx == len(path_nodes)-1 and is_threat):
            x, y = positions[nid]
            glow_traces.append(go.Scatter(
                x=[x], y=[y],
                mode="markers",
                marker=dict(
                    size=52,
                    color="rgba(255,45,107,0.06)",
                    line=dict(color="rgba(255,45,107,0.30)", width=1.5),
                ),
                hoverinfo="none", showlegend=False,
            ))

    # ── Zone band annotations ──
    zone_labels = [
        (0,   "#39ff14", "LOW SECURITY"),
        (3.5, "#ffb800", "MEDIUM SECURITY"),
        (7.0, "#ff2d6b", "HIGH SECURITY"),
    ]
    annotations = [
        dict(
            x=xpos, y=-99, xref="x", yref="y",
            text=f'<span style="font-family:Share Tech Mono;font-size:9px;'
                 f'letter-spacing:.15em;color:{col}">{label}</span>',
            showarrow=False,
            font=dict(family="Share Tech Mono", size=9, color=col),
            align="center",
        )
        for xpos, col, label in zone_labels
    ]

    # Verdict annotation on last visited node
    if is_threat and path_nodes:
        last = path_nodes[-1]
        if last in positions:
            lx, ly = positions[last]
            annotations.append(dict(
                x=lx, y=ly - 0.9,
                text="⚠ CRITICAL",
                showarrow=False,
                font=dict(family="Share Tech Mono", size=9, color="#ff2d6b"),
                bgcolor="rgba(43,0,16,0.85)",
                bordercolor="#ff2d6b",
                borderwidth=1,
                borderpad=3,
            ))

    # ── Compute axis ranges ──
    all_x = [p[0] for p in positions.values()]
    all_y = [p[1] for p in positions.values()]
    pad_x = max(1.5, (max(all_x) - min(all_x)) * 0.15)
    pad_y = max(1.5, (max(all_y) - min(all_y)) * 0.15)

    fig = go.Figure(data=glow_traces + edge_traces + [node_trace])
    fig.update_layout(
        paper_bgcolor="#060b1a",
        plot_bgcolor="#060b1a",
        height=480,
        margin=dict(l=20, r=20, t=20, b=60),
        annotations=annotations,
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[min(all_x) - pad_x, max(all_x) + pad_x],
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[min(all_y) - pad_y - 1.5, max(all_y) + pad_y],
        ),
        hovermode="closest",
    )

    # ── Legend strip ──
    legend_items = [
        ("#00e5ff", "Session Start"),
        ("#ff8c00" if is_threat else "#4fc3f7", "Visited Node"),
        ("#ff2d6b", "Critical / Unauthorized") if is_threat or unauthorized_nodes else ("#4fc3f7", "Visited Node"),
        ("#1e2d50", "Background Node"),
        ("#ff2d6b" if is_threat else "#4fc3f7", "Traversal Edge"),
    ]
    # deduplicate
    seen = set(); legend_items_dedup = []
    for item in legend_items:
        if item[1] not in seen:
            seen.add(item[1]); legend_items_dedup.append(item)

    legend_html = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:18px">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{c};'
        f'box-shadow:0 0 5px {c}40;display:inline-block"></span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:.68rem;'
        f'color:#7986a8">{l}</span></span>'
        for c, l in legend_items_dedup
    )

    # ── Threat-aware header ──
    threat_label = (
        "🔴  CRITICAL THREAT PATH — FULL TOPOLOGY OVERLAY"  if score >= 30 else
        "⚡  SUSPICIOUS TRAVERSAL — FULL TOPOLOGY OVERLAY"   if score >= 10 else
        "✓  SESSION TRAVERSAL — FULL TOPOLOGY OVERLAY"
    )
    threat_color = "#ff2d6b" if score >= 30 else "#ffa726" if score >= 10 else "#4fc3f7"
    bg_color     = "#0d0005" if score >= 30 else "#0d1428"

    dot_color   = "#7f1d1d" if score >= 30 else "#7c2d12" if score >= 10 else "#164e63"
    text_color  = "#fca5a5" if score >= 30 else "#fdba74" if score >= 10 else "#7dd3fc"
    grad_color  = "rgba(127,29,29,0.18)" if score >= 30 else "rgba(124,45,18,0.15)" if score >= 10 else "rgba(22,78,99,0.15)"

    st.markdown(
        f'<div style="'
        f'background:linear-gradient(90deg,{grad_color} 0%,transparent 100%);'
        f'border-left:2px solid {dot_color};'
        f'border-radius:0;'
        f'padding:10px 18px;'
        f'font-family:\'Share Tech Mono\',monospace;font-size:.73rem;'
        f'color:{text_color};letter-spacing:.13em;'
        f'display:flex;align-items:center;gap:10px;margin-bottom:0">'
        f'<span style="width:6px;height:6px;border-radius:50%;'
        f'background:{text_color};opacity:0.7;flex-shrink:0"></span>'
        f'{threat_label}'
        f'<span style="margin-left:auto;color:#334155;font-size:.65rem;letter-spacing:.08em">'
        f'{len(path_nodes)} of {len(all_devices)} nodes visited</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        f'<div style="'
        f'border-top:1px solid #1e293b;'
        f'padding:9px 18px;margin-top:0">'
        + legend_html +
        f'</div>',
        unsafe_allow_html=True,
    )

def page_session_analysis():
    st.markdown(
        '<h2 style="font-family:\'Share Tech Mono\',monospace;color:#00e5ff;'
        'letter-spacing:.15em;font-size:1.25rem">🎯 SESSION ANALYSIS</h2>',
        unsafe_allow_html=True,
    )

    users      = get_users(engine_obj)
    devices    = get_devices(engine_obj)
    device_ids = [d["id"] for d in devices]
    device_map = {d["id"]: d for d in devices}

    if not users:
        st.warning("No users found. Please add users in User Management or load a config file.")
        return

    col_left, col_right = st.columns([4, 6])

    with col_left:
        st.markdown(sec_header("// USER"), unsafe_allow_html=True)
        usernames = [""] + [u["username"] for u in users]
        sel_user  = st.selectbox(
            "Select User",
            usernames,
            index=0,
            format_func=lambda x: "— Select a user —" if x == "" else x,
            label_visibility="collapsed",
        )
        udata = next((u for u in users if u["username"] == sel_user), None)

        if not sel_user:
            st.markdown(
                '<div style="background:#0d1428;border:1px dashed #2a3352;border-radius:6px;'
                'padding:14px;margin-top:8px;font-family:\'Share Tech Mono\',monospace;'
                'font-size:.78rem;color:#3a5070;text-align:center">'
                'Select a user to begin analysis'
                '</div>',
                unsafe_allow_html=True,
            )
        if udata:
            role_color = {
                "ADMIN": "#ff2d6b", "SENIOR": "#ffb800",
                "OPS": "#00e5ff",   "TELLER": "#39ff14",
            }.get(udata["role"], "#5a7099")
            st.markdown(
                f'<div style="background:#0d1428;border:1px solid #1e2d50;border-radius:6px;'
                f'padding:14px;margin-top:8px;font-family:\'Share Tech Mono\',monospace;font-size:.78rem">'
                f'<span style="color:#5a7099">USER </span>'
                f'<span style="color:#c8d8f0;font-weight:700">{udata["username"]}</span><br>'
                f'<span style="color:#5a7099">ROLE </span>'
                f'<span style="color:{role_color}">{udata["role"]}</span><br>'
                f'<span style="color:#5a7099">NODE </span>'
                f'<span style="color:#8fbbdd">{udata["machine"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        threshold = 30
        if engine_obj:
            try: threshold = engine_obj.getRiskThreshold()
            except: pass

        st.markdown(sec_header("// RISK THRESHOLD"), unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#0d1428;border:1px solid #1e2d50;border-radius:6px;'
            f'padding:12px 16px;font-family:\'Share Tech Mono\',monospace;font-size:.78rem">'
            f'Alert triggers at score ≥ '
            f'<span style="color:#ff2d6b;font-size:1.1rem">{threshold}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Live status panel ──────────────────────────────────────────────────
        st.markdown(sec_header("// LIVE MONITOR"), unsafe_allow_html=True)
        live_score    = st.session_state.live_score
        alert_status  = st.session_state.alert_status
        score_col     = score_color(live_score)
        status_cfg = {
            "Monitoring":    ("#00e5ff", "●", "MONITORING"),
            "Suspicious":    ("#ffa726", "⚡", "SUSPICIOUS — DASHBOARD ONLY"),
            "Medium Alert":  ("#ff8c00", "⚠", "MEDIUM ALERT"),
            "Strong Alert":  ("#ff2d6b", "🔴", "STRONG ALERT"),
            "Email Sent":    ("#39ff14", "✔", "EMAIL SENT"),
            "Email Failed":  ("#ff2d6b", "✘", "EMAIL FAILED"),
            "Config Loaded": ("#39ff14", "✔", "CONFIG LOADED"),
            "Config Failed": ("#ff2d6b", "✘", "CONFIG FAILED"),
        }
        s_color, s_icon, s_label = status_cfg.get(alert_status, ("#5a7099", "●", alert_status.upper()))
        st.markdown(
            f'<div style="background:#0d1428;border:1px solid #1e2d50;border-radius:6px;'
            f'padding:14px 16px;font-family:\'Share Tech Mono\',monospace;font-size:.78rem;line-height:2">'
            f'<span style="color:#5a7099">LIVE SCORE </span>'
            f'<span style="color:{score_col};font-size:1.3rem;font-weight:700">{live_score}</span><br>'
            f'<span style="color:#5a7099">STATUS&nbsp;&nbsp;&nbsp;&nbsp; </span>'
            f'<span style="color:{s_color}">{s_icon} {s_label}</span><br>'
            f'<span style="color:#3a5070;font-size:.68rem">⟳ auto-updating on every event change</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.history:
            st.markdown(sec_header("// RECENT SESSIONS"), unsafe_allow_html=True)
            for h in reversed(st.session_state.history[-5:]):
                sc  = h["score"]
                col = score_color(sc)
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:6px 10px;border-bottom:1px solid #1e2d50;'
                    f'font-family:\'Share Tech Mono\',monospace;font-size:.72rem">'
                    f'<span style="color:#8fbbdd">{h["user"]}</span>'
                    f'<span style="color:{col}">{sc}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown(sec_header("// ACCESS EVENTS"), unsafe_allow_html=True)

        # ── Add / Clear buttons ────────────────────────────────────────────────
        st.markdown(
            '<style>'
            '.btn-row{display:flex;gap:10px;margin-bottom:14px;}'
            '.btn-row button{'
            'background:transparent!important;'
            'border:1px solid #2a3352!important;'
            'color:#4fc3f7!important;'
            'font-family:"Share Tech Mono",monospace!important;'
            'font-size:.75rem!important;letter-spacing:.08em!important;'
            'padding:6px 16px!important;border-radius:4px!important;'
            'cursor:pointer;transition:all .15s!important;}'
            '.btn-row button:hover{'
            'border-color:#4fc3f7!important;background:#0d1e30!important;}'
            '</style>',
            unsafe_allow_html=True,
        )
        bc1, bc2 = st.columns([1, 1])
        with bc1:
            if st.button("＋  Add Event", use_container_width=True):
                st.session_state.events.append(
                    {"date": str(date.today()), "hour": 9, "minute": 0, "device": ""})
                st.session_state.alert_sent   = False
                st.session_state.alert_status = "Monitoring"
                st.rerun()
        with bc2:
            if st.button("✕  Clear All", use_container_width=True) and st.session_state.events:
                st.session_state.events = [
                    {"date": str(date.today()), "hour": 9, "minute": 0, "device": ""}]
                st.session_state.alert_sent   = False
                st.session_state.alert_status = "Monitoring"
                st.session_state.live_score   = 0
                st.session_state.last_output  = ""
                st.session_state.last_path    = []
                st.rerun()

        # ── Column header row ──────────────────────────────────────────────────
        st.markdown(
            '<div style="display:grid;grid-template-columns:3fr 2fr 2fr 4fr 1fr;'
            'gap:8px;padding:4px 10px;margin-bottom:4px;'
            'border-bottom:1px solid #2a3352;">'
            '<span style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
            'color:#7986a8;letter-spacing:.12em">DATE</span>'
            '<span style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
            'color:#7986a8;letter-spacing:.12em">HOUR</span>'
            '<span style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
            'color:#7986a8;letter-spacing:.12em">MIN</span>'
            '<span style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
            'color:#7986a8;letter-spacing:.12em">DEVICE ID</span>'
            '<span style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;'
            'color:#7986a8;letter-spacing:.12em">DEL</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Event rows — NO st.container() to avoid the blue border line ──────
        to_remove = []
        for i, ev in enumerate(st.session_state.events):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 4, 1])
            with c1:
                d = st.date_input(
                    "Date", value=date.fromisoformat(ev["date"]),
                    key=f"d_{i}", label_visibility="collapsed",
                )
                st.session_state.events[i]["date"] = str(d)
            with c2:
                h = st.number_input(
                    "Hr", 0, 23, ev["hour"],
                    key=f"h_{i}", label_visibility="collapsed",
                )
                st.session_state.events[i]["hour"] = h
            with c3:
                m = st.number_input(
                    "Min", 0, 59, ev["minute"],
                    key=f"m_{i}", label_visibility="collapsed",
                )
                st.session_state.events[i]["minute"] = m
            with c4:
                dev_options = [""] + device_ids
                idx = dev_options.index(ev["device"]) if ev["device"] in dev_options else 0
                dev = st.selectbox(
                    "Dev", dev_options, index=idx,
                    key=f"dev_{i}", label_visibility="collapsed",
                )
                st.session_state.events[i]["device"] = dev
                if dev and dev in device_map:
                    lvl = device_map[dev].get("security_level", "LOW")
                    st.markdown(zone_badge(lvl), unsafe_allow_html=True)
            with c5:
                if st.button("✕", key=f"rm_{i}"):
                    to_remove.append(i)
            # Thin separator between rows (no blue border)
            st.markdown(
                '<div style="border-bottom:1px solid #1e2335;margin:2px 0 6px 0;"></div>',
                unsafe_allow_html=True,
            )

        for idx in sorted(to_remove, reverse=True):
            st.session_state.events.pop(idx)
        if to_remove:
            st.session_state.alert_sent   = False
            st.session_state.alert_status = "Monitoring"
            st.rerun()

        st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)

        # ── Real-time analysis banner ──────────────────────────────────────────
        st.markdown(
            '<div style="background:#091510;border:1px solid #1a3828;border-radius:6px;'
            'padding:9px 16px;font-family:\'Share Tech Mono\',monospace;font-size:.72rem;'
            'color:#2ecc71;letter-spacing:.07em;margin-top:4px;">'
            '⟳ &nbsp;REAL-TIME ANALYSIS ACTIVE — results update automatically as events change'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── AUTO-ANALYSIS: only re-run when events actually change ────────────────
    # CHANGE 3: block analysis entirely if no user chosen
    if not sel_user:
        return

    valid_events = [e for e in st.session_state.events if e.get("device")]

    # Build a stable fingerprint
    fingerprint = (
        sel_user + "|"
        + "|".join(
            f"{e['date']}-{e['hour']}-{e['minute']}-{e['device']}"
            for e in valid_events
        )
        + f"|cfg={st.session_state.config_loaded}"
    )
    # Reset live score when user changes to a different one (or deselected)
    if sel_user != st.session_state.selected_user:
        st.session_state.live_score   = 0
        st.session_state.last_output  = ""
        st.session_state.last_path    = []
        st.session_state.alert_sent   = False
        st.session_state.alert_status = "Monitoring"
        st.session_state.selected_user = sel_user

    fingerprint_changed = (fingerprint != st.session_state.session_fingerprint)

    if valid_events and engine_obj:
        if fingerprint_changed:
            # Only call backend when something actually changed
            try:
                output = engine_obj.analyzeSession(sel_user, valid_events)
            except Exception as ex:
                output = f"[ERROR] {ex}"

            score   = parse_score(output)
            verdict = parse_verdict(output)

            st.session_state.live_score        = score
            st.session_state.last_output       = output
            st.session_state.last_path         = parse_path(output)
            st.session_state.session_fingerprint = fingerprint

            # Reset alert state only when this is genuinely a new session
            if st.session_state.alert_sent and fingerprint_changed:
                st.session_state.alert_sent      = False
                st.session_state.last_alert_level = ""

            # Extract score breakdown for email
            score_lines = re.findall(r'^\s+(.+?)\s+\+(\d+)\s*$', output, re.MULTILINE)
            score_lines = [
                (r.strip(), int(s)) for r, s in score_lines
                if r.strip() not in ("TOTAL RISK SCORE", "Flag / Reason")
            ]

            # Determine alert level
            reason_labels = [r for r, _ in score_lines]
            al = _alert_level(score, reason_labels)

            # Authorized-but-anomalous heuristic:
            # if output says "authorized" but score is still raised, flag it
            authorized_but_anomalous = (
                "authorized" in output.lower() and score >= 10
            )

            # Update history (replace last entry for same user, else append)
            hist = st.session_state.history
            if hist and hist[-1]["user"] == sel_user:
                hist[-1] = {"user": sel_user, "score": score,
                            "verdict": verdict, "ts": datetime.now().isoformat(),
                            "alert_level": al}
            else:
                hist.append({"user": sel_user, "score": score,
                             "verdict": verdict, "ts": datetime.now().isoformat(),
                             "alert_level": al})

            # ── Alert & email logic ────────────────────────────────────────────
            # Dashboard-only (10–29, no critical reasons)
            if al == "Suspicious":
                st.session_state.alert_status = "Suspicious"
                # no email for pure suspicious

            # Medium/Strong: send email once per session fingerprint
            elif al in ("Medium Alert", "Strong Alert"):
                st.session_state.alert_status = al
                if not st.session_state.alert_sent:
                    success = _send_email_alert(
                        sel_user, score, threshold, al,
                        score_lines, authorized_but_anomalous
                    )
                    st.session_state.alert_sent    = True
                    st.session_state.last_alert_level = al
                    st.session_state.alert_status  = "Email Sent" if success else "Email Failed"

            else:
                st.session_state.alert_status = "Monitoring"

    elif not engine_obj:
        output  = ""
        score   = 0
        verdict = "UNKNOWN"
    else:
        output  = st.session_state.last_output
        score   = parse_score(output) if output else 0
        verdict = parse_verdict(output) if output else "UNKNOWN"

    # ── RESULTS DISPLAY ───────────────────────────────────────────────────────
    if st.session_state.last_output:
        output  = st.session_state.last_output
        score   = parse_score(output)
        verdict = parse_verdict(output)

        st.markdown('<div style="border-top:1px solid #2a3352;margin:24px 0 16px 0;"></div>', unsafe_allow_html=True)
        st.markdown(sec_header("ANALYSIS RESULTS"), unsafe_allow_html=True)

        g1, g2 = st.columns([1, 2])
        with g1:
            gauge_color = (
                "#f06292" if score >= 30
                else "#ffa726" if score >= 10
                else "#66bb6a"
            )
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"font": {"color": gauge_color, "size": 52,
                                 "family": "Share Tech Mono"}},
                gauge={
                    "axis": {
                        "range": [0, 200],
                        "tickcolor": "#7986a8",
                        "tickfont": {"color": "#7986a8", "size": 9},
                    },
                    "bar":  {"color": gauge_color, "thickness": 0.28},
                    "bgcolor": "#181c27",
                    "bordercolor": "#2a3352",
                    "steps": [
                        {"range": [0, 10],   "color": "#1a2a1a"},
                        {"range": [10, 30],  "color": "#2a2010"},
                        {"range": [30, 200], "color": "#2a1525"},
                    ],
                    "threshold": {
                        "line": {"color": "#f06292", "width": 2},
                        "thickness": 0.75, "value": 30,
                    },
                },
            ))
            fig.update_layout(
                height=220, margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="#0f1117",
                font={"color": "#cdd6f4", "family": "Share Tech Mono"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(verdict_html(verdict), unsafe_allow_html=True)
            alert_status = st.session_state.alert_status
            alert_cfg = {
                "Suspicious":   ("#ffa726", "#1a1000",
                                 "⚡ SUSPICIOUS — Dashboard flagged. No email (score 10–29)."),
                "Medium Alert": ("#ff8c00", "#1a0d00",
                                 "⚠ MEDIUM ALERT — Email sent if score 30–39."),
                "Strong Alert": ("#ff2d6b", "#2b0010",
                                 "🔴 STRONG ALERT — Immediate email triggered (score ≥ 40 or critical reason)."),
                "Email Sent":   ("#39ff14", "#001a06",
                                 "✔ EMAIL ALERT SENT → preksha.kothari@cumminscollege.in"),
                "Email Failed": ("#ff2d6b", "#2b0010",
                                 "✘ EMAIL ALERT FAILED — check send_alert.ps1"),
            }
            if alert_status in alert_cfg:
                a_color, a_bg, a_text = alert_cfg[alert_status]
                st.markdown(
                    f'<div style="margin-top:12px;padding:10px 14px;'
                    f'background:{a_bg};border:1px solid {a_color};border-radius:4px;'
                    f'font-family:\'Share Tech Mono\',monospace;font-size:.75rem;color:{a_color}">'
                    f'{a_text}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.last_path:
            st.markdown(sec_header("ATTACK PATH"), unsafe_allow_html=True)
            st.markdown(path_html(st.session_state.last_path), unsafe_allow_html=True)

        score_lines = re.findall(r'^\s+(.+?)\s+\+(\d+)\s*$', output, re.MULTILINE)
        score_lines = [
            (r, int(s)) for r, s in score_lines
            if r.strip() not in ("TOTAL RISK SCORE", "Flag / Reason")
        ]
        if score_lines:
            st.markdown(sec_header("SCORE BREAKDOWN"), unsafe_allow_html=True)
            df_sc = pd.DataFrame(score_lines, columns=["Reason", "Points"])
            fig2 = px.bar(
                df_sc, x="Points", y="Reason", orientation="h",
                color="Points",
                color_continuous_scale=[
                    [0.0, "#2e4a6e"],
                    [0.4, "#ffa726"],
                    [1.0, "#f06292"],
                ],
                template="plotly_dark",
            )
            fig2.update_layout(
                paper_bgcolor="#0f1117",
                plot_bgcolor="#181c27",
                height=max(180, 38 * len(df_sc)),
                margin=dict(l=10, r=10, t=10, b=10),
                coloraxis_showscale=False,
                yaxis={
                    "tickfont": {"family": "Share Tech Mono", "size": 10,
                                 "color": "#cdd6f4"},
                    "gridcolor": "#2a3352",
                },
                xaxis={
                    "gridcolor": "#2a3352",
                    "tickfont": {"color": "#7986a8"},
                    "title": {"text": "Points", "font": {"color": "#7986a8"}},
                },
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # ── Session path graph ────────────────────────────────────────────────
        if st.session_state.last_path:
            st.markdown(sec_header("SESSION TRAVERSAL GRAPH"), unsafe_allow_html=True)
            render_session_path_graph(
                st.session_state.last_path,
                score,
                output,
            )

        # ── Export button — styled to match dark theme ─────────────────────────
        st.markdown(
            '<style>'
            '[data-testid="stDownloadButton"] > button {'
            'background:transparent!important;'
            'border:1px solid #2a3352!important;'
            'color:#4fc3f7!important;'
            'font-family:"Share Tech Mono",monospace!important;'
            'font-size:.75rem!important;'
            'letter-spacing:.1em!important;'
            'padding:8px 20px!important;'
            'border-radius:4px!important;'
            'margin-top:12px!important;'
            'transition:all .15s!important;}'
            '[data-testid="stDownloadButton"] > button:hover {'
            'border-color:#4fc3f7!important;'
            'background:#0d1e30!important;}'
            '</style>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "⬇  EXPORT ANALYSIS (.TXT)",
            data=output,
            file_name=f"apt_analysis_{sel_user}_{datetime.now():%Y%m%d_%H%M%S}.txt",
            mime="text/plain",
        )

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: THREAT DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown(
        '<h2 style="font-family:\'Share Tech Mono\',monospace;color:#00e5ff;'
        'letter-spacing:.15em;font-size:1.25rem">📊 THREAT INTELLIGENCE DASHBOARD</h2>',
        unsafe_allow_html=True,
    )

    report = get_report(engine_obj)

    if not report:
        st.info("No sessions analysed yet. Run some sessions from Session Analysis.")
        return

    total      = len(report)
    suspicious = sum(1 for r in report if 10 <= r["score"] < 30)
    medium     = sum(1 for r in report if 30 <= r["score"] < 40)
    strong     = sum(1 for r in report if r["score"] >= 40)
    avg_sc     = round(sum(r["score"] for r in report) / total, 1) if total else 0
    max_sc     = max(r["score"] for r in report) if report else 0

    cards_html = "".join([
        metric_card("SESSIONS ANALYSED", total,     "⬛"),
        metric_card("SUSPICIOUS",        suspicious, "⚡"),
        metric_card("MEDIUM ALERTS",     medium,     "⚠"),
        metric_card("STRONG ALERTS",     strong,     "🔴"),
        metric_card("HIGHEST SCORE",     max_sc,     "📈"),
    ])
    st.markdown(
        f'<div style="'
        f'display:flex;'
        f'flex-direction:row;'
        f'gap:12px;'
        f'width:100%;'
        f'box-sizing:border-box;'
        f'margin-bottom:20px;'
        f'">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    dc1, dc2 = st.columns([3, 2])
    with dc1:
        st.markdown(sec_header("RISK SCORES BY USER"), unsafe_allow_html=True)

        # Deduplicate: one row per user — keep highest score per user
        user_score_map = {}
        for r in report:
            u = r["user"]
            if u not in user_score_map or r["score"] > user_score_map[u]:
                user_score_map[u] = r["score"]
        # Sort descending by score
        sorted_users  = sorted(user_score_map.keys(), key=lambda u: user_score_map[u], reverse=True)
        sorted_scores = [user_score_map[u] for u in sorted_users]
        bar_colors    = [score_color(s) for s in sorted_scores]

        # Dynamic y-axis ceiling: at least 60, or max_score + 20% headroom
        y_max = max(60, max(sorted_scores) * 1.25) if sorted_scores else 60

        fig = go.Figure(go.Bar(
            x=sorted_users,
            y=sorted_scores,
            marker_color=bar_colors,
            marker_line_color="#0f1117",
            marker_line_width=1.5,
            text=[str(s) for s in sorted_scores],
            textposition="outside",
            textfont={"family": "Share Tech Mono", "size": 12, "color": "#cdd6f4"},
            cliponaxis=False,
            width=[0.45] * len(sorted_users),   # thinner bars — better single-bar look
        ))

        # Threshold annotation line + label
        fig.add_shape(
            type="line",
            x0=-0.5, x1=len(sorted_users) - 0.5,
            y0=30, y1=30,
            line=dict(color="#f06292", width=1.5, dash="dash"),
        )
        fig.add_annotation(
            x=len(sorted_users) - 0.5,
            y=30,
            text="Alert Threshold (30)",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            font=dict(family="Share Tech Mono", size=9, color="#f06292"),
            bgcolor="#0f1117",
            borderpad=2,
        )

        fig.update_layout(
            paper_bgcolor="#0f1117",
            plot_bgcolor="#181c27",
            height=320,
            margin=dict(l=40, r=20, t=40, b=50),
            xaxis=dict(
                tickfont=dict(family="Share Tech Mono", size=11, color="#cdd6f4"),
                gridcolor="#2a3352",
                showgrid=False,
                zeroline=False,
                fixedrange=True,
            ),
            yaxis=dict(
                tickfont=dict(family="Share Tech Mono", size=10, color="#7986a8"),
                gridcolor="#2a3352",
                range=[0, y_max],
                zeroline=False,
                fixedrange=True,
            ),
            bargap=0.5,
            showlegend=False,
            uniformtext_minsize=11,
            uniformtext_mode="hide",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with dc2:
        st.markdown(sec_header("// VERDICT DISTRIBUTION"), unsafe_allow_html=True)

        verdicts: dict = {}
        for r in report:
            if r["score"] >= 40:
                v = "STRONG ALERT"
            elif r["score"] >= 30:
                v = "MEDIUM ALERT"
            elif r["score"] >= 10:
                v = "SUSPICIOUS"
            else:
                v = "CLEAR"
            verdicts[v] = verdicts.get(v, 0) + 1

        pie_color_map = {
            "STRONG ALERT": "#f06292",
            "MEDIUM ALERT": "#ff8c00",
            "SUSPICIOUS":   "#ffa726",
            "CLEAR":        "#66bb6a",
        }

        labels  = list(verdicts.keys())
        values  = list(verdicts.values())
        colors  = [pie_color_map.get(k, "#7986a8") for k in labels]

        # Custom text: "LABEL\nN (XX%)" — both count and percentage, no overlap
        total_v = sum(values)
        custom_text = [
            f"{v} ({round(v / total_v * 100)}%)" for v in values
        ]

        fig2 = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.58,
            marker=dict(
                colors=colors,
                line=dict(color="#0f1117", width=3),
            ),
            text=custom_text,
            textinfo="text",
            textposition="outside",
            textfont=dict(family="Share Tech Mono", size=10, color="#cdd6f4"),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            automargin=True,
            pull=[0.04] * len(labels),         # slight pull on each slice for clarity
        ))

        fig2.update_layout(
            paper_bgcolor="#0f1117",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                orientation="v",
                font=dict(family="Share Tech Mono", size=9, color="#cdd6f4"),
                bgcolor="#181c27",
                bordercolor="#2a3352",
                borderwidth=1,
                x=1.0,
                xanchor="left",
                y=0.5,
                yanchor="middle",
                itemsizing="constant",
                tracegroupgap=4,
            ),
            showlegend=True,
            uniformtext_minsize=9,
            uniformtext_mode="hide",
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown(sec_header("// ALL THREAT RECORDS"), unsafe_allow_html=True)

    verdict_color = {
        "CRITICAL THREAT": "#f06292",
        "SUSPICIOUS":      "#ffa726",
        "CLEAR":           "#66bb6a",
    }

    rows_html = ""
    for r in report:
        vc  = verdict_color.get(r["verdict"], "#7986a8")
        sc  = score_color(r["score"])
        path_str = " → ".join(r["path"]) if r["path"] else "—"
        rows_html += (
            f'<tr>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
            f'color:#cdd6f4">{r["user"]}</td>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
            f'color:#7986a8">{r["role"]}</td>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.85rem;'
            f'color:{sc};font-weight:700">{r["score"]}</td>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
            f'color:{vc};letter-spacing:.08em">{r["verdict"]}</td>'
            f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.72rem;'
            f'color:#7986a8">{path_str}</td>'
            f'</tr>'
        )

    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;'
        f'background:#181c27;border:1px solid #2a3352;border-radius:6px;overflow:hidden">'
        f'<thead><tr>'
        + "".join(
            f'<th style="padding:10px 14px;text-align:left;background:#1e2335;'
            f'color:#7986a8;font-family:\'Share Tech Mono\',monospace;font-size:.7rem;'
            f'letter-spacing:.12em;border-bottom:1px solid #2a3352">{h}</th>'
            for h in ["USER", "ROLE", "SCORE", "VERDICT", "PATH"]
        )
        + f'</tr></thead><tbody>{rows_html}</tbody></table>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: USER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def page_user_management():
    st.markdown(
        '<h2 style="font-family:\'Share Tech Mono\',monospace;color:#00e5ff;'
        'letter-spacing:.15em;font-size:1.25rem">👥 USER MANAGEMENT</h2>',
        unsafe_allow_html=True,
    )

    users   = get_users(engine_obj)
    devices = get_devices(engine_obj)

    # ── Registered users table ──
    st.markdown(sec_header("// REGISTERED USERS"), unsafe_allow_html=True)
    if users:
        role_colors = {
            "ADMIN": "#f06292", "SENIOR": "#ffa726",
            "OPS": "#4fc3f7",   "TELLER": "#66bb6a", "LOAN": "#ce93d8",
        }
        rows_html = ""
        for u in users:
            rc = role_colors.get(u["role"], "#7986a8")
            rows_html += (
                f'<tr>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
                f'color:#cdd6f4">{u["username"]}</td>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
                f'color:{rc}">{u["role"]}</td>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
                f'color:#7986a8">{u["machine"]}</td>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
                f'color:#4fc3f7;text-align:center">'
                f'{len(u.get("permitted_devices", []))}</td>'
                f'</tr>'
            )
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;'
            f'background:#181c27;border:1px solid #2a3352;border-radius:6px;overflow:hidden">'
            f'<thead><tr>'
            + "".join(
                f'<th style="padding:10px 14px;text-align:left;background:#1e2335;'
                f'color:#7986a8;font-family:\'Share Tech Mono\',monospace;font-size:.7rem;'
                f'letter-spacing:.12em;border-bottom:1px solid #2a3352">{h}</th>'
                for h in ["USERNAME", "ROLE", "MACHINE", "PERMITTED DEVICES"]
            )
            + f'</tr></thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No users found. Add users below or load a config file.")

    # ── Add / Delete tabs ──
    tab_add, tab_del = st.tabs(["➕  Add User", "🗑️  Delete User"])

    with tab_add:
        with st.form("add_user_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                new_uname = st.text_input("Username").upper()
                new_role  = st.selectbox("Role", ["TELLER", "OPS", "SENIOR", "ADMIN"])
            with fc2:
                machine_opts = [d["id"] for d in devices] if devices else []
                new_machine  = st.selectbox("Assigned Machine", machine_opts) if machine_opts else None
                new_perms    = st.multiselect("Permitted Devices", machine_opts)
            submitted = st.form_submit_button("+ Add User")
            if submitted:
                if not new_uname:
                    st.error("Username cannot be empty.")
                elif engine_obj and new_machine:
                    ok = engine_obj.addUser(new_uname, new_role, new_machine, new_perms)
                    if ok:
                        st.success(f"User '{new_uname}' added.")
                        st.rerun()
                    else:
                        st.error("Failed to add user — check machine/device IDs.")
                else:
                    st.warning("Engine not available or no machine selected.")

    with tab_del:
        if not users:
            st.info("No users to delete.")
        elif not engine_obj:
            st.warning("Engine not available.")
        else:
            usernames = [u["username"] for u in users]
            with st.form("del_user_form"):
                del_user = st.selectbox("Select user to delete", usernames)
                # Show user info for confirmation
                udata = next((u for u in users if u["username"] == del_user), None)
                if udata:
                    st.markdown(
                        f'<div style="background:#2b0010;border:1px solid #ff2d6b;'
                        f'border-radius:6px;padding:12px;font-family:\'Share Tech Mono\','
                        f'monospace;font-size:.78rem;margin:8px 0">'
                        f'<span style="color:#ff2d6b">⚠ You are about to delete:</span><br>'
                        f'<span style="color:#5a7099">USER </span>'
                        f'<span style="color:#c8d8f0">{udata["username"]}</span>  '
                        f'<span style="color:#5a7099">ROLE </span>'
                        f'<span style="color:#ffb800">{udata["role"]}</span>  '
                        f'<span style="color:#5a7099">MACHINE </span>'
                        f'<span style="color:#8fbbdd">{udata["machine"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                confirm = st.checkbox("I confirm I want to delete this user")
                del_submitted = st.form_submit_button("🗑️  Delete User",
                                                       type="primary")
                if del_submitted:
                    if not confirm:
                        st.error("Check the confirmation box first.")
                    else:
                        ok = engine_obj.removeUser(del_user)
                        if ok:
                            st.success(f"User '{del_user}' deleted.")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete '{del_user}'.")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: NETWORK TOPOLOGY
# ─────────────────────────────────────────────────────────────────────────────
def page_network():
    st.markdown(
        '<h2 style="font-family:\'Share Tech Mono\',monospace;color:#00e5ff;'
        'letter-spacing:.15em;font-size:1.25rem">🖥️ NETWORK TOPOLOGY</h2>',
        unsafe_allow_html=True,
    )

    devices = get_devices(engine_obj)
    edges   = get_edges(engine_obj)

    if not devices:
        st.info("No devices found. Load a config file first.")
        return

    zone_color = {"LOW": "#39ff14", "MEDIUM": "#ffb800", "HIGH": "#ff2d6b", "": "#5a7099"}

    # ── Graph layout ──
    tiers = {"BRANCH": 0, "INTERNAL": 1, "CORE": 2}
    positions: dict = {}
    tier_counts = {0: 0, 1: 0, 2: 0}
    for d in devices:
        zone = d.get("zone", "BRANCH")
        tier = tiers.get(zone, 1)
        x = tier_counts[tier]
        tier_counts[tier] += 1
        positions[d["id"]] = (x * 0.8 + tier * 0.5, tier)

    edge_traces = []
    for f, t in edges:
        if f in positions and t in positions:
            x0, y0 = positions[f]
            x1, y1 = positions[t]
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line={"width": 1.5, "color": "#1e3a5f"},
                hoverinfo="none",
            ))

    nx_list, ny_list, nc_list, nt_list, nd_list = [], [], [], [], []
    for d in devices:
        nid = d["id"]
        if nid not in positions: continue
        x, y = positions[nid]
        nx_list.append(x); ny_list.append(y)
        nc_list.append(zone_color.get(d.get("security_level", ""), "#5a7099"))
        nt_list.append(nid)
        nd_list.append(
            f"<b>{nid}</b><br>Zone: {d['zone']}<br>"
            f"Security: {d.get('security_level','?')}<br>"
            f"Required Role: {d['required_role']}"
        )

    node_trace = go.Scatter(
        x=nx_list, y=ny_list, mode="markers+text",
        marker={"size": 28, "color": nc_list,
                "line": {"width": 1.5, "color": "#0d1428"}},
        text=nt_list, textposition="top center",
        textfont={"family": "Share Tech Mono", "size": 10, "color": "#c8d8f0"},
        hovertext=nd_list, hoverinfo="text",
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        paper_bgcolor="#060b1a", plot_bgcolor="#060b1a",
        height=520, margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False,
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False,
               "range": [-0.5, 2.8]},
    )
    st.plotly_chart(fig, use_container_width=True)

    lc1, lc2, lc3 = st.columns(3)
    for col, lbl, clr in [
        (lc1, "LOW SECURITY",        "#39ff14"),
        (lc2, "MEDIUM SECURITY",     "#ffb800"),
        (lc3, "HIGH SECURITY (CORE)","#ff2d6b"),
    ]:
        col.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'font-family:\'Share Tech Mono\',monospace;font-size:.72rem;color:{clr}">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{clr}"></div>'
            f'{lbl}</div>',
            unsafe_allow_html=True,
        )

    # ── Edge list + delete tabs ──
    st.markdown(sec_header("// NODES & EDGES"), unsafe_allow_html=True)
    tab_view, tab_del_node, tab_del_edge, tab_add_edge = st.tabs([
        "📋  View Edges",
        "🗑️  Delete Node",
        "✂️  Delete Edge",
        "➕  Add Edge",
    ])

    with tab_view:
        if edges:
            rows_html = "".join(
                f'<tr>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
                f'color:#cdd6f4">{f}</td>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
                f'color:#4fc3f7">→</td>'
                f'<td style="padding:9px 14px;border-bottom:1px solid #2a3352;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
                f'color:#cdd6f4">{t}</td>'
                f'</tr>'
                for f, t in edges
            )
            st.markdown(
                f'<table style="width:100%;border-collapse:collapse;'
                f'background:#181c27;border:1px solid #2a3352;border-radius:6px;overflow:hidden">'
                f'<thead><tr>'
                f'<th style="padding:10px 14px;text-align:left;background:#1e2335;color:#7986a8;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.72rem;'
                f'letter-spacing:.12em;border-bottom:1px solid #2a3352">FROM</th>'
                f'<th style="padding:10px 14px;background:#1e2335;'
                f'border-bottom:1px solid #2a3352"></th>'
                f'<th style="padding:10px 14px;text-align:left;background:#1e2335;color:#7986a8;'
                f'font-family:\'Share Tech Mono\',monospace;font-size:.72rem;'
                f'letter-spacing:.12em;border-bottom:1px solid #2a3352">TO</th>'
                f'</tr></thead>'
                f'<tbody>{rows_html}</tbody>'
                f'</table>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="color:#7986a8;font-family:\'Share Tech Mono\',monospace;'
                'font-size:.8rem;padding:12px">No edges defined.</div>',
                unsafe_allow_html=True,
            )

    with tab_del_node:
        if not engine_obj:
            st.warning("Engine not available.")
        else:
            device_ids = [d["id"] for d in devices]
            with st.form("del_node_form"):
                del_node = st.selectbox("Select node to delete", device_ids)
                # Warn about dangling edges
                affected_edges = [(f, t) for f, t in edges if f == del_node or t == del_node]
                if affected_edges:
                    st.markdown(
                        f'<div style="background:#1a1000;border:1px solid #ffb800;'
                        f'border-radius:6px;padding:10px;font-family:\'Share Tech Mono\','
                        f'monospace;font-size:.75rem;color:#ffb800;margin:8px 0">'
                        f'⚠ Deleting this node will also remove '
                        f'{len(affected_edges)} connected edge(s).</div>',
                        unsafe_allow_html=True,
                    )
                confirm_node = st.checkbox("I confirm I want to delete this node and its edges")
                del_node_btn = st.form_submit_button("🗑️  Delete Node", type="primary")
                if del_node_btn:
                    if not confirm_node:
                        st.error("Check the confirmation box first.")
                    else:
                        ok = engine_obj.removeNode(del_node)
                        if ok:
                            st.success(f"Node '{del_node}' deleted.")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete node '{del_node}'.")

    with tab_del_edge:
        if not engine_obj:
            st.warning("Engine not available.")
        elif not edges:
            st.info("No edges to delete.")
        else:
            edge_labels = [f"{f}  →  {t}" for f, t in edges]
            with st.form("del_edge_form"):
                sel_edge_idx = st.selectbox(
                    "Select edge to delete",
                    range(len(edge_labels)),
                    format_func=lambda i: edge_labels[i],
                )
                del_edge_btn = st.form_submit_button("✂️  Delete Edge", type="primary")
                if del_edge_btn:
                    from_node, to_node = edges[sel_edge_idx]
                    ok = engine_obj.removeEdge(from_node, to_node)
                    if ok:
                        st.success(f"Edge '{from_node} → {to_node}' deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete edge.")

    with tab_add_edge:
        if not engine_obj:
            st.warning("Engine not available.")
        else:
            device_ids = [d["id"] for d in devices]
            with st.form("add_edge_form"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    from_node = st.selectbox("From Node", device_ids, key="ae_from")
                with fc2:
                    to_node = st.selectbox("To Node", device_ids, key="ae_to")
                add_edge_btn = st.form_submit_button("➕  Add Edge")
                if add_edge_btn:
                    if from_node == to_node:
                        st.error("From and To nodes cannot be the same.")
                    else:
                        ok = engine_obj.addEdge(from_node, to_node)
                        if ok:
                            st.success(f"Edge '{from_node} → {to_node}' added.")
                            st.rerun()
                        else:
                            st.error("Failed to add edge.")
# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
def page_config():
    st.markdown(
        '<h2 style="font-family:\'Share Tech Mono\',monospace;color:#4fc3f7;'
        'letter-spacing:.15em;font-size:1.25rem">⚙️ CONFIGURATION & SETTINGS</h2>',
        unsafe_allow_html=True,
    )

    # ── 1. ADD NETWORK ELEMENTS (first) ──────────────────────────────────────
    st.markdown(sec_header("// ADD NETWORK ELEMENTS"), unsafe_allow_html=True)
    tab_zone, tab_node, tab_edge = st.tabs([
        "🗺️  Add Zone", "🖥️  Add Node", "🔗  Add Edge"
    ])

    with tab_zone:
        st.markdown(
            '<p style="font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
            'color:#7986a8;margin-bottom:12px">Define a security zone (e.g. BRANCH, INTERNAL, CORE)</p>',
            unsafe_allow_html=True,
        )
        with st.form("add_zone_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                z_name = st.text_input("Zone Name (e.g. BRANCH, CORE, INTERNAL)")
            with fc2:
                z_level = st.selectbox("Security Level", ["LOW", "MEDIUM", "HIGH"])
            if st.form_submit_button("➕  Add Zone"):
                z_name = z_name.strip().upper()
                if not z_name:
                    st.error("Zone name cannot be empty.")
                elif engine_obj:
                    ok = engine_obj.addZone(z_name, z_level)
                    if ok:
                        st.success(f"Zone '{z_name}' ({z_level}) added successfully.")
                    else:
                        st.error("Failed to add zone.")
                else:
                    st.warning("Engine is offline.")

    with tab_node:
        st.markdown(
            '<p style="font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
            'color:#7986a8;margin-bottom:12px">Add a network device/node to an existing zone</p>',
            unsafe_allow_html=True,
        )
        zones = get_zones()
        zone_names = [z["name"] for z in zones]
        with st.form("add_node_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                n_id = st.text_input("Node ID (e.g. WS-OPS-01, VAULT-DB-01)")
            with fc2:
                if zone_names:
                    n_zone = st.selectbox("Zone", zone_names)
                else:
                    n_zone = st.text_input("Zone (no zones defined yet — add a zone first)")
            n_role = st.selectbox("Required Role", ["TELLER", "OPS", "LOAN", "SENIOR", "ADMIN"])
            if st.form_submit_button("➕  Add Node"):
                n_id = n_id.strip().upper()
                if not n_id:
                    st.error("Node ID cannot be empty.")
                elif engine_obj:
                    ok = engine_obj.addNode(n_id, n_zone, n_role)
                    if ok:
                        st.success(f"Node '{n_id}' added to zone '{n_zone}' (requires {n_role}).")
                    else:
                        st.error("Failed — ensure the zone exists first.")
                else:
                    st.warning("Engine is offline.")

    with tab_edge:
        st.markdown(
            '<p style="font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
            'color:#7986a8;margin-bottom:12px">Add a directed connection between two nodes</p>',
            unsafe_allow_html=True,
        )
        devices    = get_devices()
        device_ids = [d["id"] for d in devices]
        with st.form("add_edge_cfg_form"):
            if device_ids:
                fc1, fc2 = st.columns(2)
                with fc1:
                    e_from = st.selectbox("From Node", device_ids, key="cfg_ef")
                with fc2:
                    e_to   = st.selectbox("To Node",   device_ids, key="cfg_et")
            else:
                st.info("No nodes defined yet — add nodes first.")
                e_from = e_to = None
            if st.form_submit_button("➕  Add Edge"):
                if not device_ids:
                    st.error("Add nodes before adding edges.")
                elif e_from == e_to:
                    st.error("From and To nodes cannot be the same.")
                elif engine_obj:
                    ok = engine_obj.addEdge(e_from, e_to)
                    if ok:
                        st.success(f"Edge '{e_from}  →  {e_to}' added.")
                    else:
                        st.error("Failed to add edge.")
                else:
                    st.warning("Engine is offline.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. LOAD CONFIG FILE (second) ─────────────────────────────────────────
    st.markdown(sec_header("// LOAD CONFIG FILE"), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'Share Tech Mono\',monospace;font-size:.75rem;'
        'color:#7986a8;margin-bottom:10px">'
        'Upload a config.txt to load all zones, nodes, edges, users and APT signatures at once.</p>',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("Upload config.txt", type=["txt"], label_visibility="collapsed")
    if uploaded:
        st.info(f"📄 File received: **{uploaded.name}** ({uploaded.size} bytes) — loading into engine…")
        content = uploaded.read().decode()
        with open("config.txt", "w", encoding="utf-8") as f:
            f.write(content)
        try:
            import apt_engine
            new_engine = apt_engine.APTEngine()
            ok = new_engine.loadConfig("config.txt")
            if ok:
                st.session_state.engine_obj       = new_engine
                st.session_state.config_loaded    = True
                st.session_state.engine_error     = None
                st.session_state.alert_status     = "Config Loaded"
                # Reset session analysis state so old fingerprint doesn't block re-analysis
                st.session_state.session_fingerprint = ""
                st.session_state.alert_sent          = False
                summary = new_engine.getConfigSummary()
                st.success(
                    f"✔ Config file **{uploaded.name}** loaded successfully. "
                    f"Engine is now using this configuration."
                )
                st.markdown(
                    f'<div style="background:#001a06;border:1px solid #39ff14;border-radius:6px;'
                    f'padding:14px 18px;font-family:\'Share Tech Mono\',monospace;font-size:.78rem;'
                    f'margin-top:10px;line-height:2">'
                    f'<span style="color:#39ff14;font-size:.85rem;letter-spacing:.1em">CONFIG SUMMARY</span><br>'
                    f'<span style="color:#7986a8">Users&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</span> '
                    f'<span style="color:#cdd6f4">{summary.get("users", 0)}</span><br>'
                    f'<span style="color:#7986a8">Devices&nbsp;&nbsp;&nbsp;&nbsp;:</span> '
                    f'<span style="color:#cdd6f4">{summary.get("devices", 0)}</span><br>'
                    f'<span style="color:#7986a8">Zones&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</span> '
                    f'<span style="color:#cdd6f4">{summary.get("zones", 0)}</span><br>'
                    f'<span style="color:#7986a8">APT Sigs&nbsp;&nbsp;&nbsp;:</span> '
                    f'<span style="color:#cdd6f4">{summary.get("apt_signatures", 0)}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.rerun()
            else:
                st.session_state.alert_status = "Config Failed"
                st.error(
                    f"✘ Config file **{uploaded.name}** could not be parsed. "
                    f"Check the file format — zones, nodes, edges, users, and APT lines must be correct."
                )
        except Exception as e:
            st.session_state.alert_status = "Config Failed"
            st.error(f"✘ Engine error while loading config: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if "Configuration" in page:
    page_config()
elif "Network Topology" in page:
    page_network()
elif "User Management" in page:
    page_user_management()
elif "Session Analysis" in page:
    page_session_analysis()
elif "Threat Dashboard" in page:
    page_dashboard()
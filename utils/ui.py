import streamlit as st

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#172B3A; --muted:#718292; --teal:#168C88; --teal-dark:#116E6B; --line:#E4EBEF; --canvas:#F5F8FA; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:var(--canvas); }
    [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top:1.25rem; }
    .brand { display:flex; align-items:center; gap:11px; padding:4px 4px 15px 4px; }
    .brand-mark { background:linear-gradient(145deg,#1BA7A0,#126F70); color:white; width:39px;height:39px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-family:Manrope;font-size:21px;font-weight:800;box-shadow:0 5px 14px #168c8830; }
    .brand-name { font-family:Manrope;font-size:18px;font-weight:800;letter-spacing:-.5px;color:#183344; }
    .brand-sub { font-size:9px;letter-spacing:1.25px;color:#8494A0;font-weight:700;margin-top:1px; }
    .sidebar-note { color:#718292;font-size:10px;letter-spacing:1px;font-weight:700;line-height:1.9;padding:10px 4px; }
    .sidebar-note span { color:#168C88;letter-spacing:0;font-size:11px;font-weight:500; }
    h1,h2,h3 { font-family:Manrope,sans-serif !important; letter-spacing:-.6px; }
    .page-eyebrow { color:var(--teal);font-size:10px;font-weight:800;letter-spacing:1.7px;margin-bottom:7px; }
    .page-title { font-family:Manrope,sans-serif;font-size:31px;font-weight:800;color:#183344;letter-spacing:-1.1px;line-height:1.2; }
    .page-subtitle { color:#718292;font-size:14px;margin-top:7px;margin-bottom:25px; }
    .notice { background:#EAF5F4;border:1px solid #CFE8E5;border-radius:12px;padding:12px 15px;color:#416C6A;font-size:12px;margin:8px 0 20px; }
    .metric-card { background:white;border:1px solid var(--line);border-radius:15px;padding:18px 19px;min-height:126px;box-shadow:0 3px 12px #18334406; }
    .metric-label { color:#83929D;font-size:9px;font-weight:800;letter-spacing:1.1px; }
    .metric-value { color:#183344;font-family:Manrope;font-weight:800;font-size:30px;margin:8px 0 2px; }
    .metric-help { color:#8997A1;font-size:11px; }
    .section-kicker { color:var(--teal);font-size:9px;letter-spacing:1.5px;font-weight:800;margin:22px 0 5px; }
    .section-title { color:#183344;font-family:Manrope;font-weight:800;font-size:20px;letter-spacing:-.5px;margin-bottom:13px; }
    .module-card { display:flex;gap:15px;align-items:center;background:white;border:1px solid var(--line);border-radius:13px;padding:15px;margin:9px 0 5px; }
    .module-number { width:35px;height:35px;border-radius:10px;background:#EAF5F4;color:var(--teal);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;flex-shrink:0; }
    .module-title { color:#183344;font-weight:700;font-size:14px; }
    .module-desc { color:#82919B;font-size:11px;margin-top:3px; }
    .panel { background:white;border:1px solid var(--line);border-radius:14px;padding:18px;margin:9px 0 14px; }
    .panel-title { color:#183344;font-weight:800;font-size:14px;margin-bottom:12px; }
    .check-row { color:#526B78;font-size:12px;padding:7px 0;border-bottom:1px solid #F0F3F5; }
    .subtle-panel { background:#F0F7F7; }
    .subtle-panel p { color:#657D86;font-size:12px;line-height:1.6;margin-bottom:0; }
    div[data-testid="stMetric"] { background:white;border:1px solid var(--line);padding:14px 16px;border-radius:13px; }
    .stButton>button { border-radius:9px;border:1px solid #D7E5E5;background:white;color:#167D79;font-weight:600; }
    .stButton>button:hover { border-color:#168C88;color:#116E6B; }
    .stTextInput input,.stNumberInput input,.stDateInput input,.stSelectbox div[data-baseweb="select"] { border-radius:9px; }
    [data-testid="stDataFrame"] { border:1px solid var(--line);border-radius:12px;overflow:hidden; }
    footer {visibility:hidden;}
    </style>
    """, unsafe_allow_html=True)

def page_header(title, subtitle, eyebrow="THYROGUARD WORKSPACE"):
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div><div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

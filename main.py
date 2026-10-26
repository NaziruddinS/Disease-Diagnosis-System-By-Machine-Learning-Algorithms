import streamlit as st
import numpy as np
import pickle
import os
from pathlib import Path
from PIL import Image

# Resolve base directory robustly regardless of Streamlit's __file__ behaviour
BASE_DIR = Path(__file__).resolve().parent if "__file__" in dir() else Path.cwd()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diagnosify – AI Medical Diagnosis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0e1a !important;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1224 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1200px !important; }
/* Ensure sidebar toggle button is visible */
[data-testid="stSidebarNav"] { display: block !important; }

/* ── Hero ──────────────────────────────────────────────────────────────── */
.hero-section {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 40%, #1a1033 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 24px;
    padding: 3.5rem 3rem;
    margin-bottom: 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: \'\';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(139,92,246,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4);
    color: #c4b5fd;
    padding: 6px 18px;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: \'Outfit\', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 1rem;
    background: linear-gradient(135deg, #f0f4ff 0%, #a78bfa 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #b0bfd3;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Stats ─────────────────────────────────────────────────────────────── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.stat-box {
    background: rgba(15,23,42,0.9);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
}
.stat-value {
    font-family: \'Outfit\', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label { font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }

/* ── Section Titles ─────────────────────────────────────────────────────── */
.section-title {
    font-family: \'Outfit\', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #e2e8f0, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
}
.section-desc { color: #94a3b8; font-size: 0.97rem; margin-bottom: 1.5rem; font-weight: 400; }

/* ── Cards ──────────────────────────────────────────────────────────────── */
.card {
    background: linear-gradient(145deg, #131929 0%, #0f172a 100%);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 18px;
    padding: 1.8rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    height: 100%;
}
.card:hover {
    border-color: rgba(139,92,246,0.5);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px rgba(139,92,246,0.1);
}
.card-icon { font-size: 2.8rem; margin-bottom: 1rem; display: block; }
.card-title { font-family: \'Outfit\', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.6rem; }
.card-desc { font-size: 0.9rem; color: #94a3b8; line-height: 1.7; }

/* ── Pills ──────────────────────────────────────────────────────────────── */
.metric-pill {
    display: inline-block;
    background: rgba(139,92,246,0.14);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 8px;
    padding: 0.4rem 0.95rem;
    font-size: 0.82rem;
    color: #c4b5fd;
    margin: 0.25rem;
    font-weight: 500;
}

/* ── Form Panel ─────────────────────────────────────────────────────────── */
.form-panel {
    background: rgba(13,18,36,0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}

/* ── Streamlit Widget Overrides ─────────────────────────────────────────── */

/* Widget label text — the single biggest visibility fix */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
label[data-baseweb="label"],
.stNumberInput label, .stSlider label,
.stSelectbox label, .stRadio label,
.stTextInput label, .stFileUploader label {
    color: #cbd5e1 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Number / text input boxes */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
input[type="number"], input[type="text"] {
    background: rgba(22,32,54,0.95) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: border-color 0.2s !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: rgba(139,92,246,0.7) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
    outline: none !important;
}

/* Number input stepper +/- buttons */
[data-testid="stNumberInput"] button {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #a78bfa !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(99,102,241,0.3) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(22,32,54,0.95) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}

/* Radio buttons */
[data-testid="stRadio"] div[role="radiogroup"] label {
    color: #cbd5e1 !important;
    font-size: 0.9rem !important;
    padding: 0.35rem 0 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:hover { color: #a78bfa !important; }

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #7c3aed !important;
    border-color: #a78bfa !important;
}
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
}

/* Help tooltip icon */
[data-testid="stTooltipIcon"] { color: #64748b !important; }

/* Metric widget */
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.85rem !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; }

/* ── Sidebar nav buttons: transparent nav style ─────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(139,92,246,0.12) !important;
    border-color: rgba(139,92,246,0.25) !important;
    color: #c4b5fd !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Buttons (both regular and form submit) */
[data-testid="stFormSubmitButton"] > button,
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    font-family: \'Inter\', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
    letter-spacing: 0.3px;
}
[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%) !important;
    box-shadow: 0 6px 28px rgba(124,58,237,0.55) !important;
    transform: translateY(-2px) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(22,32,54,0.7) !important;
    border: 2px dashed rgba(139,92,246,0.4) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(139,92,246,0.7) !important; }
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p { color: #94a3b8 !important; }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(13,18,36,0.9) !important;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(99,102,241,0.15);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: \'Inter\', sans-serif !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    background: transparent !important;
    transition: all 0.2s !important;
    font-size: 0.9rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(139,92,246,0.2) !important;
    color: #c4b5fd !important;
    font-weight: 600 !important;
}

/* Spinner */
[data-testid="stSpinner"] p { color: #94a3b8 !important; }
[data-testid="stAlert"] { border-radius: 12px !important; }

/* ── Results ─────────────────────────────────────────────────────────────── */
.result-positive {
    background: linear-gradient(135deg, rgba(220,38,38,0.18), rgba(239,68,68,0.08));
    border: 1px solid rgba(239,68,68,0.45);
    border-radius: 16px; padding: 2rem; text-align: center;
    margin-top: 1.5rem; animation: fadeIn 0.5s ease;
}
.result-negative {
    background: linear-gradient(135deg, rgba(5,150,105,0.18), rgba(16,185,129,0.08));
    border: 1px solid rgba(16,185,129,0.45);
    border-radius: 16px; padding: 2rem; text-align: center;
    margin-top: 1.5rem; animation: fadeIn 0.5s ease;
}
.result-title { font-family: \'Outfit\', sans-serif; font-size: 1.6rem; font-weight: 700; margin-bottom: 0.5rem; }
.result-desc { font-size: 0.93rem; color: #b0bfd3; line-height: 1.7; margin-top: 0.5rem; }

/* Alzheimer result classes */
.alz-result { border-radius: 16px; padding: 2rem; text-align: center; margin-top: 1.5rem; animation: fadeIn 0.5s ease; }
.alz-Non_Demented { background: linear-gradient(135deg, rgba(5,150,105,0.18), rgba(16,185,129,0.08)); border: 1px solid rgba(16,185,129,0.45); }
.alz-Very_Mild_Demented { background: linear-gradient(135deg, rgba(217,119,6,0.18), rgba(245,158,11,0.08)); border: 1px solid rgba(245,158,11,0.45); }
.alz-Mild_Demented { background: linear-gradient(135deg, rgba(220,38,38,0.15), rgba(251,146,60,0.08)); border: 1px solid rgba(251,146,60,0.45); }
.alz-Moderate_Demented { background: linear-gradient(135deg, rgba(127,29,29,0.25), rgba(220,38,38,0.08)); border: 1px solid rgba(220,38,38,0.55); }

/* ── Info Box ────────────────────────────────────────────────────────────── */
.info-box {
    background: rgba(99,102,241,0.1);
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 1.1rem 1.5rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #b0bfd3;
    line-height: 1.7;
}
.info-box strong { color: #e2e8f0; }

/* ── Divider ─────────────────────────────────────────────────────────────── */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), transparent);
    margin: 2rem 0;
}



/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.7); }

@keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade { animation: fadeIn 0.6s ease forwards; }

</style>
""", unsafe_allow_html=True)


# ─── Model Loaders ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_diabetes_model():
    model_path = BASE_DIR / "models" / "diabetes_model.sav"
    with open(model_path, "rb") as f:
        return pickle.load(f)

@st.cache_resource(show_spinner=False)
def load_alzheimer_model():
    try:
        from tensorflow.keras.models import load_model
        model_path = BASE_DIR / "models" / "alzheimer_cnn_model.h5"
        return load_model(str(model_path))
    except Exception:
        return None


# ─── Sidebar Navigation ───────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

NAV_PAGES = [
    ("🏠", "Home"),
    ("🩸", "Diabetes Prediction"),
    ("🧠", "Alzheimer's Detection"),
    ("⚖️", "BMI Calculator"),
    ("ℹ️", "About"),
]

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1.2rem;margin-bottom:1.2rem;border-bottom:1px solid rgba(148,163,184,0.12);">
        <span style="font-size:2.8rem;display:block;margin-bottom:0.4rem;">🩺</span>
        <div style="font-family:'Outfit',sans-serif;font-size:1.5rem;font-weight:700;
                    background:linear-gradient(135deg,#f0f4ff,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">Diagnosify</div>
        <div style="font-size:0.72rem;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-top:0.2rem;">
            AI-Powered Diagnostics
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='margin-bottom:0.5rem;font-size:0.7rem;color:#475569;"
        "text-transform:uppercase;letter-spacing:1.2px;font-weight:600;"
        "padding-left:0.25rem;'>Navigation</div>",
        unsafe_allow_html=True
    )

    for icon, label in NAV_PAGES:
        full_label = f"{icon} {label}"
        if st.button(f"{icon}  {label}", key=f"nav_{label}"):
            st.session_state.page = full_label
            st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:1rem;background:rgba(139,92,246,0.08);border-radius:12px;
                border:1px solid rgba(139,92,246,0.2);">
        <div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:1px;margin-bottom:0.7rem;font-weight:600;">Models Active</div>
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
            <span style="width:7px;height:7px;background:#10b981;border-radius:50%;
                         display:inline-block;flex-shrink:0;box-shadow:0 0 6px #10b981;"></span>
            <span style="font-size:0.82rem;color:#94a3b8;">Diabetes SVM</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;">
            <span style="width:7px;height:7px;background:#10b981;border-radius:50%;
                         display:inline-block;flex-shrink:0;box-shadow:0 0 6px #10b981;"></span>
            <span style="font-size:0.82rem;color:#94a3b8;">Alzheimer's CNN</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:2rem;padding-top:1rem;font-size:0.7rem;color:#475569;
               text-align:center;border-top:1px solid rgba(148,163,184,0.1);'>
        ⚠️ For research use only.<br>Not a substitute for clinical diagnosis.
    </div>
    """, unsafe_allow_html=True)

page = st.session_state.page


# ══════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown("""
    <div class="hero-section animate-fade">
        <div class="hero-badge">🔬 AI-Powered Medical Diagnostics</div>
        <h1 class="hero-title">Diagnose Smarter.<br>Live Healthier.</h1>
        <p class="hero-subtitle">
            Diagnosify uses state-of-the-art machine learning to screen for
            Diabetes and Alzheimer's Disease — fast, accurate, and accessible
            right in your browser.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-row animate-fade">
        <div class="stat-box">
            <div class="stat-value">92%</div>
            <div class="stat-label">Diabetes Accuracy</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">96%</div>
            <div class="stat-label">Alzheimer Accuracy</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">3</div>
            <div class="stat-label">AI Tools</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title" style="margin:2rem 0 0.4rem;">What can Diagnosify do?</div>
    <div class="section-desc">Choose a diagnostic tool from the sidebar to get started.</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    features = [
        ("🩸", "Diabetes Prediction", "SVM-based model trained on the PIMA dataset. Enter 8 clinical measurements for an instant risk assessment.", ["SVM", "8 Features", "~92% Acc"]),
        ("🧠", "Alzheimer's Detection", "CNN analyzes MRI brain scans and classifies dementia severity across 4 stages with confidence scores.", ["CNN", "MRI Input", "4 Classes"]),
        ("⚖️", "BMI Calculator", "Instantly calculate your Body Mass Index from height and weight, with category classification and health guidance.", ["BMI", "kg & cm", "Instant"]),
    ]
    for col, (icon, title, desc, pills) in zip([col1, col2, col3], features):
        with col:
            pill_html = "".join(f'<span class="metric-pill">{p}</span>' for p in pills)
            st.markdown(f"""
            <div class="card animate-fade">
                <span class="card-icon">{icon}</span>
                <div class="card-title">{title}</div>
                <div class="card-desc">{desc}</div>
                <div style="margin-top:1rem;">{pill_html}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='styled-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='margin-bottom:1.5rem;'>How It Works</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    steps = [
        ("1️⃣", "Select a Tool", "Choose a diagnostic tool from the sidebar navigation."),
        ("2️⃣", "Enter Your Data", "Provide clinical parameters or upload an MRI scan image."),
        ("3️⃣", "Get Results", "Receive instant AI-powered predictions with explanations."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:1.5rem 1rem;background:rgba(15,23,42,0.6);border:1px solid rgba(148,163,184,0.1);border-radius:16px;">
                <div style="font-size:2rem;margin-bottom:0.8rem;">{icon}</div>
                <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:1.05rem;color:#f1f5f9;margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.86rem;color:#64748b;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='styled-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        ⚠️ <strong>Disclaimer:</strong> Diagnosify is an AI screening tool for educational and research
        purposes only. Results do <em>not</em> replace professional medical advice, diagnosis, or treatment.
        Always consult a qualified healthcare provider.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DIABETES PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🩸 Diabetes Prediction":
    st.markdown("""
    <div class="section-title animate-fade">🩸 Diabetes Prediction</div>
    <div class="section-desc">Enter patient clinical measurements to get an AI-powered diabetes risk assessment.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span class="metric-pill">📊 PIMA Indian Dataset</span>
        <span class="metric-pill">⚙️ SVM – Linear Kernel</span>
        <span class="metric-pill">🎯 ~92% Accuracy</span>
        <span class="metric-pill">📐 8 Features</span>
    </div>
    """, unsafe_allow_html=True)

    tab_pred, tab_about = st.tabs(["🔬 Predict", "📖 Model Info"])

    with tab_pred:
        with st.form("diabetes_form"):
            st.markdown("""
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:600;color:#e2e8f0;margin-bottom:1.2rem;">
                Patient Clinical Parameters
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="large")
            with col1:
                pregnancies = st.number_input("🤰 Number of Pregnancies", min_value=0, max_value=20, value=1, step=1, help="Total number of pregnancies")
                glucose = st.number_input("🍬 Glucose (mg/dL)", min_value=0, max_value=300, value=117, step=1, help="Plasma glucose — 2-hour oral glucose tolerance test")
                blood_pressure = st.number_input("🩺 Blood Pressure (mm Hg)", min_value=0, max_value=200, value=72, step=1, help="Diastolic blood pressure")
                skin_thickness = st.number_input("📏 Skin Thickness (mm)", min_value=0, max_value=100, value=23, step=1, help="Triceps skin fold thickness")
            with col2:
                insulin = st.number_input("💉 Insulin (µU/mL)", min_value=0, max_value=1000, value=0, step=1, help="2-hour serum insulin")
                bmi = st.number_input("⚖️ BMI (kg/m²)", min_value=0.0, max_value=70.0, value=32.0, step=0.1, help="Body mass index")
                dpf = st.number_input("🧬 Diabetes Pedigree Function", min_value=0.000, max_value=3.000, value=0.352, step=0.001, format="%.3f", help="Genetic predisposition score")
                age = st.number_input("🎂 Age (years)", min_value=1, max_value=120, value=33, step=1)

            submitted = st.form_submit_button("🔍 Predict Diabetes Risk")

        if submitted:
            try:
                model = load_diabetes_model()
                input_arr = np.array([[pregnancies, glucose, blood_pressure, skin_thickness,
                                       insulin, bmi, dpf, age]])
                pred = model.predict(input_arr)
                if pred[0] == 1:
                    st.markdown("""
                    <div class="result-positive animate-fade">
                        <div style="font-size:3rem;margin-bottom:0.5rem;">⚠️</div>
                        <div class="result-title" style="color:#f87171;">Diabetic Risk Detected</div>
                        <div class="result-desc">
                            The model predicts a <strong style="color:#f87171;">positive</strong> result for diabetes
                            based on the provided parameters. Please consult a qualified physician for further clinical evaluation and testing.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="result-negative animate-fade">
                        <div style="font-size:3rem;margin-bottom:0.5rem;">✅</div>
                        <div class="result-title" style="color:#34d399;">Low Diabetes Risk</div>
                        <div class="result-desc">
                            The model predicts a <strong style="color:#34d399;">negative</strong> result for diabetes.
                            Maintain a healthy lifestyle with balanced diet and regular exercise. Continue routine check-ups.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ Prediction error: {e}")

    with tab_about:
        st.markdown("""
        <div class="form-panel">
            <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">Diabetes SVM Model</div>
            <p style="color:#94a3b8;line-height:1.8;">
                A <strong style="color:#a78bfa;">Support Vector Machine</strong> with a linear kernel trained on the
                <strong style="color:#a78bfa;">PIMA Indian Diabetes Dataset</strong> (768 patients, 8 clinical features, binary output).
            </p>
            <div style="margin-top:1.2rem;">
                <div style="font-weight:600;color:#cbd5e1;margin-bottom:0.7rem;">Input Features:</div>
                <table style="width:100%;border-collapse:collapse;font-size:0.87rem;">
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.15);">
                        <th style="text-align:left;padding:0.5rem 0.7rem;color:#6366f1;font-weight:600;">Feature</th>
                        <th style="text-align:left;padding:0.5rem 0.7rem;color:#6366f1;font-weight:600;">Description</th>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Pregnancies</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Number of pregnancies</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Glucose</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Plasma glucose (2-hr OGTT)</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Blood Pressure</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Diastolic blood pressure (mm Hg)</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Skin Thickness</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Triceps skin fold (mm)</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Insulin</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">2-hour serum insulin (µU/mL)</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">BMI</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Body mass index (kg/m²)</td></tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,0.08);"><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Diabetes Pedigree</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Family history genetic score</td></tr>
                    <tr><td style="padding:0.5rem 0.7rem;color:#e2e8f0;">Age</td><td style="padding:0.5rem 0.7rem;color:#94a3b8;">Age in years</td></tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ALZHEIMER'S DETECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Alzheimer's Detection":
    st.markdown("""
    <div class="section-title animate-fade">🧠 Alzheimer's Detection</div>
    <div class="section-desc">Upload an MRI brain scan to classify Alzheimer's disease severity.</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span class="metric-pill">🖼️ MRI Brain Scans</span>
        <span class="metric-pill">⚙️ CNN (TF/Keras)</span>
        <span class="metric-pill">🎯 ~96% Accuracy</span>
        <span class="metric-pill">📂 4 Classes</span>
    </div>
    """, unsafe_allow_html=True)

    # Class summary cards
    col1, col2, col3, col4 = st.columns(4, gap="small")
    class_cards = [
        ("💚", "Non-Demented", "#10b981", "No Alzheimer's signs"),
        ("💛", "Very Mild", "#f59e0b", "Earliest detectable stage"),
        ("🟠", "Mild", "#f97316", "Clear cognitive decline"),
        ("🔴", "Moderate", "#ef4444", "Significant impairment"),
    ]
    for col, (icon, label, color, desc) in zip([col1, col2, col3, col4], class_cards):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem 0.6rem;background:rgba(15,23,42,0.6);border:1px solid rgba(148,163,184,0.1);border-radius:14px;margin-bottom:1rem;">
                <div style="font-size:1.4rem;">{icon}</div>
                <div style="font-weight:700;font-size:0.85rem;color:{color};margin:0.3rem 0;">{label}</div>
                <div style="font-size:0.73rem;color:#64748b;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    tab_pred, tab_about = st.tabs(["🔬 Analyze", "📖 Model Info"])

    with tab_pred:
        st.markdown("""
        <div class="info-box">
            📌 <strong>Instructions:</strong> Upload a grayscale or color MRI brain scan (JPG/PNG).
            The image is automatically resized to 128×128 pixels. For best results, use a coronal or axial MRI slice.
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload MRI Brain Scan", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

        if uploaded_file is not None:
            col_img, col_res = st.columns([1, 1.5], gap="large")

            with col_img:
                image_pil = Image.open(uploaded_file)
                st.markdown("<div style='font-size:0.84rem;color:#64748b;margin-bottom:0.4rem;'>Uploaded MRI Scan</div>", unsafe_allow_html=True)
                st.image(image_pil, use_column_width=True)
                st.markdown(f"""
                <div style="font-size:0.76rem;color:#475569;margin-top:0.3rem;text-align:center;">
                    {uploaded_file.name} · {image_pil.size[0]}×{image_pil.size[1]}px
                </div>
                """, unsafe_allow_html=True)

            with col_res:
                if st.button("🧠 Analyze MRI Scan"):
                    model = load_alzheimer_model()
                    if model is None:
                        st.error("Could not load the CNN model. Ensure TensorFlow is installed and `models/alzheimer_cnn_model.h5` exists.")
                    else:
                        with st.spinner("Analyzing MRI scan with CNN..."):
                            try:
                                # Preprocess — grayscale, 128×128 (matching training)
                                img = image_pil.convert("L").resize((128, 128))
                                img_array = np.array(img) / 255.0
                                img_array = img_array.reshape(-1, 128, 128, 1)

                                prediction = model.predict(img_array)
                                pred_idx = int(np.argmax(prediction[0]))
                                confidence = float(prediction[0][pred_idx]) * 100

                                class_keys = ["Non_Demented", "Very_Mild_Demented", "Mild_Demented", "Moderate_Demented"]
                                display_map = {
                                    "Non_Demented": "Non-Demented",
                                    "Very_Mild_Demented": "Very Mild Demented",
                                    "Mild_Demented": "Mild Demented",
                                    "Moderate_Demented": "Moderate Demented",
                                }
                                desc_map = {
                                    "Non_Demented": "No significant Alzheimer's pathology detected. Brain scan appears within normal limits.",
                                    "Very_Mild_Demented": "Very mild cognitive impairment detected. Early monitoring and lifestyle changes are advised.",
                                    "Mild_Demented": "Mild dementia detected. Consult a neurologist promptly for clinical evaluation.",
                                    "Moderate_Demented": "Moderate dementia detected. Immediate medical consultation is strongly recommended.",
                                }
                                emoji_map = {"Non_Demented": "✅", "Very_Mild_Demented": "⚠️", "Mild_Demented": "🟠", "Moderate_Demented": "🔴"}
                                color_map = {"Non_Demented": "#34d399", "Very_Mild_Demented": "#fbbf24", "Mild_Demented": "#fb923c", "Moderate_Demented": "#f87171"}

                                pred_key = class_keys[pred_idx]
                                st.markdown(f"""
                                <div class="alz-result alz-{pred_key} animate-fade">
                                    <div style="font-size:2.5rem;margin-bottom:0.6rem;">{emoji_map[pred_key]}</div>
                                    <div class="result-title" style="color:{color_map[pred_key]};">{display_map[pred_key]}</div>
                                    <div style="margin:0.8rem 0;">
                                        <div style="font-size:0.8rem;color:#64748b;margin-bottom:0.3rem;">Confidence</div>
                                        <div style="font-size:2rem;font-weight:800;font-family:'Outfit',sans-serif;color:{color_map[pred_key]};">{confidence:.1f}%</div>
                                    </div>
                                    <div class="result-desc">{desc_map[pred_key]}</div>
                                </div>
                                """, unsafe_allow_html=True)

                                # Probability bars
                                st.markdown("<div style='margin-top:1.5rem;font-size:0.84rem;color:#64748b;font-weight:600;margin-bottom:0.6rem;'>Class Probabilities</div>", unsafe_allow_html=True)
                                for i, ck in enumerate(class_keys):
                                    prob = float(prediction[0][i]) * 100
                                    bar_color = color_map[ck]
                                    st.markdown(f"""
                                    <div style="display:flex;align-items:center;margin-bottom:0.5rem;gap:0.6rem;">
                                        <span style="font-size:0.8rem;color:#94a3b8;min-width:130px;">{display_map[ck]}</span>
                                        <div style="flex:1;background:rgba(30,41,59,0.8);border-radius:99px;height:6px;overflow:hidden;">
                                            <div style="width:{prob:.1f}%;height:100%;background:{bar_color};border-radius:99px;transition:width 0.5s;"></div>
                                        </div>
                                        <span style="font-size:0.8rem;color:#a78bfa;font-weight:600;min-width:38px;text-align:right;">{prob:.1f}%</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                            except Exception as e:
                                st.error(f"Analysis error: {e}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;background:rgba(15,23,42,0.4);border:2px dashed rgba(139,92,246,0.2);border-radius:18px;">
                <div style="font-size:3rem;margin-bottom:1rem;">🧠</div>
                <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:600;color:#64748b;margin-bottom:0.4rem;">No Image Uploaded</div>
                <div style="font-size:0.85rem;color:#475569;">Upload an MRI brain scan above to begin analysis</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_about:
        st.markdown("""
        <div class="form-panel">
            <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">Alzheimer's CNN Model</div>
            <p style="color:#94a3b8;line-height:1.8;">
                A <strong style="color:#a78bfa;">CNN</strong> trained on 6,400+ MRI brain images across four dementia classes.
                Built with <strong style="color:#a78bfa;">TensorFlow/Keras</strong>, using Conv2D, MaxPooling, and Dropout layers.
            </p>
            <div style="margin-top:1.5rem;display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.9rem;">
                    <div style="font-weight:600;color:#34d399;margin-bottom:0.3rem;">💚 Non-Demented</div>
                    <div style="font-size:0.82rem;color:#64748b;">No dementia. Normal cognitive function.</div>
                </div>
                <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:0.9rem;">
                    <div style="font-weight:600;color:#fbbf24;margin-bottom:0.3rem;">💛 Very Mild Demented</div>
                    <div style="font-size:0.82rem;color:#64748b;">Earliest detectable memory lapses.</div>
                </div>
                <div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.2);border-radius:10px;padding:0.9rem;">
                    <div style="font-weight:600;color:#fb923c;margin-bottom:0.3rem;">🟠 Mild Demented</div>
                    <div style="font-size:0.82rem;color:#64748b;">Noticeable cognitive decline, daily impact.</div>
                </div>
                <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.9rem;">
                    <div style="font-weight:600;color:#f87171;margin-bottom:0.3rem;">🔴 Moderate Demented</div>
                    <div style="font-size:0.82rem;color:#64748b;">Severe impairment, needs medical attention.</div>
                </div>
            </div>
            <div style="margin-top:1.5rem;font-size:0.87rem;color:#64748b;line-height:2;">
                <strong style="color:#cbd5e1;">Architecture:</strong>
                Conv2D → MaxPooling → Dropout → Dense → Softmax<br>
                <strong style="color:#cbd5e1;">Input:</strong> 128 × 128 grayscale MRI scans<br>
                <strong style="color:#cbd5e1;">Training:</strong> EarlyStopping, ImageDataGenerator augmentation
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  BMI CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ BMI Calculator":
    st.markdown("""
    <div class="section-title animate-fade">⚖️ BMI Calculator</div>
    <div class="section-desc">Calculate your Body Mass Index and understand your weight category.</div>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([1, 1], gap="large")

    with col_form:
        with st.form("bmi_form"):
            st.markdown("""
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:600;color:#e2e8f0;margin-bottom:1.2rem;">
                Your Measurements
            </div>
            """, unsafe_allow_html=True)

            weight = st.number_input("⚖️ Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.5)
            height = st.number_input("📏 Height (cm)", min_value=50.0, max_value=300.0, value=170.0, step=0.5)
            calc = st.form_submit_button("Calculate BMI")

        if calc:
            bmi = weight / (height / 100) ** 2
            if bmi < 18.5:
                cat, cat_color, cat_emoji = "Underweight", "#60a5fa", "💙"
                tip = "Consider a nutrient-rich diet to reach a healthy weight. Consult a nutritionist."
            elif bmi < 25:
                cat, cat_color, cat_emoji = "Normal Weight", "#34d399", "💚"
                tip = "Great job! Maintain your healthy weight with a balanced diet and regular exercise."
            elif bmi < 30:
                cat, cat_color, cat_emoji = "Overweight", "#fbbf24", "💛"
                tip = "Consider moderate dietary changes and increasing physical activity."
            else:
                cat, cat_color, cat_emoji = "Obese", "#f87171", "❤️"
                tip = "Please consult a healthcare provider for personalized guidance on weight management."

            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(148,163,184,0.12);border-radius:20px;padding:2rem;text-align:center;margin-top:1rem;animation:fadeIn 0.5s ease;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">{cat_emoji}</div>
                <div style="font-size:3.5rem;font-weight:800;font-family:'Outfit',sans-serif;color:{cat_color};line-height:1;">{bmi:.1f}</div>
                <div style="font-size:0.82rem;color:#64748b;margin:0.3rem 0 0.8rem;">BMI Score</div>
                <div style="font-family:'Outfit',sans-serif;font-size:1.3rem;font-weight:700;color:{cat_color};margin-bottom:0.8rem;">{cat}</div>
                <div style="font-size:0.87rem;color:#94a3b8;line-height:1.6;">{tip}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        st.markdown("""
        <div class="form-panel">
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">BMI Categories</div>
            <div style="display:flex;flex-direction:column;gap:0.7rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem;background:rgba(96,165,250,0.1);border-radius:10px;border:1px solid rgba(96,165,250,0.2);">
                    <span style="font-size:0.9rem;color:#93c5fd;">💙 Underweight</span>
                    <span style="font-size:0.87rem;color:#64748b;">BMI &lt; 18.5</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem;background:rgba(52,211,153,0.1);border-radius:10px;border:1px solid rgba(52,211,153,0.2);">
                    <span style="font-size:0.9rem;color:#6ee7b7;">💚 Normal Weight</span>
                    <span style="font-size:0.87rem;color:#64748b;">18.5 – 24.9</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem;background:rgba(251,191,36,0.1);border-radius:10px;border:1px solid rgba(251,191,36,0.2);">
                    <span style="font-size:0.9rem;color:#fde68a;">💛 Overweight</span>
                    <span style="font-size:0.87rem;color:#64748b;">25 – 29.9</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem;background:rgba(248,113,113,0.1);border-radius:10px;border:1px solid rgba(248,113,113,0.2);">
                    <span style="font-size:0.9rem;color:#fca5a5;">❤️ Obese</span>
                    <span style="font-size:0.87rem;color:#64748b;">BMI ≥ 30</span>
                </div>
            </div>
            <div style="margin-top:1.2rem;">
                <div class="info-box" style="font-size:0.82rem;">
                    BMI is a general indicator. It does not account for muscle mass, bone density, age, or sex.
                    Always consult a healthcare professional for a complete assessment.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ABOUT PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown("""
    <div class="hero-section animate-fade">
        <div class="hero-badge">About This Project</div>
        <h1 class="hero-title" style="font-size:2.6rem;">Built with ❤️ & AI</h1>
        <p class="hero-subtitle">
            Diagnosify is an AI-powered medical screening platform for educational
            and research use, combining classical ML and deep learning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div class="form-panel">
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">🛠️ Technology Stack</div>
            <div style="font-size:0.88rem;color:#94a3b8;line-height:2.2;">
                🐍 <strong style="color:#e2e8f0;">Python 3.11</strong> — Core language<br>
                🎈 <strong style="color:#e2e8f0;">Streamlit</strong> — Web UI framework<br>
                🤖 <strong style="color:#e2e8f0;">Scikit-learn</strong> — Diabetes SVM model<br>
                🧠 <strong style="color:#e2e8f0;">TensorFlow / Keras</strong> — Alzheimer's CNN<br>
                📊 <strong style="color:#e2e8f0;">NumPy</strong> — Numerical computation<br>
                🖼️ <strong style="color:#e2e8f0;">Pillow</strong> — MRI image processing
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="form-panel">
            <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">📂 Datasets</div>
            <div style="font-size:0.88rem;color:#94a3b8;line-height:2.2;">
                🩸 <strong style="color:#e2e8f0;">PIMA Indian Diabetes Dataset</strong><br>
                &nbsp;&nbsp;&nbsp;&nbsp;768 samples · 8 features · Binary<br><br>
                🧠 <strong style="color:#e2e8f0;">Alzheimer's MRI Dataset</strong><br>
                &nbsp;&nbsp;&nbsp;&nbsp;6,400 images · 4 classes<br>
                &nbsp;&nbsp;&nbsp;&nbsp;Non / Very Mild / Mild / Moderate
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="form-panel">
        <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">⚠️ Medical Disclaimer</div>
        <p style="color:#94a3b8;line-height:1.8;font-size:0.9rem;">
            Diagnosify is designed <strong style="color:#f1f5f9;">strictly for educational and research purposes</strong>.
            The AI predictions are based on ML models trained on limited datasets and should
            <strong style="color:#f87171;">NOT</strong> be used as a substitute for professional medical advice,
            diagnosis, or treatment. Always consult a licensed healthcare provider for any medical decisions.
            The developers assume no liability for clinical decisions made using this tool.
        </p>
    </div>
    """, unsafe_allow_html=True)

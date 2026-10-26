"""
AI School Analytics — Teacher Dashboard
Matches the design of the AI Report Generator website exactly.
Run with: streamlit run dashboard.py
"""

import os
import glob
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Force fresh state on every load
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.cache_data.clear()

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Report Generator — Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── EXACT DESIGN TOKENS FROM index.html ────────────────────────────────────
BG       = "#f7f5f2"
SURFACE  = "#ffffff"
SURFACE2 = "#f0ede8"
BORDER   = "#e2ddd7"
BORDER2  = "#cdc7bf"
SAGE     = "#5a7a5e"
SAGE_LT  = "#eaf1eb"
SAGE_MID = "#c5d9c7"
AMBER    = "#c47b2b"
AMBER_LT = "#fdf3e7"
ROSE     = "#b5534a"
ROSE_LT  = "#fceeed"
INK      = "#2d2926"
INK2     = "#5c544c"
MUTED    = "#9a9189"
SHADOW   = "rgba(45,41,38,0.06)"
SHADOW2  = "rgba(45,41,38,0.12)"

# Chart layout matching the warm paper aesthetic
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=INK2, size=12),
    margin=dict(l=0, r=8, t=8, b=0),
    showlegend=False,
)
AX = dict(
    showgrid=True, gridcolor=BORDER,
    color=MUTED, tickfont=dict(color=MUTED, size=11),
    linecolor=BORDER, zeroline=False,
)
AX_NOGRID = {**AX, "showgrid": False}

# ── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"], .stApp {{
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background-color: {BG} !important;
  color: {INK} !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* ── HIDE SIDEBAR TOGGLE BUTTON PERMANENTLY ── */
[data-testid="collapsedControl"] {{ display: none !important; }}
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
button[kind="header"] {{ display: none !important; }}
.st-emotion-cache-czk5ss {{ display: none !important; }}
section[data-testid="stSidebar"] > div:first-child > div > div > div > div > button {{
  display: none !important;
}}

/* Paper texture */
.stApp::before {{
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='400' height='400' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 0;
}}

/* ── SIDEBAR — matches nav style ── */
[data-testid="stSidebar"] {{
  background: {SURFACE} !important;
  border-right: 1px solid {BORDER} !important;
}}

[data-testid="stSidebar"] * {{ color: {INK} !important; }}

[data-testid="stSidebar"] .stRadio label {{
  font-size: 13px !important;
  color: {INK2} !important;
  font-weight: 500 !important;
  padding: 6px 0 !important;
}}

[data-testid="stSidebar"] hr {{
  border-color: {BORDER} !important;
}}

/* File uploader */
[data-testid="stFileUploader"] section {{
  background: {SURFACE2} !important;
  border: 1.5px dashed {BORDER2} !important;
  border-radius: 12px !important;
  transition: all .25s !important;
}}

[data-testid="stFileUploader"] section:hover {{
  border-color: {SAGE} !important;
  background: {SAGE_LT} !important;
}}

[data-testid="stFileUploaderDropzoneInstructions"] {{
  color: {MUTED} !important;
}}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {{
  background: {SURFACE2} !important;
  border: 1.5px solid {BORDER} !important;
  border-radius: 8px !important;
  color: {INK} !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

[data-testid="stSelectbox"] > div > div:focus-within {{
  border-color: {SAGE} !important;
  box-shadow: 0 0 0 3px rgba(90,122,94,0.1) !important;
}}

/* Radio buttons */
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
  font-size: 13px !important;
  color: {INK2} !important;
}}

/* Download button — matches submit-btn style */
.stDownloadButton > button {{
  background: {SAGE} !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 12px 18px !important;
  transition: all .25s !important;
  width: 100% !important;
}}

.stDownloadButton > button:hover {{
  background: #4a6a4e !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 16px rgba(90,122,94,0.25) !important;
}}

/* Success / info / warning / error */
[data-testid="stAlert"] {{
  border-radius: 10px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 13px !important;
}}

div[data-baseweb="notification"][kind="positive"] {{
  background: {SAGE_LT} !important;
  border: 1px solid {SAGE_MID} !important;
  color: {SAGE} !important;
  border-radius: 10px !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
  background: transparent !important;
  gap: 4px !important;
  border-bottom: 1px solid {BORDER} !important;
}}

.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  border-radius: 8px 8px 0 0 !important;
  color: {MUTED} !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 8px 16px !important;
}}

.stTabs [aria-selected="true"] {{
  color: {INK} !important;
  border-bottom: 2px solid {SAGE} !important;
  background: {SURFACE} !important;
}}

/* ── CUSTOM COMPONENTS ── */

/* NAV — matches index.html .nav */
.dash-nav {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0 16px;
  border-bottom: 1px solid {BORDER};
  margin-bottom: 32px;
}}

.dash-nav-brand {{
  display: flex; align-items: center; gap: 10px;
}}

.dash-nav-icon {{
  width: 34px; height: 34px;
  background: {SAGE};
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}}

.dash-nav-name {{
  font-family: 'Lora', serif;
  font-size: 17px; font-weight: 600;
  color: {INK}; letter-spacing: -0.01em;
}}

.dash-nav-status {{
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: {SAGE}; font-weight: 500;
}}

.dash-dot {{
  width: 7px; height: 7px;
  border-radius: 50%; background: {SAGE};
  animation: breathe 3s ease-in-out infinite;
}}

@keyframes breathe {{
  0%, 100% {{ opacity: 1; transform: scale(1); }}
  50%       {{ opacity: 0.5; transform: scale(0.85); }}
}}

/* PAGE TITLE — matches .page-title */
.page-eyebrow {{
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: {SAGE}; margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}}

.page-eyebrow::before {{
  content: '';
  width: 20px; height: 1.5px;
  background: {SAGE}; border-radius: 1px;
}}

.page-h1 {{
  font-family: 'Lora', serif;
  font-size: 28px; font-weight: 600;
  line-height: 1.2; letter-spacing: -0.02em;
  color: {INK}; margin-bottom: 6px;
}}

.page-h1 em {{ font-style: italic; color: {SAGE}; }}

.page-sub {{
  font-size: 14px; color: {INK2};
  font-weight: 400; line-height: 1.65;
  margin-bottom: 28px;
}}

/* CARD — matches .form-card */
.card {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 16px;
  box-shadow: 0 4px 24px {SHADOW}, 0 1px 2px {SHADOW};
  overflow: hidden;
  margin-bottom: 20px;
}}

.card-section {{
  padding: 22px 26px;
  border-bottom: 1px solid {BORDER};
}}

.card-section:last-child {{ border-bottom: none; }}

/* SECTION LABEL — matches .section-label */
.section-label {{
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
  color: {MUTED}; margin-bottom: 16px;
}}

.section-num {{
  width: 20px; height: 20px;
  background: {INK}; color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}}

/* KPI cards — matches .stat */
.kpi-grid {{
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;
  margin-bottom: 24px;
}}

.kpi {{
  background: {SURFACE2};
  border: 1px solid {BORDER};
  border-radius: 10px; padding: 14px 16px;
  transition: box-shadow .2s;
}}

.kpi:hover {{ box-shadow: 0 4px 12px {SHADOW2}; }}

.kpi-label {{
  font-size: 10px; font-weight: 600;
  letter-spacing: 0.07em; text-transform: uppercase;
  color: {MUTED}; margin-bottom: 5px;
}}

.kpi-val {{
  font-family: 'Lora', serif;
  font-size: 24px; font-weight: 600; color: {INK}; line-height: 1;
}}

.kpi-val.sage  {{ color: {SAGE}; }}
.kpi-val.amber {{ color: {AMBER}; }}
.kpi-val.sm    {{ font-size: 15px; padding-top: 5px; }}

/* Leaderboard row */
.lb-row {{
  display: flex; align-items: center; gap: 14px;
  padding: 12px 16px;
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 10px; margin-bottom: 7px;
  transition: border-color .2s, box-shadow .2s;
}}

.lb-row:hover {{
  border-color: {SAGE_MID};
  box-shadow: 0 2px 8px {SHADOW};
}}

.lb-rank  {{ font-size: 18px; width: 28px; text-align: center; flex-shrink: 0; }}
.lb-name  {{ font-weight: 600; color: {INK}; flex: 1; font-size: 14px; }}
.lb-score {{
  font-family: 'Lora', serif;
  font-size: 18px; color: {SAGE};
  background: {SAGE_LT};
  border-radius: 6px; padding: 3px 12px;
}}

/* Needs help row */
.help-row {{
  display: flex; align-items: center; gap: 14px;
  padding: 12px 16px;
  background: {AMBER_LT};
  border: 1px solid rgba(196,123,43,0.2);
  border-radius: 10px; margin-bottom: 7px;
}}

.help-name  {{ font-weight: 600; color: {INK}; flex: 1; font-size: 14px; }}
.help-score {{
  font-family: 'Lora', serif;
  font-size: 18px; color: {AMBER};
  background: {SURFACE};
  border-radius: 6px; padding: 3px 12px;
}}

/* Tags — matches automation log items */
.tag-s {{
  display: inline-block;
  background: {SAGE_LT}; color: {SAGE};
  border: 1px solid {SAGE_MID};
  border-radius: 4px; padding: 2px 8px;
  font-size: 11px; font-weight: 500; margin: 2px;
}}

.tag-w {{
  display: inline-block;
  background: {AMBER_LT}; color: {AMBER};
  border: 1px solid rgba(196,123,43,0.3);
  border-radius: 4px; padding: 2px 8px;
  font-size: 11px; font-weight: 500; margin: 2px;
}}

/* Student profile card */
.profile-wrap {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 16px;
  box-shadow: 0 4px 24px {SHADOW};
  overflow: hidden;
  margin-bottom: 20px;
}}

.profile-header {{
  padding: 22px 26px;
  border-bottom: 1px solid {BORDER};
  display: flex; align-items: center; gap: 16px;
  background: {SURFACE2};
}}

.avatar {{
  width: 52px; height: 52px;
  background: {SAGE};
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Lora', serif;
  font-size: 22px; color: white; flex-shrink: 0;
}}

.profile-body {{ padding: 22px 26px; }}

.stat-mini-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  margin-bottom: 16px;
}}

.stat-mini {{
  background: {SURFACE2};
  border: 1px solid {BORDER};
  border-radius: 8px; padding: 10px 12px; text-align: center;
}}

.sml {{ font-size: 9px; font-weight: 600; letter-spacing: .08em;
        text-transform: uppercase; color: {MUTED}; margin-bottom: 4px; }}

.smv {{
  font-family: 'Lora', serif;
  font-size: 20px; color: {INK};
}}

.smv.sage  {{ color: {SAGE}; }}
.smv.amber {{ color: {AMBER}; }}

/* Mini grid cards */
.mini-card {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 12px; padding: 16px;
  text-align: center;
  box-shadow: 0 2px 8px {SHADOW};
  transition: box-shadow .2s, border-color .2s;
}}

.mini-card:hover {{
  box-shadow: 0 4px 16px {SHADOW2};
  border-color: {SAGE_MID};
}}

/* Intervention card */
.interv {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-left: 3px solid {AMBER};
  border-radius: 0 12px 12px 0;
  padding: 16px 18px; margin-bottom: 10px;
  box-shadow: 0 2px 8px {SHADOW};
}}

/* PDF badge */
.pdf-ok {{
  display: inline-flex; align-items: center; gap: 6px;
  background: {SAGE_LT}; color: {SAGE};
  border: 1px solid {SAGE_MID};
  border-radius: 6px; padding: 4px 10px;
  font-size: 11px; font-weight: 600;
}}

.pdf-no {{
  display: inline-flex; align-items: center; gap: 6px;
  background: {SURFACE2}; color: {MUTED};
  border: 1px solid {BORDER};
  border-radius: 6px; padding: 4px 10px;
  font-size: 11px; font-weight: 600;
}}

/* Submit button matches .submit-btn */
.stButton > button {{
  background: {SAGE} !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 14px !important;
  transition: all .25s !important;
}}

.stButton > button:hover {{
  background: #4a6a4e !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 16px rgba(90,122,94,0.25) !important;
}}

/* Tip card — matches .tip-card */
.tip-card {{
  background: {SAGE_LT};
  border: 1px solid {SAGE_MID};
  border-radius: 12px; padding: 16px 18px;
  margin-bottom: 14px;
}}

.tip-label {{
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: {SAGE}; margin-bottom: 8px;
}}

.tip-text {{
  font-size: 12px; color: {INK2}; line-height: 1.6;
}}

/* Step list — matches .step-list */
.step-list {{ display: flex; flex-direction: column; gap: 12px; }}

.step-item {{ display: flex; gap: 11px; align-items: flex-start; }}

.step-dot {{
  width: 22px; height: 22px;
  background: {INK}; color: #fff;
  border-radius: 50%;
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}}

.step-txt {{ font-size: 12px; color: {INK2}; line-height: 1.55; }}
.step-txt strong {{ color: {INK}; font-weight: 600; }}

/* Divider */
.soft-rule {{
  border: none; border-top: 1px solid {BORDER}; margin: 24px 0;
}}

/* Footer — matches .footer */
.dash-footer {{
  padding: 18px 0 8px;
  border-top: 1px solid {BORDER};
  display: flex; align-items: center; justify-content: space-between;
  font-size: 11px; color: {MUTED};
  margin-top: 40px;
}}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ─────────────────────────────────────────────────────────────────

def analyse(df: pd.DataFrame) -> dict:
    df = df.copy()
    df.columns = df.columns.str.strip()
    sa  = df.groupby("Student")["Marks"].mean().round(2)
    sub = df.groupby("Subject")["Marks"].mean().round(2)
    ov  = round(df["Marks"].mean(), 2)
    students = []
    for name in df["Student"].unique():
        sdf   = df[df["Student"] == name]
        marks = dict(zip(sdf["Subject"], sdf["Marks"].astype(float)))
        avg   = round(sdf["Marks"].mean(), 2)
        rank  = int(sa.rank(ascending=False)[name])
        students.append(dict(
            name=name, average=avg, rank=rank, marks=marks,
            strengths=[s for s,m in marks.items() if m >= ov],
            weak=[s for s,m in marks.items() if m < ov],
        ))
    return dict(
        overall=ov, top=sa.idxmax(), top_score=float(sa.max()),
        n_students=int(df["Student"].nunique()),
        n_subjects=int(df["Subject"].nunique()),
        student_avg=sa.to_dict(), subject_avg=sub.to_dict(),
        weak_subjects={k:v for k,v in sub.items() if v < ov},
        students=students, df=df,
    )


def find_last_job():
    jobs = [d for d in glob.glob("tmp/outputs/*/") if os.path.isdir(d)]
    if not jobs:
        return None, []
    latest = max(jobs, key=os.path.getmtime)
    jid  = os.path.basename(latest.rstrip("/"))
    pdfs = glob.glob(os.path.join(latest, "*.pdf"))
    return jid, pdfs


def pdf_for(job_id, name):
    if not job_id:
        return None
    p = f"tmp/outputs/{job_id}/{name.replace(' ','_')}_report.pdf"
    return p if os.path.exists(p) else None


def rank_icon(r):
    return {1:"🥇",2:"🥈",3:"🥉"}.get(r, f"#{r}")


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;padding-top:8px">
      <div style="width:32px;height:32px;background:{SAGE};border-radius:8px;
        display:flex;align-items:center;justify-content:center;font-size:15px">🎓</div>
      <div style="font-family:'Lora',serif;font-size:16px;font-weight:600;color:{INK}">AI Report Generator</div>
    </div>
    <div style="font-size:11px;color:{MUTED};margin-bottom:20px;padding-left:42px">Teacher Dashboard</div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f'<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin-bottom:10px">Data Source</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["Upload CSV", "Last processed job"], label_visibility="collapsed")

    df = None
    job_id = None

    if mode == "Upload CSV":
        up = st.file_uploader("Drop CSV here", type=["csv"], label_visibility="collapsed")
        if up:
            df = pd.read_csv(up)
            st.success(f"✓ {up.name} loaded")
    else:
        job_id, pdfs = find_last_job()
        if job_id:
            st.success(f"✓ Job {job_id[:8]}")
            st.caption(f"{len(pdfs)} PDF(s) available")
            csv_path = f"tmp/uploads/{job_id}.csv"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
            else:
                up2 = st.file_uploader("Upload CSV for this job", type=["csv"], label_visibility="collapsed")
                if up2:
                    df = pd.read_csv(up2)
        else:
            st.warning("No processed jobs found yet.")

    st.divider()

    st.markdown(f'<div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin-bottom:10px">Navigate</div>', unsafe_allow_html=True)
    page = st.radio("nav", ["📊 Overview", "🏆 Leaderboard", "⚠️ Needs Help", "📚 Student Profiles"], label_visibility="collapsed")

    st.divider()

    # Tip card
    st.markdown(f"""
    <div class="tip-card">
      <div class="tip-label">📌 CSV Format</div>
      <div class="tip-text">
        <strong>Student</strong> — full name<br/>
        <strong>Subject</strong> — subject name<br/>
        <strong>Marks</strong> — numerical score<br/><br/>
        One row per student per subject.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:11px;color:{MUTED};margin-top:8px">AI Report Generator v2.0</div>', unsafe_allow_html=True)


# ── EMPTY STATE ──────────────────────────────────────────────────────────────
if df is None:
    st.markdown(f"""
    <div class="dash-nav">
      <div class="dash-nav-brand">
        <div class="dash-nav-icon">🎓</div>
        <div class="dash-nav-name">AI Report Generator</div>
      </div>
      <div class="dash-nav-status">
        <div class="dash-dot"></div> Dashboard ready
      </div>
    </div>
    <div style="text-align:center;padding:80px 40px">
      <div style="width:72px;height:72px;background:{SURFACE2};border:1px solid {BORDER};
        border-radius:16px;display:flex;align-items:center;justify-content:center;
        font-size:30px;margin:0 auto 20px">📋</div>
      <div class="page-h1" style="margin-bottom:8px">No data loaded</div>
      <div class="page-sub">Upload a CSV or load the last processed job from the sidebar.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

data = analyse(df)
students = data["students"]


# ── NAV BAR (shown on every page) ────────────────────────────────────────────
st.markdown(f"""
<div class="dash-nav">
  <div class="dash-nav-brand">
    <div class="dash-nav-icon">🎓</div>
    <div class="dash-nav-name">AI Report Generator</div>
  </div>
  <div class="dash-nav-status">
    <div class="dash-dot"></div> {data['n_students']} students · {data['n_subjects']} subjects
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":

    st.markdown('<div class="page-eyebrow">Analytics</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-h1">Class <em>Overview</em></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Full performance breakdown across all students and subjects.</div>', unsafe_allow_html=True)

    # KPI row
    k1,k2,k3,k4,k5 = st.columns(5)
    for col, label, val, cls in zip(
        [k1,k2,k3,k4,k5],
        ["Class Average","Top Student","Top Score","Total Students","Weak Subjects"],
        [data["overall"], data["top"], data["top_score"], data["n_students"], len(data["weak_subjects"])],
        ["sage","sm","sage","","amber"],
    ):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-val {cls}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="soft-rule"/>', unsafe_allow_html=True)

    # Charts
    left, right = st.columns(2)

    with left:
        st.markdown(f'<div class="section-label"><div class="section-num">1</div>Student Averages</div>', unsafe_allow_html=True)
        sa   = data["student_avg"]
        s_df = pd.DataFrame({"Student": list(sa.keys()), "Average": list(sa.values())}).sort_values("Average")
        colors = [AMBER if v < data["overall"] else SAGE for v in s_df["Average"]]

        fig = go.Figure(go.Bar(
            x=s_df["Average"], y=s_df["Student"],
            orientation="h",
            marker=dict(color=colors, opacity=0.8),
            text=s_df["Average"], textposition="outside",
            textfont=dict(color=MUTED, size=12),
        ))
        fig.add_vline(x=data["overall"], line_dash="dot", line_color=BORDER2,
            annotation_text=f"avg {data['overall']}",
            annotation_font=dict(color=MUTED, size=10),
            annotation_position="top right")
        fig.update_layout(**CHART,
            height=max(160, len(sa)*58),
            xaxis=dict(**AX, range=[0, max(sa.values())*1.18]),
            yaxis=dict(**AX_NOGRID),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(f'<div class="section-label"><div class="section-num">2</div>Subject Difficulty</div>', unsafe_allow_html=True)
        sub    = data["subject_avg"]
        sub_df = pd.DataFrame({"Subject": list(sub.keys()), "Average": list(sub.values())}).sort_values("Average", ascending=False)
        colors2 = [ROSE if v < data["overall"] else SAGE for v in sub_df["Average"]]

        fig2 = go.Figure(go.Bar(
            x=sub_df["Subject"], y=sub_df["Average"],
            marker=dict(color=colors2, opacity=0.8),
            text=sub_df["Average"], textposition="outside",
            textfont=dict(color=MUTED, size=12),
        ))
        fig2.add_hline(y=data["overall"], line_dash="dot", line_color=BORDER2,
            annotation_text=f"avg {data['overall']}",
            annotation_font=dict(color=MUTED, size=10),
            annotation_position="top right")
        fig2.update_layout(**CHART,
            height=max(160, len(sub)*58),
            xaxis=dict(**AX_NOGRID),
            yaxis=dict(**AX, range=[0, max(sub.values())*1.22]),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="soft-rule"/>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label"><div class="section-num">3</div>Full Class Heatmap</div>', unsafe_allow_html=True)

    pivot = df.pivot_table(index="Student", columns="Subject", values="Marks", aggfunc="mean")
    fig3 = px.imshow(
        pivot, text_auto=True, aspect="auto",
        color_continuous_scale=[[0, ROSE_LT], [0.5, SURFACE2], [1, SAGE_LT]],
    )
    fig3.update_traces(textfont=dict(size=13, color=INK), xgap=3, ygap=3)
    fig3.update_layout(**CHART,
        height=max(160, len(pivot)*54+60),
        xaxis=dict(side="top", **AX_NOGRID),
        yaxis=dict(**AX_NOGRID),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Leaderboard":

    st.markdown('<div class="page-eyebrow">Rankings</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-h1">Top <em>Performers</em></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Students ranked by overall average across all subjects.</div>', unsafe_allow_html=True)

    ranked = sorted(students, key=lambda s: s["average"], reverse=True)
    left, right = st.columns([1.8, 1])

    with left:
        for s in ranked:
            stags = "".join(f'<span class="tag-s">{t}</span>' for t in s["strengths"])
            st.markdown(f"""
            <div class="lb-row">
              <div class="lb-rank">{rank_icon(s['rank'])}</div>
              <div class="lb-name">{s['name']}</div>
              <div style="flex:1">{stags}</div>
              <div class="lb-score">{s['average']}</div>
            </div>""", unsafe_allow_html=True)

    with right:
        st.markdown(f'<div class="section-label"><div class="section-num">✦</div>Score Distribution</div>', unsafe_allow_html=True)
        medal = [AMBER if i==0 else MUTED if i==1 else INK2 if i==2 else SAGE_MID for i in range(len(ranked))]
        fig4 = go.Figure(go.Bar(
            x=[s["name"] for s in ranked],
            y=[s["average"] for s in ranked],
            marker=dict(color=medal, opacity=0.85),
            text=[s["average"] for s in ranked],
            textposition="outside",
            textfont=dict(color=MUTED, size=12),
        ))
        fig4.update_layout(**CHART,
            height=300,
            xaxis=dict(**AX_NOGRID),
            yaxis=dict(**AX, range=[0, max(s["average"] for s in ranked)*1.2]),
        )
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: NEEDS HELP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Needs Help":

    st.markdown('<div class="page-eyebrow">Attention Required</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-h1">Students Needing <em>Help</em></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Scoring below the class average in one or more subjects.</div>', unsafe_allow_html=True)

    at_risk = sorted([s for s in students if s["weak"]], key=lambda s: s["average"])

    if not at_risk:
        st.markdown(f"""
        <div style="background:{SAGE_LT};border:1px solid {SAGE_MID};border-radius:12px;
          padding:20px 24px;font-size:14px;color:{SAGE}">
          🎉 All students are performing at or above the class average.
        </div>""", unsafe_allow_html=True)
    else:
        left, right = st.columns([1.8, 1])

        with left:
            for s in at_risk:
                wtags = "".join(f'<span class="tag-w">{t}</span>' for t in s["weak"])
                st.markdown(f"""
                <div class="help-row">
                  <div class="help-name">{s['name']}</div>
                  <div style="flex:1">{wtags}</div>
                  <div class="help-score">{s['average']}</div>
                </div>""", unsafe_allow_html=True)

        with right:
            st.markdown(f'<div class="section-label"><div class="section-num">✦</div>Frequency by Subject</div>', unsafe_allow_html=True)
            freq = {}
            for s in at_risk:
                for sub in s["weak"]:
                    freq[sub] = freq.get(sub, 0) + 1
            if freq:
                fig5 = go.Figure(go.Bar(
                    x=list(freq.keys()), y=list(freq.values()),
                    marker=dict(color=AMBER, opacity=0.75),
                    text=list(freq.values()), textposition="outside",
                    textfont=dict(color=MUTED, size=12),
                ))
                fig5.update_layout(**CHART,
                    height=240,
                    xaxis=dict(**AX_NOGRID),
                    yaxis=dict(**AX, tickformat="d", range=[0, max(freq.values())+1.5]),
                )
                st.plotly_chart(fig5, use_container_width=True)

        st.markdown('<hr class="soft-rule"/>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-label"><div class="section-num">✦</div>Intervention Plans</div>', unsafe_allow_html=True)
        cols = st.columns(min(3, max(1, len(at_risk))))
        for i, s in enumerate(at_risk):
            with cols[i % len(cols)]:
                st.markdown(f"""
                <div class="interv">
                  <div style="font-weight:600;color:{INK};font-size:14px;margin-bottom:4px">{s['name']}</div>
                  <div style="font-size:11px;color:{MUTED};margin-bottom:10px">Avg {s['average']} · Rank #{s['rank']}</div>
                  <div style="font-size:12px;color:{AMBER};font-weight:600;margin-bottom:7px">⚠ {', '.join(s['weak'])}</div>
                  <div style="font-size:12px;color:{INK2};line-height:1.55">
                    Schedule extra sessions for {s['weak'][0]}. Provide additional practice materials and check in weekly.
                  </div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENT PROFILES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📚 Student Profiles":

    st.markdown('<div class="page-eyebrow">Individual Records</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-h1">Student <em>Profiles</em></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Individual performance breakdown and PDF report access for each student.</div>', unsafe_allow_html=True)

    names    = [s["name"] for s in students]
    sel_name = st.selectbox(
        "Student",
        names,
        format_func=lambda n: f"{rank_icon(next(s['rank'] for s in students if s['name']==n))}  {n}",
        label_visibility="collapsed",
    )
    sel = next(s for s in students if s["name"] == sel_name)

    st.markdown("<br/>", unsafe_allow_html=True)

    col_prof, col_chart, col_pdf = st.columns([1, 2, 1])

    # ── PROFILE CARD ──
    with col_prof:
        init  = sel_name[0].upper()
        stags = "".join(f'<span class="tag-s">{t}</span>' for t in sel["strengths"]) or f'<span style="font-size:12px;color:{MUTED}">None</span>'
        wtags = "".join(f'<span class="tag-w">{t}</span>' for t in sel["weak"]) or f'<span style="font-size:12px;color:{SAGE}">All above avg ✓</span>'
        diff  = round(sel["average"] - data["overall"], 2)
        dc    = SAGE if diff >= 0 else AMBER
        ds    = f"+{diff}" if diff >= 0 else str(diff)

        st.markdown(f"""
        <div class="profile-wrap">
          <div class="profile-header">
            <div class="avatar">{init}</div>
            <div>
              <div style="font-family:'Lora',serif;font-size:18px;font-weight:600;color:{INK}">{sel_name}</div>
              <div style="font-size:12px;color:{MUTED}">{rank_icon(sel['rank'])} Rank {sel['rank']} of {data['n_students']}</div>
            </div>
          </div>
          <div class="profile-body">
            <div class="stat-mini-grid">
              <div class="stat-mini">
                <div class="sml">Average</div>
                <div class="smv sage">{sel['average']}</div>
              </div>
              <div class="stat-mini">
                <div class="sml">vs Class</div>
                <div class="smv" style="color:{dc};font-size:16px;padding-top:4px">{ds}</div>
              </div>
            </div>
            <div style="margin-bottom:12px">
              <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin-bottom:6px">Strengths</div>
              {stags}
            </div>
            <div>
              <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin-bottom:6px">Needs Work</div>
              {wtags}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CHARTS ──
    with col_chart:
        st.markdown(f'<div class="section-label"><div class="section-num">1</div>Subject Scores</div>', unsafe_allow_html=True)
        marks = sel["marks"]
        subjs = list(marks.keys())
        vals  = list(marks.values())
        bc    = [ROSE if v < data["overall"] else SAGE for v in vals]

        fig6 = go.Figure(go.Bar(
            x=subjs, y=vals,
            marker=dict(color=bc, opacity=0.8),
            text=vals, textposition="outside",
            textfont=dict(color=MUTED, size=13),
        ))
        fig6.add_hline(y=data["overall"], line_dash="dot", line_color=BORDER2,
            annotation_text=f"class avg {data['overall']}",
            annotation_font=dict(color=MUTED, size=10),
            annotation_position="top right")
        fig6.update_layout(**CHART,
            height=240,
            xaxis=dict(**AX_NOGRID),
            yaxis=dict(**AX, range=[0, max(vals+[data["overall"]])*1.24]),
        )
        st.plotly_chart(fig6, use_container_width=True)

        if len(subjs) >= 3:
            st.markdown(f'<div class="section-label" style="margin-top:4px"><div class="section-num">2</div>Radar Profile</div>', unsafe_allow_html=True)
            fig7 = go.Figure(go.Scatterpolar(
                r=vals+[vals[0]], theta=subjs+[subjs[0]],
                fill="toself",
                fillcolor=f"rgba(90,122,94,0.1)",
                line=dict(color=SAGE, width=1.5),
            ))
            fig7.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,100],
                                    gridcolor=BORDER, tickfont=dict(color=MUTED, size=10), color=MUTED),
                    angularaxis=dict(gridcolor=BORDER, tickfont=dict(color=INK2, size=11)),
                ),
                margin=dict(l=20, r=20, t=20, b=20),
                height=220,
                font=dict(family="Plus Jakarta Sans", color=INK2),
                showlegend=False,
            )
            st.plotly_chart(fig7, use_container_width=True)

    # ── PDF ──
    with col_pdf:
        st.markdown(f'<div class="section-label"><div class="section-num">✦</div>PDF Report</div>', unsafe_allow_html=True)
        pdf_path = pdf_for(job_id, sel_name)

        if pdf_path:
            st.markdown('<span class="pdf-ok">✓ Report ready</span>', unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇ Download PDF",
                    data=f.read(),
                    file_name=f"{sel_name.replace(' ','_')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.markdown('<span class="pdf-no">⏳ Not generated yet</span>', unsafe_allow_html=True)
            st.markdown(f"<br/><div style='font-size:12px;color:{MUTED};line-height:1.6'>Generate a report from the main website first, then reload this dashboard.</div>", unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        for label, val, cls in [
            ("Average", sel["average"], SAGE),
            ("Rank", f"#{sel['rank']}", INK),
            ("Strong", len(sel["strengths"]), SAGE),
            ("Weak", len(sel["weak"]), AMBER),
        ]:
            st.markdown(f"""
            <div style="margin-bottom:12px">
              <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{MUTED};margin-bottom:3px">{label}</div>
              <div style="font-family:'Lora',serif;font-size:20px;font-weight:600;color:{cls}">{val}</div>
            </div>""", unsafe_allow_html=True)

    # ── ALL STUDENTS MINI GRID ──
    st.markdown('<hr class="soft-rule"/>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-label"><div class="section-num">3</div>All Students</div>', unsafe_allow_html=True)

    grid = st.columns(min(4, len(students)))
    for i, s in enumerate(sorted(students, key=lambda x: x["rank"])):
        with grid[i % len(grid)]:
            pdf_ok  = bool(pdf_for(job_id, s["name"]))
            pbadge  = f'<span class="pdf-ok" style="font-size:10px">✓ PDF</span>' if pdf_ok else f'<span class="pdf-no" style="font-size:10px">No PDF</span>'
            acolor  = SAGE if s["average"] >= data["overall"] else AMBER
            st.markdown(f"""
            <div class="mini-card">
              <div style="width:42px;height:42px;background:{SAGE};border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-family:'Lora',serif;font-size:18px;color:white;margin:0 auto 10px">{s['name'][0]}</div>
              <div style="font-weight:600;color:{INK};font-size:14px;margin-bottom:2px">{s['name']}</div>
              <div style="font-size:11px;color:{MUTED};margin-bottom:8px">{rank_icon(s['rank'])}</div>
              <div style="font-family:'Lora',serif;font-size:22px;font-weight:600;color:{acolor};margin-bottom:8px">{s['average']}</div>
              <div style="font-size:11px;color:{MUTED};margin-bottom:8px">{len(s['strengths'])} strong · {len(s['weak'])} weak</div>
              {pbadge}
            </div>""", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-footer">
  <span>AI Report Generator — Teacher Dashboard</span>
  <span>{data['n_students']} students · {data['n_subjects']} subjects loaded</span>
</div>
""", unsafe_allow_html=True)
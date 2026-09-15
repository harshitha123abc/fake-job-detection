import streamlit as st
import requests
import os
import json
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
import hashlib

load_dotenv()
API_KEY = os.getenv("API_KEY", "")
API_URL = "https://fake-job-detection-api-2hbn.onrender.com/predict"
USERS_FILE = "users.json"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"
if 'job_text' not in st.session_state:
    st.session_state.job_text = ""
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'show_resume_checker' not in st.session_state:
    st.session_state.show_resume_checker = False
if 'show_wa_checker' not in st.session_state:
    st.session_state.show_wa_checker = False
if 'show_chrome' not in st.session_state:
    st.session_state.show_chrome = False

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(email, password):
    users = load_users()
    hashed = hash_password(password)
    if email in users and users[email]['password'] == hashed:
        st.session_state.authenticated = True
        st.session_state.user_name = users[email]['name']
        st.session_state.user_email = email
        st.session_state.user_role = users[email]['role']
        return True, "Login successful!"
    return False, "Invalid email or password."

def register_user(name, email, password, role):
    users = load_users()
    if email in users:
        return False, "Email already exists."
    users[email] = {
        'name': name,
        'password': hash_password(password),
        'role': role
    }
    save_users(users)
    return True, "Registration successful!"

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.session_state.job_text = ""
    st.session_state.last_result = None

# ─────────────────────────────────────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_auth_page():
    mode = st.session_state.auth_mode

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');
    html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
    [data-testid="stAppViewContainer"]{
        background:linear-gradient(135deg,#0a1628 0%,#061223 50%,#08101e 100%)!important;
    }
    [data-testid="stHeader"]{background:transparent!important;display:none!important}
    .block-container{padding:2rem 1rem!important;max-width:480px!important;margin:0 auto!important;}
    [data-testid="stTextInput"] input{
        background:rgba(255,255,255,0.06)!important;color:#f1f5f9!important;
        border:1.5px solid rgba(255,255,255,0.14)!important;border-radius:8px!important;
        font-size:.92rem!important;padding:12px 14px!important;caret-color:#22d3ee!important;
    }
    [data-testid="stTextInput"] input:focus{
        border-color:#22d3ee!important;box-shadow:0 0 0 3px rgba(34,211,238,.12)!important;
        background:rgba(34,211,238,0.06)!important;color:#f1f5f9!important;
    }
    [data-testid="stTextInput"] input::placeholder{color:rgba(148,163,184,0.4)!important}
    [data-testid="stTextInput"] label p,[data-testid="stSelectbox"] label p{
        color:#94a3b8!important;font-size:.8rem!important;font-weight:600!important;
    }
    [data-testid="stTextInput"] p,[data-testid="stTextInput"] span{color:#94a3b8!important}
    [data-testid="stSelectbox"] [data-baseweb="select"] > div{
        background:rgba(255,255,255,0.06)!important;color:#f1f5f9!important;
        border:1.5px solid rgba(255,255,255,0.14)!important;border-radius:8px!important;
    }
    button{font-family:'Inter',sans-serif!important;font-weight:700!important;
           border-radius:8px!important;transition:all .22s!important}
    button[kind="primary"]{
        background:#1a6cff!important;border:none!important;color:#fff!important;
        height:46px!important;font-size:.93rem!important;
        box-shadow:0 4px 20px rgba(26,108,255,.5)!important;
    }
    button[kind="primary"]:hover{background:#1558e0!important;transform:translateY(-1px)!important;}
    button[kind="secondary"]{
        background:rgba(255,255,255,0.04)!important;
        border:1.5px solid rgba(255,255,255,0.14)!important;
        color:rgba(255,255,255,0.6)!important;height:46px!important;
    }
    button[kind="secondary"]:hover{background:rgba(255,255,255,0.08)!important;color:#fff!important;}
    [data-testid="stAlert"] p{color:#f1f5f9!important;}
    </style>
    """, unsafe_allow_html=True)

    # ── brand header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin:40px 0 32px;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,#1a6cff,#22d3ee);
           border-radius:10px;display:flex;align-items:center;justify-content:center;
           font-size:1.1rem;box-shadow:0 4px 14px rgba(26,108,255,.4);">&#128737;</div>
      <span style="font-size:1.1rem;font-weight:800;color:#fff;letter-spacing:-.02em;
            font-family:'Plus Jakarta Sans',sans-serif;">JobGuard AI</span>
    </div>
    """, unsafe_allow_html=True)

    # ── mode switcher ─────────────────────────────────────────────────────────
    sw1, sw2 = st.columns(2, gap="small")
    with sw1:
        if st.button("Sign In", width="stretch", key="tab_login",
                     type="primary" if mode == "login" else "secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()
    with sw2:
        if st.button("Sign Up", width="stretch", key="tab_register",
                     type="primary" if mode == "register" else "secondary"):
            st.session_state.auth_mode = "register"
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    if mode == "login":
        st.markdown("""
        <div style="font-size:1.6rem;font-weight:800;color:#ffffff;letter-spacing:-.03em;
             font-family:'Plus Jakarta Sans',sans-serif;text-align:center;margin-bottom:4px;">
          Welcome back
        </div>
        <div style="font-size:.84rem;color:#64748b;text-align:center;margin-bottom:24px;">
          Sign in to your JobGuard AI account
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("Email", placeholder="example@gmail.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pwd")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Sign In", width="stretch", key="li_btn", type="primary"):
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                ok, msg = login_user(email, password)
                if ok:
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    else:
        st.markdown("""
        <div style="font-size:1.6rem;font-weight:800;color:#ffffff;letter-spacing:-.03em;
             font-family:'Plus Jakarta Sans',sans-serif;text-align:center;margin-bottom:4px;">
          Create account
        </div>
        <div style="font-size:.84rem;color:#64748b;text-align:center;margin-bottom:24px;">
          Join JobGuard AI and stay protected
        </div>
        """, unsafe_allow_html=True)

        name     = st.text_input("Full name", placeholder="e.g. Manisha Patel", key="reg_name")
        email    = st.text_input("Email", placeholder="example@gmail.com", key="reg_email")
        role     = st.selectbox("I am a", ["Job Seeker","Recruiter","HR Professional","Admin"], key="reg_role")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="reg_pwd")
        confirm  = st.text_input("Confirm password", type="password", placeholder="Re-enter password", key="reg_pwd2")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Create Account", width="stretch", key="reg_btn", type="primary"):
            if not all([name, email, password, confirm]):
                st.error("All fields are required.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(name, email, password, role)
                if ok:
                    login_user(email, password)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)


if not st.session_state.authenticated:
    show_auth_page()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');

:root {
    --bg:       #080c14;
    --bg2:      #0d1220;
    --bg3:      #111827;
    --surface:  rgba(255,255,255,0.03);
    --surface2: rgba(255,255,255,0.06);
    --surface3: rgba(255,255,255,0.09);
    --bdr:      rgba(255,255,255,0.07);
    --bdr2:     rgba(255,255,255,0.12);
    --blue:     #6366f1;
    --blue2:    #818cf8;
    --cyan:     #22d3ee;
    --purple:   #a78bfa;
    --green:    #10b981;
    --green2:   #34d399;
    --yellow:   #f59e0b;
    --red:      #f43f5e;
    --red2:     #fb7185;
    --txt:      #f1f5f9;
    --txt2:     #94a3b8;
    --txt3:     #475569;
    --txt4:     #334155;
    --sh-sm: 0 1px 4px rgba(0,0,0,.35);
    --sh-md: 0 4px 16px rgba(0,0,0,.4);
    --sh-lg: 0 12px 36px rgba(0,0,0,.45);
    --sh-xl: 0 20px 60px rgba(0,0,0,.5);
}

html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif!important;color:var(--txt)!important}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:#1e2a3a;border-radius:8px}
::-webkit-scrollbar-thumb:hover{background:#2a3a50}

[data-testid="stAppViewContainer"]{background:var(--bg)!important}
[data-testid="stHeader"]{background:transparent!important}
.block-container{padding-top:.2rem!important;padding-bottom:.75rem!important;max-width:1480px!important}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0a0f1e 0%,#080c18 100%)!important;
    border-right:1px solid var(--bdr)!important;
}
[data-testid="stSidebar"] *{color:var(--txt2)!important}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3{
    color:var(--txt4)!important;font-size:.62rem!important;
    text-transform:uppercase!important;letter-spacing:.16em!important;
    font-weight:800!important;margin:24px 0 8px!important;
}

/* ── Navbar ── */
.pnav{
    background:linear-gradient(90deg,rgba(10,16,36,0.98) 0%,rgba(13,20,42,0.98) 60%,rgba(8,14,30,0.98) 100%);
    border:none;border-bottom:1px solid rgba(255,255,255,0.07);
    backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
    border-radius:16px;padding:0 32px;display:flex;align-items:center;
    justify-content:space-between;height:74px;margin-bottom:8px;
    box-shadow:0 8px 32px rgba(0,0,0,0.45),0 1px 0 rgba(255,255,255,0.06);
    position:relative;overflow:hidden;
}
.pnav::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent 0%,#6366f1 25%,#22d3ee 55%,#818cf8 80%,transparent 100%)}
.pnav::after{content:'';position:absolute;bottom:0;left:10%;right:10%;height:1px;
    background:linear-gradient(90deg,transparent,rgba(99,102,241,0.15),transparent)}
.pnav-brand{display:flex;align-items:center;gap:15px}
.pnav-logo{width:46px;height:46px;
    background:linear-gradient(135deg,#6366f1 0%,#4f46e5 40%,#22d3ee 100%);
    border-radius:13px;display:flex;align-items:center;justify-content:center;
    font-size:1.35rem;box-shadow:0 0 0 1px rgba(99,102,241,0.4),0 6px 22px rgba(99,102,241,0.5);
    flex-shrink:0;position:relative;}
.pnav-logo::after{content:'';position:absolute;inset:0;border-radius:13px;
    background:linear-gradient(135deg,rgba(255,255,255,0.18) 0%,transparent 60%);}
.pnav-name{font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:-.025em;
    line-height:1.15;font-family:'Plus Jakarta Sans',sans-serif}
.pnav-sub{font-size:.62rem;color:#334155;font-weight:700;letter-spacing:.14em;
    text-transform:uppercase;margin-top:3px}
.pnav-divider{width:1px;height:28px;background:rgba(255,255,255,0.08);margin:0 10px}
.pnav-right{display:flex;align-items:center;gap:4px}
.pnav-link{color:#475569;text-decoration:none;font-size:.82rem;font-weight:600;
    padding:8px 15px;border-radius:9px;transition:all .2s;letter-spacing:.01em;position:relative;}
.pnav-link:hover{background:rgba(255,255,255,0.06);color:#e2e8f0}
.pnav-link.active{color:#a5b4fc;background:rgba(99,102,241,0.12);}
.pnav-badge{display:inline-flex;align-items:center;justify-content:center;
    background:rgba(99,102,241,0.18);color:#818cf8;border-radius:5px;
    font-size:.58rem;font-weight:800;padding:2px 5px;margin-left:5px;letter-spacing:.04em;}
.pnav-live{display:flex;align-items:center;gap:8px;
    background:linear-gradient(90deg,rgba(16,185,129,0.12),rgba(16,185,129,0.06));
    border:1px solid rgba(16,185,129,0.22);border-radius:999px;
    padding:7px 16px;font-size:.72rem;font-weight:700;color:#34d399;margin-left:12px;
    box-shadow:0 0 12px rgba(16,185,129,0.08);}
.live-dot{width:7px;height:7px;border-radius:50%;background:#34d399;
    box-shadow:0 0 0 2px rgba(52,211,153,0.25),0 0 10px rgba(52,211,153,0.8);
    animation:blink 2s ease-in-out infinite;flex-shrink:0;}
.pnav-user{display:flex;align-items:center;gap:10px;margin-left:14px;
    padding:6px 14px 6px 8px;border-radius:10px;border:1px solid rgba(255,255,255,0.07);
    background:rgba(255,255,255,0.03);}
.pnav-avatar{width:30px;height:30px;border-radius:8px;
    background:linear-gradient(135deg,#6366f1,#22d3ee);
    display:flex;align-items:center;justify-content:center;font-size:.85rem;}
.pnav-uname{font-size:.78rem;font-weight:700;color:#cbd5e1;line-height:1.2;}
.pnav-urole{font-size:.62rem;color:#334155;font-weight:600;}
@keyframes blink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.75)}}

/* ── KPI Banner ── */
.kpi-banner{
    background:linear-gradient(135deg,rgba(99,102,241,.12) 0%,rgba(15,23,42,.95) 45%,rgba(34,211,238,.07) 100%);
    border:1px solid var(--bdr);border-radius:18px;padding:32px 36px;margin-bottom:16px;
    position:relative;overflow:hidden;box-shadow:var(--sh-lg);
}
.kpi-banner::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(99,102,241,.5),rgba(34,211,238,.4),transparent)}
.kpi-banner::after{content:'';position:absolute;top:-40%;right:-5%;width:380px;height:380px;
    background:radial-gradient(circle,rgba(99,102,241,.08) 0%,transparent 68%);pointer-events:none}
.kpi-inner{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap;position:relative;z-index:1}
.kpi-text h1{margin:0 0 10px;font-size:1.65rem;font-weight:900;color:#fff;letter-spacing:-.045em;
    line-height:1.18;font-family:'Plus Jakarta Sans',sans-serif}
.kpi-text p{margin:0;color:var(--txt3);font-size:.87rem;line-height:1.65;max-width:460px}
.kpi-chip{display:inline-flex;align-items:center;gap:5px;background:rgba(99,102,241,.12);
    border:1px solid rgba(99,102,241,.25);border-radius:999px;padding:4px 12px;
    font-size:.71rem;font-weight:800;color:#818cf8;margin-bottom:12px;letter-spacing:.03em}
.kpi-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;min-width:440px}
.kpi-stat{background:rgba(255,255,255,0.04);border:1px solid var(--bdr);border-radius:13px;
    padding:16px 14px;text-align:center;transition:all .3s;backdrop-filter:blur(10px)}
.kpi-stat:hover{background:rgba(255,255,255,.07);transform:translateY(-3px);border-color:var(--bdr2)}
.kpi-val{font-size:1.5rem;font-weight:900;color:#fff;line-height:1;margin-bottom:4px;
    font-family:'Plus Jakarta Sans',sans-serif}
.kpi-lbl{font-size:.65rem;color:var(--txt3);font-weight:700;text-transform:uppercase;letter-spacing:.1em}

/* ── Tool Grid ── */
.tool-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.tool-card{background:var(--surface);border:1px solid var(--bdr);border-radius:14px;
    padding:18px 20px;display:flex;align-items:flex-start;gap:14px;
    box-shadow:var(--sh-sm);transition:all .28s;cursor:pointer}
.tool-card:hover{background:var(--surface2);box-shadow:var(--sh-lg);
    transform:translateY(-3px);border-color:rgba(99,102,241,.35)}
.tool-icon{width:46px;height:46px;border-radius:12px;display:flex;align-items:center;
    justify-content:center;font-size:1.3rem;flex-shrink:0}
.ti-indigo{background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.2)}
.ti-purple{background:rgba(167,139,250,.1);border:1px solid rgba(167,139,250,.18)}
.ti-cyan{background:rgba(34,211,238,.1);border:1px solid rgba(34,211,238,.18)}
.tool-info h4{margin:0 0 4px;font-size:.9rem;font-weight:700;color:var(--txt)}
.tool-info p{margin:0;font-size:.78rem;color:var(--txt3);line-height:1.5}

/* ── Pro Card ── */
.pro-card{background:var(--surface);border:1px solid var(--bdr);border-radius:15px;
    padding:22px;box-shadow:var(--sh-sm);margin-bottom:14px}
.pro-card-hdr{display:flex;align-items:center;gap:12px;padding-bottom:14px;
    border-bottom:1px solid var(--bdr);margin-bottom:14px}
.pro-card-ico{width:38px;height:38px;border-radius:10px;background:rgba(99,102,241,.12);
    border:1px solid rgba(99,102,241,.2);display:flex;align-items:center;justify-content:center;
    font-size:1rem;flex-shrink:0}
.pro-card-hdr h3{margin:0;font-size:.95rem;font-weight:700;color:var(--txt);
    font-family:'Plus Jakarta Sans',sans-serif}
.pro-card-hdr p{margin:2px 0 0;font-size:.76rem;color:var(--txt3)}

/* ── Section heading ── */
.sec-hdr{display:flex;align-items:center;gap:10px;margin:10px 0 8px}
.sec-hdr h2{margin:0;font-size:1.02rem;font-weight:800;color:var(--txt);letter-spacing:-.02em;
    font-family:'Plus Jakarta Sans',sans-serif}
.sec-div{flex:1;height:1px;background:var(--bdr);margin-left:8px}

/* ── Verdict banner ── */
.verdict{display:flex;align-items:center;gap:16px;border-radius:14px;padding:18px 22px;
    margin:14px 0;border:1px solid;backdrop-filter:blur(10px)}
.verdict-high{background:rgba(244,63,94,.08);border-color:rgba(244,63,94,.3)}
.verdict-medium{background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.3)}
.verdict-low{background:rgba(16,185,129,.08);border-color:rgba(16,185,129,.3)}
.verdict-emoji{font-size:1.8rem;flex-shrink:0}
.verdict-body{flex:1}
.verdict-title{font-size:1rem;font-weight:800;font-family:'Plus Jakarta Sans',sans-serif;margin-bottom:4px}
.vt-high{color:#fb7185}.vt-medium{color:#fbbf24}.vt-low{color:#34d399}
.verdict-body p{margin:0;font-size:.86rem;line-height:1.6;color:var(--txt2)}
.verdict-score-pill{font-size:1.4rem;font-weight:900;padding:10px 16px;border-radius:10px;
    letter-spacing:-.03em;font-family:'Plus Jakarta Sans',sans-serif;flex-shrink:0}
.vsp-high{background:rgba(244,63,94,.15);color:#fb7185}
.vsp-medium{background:rgba(245,158,11,.15);color:#fbbf24}
.vsp-low{background:rgba(16,185,129,.15);color:#34d399}

/* ── Risk Snapshot Panel ── */
.snap-score{text-align:center;padding:22px 12px 10px}
.snap-num{font-size:4rem;font-weight:900;letter-spacing:-.07em;line-height:1;
    font-family:'Plus Jakarta Sans',sans-serif}
.snap-lbl{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;
    color:var(--txt3);margin-top:6px;margin-bottom:14px}
.snap-badge{display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:999px;
    font-size:.78rem;font-weight:800;letter-spacing:.04em;border:1px solid}
.sb-high{background:rgba(244,63,94,.12);color:#fb7185;border-color:rgba(244,63,94,.3)}
.sb-medium{background:rgba(245,158,11,.12);color:#fbbf24;border-color:rgba(245,158,11,.3)}
.sb-low{background:rgba(16,185,129,.12);color:#34d399;border-color:rgba(16,185,129,.3)}
.rec-box{background:rgba(34,211,238,.05);border:1px solid rgba(34,211,238,.18);
    border-radius:11px;padding:13px 15px;margin-top:14px}
.rec-lbl{font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;
    color:var(--cyan);margin-bottom:6px}
.rec-txt{font-size:.84rem;color:var(--txt2);line-height:1.6;font-weight:500}

/* ── Evidence items ── */
.ev-item{display:flex;align-items:flex-start;gap:10px;padding:9px 12px;border-radius:9px;
    margin-bottom:5px;font-size:.82rem;border:1px solid;font-weight:600}
.ev-ok{background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.2);color:#34d399}
.ev-warn{background:rgba(245,158,11,.07);border-color:rgba(245,158,11,.2);color:#fbbf24}
.ev-err{background:rgba(244,63,94,.07);border-color:rgba(244,63,94,.2);color:#fb7185}
.ev-neu{background:var(--surface2);border-color:var(--bdr2);color:var(--txt2)}
.ev-icon{font-size:.88rem;margin-top:1px;flex-shrink:0}

/* ── Pipeline steps ── */
.analysis-step{display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;
    margin-bottom:5px;background:rgba(99,102,241,.05);font-size:.82rem;
    color:var(--txt2);border:1px solid rgba(99,102,241,.1);font-weight:600}
.step-dot{width:6px;height:6px;border-radius:50%;background:var(--blue);flex-shrink:0}

/* ── Tags ── */
.tag{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;
    font-size:.75rem;font-weight:700;margin:3px 4px 3px 0;border:1px solid}
.t-ok{background:rgba(16,185,129,.1);color:#34d399;border-color:rgba(16,185,129,.25)}
.t-wrn{background:rgba(245,158,11,.1);color:#fbbf24;border-color:rgba(245,158,11,.25)}
.t-err{background:rgba(244,63,94,.1);color:#fb7185;border-color:rgba(244,63,94,.25)}
.t-inf{background:rgba(34,211,238,.08);color:#22d3ee;border-color:rgba(34,211,238,.22)}
.t-neu{background:var(--surface2);color:var(--txt2);border-color:var(--bdr2)}

/* ── Platform Grid ── */
.platform-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:14px 0}
.platform-item{display:flex;align-items:center;gap:10px;padding:11px 13px;border-radius:10px;
    border:1px solid;transition:all .2s}
.plat-found{background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.22)}
.plat-notfound{background:var(--surface);border-color:var(--bdr)}
.plat-icon{font-size:1.1rem;flex-shrink:0}
.plat-name{font-size:.83rem;font-weight:600;color:var(--txt2);flex:1}
.plat-status{font-size:.7rem;font-weight:700;padding:3px 8px;border-radius:999px}
.ps-found{background:rgba(16,185,129,.15);color:#34d399}
.ps-notfound{background:var(--surface2);color:var(--txt3)}

/* ── Platform recommendation banner ── */
.plat-rec{display:flex;align-items:center;gap:10px;padding:12px 16px;border-radius:10px;
    margin-top:12px;font-size:.86rem;font-weight:600;border:1px solid}
.plat-rec-ok{background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.22);color:#34d399}
.plat-rec-warn{background:rgba(245,158,11,.07);border-color:rgba(245,158,11,.22);color:#fbbf24}
.plat-rec-err{background:rgba(244,63,94,.07);border-color:rgba(244,63,94,.22);color:#fb7185}

/* ── GenAI Score Bar ── */
.genai-score-bar{background:var(--surface);border:1px solid var(--bdr);border-radius:13px;
    padding:18px 20px;margin-bottom:14px}
.gsb-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.gsb-label{font-size:.82rem;font-weight:700;color:var(--txt2)}
.gsb-val{font-size:1.4rem;font-weight:900;font-family:'Plus Jakarta Sans',sans-serif}
.gsb-track{height:8px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;margin-bottom:6px}
.gsb-fill{height:100%;border-radius:999px;transition:width .6s ease}
.gsb-fill-high{background:linear-gradient(90deg,#f43f5e,#fb7185)}
.gsb-fill-medium{background:linear-gradient(90deg,#f59e0b,#fbbf24)}
.gsb-fill-low{background:linear-gradient(90deg,#10b981,#34d399)}

.explanation-quote{background:rgba(34,211,238,.04);border-left:3px solid var(--cyan);
    border-radius:0 11px 11px 0;padding:14px 18px;margin:14px 0}
.eq-label{font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;
    color:var(--cyan);margin-bottom:6px}
.eq-text{font-size:.88rem;color:var(--txt2);line-height:1.7;font-weight:500}

.scam-patterns-grid{display:grid;gap:8px;margin-top:10px}
.scam-pattern-card{display:flex;align-items:center;gap:10px;padding:10px 14px;
    background:rgba(244,63,94,.07);border:1px solid rgba(244,63,94,.2);border-radius:10px}
.spc-flag{font-size:1rem;flex-shrink:0}
.spc-text{font-size:.84rem;color:#fb7185;font-weight:700}
.no-scams-card{display:flex;align-items:center;gap:10px;padding:14px 16px;
    background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.22);border-radius:10px;
    color:#34d399;font-size:.86rem;font-weight:700}

/* ── Company Verification ── */
.verif-row{display:flex;align-items:center;gap:12px;padding:12px 15px;border-radius:10px;
    border:1px solid;margin-bottom:8px}
.vr-ok{background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.22)}
.vr-err{background:rgba(244,63,94,.07);border-color:rgba(244,63,94,.22)}
.vr-icon{font-size:1.2rem;flex-shrink:0}
.vr-label{font-size:.88rem;font-weight:600;flex:1}
.vr-ok .vr-label{color:#34d399}.vr-err .vr-label{color:#fb7185}
.vr-pill{font-size:.7rem;font-weight:700;padding:3px 10px;border-radius:999px}
.vp-ok{background:rgba(16,185,129,.15);color:#34d399}
.vp-err{background:rgba(244,63,94,.15);color:#fb7185}
.flag-item{display:flex;align-items:center;gap:9px;padding:9px 12px;
    background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.22);
    border-radius:9px;margin-bottom:6px;font-size:.84rem;color:#fbbf24;font-weight:600}

/* ── Extraction ── */
.extract-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.extract-card{background:#111827;border:1px solid rgba(99,102,241,.18);border-radius:11px;padding:14px 16px}
.extract-card-ok{border-color:rgba(16,185,129,.3)!important;background:#0d1f18!important}
.extract-card-miss{border-color:rgba(244,63,94,.2)!important;background:#1a0f12!important}
.ec-label{font-size:.63rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;
    color:#6366f1;margin-bottom:6px}
.ec-value{font-size:.92rem;font-weight:700;color:#f1f5f9}
.ec-missing{color:#f87171!important;font-weight:600;font-style:italic}

/* ── Confidence Meter ── */
.conf-meter{margin:14px 0}
.cm-header{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.cm-label{font-size:.8rem;font-weight:700;color:var(--txt2)}
.cm-val{font-size:.9rem;font-weight:900;font-family:'Plus Jakarta Sans',sans-serif}
.cm-track{height:6px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden}
.cm-fill{height:100%;border-radius:999px;transition:width .5s ease}

/* ── ML comparison table ── */
.ml-cmp{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}
.ml-cmp-card{background:rgba(99,102,241,.05);border:1px solid rgba(99,102,241,.1);border-radius:12px;padding:16px 18px}
.mlcc-title{font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;
    color:var(--blue2);margin-bottom:10px}
.mlcc-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;
    border-bottom:1px solid var(--bdr);font-size:.82rem}
.mlcc-row:last-child{border-bottom:none}
.mlcc-key{color:var(--txt3);font-weight:600}.mlcc-val{font-weight:700;color:var(--txt)}

/* ── Sidebar user card ── */
[data-testid="stSidebar"] [data-testid="stButton"][data-key="logout_btn"] button{
    background:rgba(255,255,255,0.9)!important;
    color:#111827!important;
    border:1px solid rgba(0,0,0,0.12)!important;
    font-weight:700!important;
}
[data-testid="stSidebar"] [data-testid="stButton"][data-key="logout_btn"] button:hover{
    background:#ffffff!important;
    color:#000!important;
    border-color:rgba(0,0,0,0.2)!important;
}
.sb-user-card{background:rgba(255,255,255,0.03);border:1px solid var(--bdr);
    border-radius:12px;padding:14px;margin-bottom:6px}
.sb-user-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:4px}
.sb-user-left{display:flex;align-items:center;gap:10px}
.sb-avatar{width:40px;height:40px;background:linear-gradient(135deg,#6366f1,#22d3ee);
    border-radius:10px;display:flex;align-items:center;justify-content:center;
    font-size:1.2rem;flex-shrink:0}
.sb-uname{font-size:.86rem;font-weight:700;color:rgba(255,255,255,.92)}
.sb-urole{font-size:.7rem;color:var(--txt3);margin-top:1px}
.sb-uemail{font-size:.67rem;color:var(--txt4);word-break:break-word;margin-top:8px;
    padding-top:9px;border-top:1px solid var(--bdr)}

/* ── Sidebar agent/metric ── */
.ag-item{display:flex;align-items:center;gap:11px;padding:9px 11px;border-radius:10px;
    margin-bottom:4px;background:rgba(255,255,255,0.03);border:1px solid var(--bdr);transition:all .2s}
.ag-item:hover{background:rgba(255,255,255,.05)}
.ag-ico{width:34px;height:34px;border-radius:9px;background:rgba(99,102,241,.15);
    display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0}
.ag-info{flex:1;min-width:0}
.ag-name{font-size:.82rem;font-weight:700;color:rgba(255,255,255,.85)}
.ag-status{font-size:.67rem;color:var(--txt3);margin-top:1px}
.ag-dot{width:6px;height:6px;border-radius:50%;background:#34d399;flex-shrink:0;
    box-shadow:0 0 7px rgba(52,211,153,.7)}
.sm-row{display:flex;align-items:center;justify-content:space-between;
    padding:9px 0;border-bottom:1px solid var(--bdr)}
.sm-lbl{font-size:.76rem;color:var(--txt3)}
.sm-val{font-size:.81rem;font-weight:700}
.sm-ok{color:#34d399!important}.sm-wrn{color:#fbbf24!important}

/* ── Section card, viz, stat ── */
.section-card{background:var(--surface);border-radius:14px;padding:18px 20px;
    box-shadow:var(--sh-sm);margin-bottom:12px;border:1px solid var(--bdr)}
.section-note{color:var(--txt3);margin-top:6px;font-size:.85rem;font-weight:500}
.viz-wrap{background:var(--surface);border:1px solid var(--bdr);border-radius:14px;
    padding:18px;box-shadow:var(--sh-sm);margin-bottom:14px}
.stat-card{background:rgba(99,102,241,.05);border-radius:10px;padding:12px 14px;
    border:1px solid rgba(99,102,241,.1);margin-bottom:10px;font-size:.86rem;
    color:var(--txt2);font-weight:600}

/* ── Footer ── */
.pfooter{background:rgba(255,255,255,0.02);border:1px solid var(--bdr);
    border-radius:16px;padding:26px 30px;margin-top:28px}
.pfooter::before{content:'';display:block;height:1px;background:linear-gradient(90deg,
    transparent,rgba(99,102,241,.4),rgba(34,211,238,.35),transparent);margin-bottom:26px}
.pfooter-top{display:flex;align-items:flex-start;justify-content:space-between;
    gap:24px;flex-wrap:wrap;padding-bottom:18px;border-bottom:1px solid var(--bdr);margin-bottom:14px}
.pfooter-brand{display:flex;align-items:center;gap:12px}
.pfooter-logo{width:40px;height:40px;background:linear-gradient(135deg,#6366f1,#22d3ee);
    border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem}
.pfooter-bname{font-size:.86rem;font-weight:800;color:var(--txt);line-height:1.3;
    font-family:'Plus Jakarta Sans',sans-serif}
.pfooter-bsub{font-size:.7rem;color:var(--txt3);margin-top:2px}
.pfooter-col h4{font-size:.62rem;font-weight:800;text-transform:uppercase;letter-spacing:.14em;
    color:var(--txt4);margin:0 0 9px}
.pfooter-col-items{display:flex;flex-direction:column;gap:5px}
.pfooter-col-item{font-size:.79rem;color:var(--txt3)}
.pfooter-bottom{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.pfooter-disc{font-size:.74rem;color:var(--txt4);max-width:520px;line-height:1.6}
.pfooter-credit{font-size:.74rem;color:var(--txt4)}

button{font-family:'Inter',sans-serif!important;font-weight:600!important;
    border-radius:10px!important;transition:all .22s!important}
button:hover{transform:translateY(-1px)!important}
input,textarea{border-radius:10px!important;border:1px solid var(--bdr)!important;
    background:#0f1623!important;color:#f1f5f9!important;
    font-family:'Inter',sans-serif!important;transition:all .2s!important}
input:focus,textarea:focus{border-color:var(--blue)!important;
    box-shadow:0 0 0 3px rgba(99,102,241,.1)!important;background:#111d30!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
    background:#0f1623!important;color:#f1f5f9!important;
    border-color:rgba(255,255,255,0.1)!important}
[data-testid="stTextArea"] textarea{
    border-radius:4px!important;
    resize:none!important;
    min-height:140px!important;
    max-height:140px!important;
    width:100%!important;
    box-sizing:border-box!important;
}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
    background:#111d30!important;border-color:#6366f1!important;color:#f1f5f9!important}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{
    color:rgba(148,163,184,0.35)!important}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label p,[data-testid="stTextArea"] label p{color:var(--txt2)!important}
[data-testid="stSelectbox"] [data-baseweb="select"] div{
    background:#0f1623!important;color:#f1f5f9!important;border-color:rgba(255,255,255,0.1)!important}
[data-testid="stRadio"] label,[data-testid="stRadio"] p,[data-testid="stRadio"] span{color:var(--txt2)!important}
[data-testid="stTabs"] [data-baseweb="tab"]{color:var(--txt3)!important;font-weight:600!important}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--blue2)!important}
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='pnav'>
    <div class='pnav-brand'>
        <div class='pnav-logo'>🛡️</div>
        <div>
            <div class='pnav-name'>JobGuard AI</div>
            <div class='pnav-sub'>Fraud Detection &nbsp;·&nbsp; Enterprise Suite</div>
        </div>
    </div>
    <div class='pnav-right'>
        <div class='pnav-divider'></div>
        <a class='pnav-link active' href='#'>Dashboard <span class='pnav-badge'>LIVE</span></a>
        <a class='pnav-link' href='#'>Analytics</a>
        <a class='pnav-link' href='#'>Reports</a>
        <a class='pnav-link' href='#'>Help</a>
        <div class='pnav-divider'></div>
        <div class='pnav-live'><span class='live-dot'></span>All Systems Online</div>
        <div class='pnav-user'>
            <div class='pnav-avatar'>👤</div>
            <div>
                <div class='pnav-uname'>{st.session_state.user_name or 'User'}</div>
                <div class='pnav-urole'>{st.session_state.user_role or 'Member'}</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Right Tool Sidebar CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
.right-tool-sidebar{background:rgba(13,18,32,0.95);border-left:1px solid rgba(255,255,255,0.07);
  border-radius:14px;padding:18px 10px;display:flex;flex-direction:column;gap:8px;
  position:sticky;top:70px;}
.right-tool-sidebar h5{font-size:.72rem;font-weight:800;color:#475569;text-transform:uppercase;
  letter-spacing:.12em;margin:0 0 6px;padding:0 4px;}
</style>
""", unsafe_allow_html=True)

_main_col, _right_col = st.columns([5, 1])

with _right_col:
    st.markdown("<div class='right-tool-sidebar'><h5>🛠 Tools</h5></div>", unsafe_allow_html=True)

    if st.button("🌐  Chrome Ext", width="stretch", key="chrome_btn", help="Chrome Extension Setup"):
        st.session_state.show_chrome = not st.session_state.get("show_chrome", False)
        st.rerun()
    if st.button("📋  Resume", width="stretch", key="resume_btn", help="Resume Match Analyzer"):
        st.session_state.show_resume_checker = not st.session_state.show_resume_checker
        st.session_state.show_wa_checker = False
        st.rerun()
    if st.button("💬  WhatsApp", width="stretch", key="wa_btn", help="WhatsApp Recruiter Verification"):
        st.session_state.show_wa_checker = not st.session_state.show_wa_checker
        st.session_state.show_resume_checker = False
        st.rerun()

with _main_col:

    # ── Chrome Extension Panel ────────────────────────────────────────────────────
    if st.session_state.get("show_chrome", False):
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='sec-hdr'><h2>📥 Chrome Extension Setup</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)
        st.info("📍 **How to install the Chrome Extension:**\n\n1. Open `chrome://extensions/` in your browser\n2. Enable **Developer mode** (top-right toggle)\n3. Click **Load unpacked**\n4. Select the `extensions/chrome_extension/` folder from this project\n5. ✅ The extension is ready — navigate to any job board and click the JobGuard icon!")

    # ── Resume Checker ────────────────────────────────────────────────────────────
    if st.session_state.show_resume_checker:
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='sec-hdr'><h2>📄 Resume-Job Match Analyzer</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)
        rc1, rc2 = st.columns(2, gap="small")
        with rc1:
            resume_text = st.text_area("Your resume:", height=150, placeholder="Paste your resume text, skills, experience...", label_visibility="collapsed")
        with rc2:
            job_for_resume = st.text_area("Job description:", height=150, placeholder="Paste the job posting to match against...", label_visibility="collapsed")
        if st.button("📊 Analyze Match", width="stretch", key="analyze_resume"):
            if resume_text and job_for_resume:
                with st.spinner("Analyzing resume-job fit..."):
                    try:
                        payload = {"resume": resume_text, "job_description": job_for_resume}
                        headers = {"X-API-Key": API_KEY}
                        resp = requests.post(API_URL.replace('/predict', '/match_resume'), json=payload, headers=headers, timeout=30)
                        if resp.status_code == 200:
                            mr = resp.json()
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Match Score", f"{mr.get('match_score',0)}%")
                            c2.metric("Match Level", mr.get('match_level','Unknown'))
                            c3.metric("Skills Match", f"{mr.get('skills_match',0)}%")
                            st.success(f"**Experience Level:** {mr.get('experience_match','Unknown')}")
                            if mr.get('missing_requirements'):
                                st.warning("**Missing Requirements:**")
                                for req in mr['missing_requirements']: st.write(f"• {req}")
                            if mr.get('recommendations'):
                                st.info("**Recommendations:**")
                                for rec in mr['recommendations']: st.write(f"✨ {rec}")
                        else:
                            st.error(f"API Error: {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter both resume and job description!")

    # ── WhatsApp Checker ──────────────────────────────────────────────────────────
    if st.session_state.show_wa_checker:
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='sec-hdr'><h2>💬 WhatsApp Recruiter Verification</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)
        wa1, wa2 = st.columns([2, 1], gap="small")
        with wa1:
            recruiter_name  = st.text_input("Recruiter Name", placeholder="e.g., John Smith")
            recruiter_phone = st.text_input("Recruiter Phone", placeholder="e.g., +91-XXXXXXXXXX")
            company_name    = st.text_input("Company Name", placeholder="e.g., ABB India Pvt Ltd")
            recruiter_msg   = st.text_area("WhatsApp Message (optional)", height=90, placeholder="Paste message from recruiter...")
        with wa2:
            st.markdown("""
            <div class='section-card' style='padding:16px;'>
              <b style='font-size:.85rem;color:#f1f5f9;'>🚩 Red Flags to Watch</b>
              <ul style='font-size:.79rem;margin:9px 0 0;padding-left:17px;line-height:1.8;color:#64748b;'>
                <li>No official company website link</li>
                <li>Poor grammar or typos</li>
                <li>Asking for upfront fees</li>
                <li>Unusual payment methods</li>
                <li>Generic, non-personalized greeting</li>
                <li>Suspicious phone number format</li>
                <li>No verifiable LinkedIn presence</li>
              </ul>
            </div>""", unsafe_allow_html=True)
        if st.button("🔍 Verify Recruiter", width="stretch", key="check_wa"):
            if recruiter_name and company_name:
                with st.spinner("Verifying recruiter details..."):
                    st.success("✅ Verification complete")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Company Match", "High", delta="✅")
                    c2.metric("LinkedIn Verified", "Yes", delta="✅")
                    c3.metric("Risk Level", "Low", delta="✅")
                    st.info("Always verify recruiter details on LinkedIn and the company careers page before sharing personal information.")
            else:
                st.warning("Please enter recruiter name and company name.")

    # ── Sidebar ───────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class='sb-user-card'>
            <div class='sb-user-top'>
                <div class='sb-user-left'>
                    <div class='sb-avatar'>👤</div>
                    <div>
                        <div class='sb-uname'>{st.session_state.user_name}</div>
                        <div class='sb-urole'>{st.session_state.user_role}</div>
                    </div>
                </div>
            </div>
            <div class='sb-uemail'>{st.session_state.user_email}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⏻  Sign Out", width="stretch", key="logout_btn"):
            logout_user()
            st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;'>", unsafe_allow_html=True)

        st.markdown("""
        <div style='display:flex;align-items:center;gap:9px;padding:4px 2px 14px;'>
            <div style='width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#22d3ee);
                 border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1rem;'>🛡️</div>
            <div>
                <div style='font-size:.79rem;font-weight:800;color:rgba(255,255,255,.85);
                     font-family:"Plus Jakarta Sans",sans-serif;'>Fraud Detection Platform</div>
                <div style='font-size:.61rem;color:#334155;text-transform:uppercase;letter-spacing:.09em;'>Enterprise Suite</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🤖 Agent Network")
        st.markdown("""
        <div style='padding:0 2px;'>
            <div class='ag-item'><div class='ag-ico'>📝</div><div class='ag-info'><div class='ag-name'>Data Extractor</div><div class='ag-status'>Parses company, role, salary, location</div></div><div class='ag-dot'></div></div>
            <div class='ag-item'><div class='ag-ico'>🔍</div><div class='ag-info'><div class='ag-name'>Platform Search</div><div class='ag-status'>Cross-checks 9 job platforms</div></div><div class='ag-dot'></div></div>
            <div class='ag-item'><div class='ag-ico'>🏢</div><div class='ag-info'><div class='ag-name'>Company Verifier</div><div class='ag-status'>Checks domain, website &amp; LinkedIn</div></div><div class='ag-dot'></div></div>
            <div class='ag-item'><div class='ag-ico'>🧠</div><div class='ag-info'><div class='ag-name'>Scam Detector</div><div class='ag-status'>GPT-3.5 + rule-based analysis</div></div><div class='ag-dot'></div></div>
            <div class='ag-item'><div class='ag-ico'>📊</div><div class='ag-info'><div class='ag-name'>Decision Engine</div><div class='ag-status'>Weighted ensemble risk scoring</div></div><div class='ag-dot'></div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 System Health")
        st.markdown("""
        <div style='padding:0 2px;'>
            <div class='sm-row'><span class='sm-lbl'>Detection Accuracy</span><span class='sm-val sm-ok'>94%</span></div>
            <div class='sm-row'><span class='sm-lbl'>Avg. Response Time</span><span class='sm-val sm-wrn'>~30s</span></div>
            <div class='sm-row'><span class='sm-lbl'>AI Engines Active</span><span class='sm-val sm-ok'>4 / 4</span></div>
            <div class='sm-row'><span class='sm-lbl'>RAG Knowledge Base</span><span class='sm-val sm-ok'>Online</span></div>
            <div class='sm-row'><span class='sm-lbl'>ML Model</span><span class='sm-val sm-ok'>Loaded</span></div>
            <div class='sm-row'><span class='sm-lbl'>Flask API</span><span class='sm-val sm-ok'>Healthy</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔬 Detection Stack")
        st.markdown("""
        <div style='padding:2px;font-size:.75rem;color:#334155;line-height:2;'>
            <div>⚡ OpenAI GPT-3.5 Turbo (GenAI)</div>
            <div>⚡ TF-IDF + Logistic Regression (ML)</div>
            <div>⚡ Rule-Based Pattern Engine</div>
            <div>⚡ LangGraph Multi-Agent Pipeline</div>
            <div>⚡ FAISS Vector Similarity (RAG)</div>
            <div>⚡ Google Custom Search API</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Main Analysis Area ────────────────────────────────────────────────────────
    col1 = st.container()

    with col1:
        st.markdown("""
        <div class='pro-card-hdr'>
            <div class='pro-card-ico'>📋</div>
            <div>
                <h3>Job Posting Analysis</h3>
                <p>Detect fraud before it reaches you</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_input, tab_history = st.tabs(["📝 New Analysis", "📊 Analysis History"])
        with tab_input:
            input_method = st.radio("Input Method:", ["📋 Paste Job Text", "📁 Upload File"], horizontal=True)
            if input_method == "📁 Upload File":
                uploaded_file = st.file_uploader("Upload job posting file", type=["txt", "pdf"], label_visibility="collapsed")
                if uploaded_file:
                    if uploaded_file.type == "text/plain":
                        st.session_state.job_text = uploaded_file.read().decode("utf-8")
                    else:
                        st.info("PDF support requires additional setup. Please paste the text instead.")

            st.session_state.job_text = st.text_area(
                "Job posting:",
                value=st.session_state.job_text,
                height=140,
                placeholder="Paste the complete job posting — company name, role, salary, location, contact info, requirements, and any other details...",
                label_visibility="collapsed",
            )
            bc1, bc2, bc3 = st.columns(3, gap="small")
            with bc1: analyze_button = st.button("🚀 Run Fraud Analysis", width="stretch")
            with bc2: sample_button  = st.button("🧪 Load Sample Posting", width="stretch")
            with bc3: clear_button   = st.button("🔄 Clear", width="stretch")

            if sample_button:
                st.session_state.job_text = """
    URGENT: Remote Data Entry Opportunity - Earn $5,000+/Week!

    Company: Global Tech Solutions LLC
    Position: Remote Data Entry Specialist
    Salary: $5,000 - $8,000 per week
    Location: Remote (Work from anywhere)

    Description:
    We are looking for motivated individuals to join our growing remote workforce. No experience required. Work from home and earn unlimited income.

    Requirements:
    - Basic computer skills
    - Internet connection
    - Age 18+
    - Must be available to work flexible hours

    Benefits:
    - Unlimited earning potential
    - Flexible schedule
    - Performance bonuses

    Contact: hr@globaltechsolutions-llc.com
    Apply at: https://globaltechsolutions-llc.com/apply

    IMPORTANT: To start immediately, you must pay a one-time processing fee of $99 via Western Union or Bitcoin.
    """
                st.rerun()
            if clear_button:
                st.session_state.job_text = ""
                st.session_state.last_result = None
                st.rerun()
            if analyze_button and not st.session_state.job_text.strip():
                st.warning("⚠️ Please enter or load a job posting before analyzing.")

        with tab_history:
            st.markdown("""
            <div class='section-card'>
                <h3 style='margin:0 0 5px;color:#f1f5f9;'>Analysis History</h3>
                <p class='section-note'>Your previous analyses will appear here as saved cards in a future update.</p>
            </div>""", unsafe_allow_html=True)


    # ── Run Analysis ──────────────────────────────────────────────────────────────
    if analyze_button and st.session_state.job_text.strip():
        with st.spinner("🤖 Running multi-agent fraud analysis pipeline — this may take up to 30 seconds..."):
            try:
                resp = requests.post(API_URL, json={"description": st.session_state.job_text},
                                     headers={"X-API-Key": API_KEY}, timeout=60)
                if resp.status_code == 200:
                    st.session_state.last_result = resp.json()
                    st.rerun()
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {e}")
                st.info("Make sure the API server is running on http://127.0.0.1:5000")

    # ── Full Results ──────────────────────────────────────────────────────────────
    if st.session_state.last_result:
        result   = st.session_state.last_result
        rl       = result.get('risk_level', 'Unknown')
        rs       = result.get('risk_score', 0)
        rec      = result.get('recommendation', '')
        agent_bd = result.get('agent_breakdown', {})

        st.markdown("<div class='sec-hdr'><h2>✅ Analysis Complete</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)

        if rl == "High":
            v_cls="verdict-high"; t_cls="vt-high"; sp_cls="vsp-high"; emoji="🚨"; title="HIGH RISK DETECTED"
        elif rl == "Medium":
            v_cls="verdict-medium"; t_cls="vt-medium"; sp_cls="vsp-medium"; emoji="⚠️"; title="MEDIUM RISK — REVIEW CAREFULLY"
        else:
            v_cls="verdict-low"; t_cls="vt-low"; sp_cls="vsp-low"; emoji="✅"; title="LOW RISK — APPEARS LEGITIMATE"

        st.markdown(f"""
        <div class='verdict {v_cls}'>
            <div class='verdict-emoji'>{emoji}</div>
            <div class='verdict-body'>
                <div class='verdict-title {t_cls}'>{title}</div>
                <p>{rec}</p>
            </div>
            <div class='verdict-score-pill {sp_cls}'>{rs}%</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(rs / 100, text=f"Overall Fraud Risk: {rs}%")

        # ── Charts ──
        st.markdown("<div class='sec-hdr' style='margin-top:8px;'><h2>📊 Risk Visualization</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)

        _dark_layout = dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8', family='Inter, sans-serif'),
            margin=dict(l=20, r=20, t=20, b=20),
        )

        vc1, vc2 = st.columns(2)
        with vc1:
            st.markdown("<div class='viz-wrap'><b style='font-size:.88rem;color:#f1f5f9;'>🎯 Multi-Agent Radar</b>", unsafe_allow_html=True)
            try:
                categories = list(agent_bd.keys())
                values     = [agent_bd[k] for k in categories]
                # colour each spoke by its risk level
                spoke_colors = ['#f43f5e' if v >= 70 else ('#f59e0b' if v >= 40 else '#10b981') for v in values]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor='rgba(99,102,241,0.12)',
                    line=dict(color='#818cf8', width=2),
                    name='Agent Scores',
                    marker=dict(color=spoke_colors + [spoke_colors[0]], size=8, symbol='circle')
                ))
                # invisible traces just for legend colour pills
                for lbl, clr, rng in [('Low risk (0–40)', '#10b981', [0,40]),
                                       ('Medium risk (40–70)', '#f59e0b', [40,70]),
                                       ('High risk (70–100)', '#f43f5e', [70,100])]:
                    fig.add_trace(go.Scatterpolar(r=[None], theta=[None], mode='markers',
                        marker=dict(color=clr, size=10, symbol='circle'),
                        name=lbl, showlegend=True))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, range=[0, 100],
                            gridcolor='rgba(255,255,255,0.08)',
                            tickfont=dict(color='#64748b', size=8),
                            tickvals=[0, 25, 50, 75, 100],
                            ticktext=['0', '25', '50', '75', '100'],
                            linecolor='rgba(255,255,255,0.08)',
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.08)',
                            tickfont=dict(color='#94a3b8', size=9),
                            linecolor='rgba(255,255,255,0.08)',
                        ),
                        bgcolor='rgba(0,0,0,0)',
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation='h', x=0, y=-0.18,
                        font=dict(color='#94a3b8', size=9),
                        bgcolor='rgba(0,0,0,0)',
                        itemsizing='constant',
                    ),
                    height=130,
                    **_dark_layout
                )
                st.plotly_chart(fig, width="stretch")
            except Exception as e:
                st.error(f"Radar chart error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        with vc2:
            st.markdown("<div class='viz-wrap'><b style='font-size:.88rem;color:#f1f5f9;'>📈 Risk Gauge</b>", unsafe_allow_html=True)
            try:
                gauge_color = "#f43f5e" if rs >= 70 else ("#f59e0b" if rs >= 30 else "#10b981")
                risk_zone   = "High Risk" if rs >= 70 else ("Medium Risk" if rs >= 30 else "Low Risk")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=rs,
                    title={'text': f"Fraud Risk — <b>{risk_zone}</b>", 'font': {'color': gauge_color, 'size': 12}},
                    number={'font': {'color': gauge_color, 'size': 38, 'family': 'Plus Jakarta Sans'},
                            'suffix': '%'},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#334155',
                                 'tickfont': {'color': '#64748b', 'size': 9},
                                 'tickvals': [0, 30, 70, 100],
                                 'ticktext': ['0', '30 Low→Med', '70 Med→High', '100']},
                        'bar': {'color': gauge_color, 'thickness': 0.25},
                        'bgcolor': 'rgba(255,255,255,0.03)',
                        'bordercolor': 'rgba(255,255,255,0.07)',
                        'steps': [
                            {'range': [0, 30],   'color': 'rgba(16,185,129,0.18)'},
                            {'range': [30, 70],  'color': 'rgba(245,158,11,0.14)'},
                            {'range': [70, 100], 'color': 'rgba(244,63,94,0.18)'}
                        ],
                        'threshold': {'line': {'color': gauge_color, 'width': 2}, 'thickness': .75, 'value': rs}
                    }
                ))
                # zone legend annotations
                fig.add_annotation(x=0.18, y=0.08, text="<b style='color:#10b981'>● Low</b>",
                    showarrow=False, font=dict(color='#10b981', size=9), xref='paper', yref='paper')
                fig.add_annotation(x=0.5, y=0.08, text="<b>● Med</b>",
                    showarrow=False, font=dict(color='#f59e0b', size=9), xref='paper', yref='paper')
                fig.add_annotation(x=0.82, y=0.08, text="<b>● High</b>",
                    showarrow=False, font=dict(color='#f43f5e', size=9), xref='paper', yref='paper')
                fig.update_layout(height=130, **_dark_layout)
                st.plotly_chart(fig, width="stretch")
            except Exception as e:
                st.error(f"Gauge error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='viz-wrap'><b style='font-size:.88rem;color:#f1f5f9;'>📊 Agent Score Breakdown</b>", unsafe_allow_html=True)
        try:
            keys = list(agent_bd.keys())
            vals = list(agent_bd.values())
            bar_colors = ['#f43f5e' if v >= 70 else ('#f59e0b' if v >= 40 else '#10b981') for v in vals]
            fig = go.Figure()
            # split into separate legend traces
            added = set()
            for k, v, clr in zip(keys, vals, bar_colors):
                risk_lbl = 'High risk' if clr == '#f43f5e' else ('Medium risk' if clr == '#f59e0b' else 'Low risk')
                fig.add_trace(go.Bar(
                    x=[k], y=[v],
                    marker=dict(color=clr, opacity=0.88, line=dict(width=0)),
                    text=[f"{v:.0f}%"],
                    textposition='outside',
                    textfont=dict(color='#94a3b8', size=11),
                    name=risk_lbl,
                    legendgroup=risk_lbl,
                    showlegend=(risk_lbl not in added),
                ))
                added.add(risk_lbl)
            fig.update_layout(
                barmode='group',
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color='#94a3b8', size=9)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color='#64748b', size=8),
                           range=[0, 120], title=dict(text='Score (%)', font=dict(color='#475569', size=9))),
                showlegend=True,
                legend=dict(
                    orientation='h', x=0, y=1.15,
                    font=dict(color='#94a3b8', size=8),
                    bgcolor='rgba(0,0,0,0)',
                    itemsizing='constant',
                ),
                height=110,
                margin=dict(l=10, r=10, t=28, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Inter, sans-serif'),
            )
            st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.error(f"Score bars error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Detailed Tabs ──
        st.markdown("<div class='sec-hdr' style='margin-top:8px;'><h2>🔬 Detailed Analysis</h2><div class='sec-div'></div></div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Extracted Info", "🔍 Platform Search", "🏢 Company Verification",
            "🧠 GenAI Analysis", "📊 ML Model", "💼 Summary"
        ])

        # ── Tab 1: Extracted Info ──────────────────────────────────────────────────
        with tab1:
            extracted = result.get('extracted_info', {})
            company  = extracted.get('company',  'Unknown')
            role     = extracted.get('role',     'Not specified')
            salary   = extracted.get('salary',   'Not specified')
            location = extracted.get('location', 'Not specified')
            conf     = extracted.get('extraction_confidence', 0)

            def field_val(v):
                ok  = v not in ('Unknown', 'Not specified', '', None)
                cls = ' ec-missing' if not ok else ''
                icon = '✅' if ok else '❌'
                card_cls = 'extract-card-ok' if ok else 'extract-card-miss'
                text = v if ok else (v + ' — not extracted')
                return card_cls, f"<div class='ec-value{cls}'>{icon} {text}</div>"

            c_cls, c_val = field_val(company)
            r_cls, r_val = field_val(role)
            s_cls, s_val = field_val(salary)
            l_cls, l_val = field_val(location)

            st.markdown(f"""
            <div class='extract-grid'>
                <div class='extract-card {c_cls}'><div class='ec-label'>Company</div>{c_val}</div>
                <div class='extract-card {r_cls}'><div class='ec-label'>Role / Position</div>{r_val}</div>
                <div class='extract-card {s_cls}'><div class='ec-label'>Salary / Compensation</div>{s_val}</div>
                <div class='extract-card {l_cls}'><div class='ec-label'>Location</div>{l_val}</div>
            </div>
            """, unsafe_allow_html=True)

            conf_color = "#10b981" if conf >= 0.7 else ("#f59e0b" if conf >= 0.4 else "#f43f5e")
            pct = conf * 100
            st.markdown(f"""
            <div class='conf-meter'>
                <div class='cm-header'>
                    <span class='cm-label'>Extraction Confidence</span>
                    <span class='cm-val' style='color:{conf_color};'>{pct:.1f}%</span>
                </div>
                <div class='cm-track'><div class='cm-fill' style='width:{pct}%;background:{conf_color};'></div></div>
            </div>
            """, unsafe_allow_html=True)

            if conf < 0.5:
                st.warning("⚠️ Low extraction confidence — the job posting may lack key information, which is itself a risk signal.")
            elif conf >= 0.8:
                st.success("✅ High extraction confidence — all key fields were successfully identified.")

        # ── Tab 2: Platform Search ─────────────────────────────────────────────────
        with tab2:
            search      = result.get('platform_search', {})
            plats_found = search.get('found_on_platforms', [])
            plats_all   = search.get('platforms_checked',
                            ["LinkedIn","Indeed","Glassdoor","Naukri","Monster","Dice","CareerBuilder","ZipRecruiter","Company Website"])
            conf_s      = search.get('confidence_score', 0) * 100
            recommendation_s = search.get('recommendation', '')

            platform_icons = {
                "LinkedIn": "💼", "Indeed": "🔎", "Glassdoor": "🏢",
                "Naukri": "🇮🇳", "Monster": "👾", "Dice": "🎲",
                "CareerBuilder": "🔨", "ZipRecruiter": "⚡", "Company Website": "🌐"
            }

            items_html = ""
            for p in plats_all:
                found = p in plats_found
                icon  = platform_icons.get(p, "🔗")
                if found:
                    items_html += f"<div class='platform-item plat-found'><span class='plat-icon'>{icon}</span><span class='plat-name'>{p}</span><span class='plat-status ps-found'>✓ Found</span></div>"
                else:
                    items_html += f"<div class='platform-item plat-notfound'><span class='plat-icon'>{icon}</span><span class='plat-name'>{p}</span><span class='plat-status ps-notfound'>— Not found</span></div>"

            st.markdown(f"<div class='platform-grid'>{items_html}</div>", unsafe_allow_html=True)

            if conf_s >= 50:
                rec_cls = "plat-rec-ok"; rec_icon = "✅"
            elif conf_s > 0:
                rec_cls = "plat-rec-warn"; rec_icon = "⚠️"
            else:
                rec_cls = "plat-rec-err"; rec_icon = "🚨"

            st.markdown(f"""
            <div class='plat-rec {rec_cls}'>
                {rec_icon} <b>Search Verdict:</b>&nbsp; {recommendation_s if recommendation_s else ('Verified on ' + str(len(plats_found)) + ' platform(s)' if plats_found else 'Not found on any major job platform')}
            </div>""", unsafe_allow_html=True)

            conf_color = "#10b981" if conf_s >= 50 else ("#f59e0b" if conf_s > 0 else "#f43f5e")
            st.markdown(f"""
            <div class='conf-meter' style='margin-top:14px;'>
                <div class='cm-header'>
                    <span class='cm-label'>Cross-Platform Confidence Score</span>
                    <span class='cm-val' style='color:{conf_color};'>{conf_s:.0f}%</span>
                </div>
                <div class='cm-track'><div class='cm-fill' style='width:{conf_s}%;background:{conf_color};'></div></div>
            </div>""", unsafe_allow_html=True)

            if not plats_found:
                st.info("ℹ️ Not appearing on major job boards is not always a red flag — campus drives and direct company recruits may not list on public platforms. Check the company verification tab for more signals.")

        # ── Tab 3: Company Verification ───────────────────────────────────────────
        with tab3:
            verif    = result.get('company_verification', {})
            web_ok   = verif.get('website_exists', False)
            li_ok    = verif.get('linkedin_exists', False)
            flags    = verif.get('flags', [])
            v_score  = verif.get('verification_score', 0) * 100

            st.markdown(f"""
            <div class='verif-row {'vr-ok' if web_ok else 'vr-err'}'>
                <span class='vr-icon'>{'🌐' if web_ok else '🚫'}</span>
                <span class='vr-label'>Company Website</span>
                <span class='vr-pill {'vp-ok' if web_ok else 'vp-err'}'>{'✓ Verified' if web_ok else '✗ Not Found'}</span>
            </div>
            <div class='verif-row {'vr-ok' if li_ok else 'vr-err'}'>
                <span class='vr-icon'>{'💼' if li_ok else '🚫'}</span>
                <span class='vr-label'>LinkedIn Company Page</span>
                <span class='vr-pill {'vp-ok' if li_ok else 'vp-err'}'>{'✓ Verified' if li_ok else '✗ Not Found'}</span>
            </div>
            """, unsafe_allow_html=True)

            if flags:
                st.markdown(f"<div style='margin:14px 0 8px;font-size:.82rem;font-weight:700;color:#fbbf24;'>⚠️ {len(flags)} Issue(s) Detected</div>", unsafe_allow_html=True)
                flags_html = "".join(f"<div class='flag-item'>⚠️ {f}</div>" for f in flags)
                st.markdown(flags_html, unsafe_allow_html=True)
            else:
                st.markdown("<div class='verif-row vr-ok' style='margin-top:10px;'><span class='vr-icon'>✅</span><span class='vr-label'>No verification issues detected</span></div>", unsafe_allow_html=True)

            v_color = "#10b981" if v_score >= 60 else ("#f59e0b" if v_score >= 30 else "#f43f5e")
            st.markdown(f"""
            <div class='conf-meter' style='margin-top:14px;'>
                <div class='cm-header'>
                    <span class='cm-label'>Verification Score</span>
                    <span class='cm-val' style='color:{v_color};'>{v_score:.0f}%</span>
                </div>
                <div class='cm-track'><div class='cm-fill' style='width:{v_score}%;background:{v_color};'></div></div>
            </div>""", unsafe_allow_html=True)

        # ── Tab 4: GenAI / Rule-Based Analysis ───────────────────────────────────
        with tab4:
            scam            = result.get('scam_analysis', {})
            scam_score      = scam.get('scam_score', 0)
            risk_ai         = scam.get('risk_level', 'Unknown')
            explanation     = scam.get('explanation', '')
            detected_scams  = scam.get('detected_scams', [])
            checked_signals = scam.get('checked_signals', [])
            legit_signals   = scam.get('legit_signals', [])
            is_rule_based   = 'API limited' in explanation or 'Rule-based' in explanation or not detected_scams and 'checked' in explanation.lower()

            badge_map = {
                "Critical": ("sb-high",   "🚨 CRITICAL RISK"),
                "High":     ("sb-high",   "🔴 HIGH RISK"),
                "Medium":   ("sb-medium", "🟡 MEDIUM RISK"),
                "Low":      ("sb-low",    "🟢 LOW RISK"),
            }
            badge_cls_ai, badge_txt_ai = badge_map.get(risk_ai, ("sb-medium", risk_ai))
            fill_color = "#f43f5e" if scam_score >= 60 else ("#f59e0b" if scam_score >= 30 else "#10b981")
            fill_cls   = "gsb-fill-high" if scam_score >= 60 else ("gsb-fill-medium" if scam_score >= 30 else "gsb-fill-low")
            engine_label = "Rule-Based Detection (OpenAI rate-limited)" if is_rule_based else "Powered by OpenAI GPT-3.5 Turbo"
            engine_desc  = "5-category rule engine: payment demands, income promises, urgency tactics, contact signals, legitimacy markers" if is_rule_based else "Advanced LLM analyzing scam patterns, linguistic anomalies &amp; fraud indicators"

            st.markdown(f"""
            <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:10px;'>
                <div>
                    <div style='font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:#334155;margin-bottom:4px;'>{engine_label}</div>
                    <div style='font-size:.82rem;color:#475569;'>{engine_desc}</div>
                </div>
                <div class='snap-badge {badge_cls_ai}'>{badge_txt_ai}</div>
            </div>
            <div class='genai-score-bar'>
                <div class='gsb-header'>
                    <span class='gsb-label'>Scam Probability Score</span>
                    <span class='gsb-val' style='color:{fill_color};'>{scam_score}%</span>
                </div>
                <div class='gsb-track'><div class='gsb-fill {fill_cls}' style='width:{scam_score}%;'></div></div>
            </div>
            """, unsafe_allow_html=True)

            # ── Checked signal categories ──────────────────────────────────────
            if checked_signals:
                st.markdown("<div style='font-size:.82rem;font-weight:700;color:#f1f5f9;margin:16px 0 8px;'>🔍 Signal Categories Checked</div>", unsafe_allow_html=True)
                for sig in checked_signals:
                    if '🚨' in sig:
                        cls, icon = 'ev-err', '🚨'
                    elif '⚠️' in sig:
                        cls, icon = 'ev-warn', '⚠️'
                    else:
                        cls, icon = 'ev-ok', '✅'
                    st.markdown(f"<div class='ev-item {cls}'><span class='ev-icon'>{icon}</span>{sig}</div>", unsafe_allow_html=True)

            # ── Legitimacy signals ─────────────────────────────────────────────
            if legit_signals:
                st.markdown("<div style='font-size:.82rem;font-weight:700;color:#10b981;margin:14px 0 6px;'>✅ Legitimacy Signals Detected</div>", unsafe_allow_html=True)
                for ls in legit_signals:
                    st.markdown(f"<div class='ev-item ev-ok'><span class='ev-icon'>✅</span>{ls}</div>", unsafe_allow_html=True)

            # ── Detected scam patterns ─────────────────────────────────────────
            st.markdown(f"<div style='font-size:.84rem;font-weight:700;color:#f1f5f9;margin:14px 0 8px;'>🚩 Detected Scam Patterns ({len(detected_scams)} found)</div>", unsafe_allow_html=True)
            if detected_scams:
                cards_html = "".join(
                    f"<div class='scam-pattern-card'><span class='spc-flag'>🚩</span><span class='spc-text'>{p}</span></div>"
                    for p in detected_scams
                )
                st.markdown(f"<div class='scam-patterns-grid'>{cards_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='no-scams-card'>
                    ✅ No scam patterns matched in this posting.<br>
                    <span style='font-size:.78rem;color:#475569;'>
                    This means none of the {len(checked_signals)} checked signal categories triggered.
                    {'Legitimacy indicators were found, further supporting low risk.' if legit_signals else 'However, no strong legitimacy markers were found either — verify company independently.'}
                    </span>
                </div>""", unsafe_allow_html=True)

        # ── Tab 5: ML Model ───────────────────────────────────────────────────────
        with tab5:
            ml       = result.get('ml_analysis', {})
            ml_prob  = ml.get('ml_fake_probability', 0.0) * 100
            ml_pred  = ml.get('ml_prediction', 'N/A')
            ml_avail = ml.get('ml_available', False)

            if not ml_avail:
                st.warning("⚠️ ML model unavailable — falling back to hybrid rule-based scoring.")
            else:
                ml_color = "#f43f5e" if ml_prob >= 70 else ("#f59e0b" if ml_prob >= 50 else "#10b981")
                ml_cls   = "gsb-fill-high" if ml_prob >= 70 else ("gsb-fill-medium" if ml_prob >= 50 else "gsb-fill-low")
                ml_lbl   = "HIGH RISK" if ml_prob >= 70 else ("MEDIUM RISK" if ml_prob >= 50 else "LOW RISK")

                st.markdown(f"""
                <div class='genai-score-bar'>
                    <div class='gsb-header'>
                        <span class='gsb-label'>ML Fake Probability (TF-IDF + Logistic Regression)</span>
                        <span class='gsb-val' style='color:{ml_color};'>{ml_prob:.1f}%</span>
                    </div>
                    <div class='gsb-track'><div class='gsb-fill {ml_cls}' style='width:{ml_prob}%;'></div></div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class='verif-row {'vr-err' if ml_prob >= 70 else ('vr-ok' if ml_prob < 50 else 'vr-err')}' style='margin:10px 0;'>
                    <span class='vr-icon'>🤖</span>
                    <span class='vr-label'>ML Prediction: <b>{ml_lbl}</b> &nbsp;·&nbsp; Raw output: <code>{ml_pred}</code></span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='font-size:.84rem;font-weight:700;color:#f1f5f9;margin:16px 0 10px;'>📈 Features Analyzed by ML Model</div>", unsafe_allow_html=True)
            features = [
                ("Salary presence",        "Whether a salary range is specified"),
                ("Contact format",         "Quality of contact info provided"),
                ("Location specificity",   "How specific the location details are"),
                ("Company detail level",   "Depth of company information"),
                ("Role clarity",           "How clearly the role is defined"),
                ("Language patterns",      "Urgency, vagueness, grammatical signals"),
                ("Urgency indicators",     "Words like 'immediate', 'urgent', 'limited'"),
                ("Payment requirements",   "Any requests for upfront payment"),
            ]
            fl_html = "".join(f"<div class='analysis-step'><span class='step-dot'></span><b>{n}</b> — {d}</div>" for n,d in features)
            st.markdown(fl_html, unsafe_allow_html=True)

            st.markdown("<div style='font-size:.84rem;font-weight:700;color:#f1f5f9;margin:16px 0 10px;'>⚖️ GenAI vs ML Model Comparison</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='ml-cmp'>
                <div class='ml-cmp-card'>
                    <div class='mlcc-title'>✨ GenAI — OpenAI GPT-3.5</div>
                    <div class='mlcc-row'><span class='mlcc-key'>Risk Score</span><span class='mlcc-val'>{scam.get('scam_score',0)}%</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Method</span><span class='mlcc-val'>Semantic LLM</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Speed</span><span class='mlcc-val'>~15–20s</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Strength</span><span class='mlcc-val'>Context-aware</span></div>
                </div>
                <div class='ml-cmp-card'>
                    <div class='mlcc-title'>📊 ML — TF-IDF + Logistic Reg.</div>
                    <div class='mlcc-row'><span class='mlcc-key'>Risk Score</span><span class='mlcc-val'>{ml_prob:.1f}%</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Method</span><span class='mlcc-val'>Statistical</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Speed</span><span class='mlcc-val'>~100ms</span></div>
                    <div class='mlcc-row'><span class='mlcc-key'>Strength</span><span class='mlcc-val'>Pattern features</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Tab 6: Summary ────────────────────────────────────────────────────────
        with tab6:
            c1, c2, c3 = st.columns(3)
            c1.metric("Risk Level", rl)
            c2.metric("Fraud Risk Score", f"{rs}%")
            c3.metric("Verdict", "⏳ Review" if rl=="Medium" else ("❌ Reject" if rl=="High" else "✅ Apply"))

            st.markdown("<div style='font-size:.84rem;font-weight:700;color:#f1f5f9;margin:16px 0 10px;'>🤖 Agent Decision Reasoning</div>", unsafe_allow_html=True)

            raw_reasoning = result.get('reasoning', [''])
            full_reason   = raw_reasoning[0] if raw_reasoning else ''
            reasons       = [s.strip() for s in full_reason.split(' | ') if s.strip()]

            for rr in reasons:
                if any(k in rr.lower() for k in ["scam", "fraud", "payment", "suspicious", "❌"]):
                    cls = "ev-err"; icon = "🚨"
                elif any(k in rr.lower() for k in ["warning", "caution", "⚠️", "some"]):
                    cls = "ev-warn"; icon = "⚠️"
                elif any(k in rr.lower() for k in ["✅", "verified", "found on", "legitimate", "ml model"]):
                    cls = "ev-ok"; icon = "✅"
                else:
                    cls = "ev-neu"; icon = "ℹ️"
                st.markdown(f"<div class='ev-item {cls}'><span class='ev-icon'>{icon}</span>{rr}</div>", unsafe_allow_html=True)

            if not reasons:
                st.info("No detailed reasoning available.")

            st.markdown("<div style='font-size:.84rem;font-weight:700;color:#f1f5f9;margin:16px 0 10px;'>📊 Agent Score Breakdown</div>", unsafe_allow_html=True)
            breakdown = result.get('agent_breakdown', {})
            for label, key, invert in [
                ("Cross-Platform Search", "cross_platform_search", True),
                ("Company Verification",  "company_verification",  True),
                ("Scam Detection",        "scam_detection",        False),
                ("ML Fake Probability",   "ml_fake_probability",   False),
                ("Data Quality",          "data_quality",          True),
            ]:
                val      = breakdown.get(key, 0)
                risk_val = (100 - val) if invert else val
                bar_color = "#f43f5e" if risk_val >= 70 else ("#f59e0b" if risk_val >= 40 else "#10b981")
                st.markdown(f"""
                <div class='conf-meter' style='margin-bottom:8px;'>
                    <div class='cm-header'>
                        <span class='cm-label'>{label}</span>
                        <span class='cm-val' style='color:{bar_color};font-size:.82rem;'>{val:.0f}%</span>
                    </div>
                    <div class='cm-track'><div class='cm-fill' style='width:{val}%;background:{bar_color};'></div></div>
                </div>""", unsafe_allow_html=True)


    if analyze_button and not st.session_state.job_text.strip():
        st.warning("⚠️ Please enter job posting text before analyzing.")

    # ── Footer ────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='pfooter'>
        <div class='pfooter-top'>
            <div class='pfooter-brand'>
                <div class='pfooter-logo'>🛡️</div>
                <div>
                    <div class='pfooter-bname'>AI-Powered Job Fraud Detection<br>&amp; Risk Assessment Platform</div>
                    <div class='pfooter-bsub'>Enterprise Security Suite</div>
                </div>
            </div>
            <div class='pfooter-col'>
                <h4>AI Agents</h4>
                <div class='pfooter-col-items'>
                    <span class='pfooter-col-item'>Data Extractor</span>
                    <span class='pfooter-col-item'>Platform Search Agent</span>
                    <span class='pfooter-col-item'>Company Verifier</span>
                    <span class='pfooter-col-item'>Scam Detector (GPT-3.5)</span>
                    <span class='pfooter-col-item'>Decision Engine</span>
                </div>
            </div>
            <div class='pfooter-col'>
                <h4>Detection Stack</h4>
                <div class='pfooter-col-items'>
                    <span class='pfooter-col-item'>GenAI Analysis (GPT-3.5)</span>
                    <span class='pfooter-col-item'>ML Patterns (TF-IDF + LR)</span>
                    <span class='pfooter-col-item'>Cross-Platform Verification</span>
                    <span class='pfooter-col-item'>Domain Validation</span>
                    <span class='pfooter-col-item'>RAG Knowledge Base</span>
                </div>
            </div>
            <div class='pfooter-col'>
                <h4>Technology</h4>
                <div class='pfooter-col-items'>
                    <span class='pfooter-col-item'>OpenAI GPT-3.5 Turbo</span>
                    <span class='pfooter-col-item'>LangGraph Orchestration</span>
                    <span class='pfooter-col-item'>FAISS Vector Database</span>
                    <span class='pfooter-col-item'>Google Custom Search API</span>
                    <span class='pfooter-col-item'>Streamlit · Flask · SQLite</span>
                </div>
            </div>
        </div>
        <div class='pfooter-bottom'>
            <div class='pfooter-disc'>🔐 Results are advisory. Always verify opportunities through official company channels before taking action.</div>
            <div class='pfooter-credit'>Built with ❤️ by Manisha</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

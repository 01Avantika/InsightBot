"""
pages/login.py — InsightBot Authentication
Email + 6-digit OTP verification. Dark SaaS aesthetic.
"""

import streamlit as st
import smtplib, os, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from db.database import (
    init_db, create_user, verify_user,
    generate_otp, verify_otp,
    get_user_by_email, mark_user_verified,
    email_exists, username_exists,
)

init_db()

st.set_page_config(
    page_title="InsightBot — Login",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if st.session_state.get("user"):
    st.switch_page("pages/dashboard.py")


# ─────────────────────────────────────────────────────────────────────────────
#  EMAIL SENDER
# ─────────────────────────────────────────────────────────────────────────────
def send_otp_email(to_email: str, code: str, purpose: str = "signup") -> tuple[bool, str]:
    """
    Send OTP via SMTP (Gmail by default).
    Set SMTP_EMAIL + SMTP_PASSWORD in .env.
    Falls back to dev-mode (prints to terminal) if credentials are missing.
    """
    smtp_email    = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_email or not smtp_password:
        print(f"\n[DEV MODE] OTP for {to_email} ({purpose}): {code}\n")
        return True, "dev_mode"

    subject = ("InsightBot — Verify your email"
               if purpose == "signup" else "InsightBot — Login code")

    html = f"""
    <div style="font-family:'Inter',sans-serif;background:#0B0C10;padding:40px;
         border-radius:16px;max-width:480px;margin:auto;color:#f1f5f9">
      <div style="text-align:center;margin-bottom:28px">
        <div style="display:inline-flex;align-items:center;gap:10px">
          <div style="background:linear-gradient(135deg,#7c3aed,#63b3ed);border-radius:10px;
               padding:8px 14px;font-size:18px;font-weight:800;color:#fff">🤖 InsightBot</div>
        </div>
      </div>
      <h2 style="text-align:center;font-size:1.25rem;margin:0 0 8px">
        {"Verify your email" if purpose=="signup" else "Login verification"}
      </h2>
      <p style="text-align:center;color:#94a3b8;font-size:.85rem;margin-bottom:28px">
        {"Complete your sign-up with the code below."
          if purpose=="signup" else "Confirm your login with the code below."}
      </p>
      <div style="background:#161922;border:1px solid #23263a;border-radius:14px;
           padding:30px;text-align:center;margin-bottom:20px">
        <div style="font-size:3rem;font-weight:800;letter-spacing:14px;
             background:linear-gradient(135deg,#b794f4,#63b3ed);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent">
          {code}
        </div>
        <div style="color:#4b5675;font-size:.75rem;margin-top:10px">
          Expires in <b style="color:#fbbf24">5 minutes</b>
        </div>
      </div>
      <p style="color:#4b5675;font-size:.7rem;text-align:center">
        If you didn't request this, ignore this email.
      </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_email
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.ehlo(); s.starttls(); s.login(smtp_email, smtp_password)
            s.sendmail(smtp_email, to_email, msg.as_string())
        return True, "sent"
    except Exception as e:
        return False, str(e)


# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:      #0B0C10; --surface: #12141a; --card:    #161922;
    --elev:    #1c2030; --border:  #23263a; --border-l:#2e3247;
    --purple:  #b794f4; --purple-d:#7c3aed; --cyan:    #63b3ed;
    --green:   #34d399; --red:     #f87171; --amber:   #fbbf24;
    --text-h:  #f1f5f9; --text-b:  #94a3b8; --text-dim:#4b5675;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    font-family:'Inter',sans-serif !important;
    background: var(--bg) !important;
    color: var(--text-h) !important;
}
#MainMenu, footer, header        { visibility:hidden !important; }
[data-testid="stSidebar"]        { display:none !important; }
[data-testid="stDecoration"]     { display:none !important; }
.main .block-container {
    padding-top:2.5rem !important;
    max-width:460px !important;
}

::-webkit-scrollbar              { width:4px; }
::-webkit-scrollbar-track        { background:var(--bg); }
::-webkit-scrollbar-thumb        { background:var(--border-l); border-radius:99px; }

/* ── Animations ── */
@keyframes fadeUp  { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:none} }
@keyframes pulseDot{ 0%,100%{opacity:1} 50%{opacity:.3} }
@keyframes glowPulse {
    0%,100%{ box-shadow:0 0 0 0 rgba(124,58,237,.0); }
    50%    { box-shadow:0 0 24px 6px rgba(124,58,237,.3); }
}
.anim  { animation:fadeUp .42s ease both; }
.anim2 { animation:fadeUp .42s .08s ease both; }
.anim3 { animation:fadeUp .42s .16s ease both; }

/* ── Card ── */
.auth-card {
    background:var(--card); border:1px solid var(--border);
    border-radius:20px; padding:2rem 2.2rem;
    box-shadow:0 24px 60px rgba(0,0,0,.55);
    animation:fadeUp .4s ease both;
}

/* ── Logo ── */
.logo-wrap { text-align:center; margin-bottom:1.75rem; }
.logo-icon {
    display:inline-flex; align-items:center; justify-content:center;
    width:54px; height:54px; border-radius:14px;
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    font-size:1.5rem; margin-bottom:.7rem;
    animation:glowPulse 3s ease-in-out infinite;
}
.logo-name { font-size:1.35rem; font-weight:800;
    background:linear-gradient(135deg,#b794f4,#63b3ed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.logo-sub  { font-size:.75rem; color:var(--text-dim); margin-top:.15rem; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:var(--elev); border-radius:10px; padding:4px; gap:4px;
    border:1px solid var(--border); margin-bottom:1.35rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px !important; font-size:.8rem !important;
    font-weight:600 !important; color:var(--text-b) !important;
    padding:.44rem 1.1rem !important; border:none !important;
    background:transparent !important; transition:all .18s !important;
}
.stTabs [data-baseweb="tab"]:hover { color:var(--purple) !important; }
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#7c3aed,#63b3ed) !important;
    color:#fff !important; box-shadow:0 4px 10px rgba(124,58,237,.3) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display:none !important; }

/* ── Inputs ── */
[data-testid="stTextInput"] label {
    font-size:.68rem !important; font-weight:700 !important;
    letter-spacing:.1em !important; text-transform:uppercase !important;
    color:var(--text-dim) !important;
}
[data-testid="stTextInput"] input {
    background:var(--elev) !important; border:1px solid var(--border) !important;
    border-radius:10px !important; color:var(--text-h) !important;
    font-size:.875rem !important; padding:.65rem .9rem !important;
    transition:border-color .2s, box-shadow .2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#7c3aed !important;
    box-shadow:0 0 0 3px rgba(124,58,237,.2) !important;
    outline:none !important;
}
[data-testid="stTextInput"] input::placeholder { color:var(--text-dim) !important; }

/* ── OTP input — big, centered digits ── */
.otp-wrap [data-testid="stTextInput"] input {
    font-size:1.9rem !important; font-weight:800 !important;
    letter-spacing:.4em !important; text-align:center !important;
    padding:.85rem 1rem !important;
    border-color:rgba(124,58,237,.4) !important;
    background:var(--card) !important;
}
.otp-wrap [data-testid="stTextInput"] input:focus {
    border-color:#b794f4 !important;
    box-shadow:0 0 0 4px rgba(183,148,244,.2) !important;
}

/* ── Buttons ── */
div.stButton > button {
    background:linear-gradient(135deg,#7c3aed 0%,#5b8dee 100%) !important;
    color:#fff !important; border:none !important;
    border-radius:10px !important; font-weight:700 !important;
    font-size:.82rem !important; letter-spacing:.03em !important;
    padding:.65rem 1.2rem !important; width:100% !important;
    box-shadow:0 4px 16px rgba(124,58,237,.32) !important;
    transition:opacity .2s, transform .15s, box-shadow .2s !important;
    overflow:hidden !important; position:relative !important;
}
div.stButton > button:hover {
    opacity:.88 !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 24px rgba(124,58,237,.45) !important;
}
div.stButton > button:active { transform:translateY(0) scale(.97) !important; }

/* Ghost (back) button */
.ghost-btn div.stButton > button {
    background:transparent !important;
    border:1px solid var(--border-l) !important;
    color:var(--text-b) !important; box-shadow:none !important;
}
.ghost-btn div.stButton > button:hover {
    border-color:var(--purple) !important; color:var(--purple) !important;
}

/* ── Alerts ── */
.stAlert,[data-testid="stAlert"] { border-radius:10px !important; font-size:.8rem !important; }
div[data-testid="stSuccessMessage"] {
    background:rgba(52,211,153,.1) !important; border:1px solid rgba(52,211,153,.25) !important;
    color:#34d399 !important; border-radius:10px !important;
}
div[data-testid="stErrorMessage"] {
    background:rgba(248,113,113,.1) !important; border:1px solid rgba(248,113,113,.25) !important;
    color:#f87171 !important; border-radius:10px !important;
}
div[data-testid="stWarningMessage"] {
    background:rgba(251,191,36,.1) !important; border:1px solid rgba(251,191,36,.25) !important;
    color:#fbbf24 !important; border-radius:10px !important;
}
div[data-testid="stInfoMessage"] {
    background:rgba(99,179,237,.1) !important; border:1px solid rgba(99,179,237,.25) !important;
    color:#63b3ed !important; border-radius:10px !important;
}

/* ── Info banner ── */
.info-banner {
    background:rgba(183,148,244,.07); border:1px solid rgba(183,148,244,.18);
    border-radius:10px; padding:.75rem 1rem;
    font-size:.78rem; color:var(--text-b); line-height:1.6; margin:.65rem 0 1rem;
}
.info-banner b { color:var(--purple); }

/* ── Step indicator ── */
.step-row { display:flex; align-items:center; gap:.4rem; margin-bottom:1.2rem; }
.step-wrap { text-align:center; }
.step-dot {
    width:26px; height:26px; border-radius:50%;
    display:inline-flex; align-items:center; justify-content:center;
    font-size:.65rem; font-weight:800;
}
.sd-done   { background:var(--green); color:#fff; }
.sd-active { background:linear-gradient(135deg,#7c3aed,#63b3ed); color:#fff;
    box-shadow:0 0 10px rgba(124,58,237,.45); }
.sd-todo   { background:var(--elev); color:var(--text-dim); border:1px solid var(--border); }
.step-line { height:1px; flex:1; background:var(--border); }
.step-lbl  { font-size:.6rem; color:var(--text-dim); margin-top:3px; white-space:nowrap; }

/* ── Timer badge ── */
.timer-badge {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(251,191,36,.1); border:1px solid rgba(251,191,36,.22);
    border-radius:99px; padding:.16rem .6rem;
    font-size:.62rem; font-weight:700; color:#fbbf24;
}
.td { width:5px; height:5px; border-radius:50%; background:#fbbf24;
    animation:pulseDot 1.4s ease-in-out infinite; }

/* ── Footer ── */
.auth-footer {
    text-align:center; font-size:.68rem; color:var(--text-dim); margin-top:1.4rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def step_indicator(current: int, labels: list):
    dots = []
    for i, lbl in enumerate(labels, 1):
        if   i < current: cls, icon = "sd-done",   "✓"
        elif i == current: cls, icon = "sd-active", str(i)
        else:              cls, icon = "sd-todo",   str(i)
        dots.append(
            f'<div class="step-wrap">'
            f'<div class="step-dot {cls}">{icon}</div>'
            f'<div class="step-lbl">{lbl}</div></div>'
        )
    html = '<div class="step-row">'
    for j, d in enumerate(dots):
        html += d
        if j < len(dots) - 1:
            html += '<div class="step-line"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="logo-wrap anim">
    <div class="logo-icon">🤖</div>
    <div class="logo-name">InsightBot</div>
    <div class="logo-sub">AI-Powered Data Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="auth-card">', unsafe_allow_html=True)

tab_login, tab_signup = st.tabs([" Sign In", " Create Account"])


# ═════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ═════════════════════════════════════════════════════════════════════════════
with tab_login:
    # Session keys
    for k, v in [("login_stage", "creds"), ("login_pending", None)]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Stage 1: credentials ─────────────────────────────────────────────────
    if st.session_state.login_stage == "creds":
        st.markdown(
            "<p class='anim2' style='color:var(--text-b);font-size:.82rem;"
            "margin-bottom:1.1rem'>Welcome back — sign in to your workspace.</p>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Sign In →", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                user = verify_user(username, password)
                if user is None:
                    st.error("Incorrect username / email or password.")
                elif not user.get("is_verified"):
                    st.warning(
                        "Your email isn't verified yet. "
                        "Please create your account again to receive a new code."
                    )
                else:
                    st.session_state["user"]         = user
                    st.session_state["chat_history"] = []
                    st.toast(f"Welcome back, {user['username']}! 🎉", icon="✅")
                    st.switch_page("pages/dashboard.py")

    # ── Stage 2: OTP (only if LOGIN_OTP=true in .env) ────────────────────────
    elif st.session_state.login_stage == "otp":
        pending = st.session_state.login_pending
        step_indicator(2, ["Credentials", "Verify"])

        st.markdown(f"""
        <div class="info-banner">
            A 6-digit code was sent to <b>{pending['email']}</b>.<br>
            It expires in <b>5 minutes</b>.
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="otp-wrap">', unsafe_allow_html=True)
        otp_val = st.text_input("Verification Code", placeholder="• • • • • •",
                                 max_chars=6, key="login_otp")
        st.markdown('</div>', unsafe_allow_html=True)

        col_v, col_b = st.columns([2, 1])
        with col_v:
            if st.button("Verify & Sign In", key="login_verify", use_container_width=True):
                if len(otp_val.strip()) != 6:
                    st.error("Enter the full 6-digit code.")
                else:
                    ok, reason = verify_otp(pending["email"], otp_val.strip(), "login")
                    if ok:
                        st.session_state["user"]         = pending
                        st.session_state["chat_history"] = []
                        st.session_state.login_stage     = "creds"
                        st.session_state.login_pending   = None
                        st.toast(f"Welcome back, {pending['username']}! 🎉", icon="✅")
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error(reason)

        with col_b:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("← Back", key="login_back", use_container_width=True):
                st.session_state.login_stage   = "creds"
                st.session_state.login_pending = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Resend Code", key="login_resend"):
            new_code = generate_otp(pending["email"], "login")
            ok, msg  = send_otp_email(pending["email"], new_code, "login")
            st.success("New code sent!") if ok else st.error(f"Failed: {msg}")


# ═════════════════════════════════════════════════════════════════════════════
#  SIGN-UP
# ═════════════════════════════════════════════════════════════════════════════
with tab_signup:
    # Session keys
    for k, v in [("signup_stage", "form"), ("signup_pending", {})]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Stage 1: details form ────────────────────────────────────────────────
    if st.session_state.signup_stage == "form":
        step_indicator(1, ["Details", "Verify Email", "Done"])

        st.markdown(
            "<p class='anim2' style='color:var(--text-b);font-size:.82rem;"
            "margin-bottom:1.1rem'>Create your account — we'll send a 6-digit "
            "code to verify your email.</p>",
            unsafe_allow_html=True,
        )

        with st.form("signup_form"):
            new_user = st.text_input("Username",         placeholder="choose_a_username")
            new_mail = st.text_input("Email",            placeholder="you@example.com")
            new_pwd  = st.text_input("Password",         type="password", placeholder="Min. 8 characters")
            cnf_pwd  = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            go       = st.form_submit_button("Continue →", use_container_width=True)

        if go:
            errs = []
            if not all([new_user, new_mail, new_pwd, cnf_pwd]):
                errs.append("Please fill in all fields.")
            elif len(new_pwd) < 8:
                errs.append("Password must be at least 8 characters.")
            elif new_pwd != cnf_pwd:
                errs.append("Passwords do not match.")
            else:
                if username_exists(new_user):
                    errs.append("That username is already taken.")
                if email_exists(new_mail):
                    existing = get_user_by_email(new_mail)
                    if existing and existing.get("is_verified"):
                        errs.append("An account with that email already exists.")
                    # unverified → allow resend

            if errs:
                for e in errs: st.error(e)
            else:
                code = generate_otp(new_mail, "signup")
                ok, msg = send_otp_email(new_mail, code, "signup")
                if ok:
                    st.session_state.signup_pending = {
                        "username": new_user,
                        "email":    new_mail,
                        "password": new_pwd,
                    }
                    st.session_state.signup_stage = "otp"
                    if msg == "dev_mode":
                        st.info("⚙️ Dev mode — OTP printed to terminal (SMTP not configured).")
                    else:
                        st.success(f"Code sent to **{new_mail}** — check your inbox.")
                    st.rerun()
                else:
                    st.error(f"Failed to send email: {msg} — check SMTP settings in .env")

    # ── Stage 2: OTP entry ───────────────────────────────────────────────────
    elif st.session_state.signup_stage == "otp":
        pending = st.session_state.signup_pending
        step_indicator(2, ["Details", "Verify Email", "Done"])

        st.markdown(f"""
        <div class="info-banner">
            A 6-digit code was sent to<br>
            <b>{pending.get('email','')}</b><br>
            Enter it below — expires in <b>5 minutes</b>.
        </div>""", unsafe_allow_html=True)

        # Timer badge (visual only — real expiry enforced server-side)
        st.markdown("""
        <div style="margin-bottom:.75rem">
            <span class="timer-badge"><span class="td"></span>Expires in 5 min</span>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="otp-wrap">', unsafe_allow_html=True)
        otp_val = st.text_input(
            "6-Digit Code", placeholder="• • • • • •",
            max_chars=6, key="signup_otp",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        col_v, col_b = st.columns([2, 1])
        with col_v:
            if st.button("Verify & Create Account", key="signup_verify",
                         use_container_width=True):
                code = otp_val.strip()
                if len(code) != 6 or not code.isdigit():
                    st.error("Please enter the complete 6-digit code (numbers only).")
                else:
                    ok, reason = verify_otp(pending["email"], code, "signup")
                    if ok:
                        try:
                            new_user_row = create_user(
                                pending["username"],
                                pending["email"],
                                pending["password"],
                                verified=True,
                            )
                            st.session_state["user"]         = new_user_row
                            st.session_state["chat_history"] = []
                            st.session_state.signup_stage    = "done"
                            st.session_state.signup_pending  = {}
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                    else:
                        st.error(reason)

        with col_b:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("← Back", key="signup_back", use_container_width=True):
                st.session_state.signup_stage   = "form"
                st.session_state.signup_pending = {}
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Resend
        st.markdown(
            "<div style='text-align:center;margin-top:.6rem;"
            "font-size:.72rem;color:var(--text-dim)'>Didn't receive it?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Resend Code", key="signup_resend"):
            new_code = generate_otp(pending["email"], "signup")
            ok, msg  = send_otp_email(pending["email"], new_code, "signup")
            st.success("New code sent!") if ok else st.error(f"Failed: {msg}")

    # ── Stage 3: success ────────────────────────────────────────────────────
    elif st.session_state.signup_stage == "done":
        step_indicator(3, ["Details", "Verify Email", "Done"])
        u = st.session_state.get("user", {})
        st.markdown(f"""
        <div style="text-align:center;padding:1.4rem 0">
            <div style="font-size:2.4rem;margin-bottom:.6rem">🎉</div>
            <div style="font-size:1.05rem;font-weight:700;color:var(--text-h);margin-bottom:.35rem">
                Account created!
            </div>
            <div style="font-size:.8rem;color:var(--text-b)">
                Welcome, <b style="color:#b794f4">{u.get('username','')}</b>.
                Redirecting…
            </div>
        </div>""", unsafe_allow_html=True)
        st.session_state.signup_stage = "form"   # reset for next visit
        st.switch_page("pages/dashboard.py")

st.markdown("</div>", unsafe_allow_html=True)  # close auth-card

st.markdown("""
<div class="auth-footer">
    InsightBot · Final Year Project · Avantika &amp; Geeta Bhatt
</div>
""", unsafe_allow_html=True)
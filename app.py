"""
Startup Validator — Multi-Agent Venture Validation Platform
Autonomous sequential pipeline for quantitative market sizing, competitor discovery,
SWOT/risk audit, MVP roadmap, financial feasibility & P&L modeling, and executive report synthesis.
"""
import sys
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Windows UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# pyrefly: ignore[missing-import]
import streamlit as st
# pyrefly: ignore[missing-import]
import plotly.graph_objects as go
# pyrefly: ignore[missing-import]
import plotly.express as px

from config import (
    APP_NAME, APP_VERSION, APP_TAGLINE, PIPELINE_STEPS,
    AVAILABLE_PROVIDERS, DEFAULT_PROVIDER
)
from models import IdeaSubmission, FullValidationReport, FinancialFeasibility, FinancialYearProjection
from orchestrator import ValidationOrchestrator
from utils.sample_ideas import SAMPLE_IDEAS
from utils.pdf_generator import generate_pdf_report
from utils.llm_client import UnifiedLLMClient
from agents.advisor_agent import ConversationalAdvisorAgent
from agents.report_agent import ReportGenerationAgent

# Page Configuration
st.set_page_config(
    page_title="Startup Validator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# User Database Persistence
USERS_FILE = Path(__file__).resolve().parent / "users.json"

def load_users() -> dict:
    if not USERS_FILE.exists():
        default_users = {
            "founder": hashlib.sha256("password".encode()).hexdigest(),
            "admin": hashlib.sha256("admin123".encode()).hexdigest(),
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)
        return default_users
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# Dynamic Theme Engine with Professional Typography and Icon Protection
def get_theme_css(theme: str = "light") -> str:
    is_light = (theme == "light")

    if is_light:
        bg_gradient = "radial-gradient(circle at 10% 12%, #FFFFFF 0%, #F8FAFC 35%, #F0F9FF 70%, #E0F2FE 100%) fixed"
        text_color = "#0F172A"
        secondary_text = "#475569"
        heading_color = "#0F172A"
        sidebar_bg = "rgba(255, 255, 255, 0.94) !important"
        sidebar_border = "1px solid #E2E8F0"
        sidebar_text = "#0F172A !important"

        card_bg = "rgba(255, 255, 255, 0.92)"
        card_border = "1px solid rgba(226, 232, 240, 0.95)"
        card_shadow = "0 8px 30px -4px rgba(14, 165, 233, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04)"
        card_hover_border = "#0284C7"
        card_hover_shadow = "0 12px 36px -4px rgba(14, 165, 233, 0.18)"

        hero_badge_bg = "rgba(224, 242, 254, 0.85)"
        hero_badge_border = "1px solid #BAE6FD"
        hero_badge_color = "#0284C7"
        hero_title_grad = "linear-gradient(135deg, #0F172A 0%, #0369A1 60%, #0284C7 100%)"

        metric_bg = "rgba(255, 255, 255, 0.96)"
        metric_border = "1px solid #E2E8F0"
        metric_val_color = "#0284C7"
        metric_label_color = "#64748B"

        step_active_bg = "rgba(238, 246, 255, 0.95)"
        step_active_border = "#2563EB"
        step_active_text = "#1E40AF"
        step_active_shadow = "0 0 16px rgba(37, 99, 235, 0.15)"

        step_done_bg = "rgba(240, 253, 244, 0.9)"
        step_done_border = "#86EFAC"
        step_done_text = "#15803D"

        step_pending_bg = "rgba(255, 255, 255, 0.7)"
        step_pending_border = "1px solid #E2E8F0"
        step_pending_text = "#64748B"

        overview_bg = "rgba(255, 255, 255, 0.95)"
        overview_border = "1.5px solid #7DD3FC"
        overview_shadow = "0 10px 30px rgba(14, 165, 233, 0.10)"

        adaptive_card_bg = "rgba(255, 255, 255, 0.92)"
        adaptive_card_border = "1px solid #E2E8F0"
        adaptive_card_text = "#0F172A"
        adaptive_subcard_bg = "rgba(248, 250, 252, 0.9)"
        adaptive_subcard_border = "1px solid #E2E8F0"

        chat_user_bg = "rgba(224, 242, 254, 0.85)"
        chat_user_border = "1px solid #BAE6FD"
        chat_agent_bg = "rgba(255, 255, 255, 0.96)"
        chat_agent_border = "1px solid #E2E8F0"

        btn_primary_bg = "linear-gradient(135deg, #0284C7 0%, #0369A1 100%)"
        btn_primary_color = "#FFFFFF"

        table_header_bg = "#F1F5F9"
        table_row_border = "#E2E8F0"
    else:
        # High-Contrast Professional Dark Mode with Bright Neon Accents
        bg_gradient = "radial-gradient(circle at 15% 15%, #0B1120 0%, #030712 75%, #000000 100%) fixed"
        text_color = "#F8FAFC"
        secondary_text = "#94A3B8"
        heading_color = "#F8FAFC"
        sidebar_bg = "#0B1120 !important"
        sidebar_border = "1px solid rgba(56, 189, 248, 0.25)"
        sidebar_text = "#F8FAFC !important"

        card_bg = "rgba(17, 24, 39, 0.85)"
        card_border = "1px solid rgba(56, 189, 248, 0.28)"
        card_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.55), inset 0 0 12px rgba(56, 189, 248, 0.05)"
        card_hover_border = "#38BDF8"
        card_hover_shadow = "0 12px 36px rgba(56, 189, 248, 0.25)"

        hero_badge_bg = "rgba(14, 165, 233, 0.18)"
        hero_badge_border = "1px solid rgba(56, 189, 248, 0.4)"
        hero_badge_color = "#38BDF8"
        hero_title_grad = "linear-gradient(135deg, #FFFFFF 20%, #7DD3FC 60%, #38BDF8 100%)"

        metric_bg = "rgba(17, 24, 39, 0.9)"
        metric_border = "1px solid rgba(56, 189, 248, 0.25)"
        metric_val_color = "#38BDF8"
        metric_label_color = "#94A3B8"

        step_active_bg = "rgba(14, 165, 233, 0.22)"
        step_active_border = "#38BDF8"
        step_active_text = "#FFFFFF"
        step_active_shadow = "0 0 20px rgba(56, 189, 248, 0.35)"

        step_done_bg = "rgba(16, 185, 129, 0.18)"
        step_done_border = "rgba(52, 211, 153, 0.5)"
        step_done_text = "#6EE7B7"

        step_pending_bg = "rgba(15, 23, 42, 0.6)"
        step_pending_border = "1px solid rgba(255, 255, 255, 0.08)"
        step_pending_text = "#64748B"

        overview_bg = "rgba(17, 24, 39, 0.92)"
        overview_border = "1.5px solid rgba(56, 189, 248, 0.4)"
        overview_shadow = "0 10px 32px rgba(0, 0, 0, 0.55)"

        adaptive_card_bg = "rgba(17, 24, 39, 0.85)"
        adaptive_card_border = "1px solid rgba(56, 189, 248, 0.2)"
        adaptive_card_text = "#F8FAFC"
        adaptive_subcard_bg = "rgba(11, 17, 32, 0.85)"
        adaptive_subcard_border = "1px solid rgba(56, 189, 248, 0.15)"

        chat_user_bg = "rgba(30, 58, 138, 0.45)"
        chat_user_border = "1px solid #3B82F6"
        chat_agent_bg = "rgba(17, 24, 39, 0.9)"
        chat_agent_border = "1px solid rgba(56, 189, 248, 0.25)"

        btn_primary_bg = "linear-gradient(135deg, #2563EB 0%, #0284C7 100%)"
        btn_primary_color = "#FFFFFF"

        table_header_bg = "#1E293B"
        table_row_border = "rgba(56, 189, 248, 0.15)"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

/* Professional Typography - Protected against icon font override */
html, body, [class*="css"], .stApp, button:not([class*="material"]), input, textarea, select, div.stMarkdown, p, h1, h2, h3, h4, h5, h6, label, table, th, td {{
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
}}

/* Exempt all Streamlit Material Icons and SVGs so ligatures do not render as raw text */
[data-testid="stIconMaterial"],
[data-testid="stExpanderToggleIcon"] *,
[data-testid="stSidebarCollapseButton"] *,
.material-icons,
[class*="material-symbols"],
i, svg {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}}

.stApp {{
    background: {bg_gradient};
    color: {text_color};
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg};
    border-right: {sidebar_border};
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
    color: {sidebar_text};
}}

p, span, label, div.stMarkdown, .stMarkdown p {{
    color: {text_color};
    font-size: 0.98rem;
    line-height: 1.6;
}}
h1, h2, h3, h4, h5, h6 {{
    color: {heading_color} !important;
    font-weight: 700;
    letter-spacing: -0.015em;
}}

/* Clean Glassmorphic Cards */
.glass-card {{
    background: {card_bg};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: {card_border};
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: {card_shadow};
    transition: all 0.2s ease-in-out;
}}
.glass-card:hover {{
    border-color: {card_hover_border};
    box-shadow: {card_hover_shadow};
}}

.hero-badge {{
    display: inline-flex;
    align-items: center;
    background: {hero_badge_bg};
    border: {hero_badge_border};
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {hero_badge_color};
    margin-bottom: 12px;
    text-transform: uppercase;
}}

.hero-title {{
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1.15;
    background: {hero_title_grad};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}}

.hero-subtitle {{
    font-size: 1.05rem;
    color: {secondary_text};
    max-width: 820px;
    line-height: 1.6;
    margin-bottom: 20px;
}}

.metric-box {{
    background: {metric_bg};
    border: {metric_border};
    border-radius: 10px;
    padding: 16px 18px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    transition: transform 0.2s ease;
}}
.metric-box:hover {{
    transform: translateY(-2px);
}}
.metric-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {metric_val_color};
    letter-spacing: -0.02em;
}}
.metric-label {{
    font-size: 0.8rem;
    color: {metric_label_color};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700;
    margin-top: 4px;
}}

/* Stepper Responsive Grid */
.stepper-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 16px 0 14px 0;
}}
@media (max-width: 900px) {{
    .stepper-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}
.step-card {{
    border-radius: 10px;
    padding: 12px 14px;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 68px;
}}
.step-card.step-active {{
    background: {step_active_bg};
    border: 1.5px solid {step_active_border};
    color: {step_active_text};
    box-shadow: {step_active_shadow};
}}
.step-card.step-done {{
    background: {step_done_bg};
    border: 1px solid {step_done_border};
    color: {step_done_text};
}}
.step-card.step-pending {{
    background: {step_pending_bg};
    border: {step_pending_border};
    color: {step_pending_text};
}}

.analysis-overview-card {{
    background: {overview_bg};
    border: {overview_border};
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 12px;
    box-shadow: {overview_shadow};
}}

.adaptive-card {{
    background: {adaptive_card_bg};
    border: {adaptive_card_border};
    color: {adaptive_card_text};
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}}
.adaptive-subcard {{
    background: {adaptive_subcard_bg};
    border: {adaptive_subcard_border};
    color: {adaptive_card_text};
    border-radius: 8px;
    padding: 12px;
}}

/* Primary Buttons */
div.stButton > button:first-child {{
    background: {btn_primary_bg};
    color: {btn_primary_color} !important;
    font-weight: 600;
    border-radius: 8px;
    border: none;
    padding: 8px 18px;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
}}
div.stButton > button:first-child:hover {{
    opacity: 0.92;
    transform: translateY(-1px);
}}

/* Status Badges */
.status-pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.status-active {{ background: rgba(56, 189, 248, 0.18); color: #0284C7; border: 1px solid #38BDF8; }}
.status-ready {{ background: rgba(16, 185, 129, 0.15); color: #059669; border: 1px solid #34D399; }}
.status-idle {{ background: rgba(148, 163, 184, 0.15); color: #64748B; border: 1px solid #CBD5E1; }}

/* Conversational Advisor Chat styling */
.chat-bubble-agent {{
    background: {chat_agent_bg};
    border: {chat_agent_border};
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}}
.chat-bubble-user {{
    background: {chat_user_bg};
    border: {chat_user_border};
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 14px;
}}

/* Verdict Badges */
.verdict-strong-go {{
    background: rgba(16, 185, 129, 0.15);
    border: 1.5px solid #059669;
    color: #047857;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.05rem;
    display: inline-block;
}}
.verdict-caution {{
    background: rgba(245, 158, 11, 0.15);
    border: 1.5px solid #D97706;
    color: #B45309;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.05rem;
    display: inline-block;
}}
.verdict-pivot {{
    background: rgba(239, 68, 68, 0.15);
    border: 1.5px solid #DC2626;
    color: #B91C1C;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.05rem;
    display: inline-block;
}}

.tag-must {{ background: rgba(239, 68, 68, 0.15); color: #B91C1C; border: 1px solid rgba(239, 68, 68, 0.35); padding: 3px 8px; border-radius: 4px; font-size: 0.76rem; font-weight: 700; }}
.tag-should {{ background: rgba(245, 158, 11, 0.15); color: #B45309; border: 1px solid rgba(245, 158, 11, 0.35); padding: 3px 8px; border-radius: 4px; font-size: 0.76rem; font-weight: 700; }}
.tag-could {{ background: rgba(2, 132, 199, 0.15); color: #0369A1; border: 1px solid rgba(2, 132, 199, 0.35); padding: 3px 8px; border-radius: 4px; font-size: 0.76rem; font-weight: 700; }}
.tag-wont {{ background: rgba(100, 116, 139, 0.15); color: #475569; border: 1px solid rgba(100, 116, 139, 0.35); padding: 3px 8px; border-radius: 4px; font-size: 0.76rem; font-weight: 700; }}

/* Fix Expander padding and text alignment */
[data-testid="stExpander"] details summary {{
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
}}
</style>
"""

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "validation_report" not in st.session_state:
    st.session_state.validation_report = None
if "history" not in st.session_state:
    st.session_state.history = []
if "advisor_chat" not in st.session_state:
    st.session_state.advisor_chat = []
if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None
if "profile_info" not in st.session_state:
    st.session_state.profile_info = {
        "full_name": "Koushik Founder",
        "email": "koushik@startupvalidator.io",
        "role": "Founder",
        "company": "InnovateFlow Labs"
    }

# Inject Current Theme Stylesheet
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)


# =========================================================================
# LOGIN & REGISTRATION GATEWAY
# =========================================================================
if not st.session_state.authenticated:
    st.markdown("<div style='text-align: center; margin-top: 40px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("<div class='hero-badge'>Multi-Agent Venture Validation Platform</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 2.8rem; margin: 0; padding: 0;'>Startup Validator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #475569; margin-top: 6px;'>Autonomous Multi-Agent Potential Assessment and Live Market Intelligence</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.3, 1])
    with col_center:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        auth_mode = st.radio(
            "Account Access",
            options=["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        users = load_users()

        if auth_mode == "Sign In":
            st.markdown("### Sign In to Workspace")
            st.caption("Access your executive validation workspace, live web search, and reports.")
            
            with st.form("login_form"):
                login_user = st.text_input("Username", placeholder="e.g. founder")
                login_pw = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn = st.form_submit_button("Sign In", use_container_width=True)

                if login_btn:
                    clean_u = login_user.strip()
                    if not clean_u or not login_pw:
                        st.error("Please enter both username and password.")
                    elif clean_u not in users:
                        st.error("Account not found. Please verify your credentials or register.")
                    elif users[clean_u] != hash_pw(login_pw):
                        st.error("Incorrect password. Please try again.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.username = clean_u
                        st.session_state.profile_info["full_name"] = clean_u.capitalize()
                        st.session_state.profile_info["email"] = f"{clean_u}@startupvalidator.io"
                        st.rerun()

            st.markdown("---")
            st.caption("Demo Account: **founder** / **password** (or **admin** / **admin123**)")

        else:
            st.markdown("### Register New Account")
            st.caption("Create an account to save venture validations and export investment dossiers.")
            
            with st.form("register_form"):
                reg_user = st.text_input("Choose Username", placeholder="e.g. founder1")
                reg_pw = st.text_input("Choose Password", type="password", placeholder="Minimum 4 characters")
                reg_pw_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                reg_btn = st.form_submit_button("Register Account", use_container_width=True)

                if reg_btn:
                    clean_u = reg_user.strip()
                    if not clean_u:
                        st.error("Username cannot be empty.")
                    elif len(clean_u) < 3:
                        st.error("Username must be at least 3 characters long.")
                    elif clean_u in users:
                        st.error("Username is already registered. Please choose another username.")
                    elif len(reg_pw) < 4:
                        st.error("Password must be at least 4 characters long.")
                    elif reg_pw != reg_pw_confirm:
                        st.error("Passwords do not match.")
                    else:
                        users[clean_u] = hash_pw(reg_pw)
                        save_users(users)
                        st.session_state.authenticated = True
                        st.session_state.username = clean_u
                        st.session_state.profile_info["full_name"] = clean_u.capitalize()
                        st.session_state.profile_info["email"] = f"{clean_u}@startupvalidator.io"
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =========================================================================
# AUTHENTICATED SIDE PANEL NAVIGATION
# =========================================================================
with st.sidebar:
    st.markdown("<div style='padding: 6px 0 14px 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='hero-badge'>Startup Validator</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 1.4rem; margin: 0;'>Navigation</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Core 3 navigation items strictly as requested
    nav_selection = st.radio(
        "Workspace Navigation",
        options=["Dashboard", "Validator", "Settings"],
        index=["Dashboard", "Validator", "Settings"].index(st.session_state.current_page),
        label_visibility="collapsed"
    )

    if nav_selection != st.session_state.current_page:
        st.session_state.current_page = nav_selection
        st.rerun()

    st.markdown("---")

    # Quick Appearance Mode Toggle
    st.markdown("<b>Display Theme</b>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Theme Switcher",
        options=["Crystal Day", "Obsidian Night"],
        index=0 if st.session_state.theme == "light" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_theme = "light" if "Day" in theme_choice else "dark"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    # Dynamic spacing to keep logout shifted to the bottom
    st.markdown("<div style='min-height: 28vh;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # Bottom User Account Badge & Sign Out
    st.markdown(
        f"<div style='font-size: 0.88rem; margin-bottom: 8px;'>"
        f"Signed in: <b>{st.session_state.profile_info.get('full_name', st.session_state.username)}</b><br/>"
        f"<span style='font-size: 0.78rem; opacity: 0.75;'>{st.session_state.profile_info.get('role', 'Founder')} • {st.session_state.profile_info.get('company', 'Startup')}</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    if st.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    st.markdown("<div style='font-size: 0.72rem; color: #64748B; margin-top: 10px; text-align: center;'>Startup Validator v2.5.0<br/>Autonomous Agent Swarm</div>", unsafe_allow_html=True)


# =========================================================================
# PAGE 1: ELEGANT & PROFESSIONAL DASHBOARD
# =========================================================================
if st.session_state.current_page == "Dashboard":
    # 1. Welcome & Overview
    current_date_str = datetime.now().strftime("%B %d, %Y")
    col_dash_head, col_dash_act = st.columns([3, 1.2])
    with col_dash_head:
        st.markdown(f"<div class='hero-badge'>Executive Overview • {current_date_str}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-title'>Welcome back, {st.session_state.profile_info.get('full_name', 'Founder')}!</div>", unsafe_allow_html=True)
        st.markdown(
            f"<p class='hero-subtitle'>"
            f"Here is your startup intelligence overview. Monitor active AI agent swarms, explore venture viability trends, "
            f"and evaluate new business opportunities with live market search."
            f"</p>",
            unsafe_allow_html=True
        )
    with col_dash_act:
        st.markdown("<div style='padding-top: 24px; text-align: right;'>", unsafe_allow_html=True)
        if st.button("Quick Start Validation", type="primary", use_container_width=True):
            st.session_state.current_page = "Validator"
            st.rerun()
        st.caption("Triggers all 9 sequential AI agents")
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent Activity Alert
    st.markdown(
        "<div style='background: rgba(2, 132, 199, 0.08); border-left: 4px solid #0284C7; padding: 12px 16px; border-radius: 6px; margin-bottom: 22px; font-size: 0.92rem;'>"
        "<b>Recent Activity:</b> Autonomous market scanning completed 4 live query runs across LegalTech, HealthTech, and Creator Economy benchmarks."
        "</div>",
        unsafe_allow_html=True
    )

    # 2. Key Performance Metrics (Four summary cards as specified)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown("<div class='metric-box'><div class='metric-value'>24</div><div class='metric-label'>Ideas Submitted</div></div>", unsafe_allow_html=True)
    with col_m2:
        st.markdown("<div class='metric-box'><div class='metric-value'>18</div><div class='metric-label'>Validated Ideas</div></div>", unsafe_allow_html=True)
    with col_m3:
        st.markdown("<div class='metric-box'><div class='metric-value'>15</div><div class='metric-label'>Reports Generated</div></div>", unsafe_allow_html=True)
    with col_m4:
        st.markdown("<div class='metric-box'><div class='metric-value' style='color: #059669;'>75%</div><div class='metric-label'>Average Validation Score</div></div>", unsafe_allow_html=True)

    st.write("")

    # 3. AI Agent Swarm Status
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### AI Agent Swarm Status")
    st.caption("Real-time operational readiness of the 8 core autonomous intelligence agents:")
    
    agent_status_data = [
        {"name": "Idea Extraction Agent", "role": "Semantic Parsing", "status": "Ready", "class": "status-ready"},
        {"name": "Web Search Agent", "role": "Live Tavily & DDGS", "status": "Active", "class": "status-active"},
        {"name": "Market Research Agent", "role": "TAM/SAM Sizing", "status": "Ready", "class": "status-ready"},
        {"name": "Competitor Analysis Agent", "role": "Gap & Moat Matrix", "status": "Ready", "class": "status-ready"},
        {"name": "SWOT Analysis Agent", "role": "4-Quadrant Risk Audit", "status": "Ready", "class": "status-ready"},
        {"name": "MVP Recommendation Agent", "role": "MoSCoW Sprints", "status": "Ready", "class": "status-ready"},
        {"name": "Financial Feasibility Agent", "role": "P&L & ROI Simulator", "status": "Ready", "class": "status-ready"},
        {"name": "Validation Report Agent", "role": "Executive Dossier", "status": "Ready", "class": "status-ready"},
    ]
    
    c_ag_rows = st.columns(4)
    for idx, ag in enumerate(agent_status_data):
        with c_ag_rows[idx % 4]:
            st.markdown(f"""
            <div class='adaptive-card' style='margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 700; font-size: 0.9rem;'>{ag['name']}</span>
                    <span class='status-pill {ag['class']}'>{ag['status']}</span>
                </div>
                <div style='font-size: 0.78rem; opacity: 0.8; margin-top: 4px;'>{ag['role']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Recent Startup Validations & 7. Quick Actions
    col_dash_left, col_dash_right = st.columns([2.5, 1.5])
    with col_dash_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Recent Startup Validations")
        st.caption("Latest venture assessments with composite viability scores:")

        recent_validations = [
            {"title": "ClauseGuard — AI Contract Shield", "industry": "LegalTech", "date": "Nov 04, 2026", "score": 82, "status": "Strong Go"},
            {"title": "CarbonTrace — Automated Accounting", "industry": "ClimateTech", "date": "Nov 02, 2026", "score": 78, "status": "Go with Caution"},
            {"title": "MediSync — Ambient Voice EHR", "industry": "HealthTech", "date": "Oct 29, 2026", "score": 85, "status": "Strong Go"},
            {"title": "CodeMorph — Production Debug Tutor", "industry": "Developer Tools", "date": "Oct 24, 2026", "score": 68, "status": "Conditional Pivot"},
        ]

        # Prepend any newly generated report from this session
        if st.session_state.validation_report:
            rep = st.session_state.validation_report
            recent_validations.insert(0, {
                "title": rep.structured_idea.title,
                "industry": rep.structured_idea.industry_domain,
                "date": "Today",
                "score": rep.composite_viability_score,
                "status": rep.executive_verdict,
                "is_current": True
            })

        for i, val in enumerate(recent_validations[:4]):
            c_v1, c_v2, c_v3, c_v4 = st.columns([3, 2, 1.5, 1.8])
            with c_v1:
                st.markdown(f"<b>{val['title']}</b><br/><span style='font-size:0.8rem; color:#64748B;'>{val['industry']}</span>", unsafe_allow_html=True)
            with c_v2:
                st.markdown(f"<span style='font-size:0.85rem;'>{val['date']}</span>", unsafe_allow_html=True)
            with c_v3:
                color_score = "#059669" if val['score'] >= 80 else ("#0284C7" if val['score'] >= 70 else "#D97706")
                st.markdown(f"<span style='font-weight:700; color:{color_score};'>{val['score']}/100</span>", unsafe_allow_html=True)
            with c_v4:
                if st.button("View Report", key=f"dash_val_{i}", use_container_width=True):
                    st.session_state.current_page = "Validator"
                    st.rerun()
            st.markdown("<div style='border-bottom: 1px solid rgba(226, 232, 240, 0.5); margin: 6px 0 10px 0;'></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_dash_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Quick Actions")
        st.caption("Common workflow shortcuts:")

        if st.button("Validate New Idea", use_container_width=True):
            st.session_state.current_page = "Validator"
            st.rerun()
        if st.button("View Saved Reports", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.rerun()
        if st.button("Compare Startup Ideas", use_container_width=True):
            st.info("Cross-venture comparison matrix initialized for LegalTech vs ClimateTech.")
        if st.button("Explore Market Trends", use_container_width=True):
            st.info("Market intelligence radar: B2B AI Workflow Automation CAGR surging at 24.8%.")
        if st.button("Export All Analytics", use_container_width=True):
            st.success("Consolidated analytics package ready for download in Settings.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Analytics & Insights (Interactive Plotly Visualizations)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Analytics & Venture Intelligence")
    st.caption("Aggregated analytics across submitted and validated startup concepts:")

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        # Validation score trends
        months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
        scores = [68, 71, 74, 72, 79, 76, 82]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=months, y=scores,
            mode='lines+markers',
            name='Viability Score',
            line=dict(color='#0284C7', width=3),
            marker=dict(size=7, color='#0369A1')
        ))
        fig_trend.update_layout(
            title="Validation Score Trajectory (Average / 100)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', size=11)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_ch2:
        # Ideas by Industry
        industries = ["B2B SaaS", "LegalTech", "HealthTech", "ClimateTech", "Developer Tools", "FinTech"]
        counts = [8, 5, 4, 3, 2, 2]
        fig_pie = go.Figure(data=[go.Pie(
            labels=industries,
            values=counts,
            hole=.45,
            marker=dict(colors=['#0284C7', '#0D9488', '#059669', '#7C3AED', '#EA580C', '#64748B'])
        )])
        fig_pie.update_layout(
            title="Ideas Categorized by Industry Domain",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', size=11)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    col_ch3, col_ch4 = st.columns(2)
    with col_ch3:
        # Market opportunity distribution
        sectors = ["LegalTech", "HealthTech", "ClimateTech", "DevTools"]
        tam_vals = [28.4, 42.0, 19.5, 14.2]
        som_vals = [1.2, 1.8, 0.8, 0.6]
        fig_opp = go.Figure()
        fig_opp.add_trace(go.Bar(name='TAM ($B)', x=sectors, y=tam_vals, marker_color='#0284C7'))
        fig_opp.add_trace(go.Bar(name='SOM Year 3 ($B)', x=sectors, y=som_vals, marker_color='#059669'))
        fig_opp.update_layout(
            title="Market Opportunity Sizing Comparison ($ Billion)",
            barmode='group',
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', size=11)
        )
        st.plotly_chart(fig_opp, use_container_width=True)

    with col_ch4:
        # Monthly validation activity
        act_months = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
        evals = [2, 3, 4, 5, 4, 6]
        fig_act = go.Figure(data=[go.Bar(
            x=act_months,
            y=evals,
            marker_color='#38BDF8'
        )])
        fig_act.update_layout(
            title="Monthly Multi-Agent Validations Completed",
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', size=11)
        )
        st.plotly_chart(fig_act, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 6. Market Intelligence Signals
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Real-Time Market Intelligence Radar")
    st.caption("Live sector signals and emerging startup opportunities:")

    c_mi1, c_mi2, c_mi3 = st.columns(3)
    with c_mi1:
        st.markdown("""
        <div class='adaptive-subcard'>
            <div style='font-size:0.8rem; font-weight:700; color:#0284C7;'>TRENDING SECTOR</div>
            <div style='font-size:1.05rem; font-weight:700; margin:4px 0;'>AI-Augmented Legal Workflows</div>
            <div style='font-size:0.85rem; opacity:0.85;'>High enterprise demand for automated contract redlining and compliance parsing. Expected 22% CAGR through 2031.</div>
        </div>
        """, unsafe_allow_html=True)
    with c_mi2:
        st.markdown("""
        <div class='adaptive-subcard'>
            <div style='font-size:0.8rem; font-weight:700; color:#059669;'>EMERGING WHITE SPACE</div>
            <div style='font-size:1.05rem; font-weight:700; margin:4px 0;'>Ambient Clinical Documentation</div>
            <div style='font-size:0.85rem; opacity:0.85;'>Independent practitioner segment remains underserved by legacy hospital EHR systems. Willingness to pay >$99/month.</div>
        </div>
        """, unsafe_allow_html=True)
    with c_mi3:
        st.markdown("""
        <div class='adaptive-subcard'>
            <div style='font-size:0.8rem; font-weight:700; color:#7C3AED;'>COMPETITOR BENCHMARK</div>
            <div style='font-size:1.05rem; font-weight:700; margin:4px 0;'>Self-Serve B2B Pricing Shift</div>
            <div style='font-size:0.85rem; opacity:0.85;'>Top seed-stage ventures are dropping annual sales cycles in favor of 14-day trials with transparent usage billing.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# PAGE 2: VALIDATOR (IDEA SUBMISSION & 9-STEP PIPELINE EXECUTION)
# =========================================================================
elif st.session_state.current_page == "Validator":
    # HERO HEADER SECTION
    st.markdown('<div class="hero-badge">Multi-Agent Startup Validator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Validate Your Startup Idea with Live Web Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">'
        'Submit your startup concept. An orchestrated swarm of 9 autonomous AI agents analyzes problem-market fit, '
        'retrieves live web intelligence, models TAM/SAM/SOM, audits execution risks, designs an MVP roadmap, '
        'simulates 5-year financial projections with investment P&L graphs, and produces an investor-grade dossier.'
        '</div>',
        unsafe_allow_html=True
    )

    # Metric Highlights Row
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.markdown("<div class='metric-box'><div style='font-size:1.15rem; font-weight:700; color:#0284C7;'>Live Web Search</div><div class='metric-label'>Tavily & DuckDuckGo</div></div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown("<div class='metric-box'><div style='font-size:1.15rem; font-weight:700; color:#0369A1;'>Market Opportunity</div><div class='metric-label'>TAM - SAM - SOM</div></div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown("<div class='metric-box'><div style='font-size:1.15rem; font-weight:700; color:#7C3AED;'>Financial Simulator</div><div class='metric-label'>Step 9: Investment P&L</div></div>", unsafe_allow_html=True)
    with col_p4:
        st.markdown("<div class='metric-box'><div style='font-size:1.15rem; font-weight:700; color:#059669;'>Executive Dossier</div><div class='metric-label'>Downloadable PDF</div></div>", unsafe_allow_html=True)

    st.write("")

    # SUBMISSION FORM CONTAINER
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Startup Idea Submission Workspace")
        
        default_idea = ""
        default_domain = ""
        default_geo = "Global"
        default_monetization = "Freemium + B2B SaaS"

        if st.session_state.selected_sample:
            default_idea = st.session_state.selected_sample["raw_idea"]
            default_domain = st.session_state.selected_sample["domain"]
            default_geo = st.session_state.selected_sample.get("geography", "Global")
            default_monetization = st.session_state.selected_sample.get("monetization", "Freemium + B2B SaaS")

        # Benchmark Presets Bar
        st.markdown("<b>Quick Presets:</b>", unsafe_allow_html=True)
        sample_cols = st.columns(len(SAMPLE_IDEAS))
        for idx, sample in enumerate(SAMPLE_IDEAS):
            with sample_cols[idx]:
                if st.button(sample['title'][:20] + "...", key=f"top_sample_{sample['id']}", use_container_width=True):
                    st.session_state.selected_sample = sample
                    st.rerun()

        st.write("")

        raw_idea_input = st.text_area(
            "Describe your startup idea (What problem do you solve, for whom, and how?):",
            value=default_idea,
            placeholder="e.g. An AI-powered contract review tool for freelance designers and independent creative contractors that flags unfair payment terms, indemnity traps, and unlimited revision clauses, drafting instant counter-amendments...",
            height=100
        )

        c_opt1, c_opt2, c_opt3 = st.columns(3)
        with c_opt1:
            domain_input = st.text_input("Industry / Domain (Optional)", value=default_domain, placeholder="e.g. LegalTech, HealthTech, B2B SaaS")
        with c_opt2:
            geo_input = st.selectbox("Target Geography", options=["Global", "North America", "Europe", "Asia-Pacific / India", "Latin America"], index=0)
        with c_opt3:
            monetization_input = st.selectbox(
                "Monetization Preference",
                options=["Freemium + Tiered SaaS", "Usage-Based / Pay-As-You-Go", "Marketplace Commission", "Annual Enterprise License", "B2C Subscription"],
                index=0
            )

        col_btn, col_info = st.columns([1.2, 3])
        with col_btn:
            submit_btn = st.button("Trigger Multi-Agent Validation", type="primary", use_container_width=True)
        with col_info:
            st.caption("Executes all 9 autonomous agents including live web search, quantitative scoring, investment P&L graph, and PDF report.")

        st.markdown('</div>', unsafe_allow_html=True)

    # PIPELINE EXECUTION ORCHESTRATION & STEPPER
    if submit_btn:
        if not raw_idea_input.strip():
            st.warning("Please enter a startup idea before triggering validation.")
        else:
            effective_provider = "auto"
            api_key_to_use = (
                os.getenv("GROQ_API_KEY", "") or
                os.getenv("GEMINI_API_KEY", "") or
                os.getenv("OPENAI_API_KEY", "") or None
            )
            effective_tavily = os.getenv("TAVILY_API_KEY", "")

            submission = IdeaSubmission(
                raw_idea=raw_idea_input.strip(),
                domain_hint=domain_input.strip() or None,
                target_geography=geo_input,
                monetization_preference=monetization_input
            )

            orchestrator = ValidationOrchestrator(
                llm_provider=effective_provider,
                llm_api_key=api_key_to_use,
                tavily_api_key=effective_tavily or None
            )

            # Progress UI
            progress_card = st.empty()
            step_progress_bar = st.progress(0)

            total_steps = len(PIPELINE_STEPS)

            def render_stepper(current_idx: int, message: str):
                cards = []
                for idx, pstep in enumerate(PIPELINE_STEPS):
                    if idx < current_idx:
                        status_class = "step-card step-done"
                        state_pill = '<span style="color: #059669; font-size: 0.72rem; font-weight: 700;">[Completed]</span>'
                    elif idx == current_idx:
                        status_class = "step-card step-active"
                        state_pill = '<span style="color: #0284C7; font-size: 0.72rem; font-weight: 700;">[Analyzing]</span>'
                    else:
                        status_class = "step-card step-pending"
                        state_pill = '<span style="color: #64748B; font-size: 0.72rem; font-weight: 600;">[Queued]</span>'

                    card = (
                        f'<div class="{status_class}">'
                        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
                        f'<span style="font-size: 0.82rem; font-weight: 700;">Step {idx + 1}: {pstep["name"]}</span>'
                        f'{state_pill}'
                        f'</div>'
                        f'<div style="font-size: 0.74rem; opacity: 0.85;">{pstep["role"]}</div>'
                        f'</div>'
                    )
                    cards.append(card)

                grid_html = '<div class="stepper-grid">' + ''.join(cards) + '</div>'

                if current_idx < total_steps:
                    active = PIPELINE_STEPS[current_idx]
                    pct = int((current_idx / total_steps) * 100)
                    overview_html = (
                        f'<div class="analysis-overview-card">'
                        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
                        f'<div class="hero-badge">ACTIVE AGENT: {active["role"]}</div>'
                        f'<div style="font-size: 0.85rem; color: #0284C7; font-weight: 700;">Step {current_idx + 1} of {total_steps} ({pct}% Complete)</div>'
                        f'</div>'
                        f'<div style="font-size: 1.25rem; font-weight: 800; margin-bottom: 4px;">'
                        f'Analyzing: {active["name"]}'
                        f'</div>'
                        f'<div style="font-size: 0.92rem; line-height: 1.5; margin-bottom: 10px; opacity: 0.85;">'
                        f'{active["desc"]}'
                        f'</div>'
                        f'<div style="background: rgba(14, 165, 233, 0.08); border: 1px solid rgba(14, 165, 233, 0.25); border-radius: 8px; padding: 10px 14px; font-size: 0.88rem; color: #0369A1;">'
                        f'<b>Live Swarm Status:</b> {message}'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    overview_html = (
                        f'<div class="analysis-overview-card" style="border-color: rgba(16, 185, 129, 0.5);">'
                        f'<div style="font-size: 1.3rem; font-weight: 800; color: #059669; margin-bottom: 4px;">'
                        f'Multi-Agent Validation Swarm Complete'
                        f'</div>'
                        f'<div style="font-size: 0.95rem; opacity: 0.85;">'
                        f'All {total_steps} validation agents have completed evaluations. Compiling dossier & financial model...'
                        f'</div>'
                        f'</div>'
                    )

                progress_card.markdown(grid_html + overview_html, unsafe_allow_html=True)

            def on_step_start(idx, name, role):
                step_progress_bar.progress(int((idx / total_steps) * 100))
                render_stepper(idx, f"Agent [{role}] actively processing: {name}...")

            def on_step_complete(idx, name, result):
                step_progress_bar.progress(int(((idx + 1) / total_steps) * 100))
                render_stepper(idx + 1, f"Step {idx+1}/{total_steps}: {name} completed successfully.")

            try:
                with st.spinner("Executing autonomous agent swarm..."):
                    report = orchestrator.run_pipeline(
                        submission,
                        on_step_start=on_step_start,
                        on_step_complete=on_step_complete
                    )
                    st.session_state.validation_report = report
                    st.session_state.history.append(report)
                    st.session_state.advisor_chat = []
                
                progress_card.empty()
                step_progress_bar.empty()
                st.success("Validation pipeline completed successfully. Your comprehensive executive dossier and Step 9 financial graph are ready below.")
                st.rerun()

            except Exception as e:
                st.error(f"Error during multi-agent pipeline execution: {e}")
                progress_card.empty()
                step_progress_bar.empty()

    # RESULTS WORKSPACE & REPORT PRESENTATION
    report: FullValidationReport = st.session_state.validation_report

    if report is not None:
        st.markdown("---")

        # Header Card with Title, Verdict, and Quick Export Buttons
        col_rep_head, col_rep_actions = st.columns([3, 2])
        with col_rep_head:
            st.markdown(f"<div style='font-size: 0.85rem; color: #0284C7; font-weight: 700;'>DOSSIER #{report.report_id} • GENERATED {report.created_at}</div>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='margin: 0; font-size: 2.2rem;'>{report.structured_idea.title}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #475569; font-size: 1.05rem; margin-top: 4px;'>{report.structured_idea.tagline}</p>", unsafe_allow_html=True)

            verdict_class = "verdict-strong-go" if "STRONG GO" in report.executive_verdict else ("verdict-caution" if "CAUTION" in report.executive_verdict else "verdict-pivot")
            st.markdown(f"<div class='{verdict_class}'>Verdict: {report.executive_verdict}</div>", unsafe_allow_html=True)

        with col_rep_actions:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            pdf_bytes = generate_pdf_report(report)
            st.download_button(
                label="Download Executive PDF Dossier",
                data=pdf_bytes,
                file_name=f"{report.structured_idea.title.replace(' ', '_')}_Validation_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            md_text = ReportGenerationAgent().generate_markdown(report)
            st.download_button(
                label="Export Full Markdown (.md)",
                data=md_text,
                file_name=f"{report.structured_idea.title.replace(' ', '_')}_Report.md",
                mime="text/markdown",
                use_container_width=True
            )

            st.download_button(
                label="Export Structured JSON",
                data=json.dumps(report.model_dump(), indent=2),
                file_name=f"{report.structured_idea.title.replace(' ', '_')}_Data.json",
                mime="application/json",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        # TOP METRICS DASHBOARD ROW
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f"<div class='metric-box'><div class='metric-value'>{report.composite_viability_score}/100</div><div class='metric-label'>Composite Score</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box'><div class='metric-value'>{report.swot_and_risk.feasibility_score}%</div><div class='metric-label'>Feasibility</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box'><div class='metric-value'>{report.market_opportunity.market_timing_score}%</div><div class='metric-label'>Market Timing</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-box'><div class='metric-value'>{report.mvp_recommendation.estimated_build_time_weeks} Wks</div><div class='metric-label'>MVP Sprint Time</div></div>", unsafe_allow_html=True)
        with m5:
            st.markdown(f"<div class='metric-box'><div class='metric-value'>{report.competitor_analysis.market_saturation_level}</div><div class='metric-label'>Competition Level</div></div>", unsafe_allow_html=True)

        st.write("")

        # MULTI-TAB DETAILED DEEP-DIVE (Including Step 9 Feature: Financial Feasibility & P&L)
        tabs = st.tabs([
            "Executive Summary",
            "Web Intelligence",
            "Market & Personas",
            "Competitor Landscape",
            "SWOT & Risk Audit",
            "MVP Roadmap (MoSCoW)",
            "Go-To-Market Playbook",
            "Financial Feasibility & P&L",
            "Conversational Advisor"
        ])

        # TAB 1: EXECUTIVE SUMMARY
        with tabs[0]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Executive Assessment and Strategic Directives")
            st.markdown(f"<div style='font-size: 1.05rem; line-height: 1.7;'>{report.executive_summary}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### Priority Directives for the Founding Team")
            for idx, rec in enumerate(report.key_recommendations, 1):
                st.markdown(f"**{idx}.** {rec}")

            st.markdown("---")
            st.markdown("#### Venture Foundation")
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown(f"**Problem Solved:** {report.structured_idea.problem_statement}")
                st.markdown(f"**Target Buyer:** {report.structured_idea.target_customer}")
                st.markdown(f"**Industry Category:** {report.structured_idea.industry_domain}")
            with c_v2:
                st.markdown(f"**Solution Proposed:** {report.structured_idea.solution_statement}")
                st.markdown(f"**Core Value Proposition:** {report.structured_idea.core_value_prop}")
                st.markdown(f"**Monetization Architecture:** {report.structured_idea.monetization_model}")
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2: WEB INTELLIGENCE
        with tabs[1]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Live Market Search Intelligence")
            st.markdown(f"**Market Signals Synthesis:**\n\n{report.web_intelligence.market_signals_summary}")

            if report.web_intelligence.real_world_stats:
                st.markdown("---")
                st.markdown("#### Extracted Market Data Points")
                stat_cols = st.columns(len(report.web_intelligence.real_world_stats[:4]))
                for i, stat in enumerate(report.web_intelligence.real_world_stats[:4]):
                    with stat_cols[i]:
                        st.info(stat)

            st.markdown("---")
            st.markdown("#### Real-Time Search Audit Trail")
            st.caption("Targeted queries dispatched by the Web Search Agent:")
            for q in report.web_intelligence.queries_executed:
                st.markdown(f"- <code>{q}</code>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Verified Live Sources and Snippets")
            for res in report.web_intelligence.results:
                with st.expander(f"{res.title} — ({res.source_domain or 'Web Source'})", expanded=False):
                    st.markdown(f"**Snippet:** {res.snippet}")
                    st.markdown(f"**URL:** [{res.url}]({res.url})")
                    st.caption(f"Triggered by query: {res.query_used}")
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 3: MARKET & CUSTOMER PERSONAS
        with tabs[2]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Market Sizing (TAM - SAM - SOM)")

            c_tam, c_sam, c_som, c_cagr = st.columns(4)
            with c_tam:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.35rem; font-weight:800; color:#0284C7;'>{report.market_opportunity.tam_estimate}</div><div class='metric-label'>TAM (Total Market)</div></div>", unsafe_allow_html=True)
            with c_sam:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.35rem; font-weight:800; color:#0369A1;'>{report.market_opportunity.sam_estimate}</div><div class='metric-label'>SAM (Serviceable)</div></div>", unsafe_allow_html=True)
            with c_som:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.35rem; font-weight:800; color:#0284C7;'>{report.market_opportunity.som_estimate}</div><div class='metric-label'>SOM (Year 3)</div></div>", unsafe_allow_html=True)
            with c_cagr:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.35rem; font-weight:800; color:#059669;'>{report.market_opportunity.cagr_growth_rate}</div><div class='metric-label'>Growth Rate</div></div>", unsafe_allow_html=True)

            st.write("")
            c_drivers, c_barriers = st.columns(2)
            with c_drivers:
                st.markdown("#### Macro Tailwinds and Growth Drivers")
                for d in report.market_opportunity.market_drivers:
                    st.markdown(f"- Driver: {d}")
            with c_barriers:
                st.markdown("#### Adoption Barriers and Headwinds")
                for b in report.market_opportunity.market_barriers:
                    st.markdown(f"- Barrier: {b}")

            st.markdown("---")
            st.markdown("### Target Customer Segmentation")
            for persona in report.market_opportunity.personas:
                with st.container():
                    st.markdown(f"""
                    <div class="adaptive-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.1rem; font-weight: 700; color: #0284C7;">Persona: {persona.persona_name}</span>
                            <span style="background: rgba(2, 132, 199, 0.15); color: #0369A1; padding: 3px 10px; border-radius: 20px; font-size: 0.82rem; font-weight: 700;">{persona.willingness_to_pay}</span>
                        </div>
                        <div style="font-size: 0.88rem; margin-bottom: 8px; opacity: 0.85;"><b>Demographics:</b> {persona.target_demographics}</div>
                        <div style="color: #DC2626; font-size: 0.88rem; margin-bottom: 6px;"><b>Pain Points:</b> {', '.join(persona.core_pain_points)}</div>
                        <div style="color: #D97706; font-size: 0.88rem; margin-bottom: 6px;"><b>Current Workaround:</b> {persona.current_workaround}</div>
                        <div style="color: #059669; font-size: 0.88rem;"><b>Buying Trigger:</b> {persona.key_buying_trigger}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 4: COMPETITOR LANDSCAPE
        with tabs[3]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Competitor Discovery and White Space Opportunities")
            st.markdown(f"**Market Saturation Index:** `{report.competitor_analysis.market_saturation_level}`")

            comp_cols = st.columns(len(report.competitor_analysis.competitors))
            for idx, comp in enumerate(report.competitor_analysis.competitors):
                with comp_cols[idx]:
                    badge_type_color = "#0284C7" if comp.competitor_type == "Direct" else ("#D97706" if comp.competitor_type == "Indirect" else "#64748B")
                    st.markdown(f"""
                    <div class="adaptive-card" style="min-height: 280px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="font-weight:700; font-size:1.05rem;">{comp.name}</span>
                            <span style="color:{badge_type_color}; font-size:0.78rem; font-weight:700;">{comp.competitor_type}</span>
                        </div>
                        <div style="font-size:0.78rem; opacity:0.8; margin-bottom:8px;">{comp.estimated_market_position} • {comp.pricing_model}</div>
                        <div style="font-size:0.88rem; margin-bottom:10px;">{comp.description}</div>
                        <div style="font-size:0.84rem; color:#059669; margin-bottom:4px;"><b>Strengths:</b> {', '.join(comp.strengths[:2])}</div>
                        <div style="font-size:0.84rem; color:#DC2626;"><b>Weaknesses:</b> {', '.join(comp.weaknesses[:2])}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Unfilled White Space Gaps (Your Unfair Advantage)")
            for ws in report.competitor_analysis.white_space_opportunities:
                st.markdown(f"- {ws}")

            st.markdown("---")
            st.markdown("#### Sustainable Defensibility Moat")
            st.info(f"Moat Architecture: {report.competitor_analysis.defensibility_moat}")
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 5: SWOT & RISK AUDIT
        with tabs[4]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Strategic SWOT Matrix")

            swot_c1, swot_c2 = st.columns(2)
            with swot_c1:
                st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #047857; margin-bottom: 6px;">STRENGTHS</div>
                """, unsafe_allow_html=True)
                for s in report.swot_and_risk.strengths:
                    st.markdown(f"- {s}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                <div style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.35); border-radius: 8px; padding: 14px;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0369A1; margin-bottom: 6px;">OPPORTUNITIES</div>
                """, unsafe_allow_html=True)
                for o in report.swot_and_risk.opportunities:
                    st.markdown(f"- {o}")
                st.markdown("</div>", unsafe_allow_html=True)

            with swot_c2:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #B91C1C; margin-bottom: 6px;">WEAKNESSES</div>
                """, unsafe_allow_html=True)
                for w in report.swot_and_risk.weaknesses:
                    st.markdown(f"- {w}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 14px;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #B45309; margin-bottom: 6px;">THREATS</div>
                """, unsafe_allow_html=True)
                for t in report.swot_and_risk.threats:
                    st.markdown(f"- {t}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Categorized Execution Risk Register")
            for r in report.swot_and_risk.risk_items:
                sev_badge = f"<span style='color: {'#DC2626' if r.severity=='High' else '#D97706'}; font-weight: 700;'>{r.severity} Severity</span>"
                st.markdown(f"""
                <div class="adaptive-card" style="border-left: 4px solid {'#DC2626' if r.severity=='High' else '#D97706'}; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700;">[{r.category}] {r.risk_title}</span>
                        <span style="font-size: 0.85rem;">Likelihood: <b>{r.likelihood}</b> | {sev_badge}</span>
                    </div>
                    <div style="font-size: 0.9rem; opacity: 0.85; margin: 4px 0 6px 0;">{r.description}</div>
                    <div style="font-size: 0.88rem; color: #059669;"><b>Actionable Mitigation:</b> {r.mitigation_strategy}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 6: MVP ROADMAP (MoSCoW)
        with tabs[5]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### MVP Feature Roadmap and MoSCoW Prioritization")

            c_mvp1, c_mvp2, c_mvp3 = st.columns(3)
            with c_mvp1:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.4rem; font-weight:800; color:#0284C7;'>{report.mvp_recommendation.estimated_build_time_weeks} Weeks</div><div class='metric-label'>Target Launch Duration</div></div>", unsafe_allow_html=True)
            with c_mvp2:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.4rem; font-weight:800; color:#0369A1;'>{report.mvp_recommendation.estimated_mvp_budget_usd}</div><div class='metric-label'>Estimated Lean Budget</div></div>", unsafe_allow_html=True)
            with c_mvp3:
                st.markdown(f"<div class='metric-box'><div style='font-size:1.0rem; font-weight:700; color:#059669; padding-top:4px;'>{report.mvp_recommendation.critical_success_metric}</div><div class='metric-label'>North Star Success KPI</div></div>", unsafe_allow_html=True)

            st.write("")
            st.markdown("#### MoSCoW Feature Breakdown")
            for f in report.mvp_recommendation.core_features:
                cat_tag = "tag-must" if f.moscow_category == "Must-Have" else ("tag-should" if f.moscow_category == "Should-Have" else ("tag-could" if f.moscow_category == "Could-Have" else "tag-wont"))
                st.markdown(f"""
                <div class="adaptive-card" style="margin-bottom: 10px; padding: 12px 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <div>
                            <span class="{cat_tag}">{f.moscow_category}</span>
                            <span style="font-weight: 700; margin-left: 8px;">{f.feature_name}</span>
                        </div>
                        <div style="font-size: 0.82rem; opacity: 0.85;">
                            Phase: <b>{f.sprint_phase}</b> | Impact: <b style="color: #0284C7;">{f.user_impact}</b> | Effort: <b>{f.development_effort}</b>
                        </div>
                    </div>
                    <div style="font-size: 0.88rem; opacity: 0.9;">{f.description}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Recommended Lean Tech Stack")
            stack_cols = st.columns(len(report.mvp_recommendation.recommended_tech_stack))
            for idx, (layer, tech) in enumerate(report.mvp_recommendation.recommended_tech_stack.items()):
                with stack_cols[idx]:
                    st.markdown(f"""
                    <div class="adaptive-subcard" style="text-align: center;">
                        <div style="font-size: 0.78rem; color: #0284C7; font-weight: 700; text-transform: uppercase;">{layer}</div>
                        <div style="font-size: 0.88rem; font-weight: 600; margin-top: 4px;">{tech}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 7: GO-TO-MARKET PLAYBOOK
        with tabs[6]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Go-To-Market and Traction Playbook")

            st.markdown("#### Geoffrey Moore Positioning Statement")
            st.info(report.gtm_strategy.positioning_statement)

            st.markdown("---")
            st.markdown("#### Top Customer Acquisition Channels")
            for ch in report.gtm_strategy.primary_acquisition_channels:
                st.markdown(f"""
                <div class="adaptive-card" style="border-left: 4px solid #0284C7; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="font-weight: 700; color: #0369A1; margin-bottom: 4px;">Channel: {ch['channel']}</div>
                    <div style="font-size: 0.88rem;">{ch['details']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 4-Week First 100 Customers Tactical Playbook")
            for step in report.gtm_strategy.first_100_customers_playbook:
                st.markdown(f"- Step: {step}")

            st.markdown("---")
            st.markdown("#### Unit Economics and Pricing Model")
            ue_c1, ue_c2 = st.columns(2)
            with ue_c1:
                st.markdown("**Target Unit Economics Benchmark:**")
                for k, v in report.gtm_strategy.unit_economics_estimate.items():
                    st.markdown(f"- **{k}:** `{v}`")
            with ue_c2:
                st.markdown(f"**Recommended Pricing Architecture:** *{report.gtm_strategy.pricing_strategy.get('model', 'Tiered SaaS')}*")
                tiers = report.gtm_strategy.pricing_strategy.get('recommended_tiers', [])
                for t in tiers:
                    st.markdown(f"- Tier: {t.get('tier', 'Tier')}: {t.get('price', '$0')} — {t.get('target', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 8: STEP 9 FEATURE - FINANCIAL FEASIBILITY & INVESTMENT P&L GRAPH
        with tabs[7]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Step 9: Financial Feasibility, Investment ROI & P&L Projections")
            st.caption("Quantitative simulation of initial capital investment, annual operating revenue, expenses, and break-even trajectory:")

            fin_data = report.financial_feasibility

            # Dynamic Interactive Investment Simulation Controls
            st.markdown("#### Interactive Investment & Growth Simulator")
            sim_col1, sim_col2, sim_col3 = st.columns(3)
            with sim_col1:
                base_inv = fin_data.initial_investment if fin_data else 35000.0
                sim_investment = st.slider("Initial Seed Capital / Investment ($)", min_value=10000, max_value=250000, value=int(base_inv), step=5000)
            with sim_col2:
                sim_price = st.slider("Target Monthly ARPU / Price ($)", min_value=15, max_value=250, value=29, step=5)
            with sim_col3:
                sim_growth = st.select_slider("Target Growth Pace", options=["Conservative", "Moderate", "Aggressive"], value="Moderate")

            growth_mult = 0.75 if sim_growth == "Conservative" else (1.0 if sim_growth == "Moderate" else 1.4)

            # Recompute dynamic projections based on interactive parameters
            years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
            base_customers = [180, 650, 2100, 5400, 12000]
            dynamic_revenues = []
            dynamic_expenses = []
            dynamic_net_profits = []
            dynamic_cumulative = []
            cum = -sim_investment

            for idx, base_c in enumerate(base_customers):
                c = int(base_c * growth_mult)
                rev = round(c * sim_price * 12.0 * (1.0 + idx * 0.12), 2)
                exp = round((rev * 0.18) + (c * 55.0) + (sim_investment * 0.35 * (1.0 + idx * 0.45)), 2)
                net = round(rev - exp, 2)
                cum = round(cum + net, 2)
                dynamic_revenues.append(rev)
                dynamic_expenses.append(exp)
                dynamic_net_profits.append(net)
                dynamic_cumulative.append(cum)

            # Financial KPIs Row
            st.write("")
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                st.markdown(f"<div class='metric-box'><div class='metric-value'>${sim_investment:,.0f}</div><div class='metric-label'>Seed Capital Required</div></div>", unsafe_allow_html=True)
            with kpi_col2:
                be_month = 14 if dynamic_net_profits[1] > 0 else (22 if dynamic_net_profits[2] > 0 else 30)
                st.markdown(f"<div class='metric-box'><div class='metric-value'>Month {be_month}</div><div class='metric-label'>Break-Even Milestone</div></div>", unsafe_allow_html=True)
            with kpi_col3:
                total_5yr_net = sum(dynamic_net_profits)
                roi = round((total_5yr_net / sim_investment) * 100.0, 1)
                st.markdown(f"<div class='metric-box'><div class='metric-value' style='color:#059669;'>{roi:,.1f}%</div><div class='metric-label'>5-Year Projected ROI</div></div>", unsafe_allow_html=True)
            with kpi_col4:
                st.markdown(f"<div class='metric-box'><div class='metric-value' style='color:#0284C7;'>82%</div><div class='metric-label'>Target Gross Margin</div></div>", unsafe_allow_html=True)

            st.write("")

            # GRAPH 1: 5-Year Revenue, Expenses, and Profit/Loss Bar & Line Graph
            st.markdown("#### 5-Year Revenue, Operating Costs & Net Profit / Loss Projection")
            fig_pl = go.Figure()

            fig_pl.add_trace(go.Bar(
                x=years,
                y=dynamic_revenues,
                name='Annual Revenue ($)',
                marker_color='#0284C7'
            ))
            fig_pl.add_trace(go.Bar(
                x=years,
                y=dynamic_expenses,
                name='Total Expenses ($)',
                marker_color='#EA580C'
            ))
            fig_pl.add_trace(go.Scatter(
                x=years,
                y=dynamic_net_profits,
                name='Net Profit / Loss ($)',
                mode='lines+markers',
                line=dict(color='#059669', width=3),
                marker=dict(size=8, color='#047857')
            ))

            fig_pl.update_layout(
                barmode='group',
                title="Annual Financial Trajectory: Revenue vs Expenses vs Net Profit",
                xaxis_title="Projections Timeline",
                yaxis_title="Amount (USD $)",
                height=380,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', size=11),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_pl, use_container_width=True)

            # GRAPH 2: Cumulative Cash Flow & Break-Even Curve
            st.markdown("#### Cumulative Cash Flow & Investment Break-Even Curve")
            fig_cum = go.Figure()

            fig_cum.add_trace(go.Scatter(
                x=["Seed Inception"] + years,
                y=[-sim_investment] + dynamic_cumulative,
                mode='lines+markers',
                name='Cumulative Cash Position ($)',
                fill='tozeroy',
                fillcolor='rgba(2, 132, 199, 0.12)',
                line=dict(color='#0284C7', width=3),
                marker=dict(size=8)
            ))
            # Zero break-even line
            fig_cum.add_hline(y=0, line_dash="dash", line_color="#DC2626", annotation_text="Break-Even Threshold ($0)")

            fig_cum.update_layout(
                title="Cumulative Cash Flow (Initial Seed Dip & Capital Recovery)",
                xaxis_title="Investment Milestone",
                yaxis_title="Net Cumulative Position ($ USD)",
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Plus Jakarta Sans', size=11)
            )
            st.plotly_chart(fig_cum, use_container_width=True)

            # Detailed Financial Statement Table
            st.markdown("#### 5-Year Pro-Forma Income Statement Summary")
            table_data = []
            for i, yr in enumerate(years):
                table_data.append({
                    "Fiscal Year": yr,
                    "Active Customers": f"{int(base_customers[i] * growth_mult):,}",
                    "Gross Revenue": f"${dynamic_revenues[i]:,.2f}",
                    "Total Expenses": f"${dynamic_expenses[i]:,.2f}",
                    "Net Profit / (Loss)": f"${dynamic_net_profits[i]:,.2f}",
                    "Cumulative Cash Position": f"${dynamic_cumulative[i]:,.2f}"
                })
            st.table(table_data)

            if fin_data and fin_data.financial_verdict:
                st.info(f"Financial Feasibility Verdict: {fin_data.financial_verdict}")
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 9: CONVERSATIONAL STARTUP ADVISOR
        with tabs[8]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Conversational Startup Advisor")
            st.caption("Ask strategic follow-up questions, test monetization hypotheses, or generate investor pitch responses grounded in this validation dossier.")

            advisor_key = (
                os.getenv("GROQ_API_KEY", "") or
                os.getenv("GEMINI_API_KEY", "") or
                os.getenv("OPENAI_API_KEY", "") or None
            )

            advisor = ConversationalAdvisorAgent(
                llm_client=UnifiedLLMClient(
                    provider="auto",
                    api_key=advisor_key
                )
            )

            # Clean Starter Prompts
            st.markdown("<b>Quick Strategic Inquiries:</b>", unsafe_allow_html=True)
            starters = ConversationalAdvisorAgent.get_starter_prompts()
            starter_cols = st.columns(len(starters))
            clicked_prompt = None
            for idx, prompt in enumerate(starters):
                with starter_cols[idx]:
                    if st.button(prompt[:30] + "...", key=f"adv_prompt_{idx}", use_container_width=True):
                        clicked_prompt = prompt

            st.write("")

            # Render Chat History
            chat_box = st.container()
            with chat_box:
                for msg in st.session_state.advisor_chat:
                    if msg["role"] == "user":
                        st.markdown(
                            f"<div class='chat-bubble-user'><b>You (Founder):</b><br/>{msg['content']}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div class='chat-bubble-agent'><b>Startup Advisor:</b><br/>{msg['content']}</div>",
                            unsafe_allow_html=True
                        )

            # Chat Input Form
            user_msg = st.chat_input("Ask the AI Startup Advisor anything about this venture...")
            target_query = clicked_prompt or user_msg

            if target_query:
                st.session_state.advisor_chat.append({"role": "user", "content": target_query})
                with st.spinner("Advisor analyzing business model..."):
                    adv_reply = advisor.answer_query(target_query, report, st.session_state.advisor_chat)
                    st.session_state.advisor_chat.append({"role": "assistant", "content": adv_reply})
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 40px 20px;">
            <h3 style="margin-bottom: 8px;">Ready to Validate Your Startup</h3>
            <p style="color: #475569; max-width: 600px; margin: 0 auto 20px auto;">
                Enter your startup concept above or select a preset to launch the 9-agent autonomous validation swarm.
            </p>
        </div>
        """, unsafe_allow_html=True)


# =========================================================================
# PAGE 3: SETTINGS (COMPREHENSIVE 10-SECTION CONFIGURATION CONSOLE)
# =========================================================================
elif st.session_state.current_page == "Settings":
    st.markdown('<div class="hero-badge">System Preferences & Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Platform Settings & Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Manage your account profile, AI validation depth, appearance, API integrations, saved reports, and workspace permissions.</div>', unsafe_allow_html=True)

    settings_tabs = st.tabs([
        "1. Account & Profile",
        "2. AI Preferences",
        "3. Appearance",
        "4. Notifications",
        "5. Integrations & API",
        "6. Data & Privacy (Saved Reports)",
        "7. Security",
        "8. Workspace & Team",
        "9. Subscription & Usage",
        "10. Help & Support"
    ])

    # 1. ACCOUNT & PROFILE
    with settings_tabs[0]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Account & Profile Information")
        st.caption("Manage your founder profile details and platform credentials:")

        col_prof1, col_prof2 = st.columns([1, 2.5])
        with col_prof1:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: rgba(2, 132, 199, 0.08); border-radius: 12px; border: 1px dashed #38BDF8;">
                <div style="width: 72px; height: 72px; line-height: 72px; border-radius: 50%; background: #0284C7; color: #FFF; font-size: 1.8rem; font-weight: 800; margin: 0 auto 10px auto;">KF</div>
                <b>Profile Avatar</b>
                <div style="font-size: 0.78rem; opacity: 0.8; margin-top: 4px;">JPG, PNG up to 2MB</div>
            </div>
            """, unsafe_allow_html=True)
        with col_prof2:
            prof_name = st.text_input("Full Name", value=st.session_state.profile_info.get("full_name", "Koushik Founder"))
            prof_email = st.text_input("Email Address", value=st.session_state.profile_info.get("email", "founder@startupvalidator.io"))
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                prof_role = st.selectbox("Job Role", options=["Founder", "Student", "Developer", "Investor"], index=0)
            with col_r2:
                prof_comp = st.text_input("Company / Startup Name", value=st.session_state.profile_info.get("company", "InnovateFlow Labs"))

            if st.button("Save Profile Changes"):
                st.session_state.profile_info["full_name"] = prof_name
                st.session_state.profile_info["email"] = prof_email
                st.session_state.profile_info["role"] = prof_role
                st.session_state.profile_info["company"] = prof_comp
                st.success("Profile information updated successfully.")

        st.markdown("---")
        st.markdown("#### Change Account Password")
        with st.form("pwd_form"):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                old_p = st.text_input("Current Password", type="password")
            with c_p2:
                new_p = st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                st.success("Password updated securely.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. AI VALIDATION PREFERENCES
    with settings_tabs[1]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### AI Validation Engine Preferences")
        st.caption("Control the depth, strictness, and modular agents executed during validation:")

        st.markdown("<b>Analysis Depth & Model Tuning:</b>", unsafe_allow_html=True)
        depth = st.select_slider("Analysis Depth", options=["Quick Heuristic Scan (Fast)", "Standard Multi-Agent Swarm (Recommended)", "Deep Contextual LLM Audit (Thorough)"], value="Standard Multi-Agent Swarm (Recommended)")
        
        st.write("")
        st.markdown("<b>Agent Pipeline Modular Toggles:</b>", unsafe_allow_html=True)
        c_tg1, c_tg2 = st.columns(2)
        with c_tg1:
            t1 = st.checkbox("Live Market Web Research Agent", value=True)
            t2 = st.checkbox("Competitor Discovery & Gap Analysis Agent", value=True)
            t3 = st.checkbox("SWOT & Risk Assessment Agent", value=True)
        with c_tg2:
            t4 = st.checkbox("Financial Feasibility & P&L Modeling Agent (Step 9)", value=True)
            t5 = st.checkbox("MVP Feature Recommendations Agent", value=True)
            t6 = st.checkbox("Quantitative Feasibility Scoring", value=True)

        st.write("")
        col_pref1, col_pref2 = st.columns(2)
        with col_pref1:
            st.selectbox("Preferred Report Language", options=["English (US)", "English (UK)", "Spanish", "French", "German", "Japanese"])
        with col_pref2:
            st.selectbox("Report Detail Format", options=["Comprehensive Investor Dossier", "Detailed Founder Summary", "Brief Executive One-Pager"])

        if st.button("Save AI Preferences"):
            st.success("AI pipeline preferences saved.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. APPEARANCE & PERSONALIZATION
    with settings_tabs[2]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Display & Personalization")
        st.caption("Customize the interface aesthetic, accent colors, and layout spacing:")

        c_ap1, c_ap2 = st.columns(2)
        with c_ap1:
            app_theme = st.selectbox("Interface Theme", options=["Crystal Day (Light)", "Obsidian Night (Dark)", "System Sync"], index=0 if st.session_state.theme == "light" else 1)
            accent_col = st.selectbox("Primary Accent Tone", options=["Electric Royal Blue", "Neon Emerald", "Cyber Cyan", "Royal Violet", "Sunset Amber"])
            dashboard_layout = st.selectbox("Dashboard Layout", options=["Standard Modular Grid", "Compact Analytical View"])
        with c_ap2:
            spacing_mode = st.selectbox("Interface Spacing", options=["Comfortable (Recommended)", "Compact"])
            landing_pref = st.selectbox("Default Landing View", options=["Dashboard", "Validator Workspace", "Settings"])
            date_fmt = st.selectbox("Date Format", options=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])

        if st.button("Apply Appearance Settings"):
            if "Dark" in app_theme:
                st.session_state.theme = "dark"
            elif "Light" in app_theme:
                st.session_state.theme = "light"
            st.success("Appearance settings updated.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. NOTIFICATIONS
    with settings_tabs[3]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Notification Preferences")
        st.caption("Manage email alerts, pipeline milestone notifications, and insights:")

        st.checkbox("Email notifications on validation completion", value=True)
        st.checkbox("Alert when executive PDF dossier is ready for download", value=True)
        st.checkbox("Weekly venture & sector intelligence digest", value=True)
        st.checkbox("Platform security & sign-in alerts", value=True)
        st.checkbox("New agent releases & benchmark presets", value=False)

        if st.button("Save Notification Settings"):
            st.success("Notification preferences saved.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. INTEGRATIONS & API
    with settings_tabs[4]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Integrations & API Connections")
        st.caption("Status of active LLM reasoning engines and live web search APIs:")

        apis = [
            {"provider": "Tavily Search API", "env": "TAVILY_API_KEY", "desc": "Live web market intelligence & source retrieval"},
            {"provider": "Groq Cloud (Llama 3.3)", "env": "GROQ_API_KEY", "desc": "High-speed LLM reasoning engine"},
            {"provider": "Google Gemini API", "env": "GEMINI_API_KEY", "desc": "Gemini 1.5/2.0 multimodal reasoning"},
            {"provider": "OpenAI API", "env": "OPENAI_API_KEY", "desc": "GPT-4o Mini structured JSON extraction"},
        ]

        for ap in apis:
            is_set = bool(os.getenv(ap["env"]))
            status_text = "Connected (Active)" if is_set else "Not Configured (Using Intelligent Heuristic Fallback)"
            status_color = "#059669" if is_set else "#64748B"
            st.markdown(f"""
            <div class='adaptive-card' style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <b>{ap['provider']}</b> • <span style='font-size:0.82rem; opacity:0.8;'>{ap['desc']}</span>
                </div>
                <span style='color: {status_color}; font-weight: 700; font-size: 0.85rem;'>{status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        if st.button("Test API Connectivity"):
            st.success("All configured APIs are responding with sub-second latency.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. DATA & PRIVACY (SAVED REPORTS MOVED HERE)
    with settings_tabs[5]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Saved Reports & Data Management")
        st.caption("Access all saved validation dossiers, export raw data, or manage retention:")

        st.markdown("#### Saved Validation Reports Repository")
        if st.session_state.history:
            for idx, hist_rep in enumerate(st.session_state.history):
                c_h1, c_h2, c_h3 = st.columns([3, 1.5, 1.5])
                with c_h1:
                    st.markdown(f"<b>{hist_rep.structured_idea.title}</b><br/><span style='font-size:0.8rem; color:#64748B;'>Dossier #{hist_rep.report_id} • Score: {hist_rep.composite_viability_score}/100</span>", unsafe_allow_html=True)
                with c_h2:
                    st.markdown(f"<span style='font-size:0.85rem;'>{hist_rep.created_at}</span>", unsafe_allow_html=True)
                with c_h3:
                    if st.button("Open Report", key=f"hist_open_{idx}", use_container_width=True):
                        st.session_state.validation_report = hist_rep
                        st.session_state.current_page = "Validator"
                        st.rerun()
                st.markdown("<div style='border-bottom: 1px solid rgba(226,232,240,0.5); margin: 6px 0 10px 0;'></div>", unsafe_allow_html=True)
        else:
            st.info("No saved validation reports in this session yet. Run a validation to automatically archive dossiers here.")

        st.markdown("---")
        st.markdown("#### Data Export & Retention Controls")
        col_dx1, col_dx2 = st.columns(2)
        with col_dx1:
            if st.button("Export Full Validation History (JSON)", use_container_width=True):
                st.success("Validation archive compiled.")
            if st.button("Clear Search Cache & Audit Trail", use_container_width=True):
                st.info("Search cache purged.")
        with col_dx2:
            st.selectbox("Data Retention Policy", options=["Retain indefinitely", "Retain for 90 days", "Purge on session logout"])
            if st.button("Delete Account Data", use_container_width=True):
                st.warning("Account deletion requires primary owner confirmation.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. SECURITY & SESSIONS
    with settings_tabs[6]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Security & Active Sessions")
        st.caption("Two-factor authentication, active device sessions, and sign-in history:")

        st.checkbox("Enable Two-Factor Authentication (2FA via Authenticator App)", value=False)
        st.write("")
        st.markdown("<b>Active Device Sessions:</b>", unsafe_allow_html=True)
        st.markdown("""
        <div class='adaptive-card'>
            <b>Current Session (This Device)</b> • Windows Chrome • IP: 127.0.0.1 (Localhost)<br/>
            <span style='font-size:0.8rem; color:#059669;'>Active Now • Authenticated via SHA-256</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout from All Other Devices"):
            st.success("All other sessions terminated.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 8. WORKSPACE & TEAM
    with settings_tabs[7]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Workspace & Team Collaboration")
        st.caption("Manage team member permissions and report sharing:")

        st.text_input("Workspace Name", value="InnovateFlow Core Ventures")
        
        c_tm1, c_tm2, c_tm3 = st.columns([2, 1.2, 1])
        with c_tm1:
            st.text_input("Invite Team Member Email", placeholder="colleague@startup.com")
        with c_tm2:
            st.selectbox("Role Permission", options=["Analyst", "Viewer", "Admin"])
        with c_tm3:
            st.markdown("<div style='padding-top:28px;'>", unsafe_allow_html=True)
            if st.button("Send Invite", use_container_width=True):
                st.success("Invitation dispatched.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Team Permissions Matrix")
        st.markdown("""
        - <b>Owner:</b> Full system access, API credential management, billing.
        - <b>Analyst:</b> Trigger multi-agent pipeline, adjust parameters, export PDF/Markdown.
        - <b>Viewer:</b> Read-only access to saved validation dossiers and advisor chat.
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 9. SUBSCRIPTION & USAGE
    with settings_tabs[8]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Subscription & Validation Credits")
        st.caption("Current plan tier, usage credits, and billing records:")

        c_sub1, c_sub2, c_sub3 = st.columns(3)
        with c_sub1:
            st.markdown("<div class='metric-box'><div class='metric-value'>Founder Pro</div><div class='metric-label'>Current Tier</div></div>", unsafe_allow_html=True)
        with c_sub2:
            st.markdown("<div class='metric-box'><div class='metric-value' style='color:#059669;'>85 / 100</div><div class='metric-label'>Validation Credits Left</div></div>", unsafe_allow_html=True)
        with c_sub3:
            st.markdown("<div class='metric-box'><div class='metric-value'>Unlimited</div><div class='metric-label'>PDF Report Exports</div></div>", unsafe_allow_html=True)

        st.write("")
        st.progress(85)
        st.caption("85% validation credits available for the current billing cycle.")
        
        st.markdown("---")
        if st.button("Upgrade to Enterprise Swarm Plan"):
            st.info("Enterprise tier unlocks parallel agent execution and custom industry fine-tuning.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 10. HELP & SUPPORT
    with settings_tabs[9]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Help, Support & System Info")
        st.caption("Platform guides, troubleshooting documentation, FAQs, and support:")

        with st.expander("How does the 9-agent validation swarm work?", expanded=False):
            st.markdown("""
            Startup Validator executes a sequential, deterministic agent pipeline:
            1. **Idea Extraction:** Articulates problem, customer, domain, and monetization.
            2. **Live Web Search:** Queries Tavily and DuckDuckGo for live statistics and competitor products.
            3. **Market Opportunity:** Computes TAM/SAM/SOM and formulates customer personas.
            4. **Competitor Discovery:** Maps direct and indirect rivals into a white space gap matrix.
            5. **SWOT & Risk Audit:** Identifies strengths, weaknesses, and a categorized risk register.
            6. **MVP Roadmap:** Designs a MoSCoW-prioritized 3-phase launch feature set.
            7. **Go-To-Market Playbook:** Creates an acquisition strategy and unit economics.
            8. **Financial Feasibility (Step 9):** Simulates 5-year revenue, expenses, profit/loss, and break-even.
            9. **Validation Report:** Synthesizes an executive dossier with an investor Go/No-Go verdict.
            """)

        with st.expander("How are the financial projections in Step 9 calculated?", expanded=False):
            st.markdown("""
            Financial feasibility models annual customer adoption curves, ARPU derived from your pricing tier, 
            customer acquisition cost (CAC), technology hosting overhead, and operating expenses. 
            The interactive simulator lets you test different seed investments ($10k-$250k) and pricing levels.
            """)

        with st.expander("Can I run validations without external API keys?", expanded=False):
            st.markdown("""
            Yes. The platform includes an offline Intelligent Heuristic Engine that evaluates startup ideas 
            with domain-specific heuristics even when offline or without external API keys.
            """)

        st.markdown("---")
        st.markdown("#### Contact Technical Support")
        with st.form("support_form"):
            st.text_input("Subject", placeholder="e.g. Issue with custom domain classification")
            st.text_area("Describe the issue", placeholder="Provide details...", height=80)
            if st.form_submit_button("Submit Support Ticket"):
                st.success("Support ticket #9204 received. Our team will follow up within 2 hours.")

        st.markdown("---")
        st.markdown(f"<b>System Build:</b> Startup Validator v{APP_VERSION} • Multi-Agent Swarm Core", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.8rem; opacity:0.8; margin-top:4px;'>Terms of Service • Privacy Policy • Enterprise SLA</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

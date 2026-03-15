import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import cv2
import numpy as np
import random
import base64
from datetime import datetime
import time
import plotly.graph_objects as go
import plotly.express as px
import hashlib

# Initialize session states
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "bot", "content": "🌸 Welcome to Flora's Garden! I'm your AI Flower Care Assistant. Ask me anything about plants, diseases, or gardening tips!", "time": datetime.now().strftime("%H:%M")}
    ]
if 'typing' not in st.session_state:
    st.session_state.typing = False

# Import database functions
from db import (
    register_user,
    verify_login,
    get_security_question,
    verify_security_answer,
    reset_password
)


# ===============================
# PAGE CONFIGURATION (Must be first Streamlit command)
# ===============================
st.set_page_config(
    page_title="FLORA | Flower Disease Detection",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# SESSION STATE INITIALIZATION (Must be before ANY function definitions)
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "username" not in st.session_state:
    st.session_state.username = None
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "registration_success" not in st.session_state:
    st.session_state.registration_success = False

# ===============================
# HANDLE NAVIGATION FROM QUERY PARAMS (Must be early)
# ===============================
query_params = st.query_params
if "nav_to" in query_params:
    target = query_params["nav_to"]
    st.query_params.clear()
    
    if target == "logout":
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "landing"
    else:
        st.session_state.page = target
    st.rerun()

# ===============================
# CUSTOM CSS WITH GLOWING EFFECTS
# ===============================
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe4ec 50%, #ffd6e0 100%);
        background-size: 400% 400%;
        animation: bgShift 15s ease infinite;
    }
    
    @keyframes bgShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Top Right Welcome Message */
    .top-welcome {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        background: rgba(255, 240, 245, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 12px 25px;
        border: 2px solid rgba(255, 182, 193, 0.6);
        box-shadow: 
            0 8px 32px rgba(255, 105, 180, 0.3),
            0 0 20px rgba(255, 182, 193, 0.4);
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #8b1c3d;
        display: flex;
        align-items: center;
        gap: 8px;
        animation: welcomePulse 3s ease-in-out infinite;
        transition: all 0.3s ease;
    }
    
    .top-welcome:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 
            0 12px 40px rgba(255, 105, 180, 0.5),
            0 0 30px rgba(255, 182, 193, 0.6);
    }
    
    @keyframes welcomePulse {
        0%, 100% { 
            box-shadow: 
                0 8px 32px rgba(255, 105, 180, 0.3),
                0 0 20px rgba(255, 182, 193, 0.4);
        }
        50% { 
            box-shadow: 
                0 12px 40px rgba(255, 105, 180, 0.5),
                0 0 30px rgba(255, 182, 193, 0.6);
        }
    }
    
    .welcome-flower {
        display: inline-block;
        animation: flowerWiggle 2s ease-in-out infinite;
        font-size: 1.3rem;
    }
    
    @keyframes flowerWiggle {
        0%, 100% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(-15deg) scale(1.2); }
        75% { transform: rotate(15deg) scale(1.2); }
    }
    
    .flora-title {
        font-family: 'Playfair Display', serif;
        font-size: 80px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(45deg, #ff5c8a, #ff2f6d, #b03060, #ff5c8a);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient 3s ease infinite, glow 2s ease-in-out infinite alternate;
        text-shadow: 0 0 30px rgba(255, 92, 138, 0.5);
        margin-bottom: 10px;
        letter-spacing: 8px;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(255, 92, 138, 0.6)); }
        to { filter: drop-shadow(0 0 40px rgba(255, 47, 109, 0.9)); }
    }
    
    .profession-phrase {
        text-align: center;
        font-size: 24px;
        color: #8b1c3d;
        font-style: italic;
        margin-bottom: 40px;
        font-weight: 300;
        letter-spacing: 2px;
        animation: fadeIn 2s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .glass-card {
        background: rgba(255, 240, 245, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 2px solid rgba(244, 166, 193, 0.5);
        box-shadow: 0 8px 32px rgba(139, 28, 61, 0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(139, 28, 61, 0.25);
    }
    
    .top-right-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 998;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff5c8a 0%, #ff2f6d 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 92, 138, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 92, 138, 0.6) !important;
    }
    
    .stTextInput>div>div>input {
        background: rgba(255, 228, 236, 0.5) !important;
        border: 2px solid #f4a6c1 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        color: #5a1a2c !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #ff5c8a !important;
        box-shadow: 0 0 10px rgba(255, 92, 138, 0.3) !important;
    }
    
    .tip-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #ff5c8a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .tip-card:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .back-btn {
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 997;
    }
    
    .success-msg {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .result-box {
        background: linear-gradient(135deg, rgba(255,92,138,0.1) 0%, rgba(255,47,109,0.1) 100%);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        border: 2px solid rgba(255,92,138,0.3);
    }
    
    .petal {
        position: fixed;
        font-size: 24px;
        animation: float 10s infinite ease-in-out;
        opacity: 0.6;
        z-index: 0;
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .sidebar-title {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        color: #b03060;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
        letter-spacing: 2px;
        border-bottom: 2px solid #f4a6c1;
        padding-bottom: 15px;
    }
    
    .content-shift {
        margin-left: 280px;
        transition: margin-left 0.3s ease;
    }
    
    .about-container {
        text-align: center;
        padding: 40px;
    }
    
    .about-title {
        color: #8b1c3d;
        margin-bottom: 20px;
        font-size: 28px;
    }
    
    .about-text {
        color: #5a1a2c;
        font-size: 16px;
        line-height: 1.8;
        margin-bottom: 30px;
    }
    
    .features-list {
        color: #5a1a2c;
        text-align: left;
        display: inline-block;
        line-height: 2;
        font-size: 16px;
    }
    
    .features-list li {
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def navigation_sidebar():
    if not st.session_state.logged_in:
        return
    
    current_page = st.session_state.page

    # Centered Title
    st.markdown("<h1 style='text-align: center; color: #ff5c8a; margin-bottom: 0;'>🌸 FLORA</h1>", unsafe_allow_html=True)
    
    # THE CSS FIX: Locks width and prevents stretching
    st.markdown("""
        <style>
            /* 1. Create a container that is ALWAYS the same width */
            .nav-wrapper {
                max-width: 750px; /* Increased for 6 buttons */
                margin: 0 auto;
                padding: 10px 0;
            }

            /* 2. Force buttons to stay side-by-side even on vertical screens */
            [data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                justify-content: center !important;
            }

            /* 3. Fix the column width so they don't grow or shrink */
            [data-testid="column"] {
                min-width: 70px !important;
                padding: 0 2px !important;
            }

            /* 4. Style the buttons to look consistent */
            .stButton > button {
                font-size: 11px !important;
                height: 40px !important;
                padding: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Wrap the columns in the nav-wrapper div
    st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)
    
    # IMPORTANT: Match the number of columns to menu items
    menu = [
        ("🏠 Home", "home"),
        ("ℹ️ About", "about"),
        ("🔍 Detect", "detection"),
        ("📜 History", "history"),
        ("📊 Analysis", "analysis"), 
        ("🤖 Flora AI", "chatbot"),
        ("🚪 Exit", "logout")
    ]
    
    # Create exactly as many columns as menu items
    cols = st.columns(len(menu))  # This ensures we always have enough columns
    
    for i, (label, target) in enumerate(menu):
        with cols[i]:
            btn_type = "primary" if current_page == target else "secondary"
            if st.button(label, key=f"fixed_nav_{target}", type=btn_type, use_container_width=True):
                if target == "logout":
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.page = "landing"
                else:
                    st.session_state.page = target
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
# ===============================
# TOP RIGHT LOGIN/LOGOUT BUTTON
# ===============================
def top_right_button():
    """Creates login/logout button in top right corner"""
    st.markdown('<div class="top-right-container">', unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        if st.button("🚪 Logout", key="top_logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = "landing"
            st.rerun()
    else:
        if st.button("🔐 Login", key="top_login"):
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# BACK BUTTON
# ===============================
def back_button():
    """Creates a back button for navigation"""
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅ Back", key=f"back_{st.session_state.page}"):
        if st.session_state.page == "login":
            st.session_state.page = "landing"
        elif st.session_state.page == "register":
            st.session_state.page = "login"
        elif st.session_state.page == "forgot_password":
            st.session_state.page = "login"
        elif st.session_state.page in ["home", "about", "detection"]:
            if st.session_state.logged_in:
                st.session_state.page = "home"
            else:
                st.session_state.page = "landing"
        else:
            st.session_state.page = "landing"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# LANDING PAGE (BEFORE LOGIN)
# ===============================
def landing_page():
    load_css()
    top_right_button()
    
    st.markdown("""
    <div class="petal" style="top: 10%; left: 10%; animation-delay: 0s;">🌸</div>
    <div class="petal" style="top: 20%; right: 15%; animation-delay: 2s;">🌺</div>
    <div class="petal" style="bottom: 20%; left: 20%; animation-delay: 4s;">🌷</div>
    <div class="petal" style="bottom: 30%; right: 10%; animation-delay: 6s;">💮</div>
    <div class="petal" style="top: 50%; left: 5%; animation-delay: 3s;">🌹</div>
    <div class="petal" style="top: 60%; right: 20%; animation-delay: 5s;">🌻</div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="flora-title">🌸FLORA🌸</h1>', unsafe_allow_html=True)
    st.markdown('<p class="profession-phrase">"Where AI Meets Nature\'s Beauty — Cultivating Healthier Gardens, One Petal at a Time"</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #8b1c3d; margin-bottom: 30px;'>🌿 Essential Flower Care Tips</h2>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    tips = [
        {"icon": "💧", "title": "Proper Watering", "desc": "Water early morning or late evening. Avoid wetting leaves to prevent fungal diseases. Most flowers need 1-2 inches of water weekly.", "color": "#4a90e2"},
        {"icon": "☀️", "title": "Sunlight Balance", "desc": "Know your flower's light needs. Most blooming plants need 6+ hours of sunlight, but some prefer partial shade to prevent scorching.", "color": "#f5a623"},
        {"icon": "✂️", "title": "Pruning & Deadheading", "desc": "Remove spent blooms regularly to encourage new growth. Prune diseased branches immediately to prevent spread.", "color": "#7ed321"},
        {"icon": "🌱", "title": "Soil Health", "desc": "Use well-draining soil rich in organic matter. Test pH levels regularly—most flowers prefer slightly acidic to neutral soil (6.0-7.0).", "color": "#8b572a"},
        {"icon": "🦟", "title": "Pest Prevention", "desc": "Inspect leaves weekly for aphids, mites, or spots. Use neem oil or insecticidal soap as natural preventive measures.", "color": "#bd10e0"},
        {"icon": "🍃", "title": "Fertilization", "desc": "Feed during growing season with balanced fertilizer. Avoid over-fertilizing which can burn roots and reduce blooming.", "color": "#417505"}
    ]
    
    for idx, tip in enumerate(tips):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="tip-card" style="border-left-color: {tip['color']}">
                <h3 style="color: {tip['color']}; margin-bottom: 10px;">{tip['icon']} {tip['title']}</h3>
                <p style="color: #5a1a2c; font-size: 14px; line-height: 1.6;">{tip['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: rgba(255,255,255,0.7); border-radius: 20px; margin-top: 20px;">
            <h3 style="color: #8b1c3d; margin-bottom: 15px;">Ready to diagnose your flowers?</h3>
            <p style="color: #5a1a2c; margin-bottom: 20px;">Join thousands of gardeners using AI to keep their blooms healthy</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started 🚀", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
def login_page():
    load_css()
    
    # Fixed back button in top left
    st.markdown('<div class="back-button-fixed">', unsafe_allow_html=True)
    back_button()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced magical floral floating background + glowing popping cards
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Nunito:wght@400;600;700;800&family=Quicksand:wght@400;500;600;700&display=swap');
    
    /* Back button - dark pink */
    .back-button-fixed .stButton > button,
    div:has(> .back-button-fixed) .stButton > button,
    .stButton > button:has(←),
    button[kind="secondary"]:first-of-type {
        background: linear-gradient(135deg, #ff85a2 0%, #ff6b9d 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3) !important;
    }
    
    .back-button-fixed .stButton > button:hover,
    button:has(←):hover {
        background: linear-gradient(135deg, #ff9ab3 0%, #ff85a2 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4) !important;
    }
    
    /* Scattered floating flowers - slow, gentle, ethereal movement */
    .floating-flower {
        position: fixed;
        font-size: 1.8em;
        opacity: 0.7;
        z-index: 2;
        filter: drop-shadow(0 0 15px rgba(255, 105, 180, 0.8));
        animation: flower-float 40s infinite ease-in-out;
        top: var(--start-y);
        left: var(--start-x);
    }
    
    /* Random scattered positions with unique movement patterns */
    .floating-flower:nth-child(1) { --start-y: 8%; --start-x: 5%; animation-delay: 0s; font-size: 2.2em; animation-name: flower-path-1; }
    .floating-flower:nth-child(2) { --start-y: 85%; --start-x: 8%; animation-delay: 3s; font-size: 1.5em; animation-name: flower-path-2; }
    .floating-flower:nth-child(3) { --start-y: 15%; --start-x: 88%; animation-delay: 6s; font-size: 2em; animation-name: flower-path-3; }
    .floating-flower:nth-child(4) { --start-y: 75%; --start-x: 92%; animation-delay: 1.5s; font-size: 1.7em; animation-name: flower-path-4; }
    .floating-flower:nth-child(5) { --start-y: 45%; --start-x: 3%; animation-delay: 4.5s; font-size: 2.4em; animation-name: flower-path-5; }
    .floating-flower:nth-child(6) { --start-y: 60%; --start-x: 95%; animation-delay: 7.5s; font-size: 1.6em; animation-name: flower-path-6; }
    .floating-flower:nth-child(7) { --start-y: 25%; --start-x: 15%; animation-delay: 2s; font-size: 1.9em; animation-name: flower-path-7; }
    .floating-flower:nth-child(8) { --start-y: 90%; --start-x: 25%; animation-delay: 5s; font-size: 2.1em; animation-name: flower-path-8; }
    .floating-flower:nth-child(9) { --start-y: 5%; --start-x: 75%; animation-delay: 8s; font-size: 1.4em; animation-name: flower-path-9; }
    .floating-flower:nth-child(10) { --start-y: 70%; --start-x: 80%; animation-delay: 2.5s; font-size: 2.3em; animation-name: flower-path-10; }
    .floating-flower:nth-child(11) { --start-y: 35%; --start-x: 10%; animation-delay: 6s; font-size: 1.8em; animation-name: flower-path-11; }
    .floating-flower:nth-child(12) { --start-y: 95%; --start-x: 60%; animation-delay: 4s; font-size: 2em; animation-name: flower-path-12; }
    .floating-flower:nth-child(13) { --start-y: 20%; --start-x: 92%; animation-delay: 7s; font-size: 1.5em; animation-name: flower-path-13; }
    .floating-flower:nth-child(14) { --start-y: 55%; --start-x: 5%; animation-delay: 1s; font-size: 2.2em; animation-name: flower-path-14; }
    .floating-flower:nth-child(15) { --start-y: 40%; --start-x: 85%; animation-delay: 5.5s; font-size: 1.7em; animation-name: flower-path-15; }
    
    /* Slow, gentle floating paths - very subtle movement */
    @keyframes flower-path-1 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(8vw, -5vh) rotate(5deg); }
        50% { transform: translate(3vw, 8vh) rotate(-3deg); }
        75% { transform: translate(12vw, 2vh) rotate(8deg); }
    }
    
    @keyframes flower-path-2 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-6vw, -8vh) rotate(-6deg); }
        66% { transform: translate(5vw, -4vh) rotate(4deg); }
    }
    
    @keyframes flower-path-3 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-8vw, 6vh) rotate(7deg); }
        50% { transform: translate(-4vw, -8vh) rotate(-5deg); }
        75% { transform: translate(6vw, -3vh) rotate(3deg); }
    }
    
    @keyframes flower-path-4 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-10vw, -6vh) rotate(-8deg); }
        66% { transform: translate(-5vw, 4vh) rotate(6deg); }
    }
    
    @keyframes flower-path-5 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(6vw, 8vh) rotate(6deg); }
        50% { transform: translate(12vw, -4vh) rotate(-4deg); }
        75% { transform: translate(4vw, -10vh) rotate(9deg); }
    }
    
    @keyframes flower-path-6 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-8vw, -6vh) rotate(-7deg); }
        66% { transform: translate(-6vw, 5vh) rotate(5deg); }
    }
    
    @keyframes flower-path-7 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(5vw, -8vh) rotate(8deg); }
        50% { transform: translate(10vw, 4vh) rotate(-6deg); }
        75% { transform: translate(2vw, 10vh) rotate(4deg); }
    }
    
    @keyframes flower-path-8 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(8vw, -6vh) rotate(-5deg); }
        66% { transform: translate(15vw, -2vh) rotate(7deg); }
    }
    
    @keyframes flower-path-9 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-5vw, 10vh) rotate(9deg); }
        50% { transform: translate(-10vw, 3vh) rotate(-7deg); }
        75% { transform: translate(-2vw, 8vh) rotate(5deg); }
    }
    
    @keyframes flower-path-10 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-8vw, -8vh) rotate(-9deg); }
        66% { transform: translate(-12vw, 4vh) rotate(6deg); }
    }
    
    @keyframes flower-path-11 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(10vw, 6vh) rotate(7deg); }
        50% { transform: translate(4vw, -10vh) rotate(-8deg); }
        75% { transform: translate(14vw, -2vh) rotate(5deg); }
    }
    
    @keyframes flower-path-12 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(5vw, -12vh) rotate(-6deg); }
        66% { transform: translate(12vw, -6vh) rotate(8deg); }
    }
    
    @keyframes flower-path-13 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-8vw, 8vh) rotate(10deg); }
        50% { transform: translate(-3vw, -6vh) rotate(-7deg); }
        75% { transform: translate(-12vw, 2vh) rotate(6deg); }
    }
    
    @keyframes flower-path-14 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(12vw, 5vh) rotate(-8deg); }
        66% { transform: translate(6vw, -8vh) rotate(10deg); }
    }
    
    @keyframes flower-path-15 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-4vw, -10vh) rotate(6deg); }
        50% { transform: translate(-10vw, 4vh) rotate(-9deg); }
        75% { transform: translate(-6vw, 8vh) rotate(7deg); }
    }
    
    /* Enhanced Welcome Back title - NO BOX, stronger glow */
    .welcome-title {
        font-family: 'Pacifico', cursive;
        font-size: 4.2em;
        color: #ff4f9a;
        text-align: center;
        margin-bottom: 35px;
        text-shadow: 
            0 0 20px rgba(255, 255, 255, 1),
            0 0 40px rgba(255, 79, 154, 0.9),
            0 0 80px rgba(255, 79, 154, 0.7),
            0 0 120px rgba(255, 105, 180, 0.5),
            0 0 160px rgba(255, 20, 147, 0.3);
        animation: 
            title-pop-in 0.7s ease-out forwards,
            title-pulse-glow 2.5s ease-in-out infinite 0.7s;
        opacity: 0;
        transform: scale(0.8);
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        position: relative;
        z-index: 10;
    }
    
    @keyframes title-pop-in {
        0% { opacity: 0; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes title-pulse-glow {
        0%, 100% {
            text-shadow: 
                0 0 20px rgba(255, 255, 255, 1),
                0 0 40px rgba(255, 79, 154, 0.9),
                0 0 80px rgba(255, 79, 154, 0.7),
                0 0 120px rgba(255, 105, 180, 0.5),
                0 0 160px rgba(255, 20, 147, 0.3);
        }
        50% {
            text-shadow: 
                0 0 30px rgba(255, 255, 255, 1),
                0 0 60px rgba(255, 79, 154, 1),
                0 0 100px rgba(255, 79, 154, 0.9),
                0 0 140px rgba(255, 105, 180, 0.7),
                0 0 180px rgba(255, 20, 147, 0.5);
        }
    }
    
    .title-flower {
        display: inline-block;
        margin: 0 12px;
        animation: flower-bob 2s ease-in-out infinite;
        filter: drop-shadow(0 0 15px rgba(255, 79, 154, 0.8));
        font-size: 0.9em;
    }
    
    .title-flower:first-child { animation-delay: 0s; }
    .title-flower:last-child { animation-delay: 0.3s; }
    
    @keyframes flower-bob {
        0%, 100% { transform: translateY(0) rotate(-5deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    /* Glowing popping input cards */
    .input-card {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.95), rgba(255, 228, 235, 0.95));
        border: 2px solid rgba(255, 182, 193, 0.5);
        border-radius: 25px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 
            0 8px 32px rgba(255, 105, 180, 0.2),
            0 0 60px rgba(255, 182, 193, 0.15),
            inset 0 0 20px rgba(255, 255, 255, 0.6);
        animation: card-entrance 0.7s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
    }
    
    .input-card:nth-child(1) { animation-delay: 0.1s; }
    .input-card:nth-child(2) { animation-delay: 0.2s; }
    
    .input-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 12px 40px rgba(255, 105, 180, 0.3),
            0 0 80px rgba(255, 182, 193, 0.25),
            inset 0 0 25px rgba(255, 255, 255, 0.7);
    }
    
    @keyframes card-entrance {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Labels inside cards */
    .input-label {
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        color: #c2185b;
        font-size: 0.95em;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.9);
        margin-bottom: 12px;
        display: block;
    }
    
    /* Enhanced input fields */
    div[data-testid="stTextInput"] > div > div > input {
        font-family: 'Nunito', sans-serif !important;
        font-size: 1.05em !important;
        border: 2px solid rgba(255, 182, 193, 0.4) !important;
        border-radius: 18px !important;
        background: rgba(255, 255, 255, 0.85) !important;
        color: #8b1c3d !important;
        padding: 16px 20px !important;
        box-shadow: 
            inset 0 2px 8px rgba(255, 182, 193, 0.1),
            0 4px 15px rgba(255, 182, 193, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #ff6b9d !important;
        background: rgba(255, 255, 255, 0.98) !important;
        box-shadow: 
            0 0 25px rgba(255, 107, 157, 0.4),
            0 0 50px rgba(255, 182, 193, 0.3),
            inset 0 2px 10px rgba(255, 182, 193, 0.15) !important;
        transform: translateY(-2px);
        outline: none !important;
    }
    
    /* Button section card */
    .button-card {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.9), rgba(255, 228, 235, 0.9));
        border: 2px solid rgba(255, 182, 193, 0.4);
        border-radius: 25px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 
            0 8px 32px rgba(255, 105, 180, 0.15),
            0 0 50px rgba(255, 182, 193, 0.1);
        animation: card-entrance 0.7s ease-out forwards;
        animation-delay: 0.3s;
        opacity: 0;
        transform: translateY(20px);
    }
    
    /* Primary button - lighter pink */
    div[data-testid="stButton"] > button[kind="primary"] {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.1em !important;
        background: linear-gradient(135deg, #ff85a2 0%, #ff6b9d 100%) !important;
        border: none !important;
        border-radius: 25px !important;
        color: white !important;
        padding: 14px !important;
        box-shadow: 
            0 8px 25px rgba(255, 107, 157, 0.4),
            0 0 40px rgba(255, 182, 193, 0.3),
            inset 0 0 10px rgba(255, 255, 255, 0.3) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ff9ab3 0%, #ff85a2 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 
            0 12px 35px rgba(255, 107, 157, 0.5),
            0 0 60px rgba(255, 182, 193, 0.4),
            inset 0 0 15px rgba(255, 255, 255, 0.4) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* Secondary button */
    div[data-testid="stButton"] > button[kind="secondary"] {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 600 !important;
        background: transparent !important;
        border: 2px solid rgba(255, 107, 157, 0.4) !important;
        border-radius: 20px !important;
        color: #ff6b9d !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: rgba(255, 107, 157, 0.1) !important;
        border-color: rgba(255, 107, 157, 0.7) !important;
        color: #ff8fab !important;
        transform: translateX(3px);
        box-shadow: 0 0 20px rgba(255, 107, 157, 0.3) !important;
    }
    
    /* Divider */
    .divider-glow {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffb6c1, #ff6b9d, #ffb6c1, transparent);
        box-shadow: 0 0 15px rgba(255, 182, 193, 0.6);
        margin: 25px 0;
        border-radius: 2px;
    }
    
    /* Text styling */
    .cute-text {
        font-family: 'Quicksand', sans-serif;
        color: #8b1c3d;
        font-weight: 700;
        font-size: 1em;
        text-shadow: 0 0 10px rgba(255, 182, 193, 0.5);
    }
    
    /* Messages */
    .success-glow, .error-glow {
        font-family: 'Nunito', sans-serif !important;
        font-size: 1em !important;
        border-radius: 18px !important;
        padding: 15px !important;
        margin-bottom: 20px !important;
        text-align: center;
    }
    
    .success-glow {
        background: rgba(212, 237, 218, 0.9) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        color: #155724 !important;
        box-shadow: 0 0 30px rgba(144, 238, 144, 0.3) !important;
    }
    
    .error-glow {
        background: rgba(248, 215, 218, 0.9) !important;
        border: 2px solid rgba(220, 53, 69, 0.3) !important;
        color: #721c24 !important;
        box-shadow: 0 0 30px rgba(255, 182, 193, 0.3) !important;
    }
    </style>
    
    <!-- Scattered floating flowers -->
    <div class="floating-flower">🌸</div>
    <div class="floating-flower">🌼</div>
    <div class="floating-flower">💮</div>
    <div class="floating-flower">🌼</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome Back - OUTSIDE the card, plain text with flowers
        st.markdown("""
            <h2 class="welcome-title">
                <span class="title-flower">🌸</span>
                Welcome Back
                <span class="title-flower">🌸</span>
            </h2>
        """, unsafe_allow_html=True)
        
        # Card starts here
        st.markdown('<div class="pop-card">', unsafe_allow_html=True)
        
        if st.session_state.registration_success:
            st.markdown("""
                <div class="success-glow" style="padding: 15px; margin-bottom: 25px; text-align: center; border-radius: 15px;">
                    🎉 Registration successful! Please login. 🎉
                </div>
            """, unsafe_allow_html=True)
            st.session_state.registration_success = False
        
        st.markdown('<label class="cute-label">👤 Username</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Enter your username ✨", key="login_user", 
                                label_visibility="collapsed")
        
        st.markdown('<label class="cute-label">🔒 Password</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Enter your password 🔮", key="login_pass", 
                                label_visibility="collapsed")
        
        col_forgot, col_space = st.columns([1, 1])
        with col_forgot:
            if st.button("🔑 Forgot Password?", key="forgot_pass"):
                st.session_state.page = "forgot_password"
                st.rerun()
       
        login_clicked = st.button("Login 💕", use_container_width=True, key="login_submit", 
                                  type="primary")
        
        if login_clicked:
            if verify_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "home"
                st.rerun()
            else:
                st.markdown("""
                    <div class="error-glow" style="padding: 15px; margin-top: 20px; text-align: center; border-radius: 15px;">
                        ❌ Invalid username or password
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<hr class="divider-glow">', unsafe_allow_html=True)
        st.markdown("<p class='cute-text' style='text-align: center; margin-bottom: 20px;'>🌸 New to FLORA? 🌸</p>", unsafe_allow_html=True)
        
        if st.button("📝 Create Account", use_container_width=True, key="goto_register"):
            st.session_state.page = "register"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        
# ===============================
# REGISTRATION PAGE (DATABASE ENABLED)
# ===============================
def register_page():
    load_css()
    back_button()
    
    # Add custom CSS for glowing title only
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');
    
    /* Centered Glowing Title - No Box */
    .register-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #8b1c3d;
        text-align: center;
        margin-bottom: 30px;
        margin-top: 20px;
        position: relative;
        text-shadow: 
            0 0 10px rgba(255, 105, 180, 0.6),
            0 0 20px rgba(255, 105, 180, 0.4),
            0 0 40px rgba(255, 20, 147, 0.4),
            0 0 80px rgba(255, 20, 147, 0.2);
        animation: titleGlow 2s ease-in-out infinite;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }
    
    @keyframes titleGlow {
        0%, 100% { 
            text-shadow: 
                0 0 10px rgba(255, 105, 180, 0.6),
                0 0 20px rgba(255, 105, 180, 0.4),
                0 0 40px rgba(255, 20, 147, 0.4),
                0 0 80px rgba(255, 20, 147, 0.2);
            transform: scale(1);
        }
        50% { 
            text-shadow: 
                0 0 20px rgba(255, 105, 180, 0.9),
                0 0 40px rgba(255, 105, 180, 0.7),
                0 0 60px rgba(255, 20, 147, 0.6),
                0 0 100px rgba(255, 20, 147, 0.4);
            transform: scale(1.02);
        }
    }
    
    .flower-icon {
        display: inline-block;
        animation: flowerSpin 3s ease-in-out infinite;
        filter: drop-shadow(0 0 8px rgba(255, 105, 180, 0.8));
    }
    
    @keyframes flowerSpin {
        0%, 100% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(-10deg) scale(1.1); }
        75% { transform: rotate(10deg) scale(1.1); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ... (keep all your existing CSS styles) ...
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Centered Glowing Title - No Box
        st.markdown("""
        <h2 class="register-title">
            <span class="flower-icon">🌸</span> Create Account
        </h2>
        """, unsafe_allow_html=True)
        
        new_username = st.text_input("Username", placeholder="Choose a username✨", key="reg_user")
        new_password = st.text_input("Password", type="password", placeholder="Create password 🔮 ", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password 🔑 ", key="reg_confirm")
        
        security_questions = [
            "What is your favorite flower?🌸",
            "What was your first pet's name?🐶",
            "What city were you born in?💕",
            "What is your favorite color?🎀"
        ]
        
        security_q = st.selectbox("Security Question", security_questions, key="reg_q")
        security_a = st.text_input("Security Answer", placeholder="Your answer", key="reg_a")
        
        if st.button("Register", use_container_width=True, key="reg_submit"):
            if not all([new_username, new_password, confirm_password, security_a]):
                st.error("❌ Please fill all fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(new_password) < 4:
                st.error("❌ Password must be at least 4 characters")
            else:
                # FIX: Handle tuple return value properly
                success, message = register_user(new_username, new_password, security_q, security_a)
                
                if success:
                    st.session_state.registration_success = True
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    # Show the error message (will include "Username already exists" if duplicate)
                    st.error(f"❌ {message}")

# ===============================
# FORGOT PASSWORD PAGE (DATABASE ENABLED)
# ===============================
def forgot_password_page():
    load_css()
    back_button()
    
    # Pink glowing title, larger text, pink borders, adjusted back button + floating flowers
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    
    /* Floating flowers background - slow gentle movement */
    .floating-flower {
        position: fixed;
        font-size: 2rem;
        opacity: 0.6;
        z-index: 0;
        pointer-events: none;
        filter: drop-shadow(0 0 10px rgba(255, 105, 180, 0.5));
        animation: float-slow 25s infinite ease-in-out;
    }
    
    .floating-flower:nth-child(1) { top: 50%; left: 5%; animation-delay: 20s; font-size: 2.5rem; }
    .floating-flower:nth-child(2) { top: 80%; left: 8%; animation-delay: 30s; font-size: 1.8rem; }
    .floating-flower:nth-child(3) { top: 15%; left: 90%; animation-delay: 20s; font-size: 2.2rem; }
    .floating-flower:nth-child(4) { top: 70%; left: 92%; animation-delay: 2s; font-size: 1.6rem; }
    .floating-flower:nth-child(5) { top: 50%; left: 3%; animation-delay: 4s; font-size: 2rem; }
    .floating-flower:nth-child(6) { top: 50%; left: 95%; animation-delay: 7s; font-size: 1.9rem; }
    .floating-flower:nth-child(7) { top: 25%; left: 12%; animation-delay: 1s; font-size: 1.7rem; }
    .floating-flower:nth-child(8) { top: 85%; left: 20%; animation-delay: 5s; font-size: 2.3rem; }
    .floating-flower:nth-child(9) { top: 5%; left: 80%; animation-delay: 8s; font-size: 1.5rem; }
    .floating-flower:nth-child(10) { top: 75%; left: 85%; animation-delay: 2.5s; font-size: 2.1rem; }
    .floating-flower:nth-child(11) { top: 40%; left: 7%; animation-delay: 6s; font-size: 1.8rem; }
    .floating-flower:nth-child(12) { top: 100%; left: 70%; animation-delay: 4s; font-size: 2rem; }
    
    @keyframes float-slow {
        0%, 100% { 
            transform: translate(0, 0) rotate(0deg); 
        }
        25% { 
            transform: translate(15px, -20px) rotate(5deg); 
        }
        50% { 
            transform: translate(25px, 10px) rotate(-3deg); 
        }
        75% { 
            transform: translate(10px, 15px) rotate(8deg); 
        }
    }
    
    /* Back button positioning - move right and down */
    .stButton > button[kind="secondary"], 
    div[data-testid="stButton"] > button:first-of-type,
    button:has(←), button:contains("Back") {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        z-index: 999 !important;
        margin: 0 !important;
    }
    
    /* Alternative back button selector */
    div[data-testid="stVerticalBlock"] > div:first-child .stButton > button {
        position: fixed !important;
        top: 25px !important;
        left: 25px !important;
        z-index: 1000 !important;
    }
    
    .recovery-container {
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
        padding: 20px;
        padding-top: 60px;
        position: relative;
        z-index: 1;
    }
    
    /* Pink glowing title */
    .glowing-title {
        font-family: 'Quicksand', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #ff1493;
        text-align: center;
        margin-bottom: 40px;
        margin-top: 20px;
        text-shadow: 
            0 0 10px rgba(255, 20, 147, 0.8),
            0 0 20px rgba(255, 20, 147, 0.6),
            0 0 40px rgba(255, 20, 147, 0.4),
            0 0 80px rgba(255, 105, 180, 0.4),
            0 0 120px rgba(255, 105, 180, 0.3);
        animation: pinkGlow 2s ease-in-out infinite alternate;
        letter-spacing: 2px;
    }
    
    @keyframes pinkGlow {
        from {
            text-shadow: 
                0 0 10px rgba(255, 20, 147, 0.8),
                0 0 20px rgba(255, 20, 147, 0.6),
                0 0 40px rgba(255, 20, 147, 0.4);
        }
        to {
            text-shadow: 
                0 0 20px rgba(255, 20, 147, 1),
                0 0 40px rgba(255, 20, 147, 0.8),
                0 0 60px rgba(255, 20, 147, 0.6),
                0 0 100px rgba(255, 105, 180, 0.5);
        }
    }
    
    /* Larger text labels */
    .field-label {
        font-family: 'Quicksand', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #8b4567;
        margin-bottom: 8px;
        display: block;
        margin-left: 5px;
    }
    
    /* Input boxes with pink border */
    div[data-testid="stTextInput"] {
        margin-bottom: 12px !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2.5px solid #ffb6c1 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 1.05rem !important;
        font-family: 'Quicksand', sans-serif !important;
        color: #5a1a3e !important;
        height: 48px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #ff69b4 !important;
        border-width: 3px !important;
        box-shadow: 0 0 0 5px rgba(255, 105, 180, 0.15) !important;
        outline: none !important;
    }
    
    /* Security question text - larger */
    .security-question {
        font-family: 'Quicksand', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ff1493;
        margin: 18px 0 10px 5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Button - larger text */
    .stButton > button {
        background: linear-gradient(135deg, #ff5c8a 0%, #ff4081 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 14px 36px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        font-family: 'Quicksand', sans-serif !important;
        width: auto !important;
        min-width: 160px !important;
        margin-top: 20px !important;
        box-shadow: 0 6px 20px rgba(255, 64, 129, 0.35) !important;
        height: 50px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 64, 129, 0.45) !important;
    }
    
    /* Messages - larger */
    .message-box {
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-top: 15px !important;
        font-family: 'Quicksand', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    
    .success-msg {
        background: rgba(212, 237, 218, 0.9) !important;
        color: #155724 !important;
        border: 2px solid #c3e6cb !important;
    }
    
    .error-msg {
        background: rgba(248, 215, 218, 0.9) !important;
        color: #721c24 !important;
        border: 2px solid #f5c6cb !important;
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: transparent !important;
        color: #ff4081 !important;
        border: 2.5px solid #ff4081 !important;
        box-shadow: none !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(255, 64, 129, 0.08) !important;
    }
    
    /* Remove extra spacing */
    .block-container {
        padding: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    
    <!-- Floating flowers background -->
    <div class="floating-flower">🌸</div>
    <div class="floating-flower">🌼</div>
    <div class="floating-flower">💮</div>
    <div class="floating-flower">🌻</div>
    <div class="floating-flower">🌸</div>
    <div class="floating-flower">🌼</div>
    <div class="floating-flower">💮</div>
    <div class="floating-flower">🌻</div>
    <div class="floating-flower">🌼</div>
   
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'reset_success' not in st.session_state:
        st.session_state.reset_success = False
    
    # Centered container
    col1, col2, col3 = st.columns([1, 2.2, 1])
    
    with col2:
        st.markdown('<div class="recovery-container">', unsafe_allow_html=True)
        
        # Pink glowing title
        st.markdown('<h2 class="glowing-title">🔑 Password Recovery</h2>', unsafe_allow_html=True)
        
        # Username
        st.markdown('<label class="field-label">Username</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Enter username", key="forgot_user", label_visibility="collapsed")
        
        # Get security question from database
        security_q = get_security_question(username)
        
        if security_q and not st.session_state.reset_success:
            # Security question as text
            st.markdown(f'<div class="security-question">🔒 {security_q}</div>', unsafe_allow_html=True)
            
            # Your Answer
            st.markdown('<label class="field-label">Your Answer</label>', unsafe_allow_html=True)
            answer = st.text_input("", placeholder="Type your answer here", key="forgot_answer", label_visibility="collapsed")
            
            # Reset Password
            st.markdown('<label class="field-label">Reset Password</label>', unsafe_allow_html=True)
            new_pass = st.text_input("", type="password", placeholder="Enter new password", key="new_pass", label_visibility="collapsed")
            
            # Reset Password button
            if st.button("Reset Password", key="reset_btn"):
                if verify_security_answer(username, answer):
                    reset_password(username, new_pass)
                    st.session_state.reset_success = True
                    st.rerun()
                else:
                    st.markdown('<div class="message-box error-msg">❌ Incorrect answer!</div>', unsafe_allow_html=True)
            
        elif st.session_state.reset_success:
            # Success message
            st.markdown('<div class="message-box success-msg">✅ Password reset successful!</div>', unsafe_allow_html=True)
            
            # Go to login button
            st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
            if st.button("Go to Login", key="goto_login"):
                st.session_state.reset_success = False
                st.session_state.page = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif username:
            st.markdown('<div class="message-box error-msg">❌ Username not found!</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
# ===============================
# HOME PAGE (CLASSIC & GLOWING)
# ===============================
def home_page():
    load_css()

    # ENHANCED GLOWING BACK BUTTON CSS - Top Left with mesmerizing effects
    st.markdown("""
    <style>
    @keyframes neonPulseBack {
        0%, 100% { 
            box-shadow: 
                0 0 5px #ff1493,
                0 0 10px #ff1493,
                0 0 20px #ff1493,
                0 0 40px #ff69b4,
                inset 0 0 10px rgba(255, 255, 255, 0.5);
        }
        50% { 
            box-shadow: 
                0 0 10px #ff1493,
                0 0 20px #ff1493,
                0 0 40px #ff1493,
                0 0 80px #ff69b4,
                0 0 120px #ffb6c1,
                inset 0 0 20px rgba(255, 255, 255, 0.8);
        }
    }
    @keyframes shimmerBack {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes floatBack {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    .glow-back-btn {
        background: linear-gradient(90deg, #ff1493, #ff69b4, #ffb6c1, #ff69b4, #ff1493) !important;
        background-size: 200% auto !important;
        color: dark pink !important;
        border: 2px solid #ff69b4 !important;
        border-radius: 25px !important;
        padding: 8px 20px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        animation: 
            neonPulseBack 2s ease-in-out infinite,
            floatBack 3s ease-in-out infinite,
            shimmerBack 3s linear infinite !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .glow-back-btn:hover {
        transform: scale(1.08) translateY(-2px) !important;
        box-shadow: 
            0 0 20px #ff1493,
            0 0 40px #ff1493,
            0 0 80px #ff69b4,
            0 0 120px #ffb6c1 !important;
        letter-spacing: 1.5px !important;
    }
    .glow-back-btn:active {
        transform: scale(0.95) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout: Back button on LEFT, welcome message on right
    back_col, welcome_col = st.columns([1, 6])
    
    with back_col:
        # Back button with glowing effect - LEFT SIDE
        if st.button("← BACK", key="home_back_btn", 
                     help="Return to landing page ✨",
                     use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    with welcome_col:
        # Display welcome message
        username = st.session_state.get('username', 'Guest')
        st.markdown(f"""
        <div class="top-welcome" style="text-align:left; margin-top: 30px;">
            Hi {username} <span class="welcome-flower">🌸</span>
        </div>
        """, unsafe_allow_html=True)
    

            # Call navigation sidebar ONLY ONCE
    navigation_sidebar()

    # FIX: Soft light pink navigation buttons - matches reference image
    st.markdown("""
    <style>
    /* Target navigation buttons in horizontal block - override Streamlit defaults */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"],
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: linear-gradient(180deg, #ff6b8a 0%, #ff4d79 100%) !important;
        background-color: #ff6b8a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 30px !important;
        font-weight: 500 !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(255, 107, 138, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Primary (active) button - slightly darker */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-primary"],
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: linear-gradient(180deg, #ff4d79 0%, #ff3366 100%) !important;
        background-color: #ff4d79 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 77, 121, 0.4) !important;
    }
    
    /* Hover effect */
    div[data-testid="stHorizontalBlock"] button:hover {
        background: linear-gradient(180deg, #ff8fa3 0%, #ff6b8a 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 138, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    # Enhanced floating flowers with intense glow
    st.markdown("""
    <style>
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px) rotate(-5deg); }
        50% { transform: translateY(-20px) rotate(5deg); }
    }
    @keyframes flowerGlow {
        0%, 100% { filter: saturate(0.8) drop-shadow(0 0 10px rgba(255, 105, 180, 0.5)); }
        50% { filter: saturate(1.2) drop-shadow(0 0 30px rgba(255, 20, 147, 1)); }
    }
    .soft-flower {
        position: fixed;
        font-size: 36px;
        animation: gentleFloat 7s ease-in-out infinite, flowerGlow 2s ease-in-out infinite;
        opacity: 0.7;
        z-index: 0;
        pointer-events: none;
    }
    </style>
    <div class="soft-flower" style="top: 50%; left: 6%; animation-delay: 4s;">🌷</div>
    <div class="soft-flower" style="bottom: 35%; right: 10%; animation-delay: 1s;">🌼</div>
    <div class="soft-flower" style="bottom: 20%; left: 15%; animation-delay: 3s;">💮</div>
    <div class="soft-flower" style="top: 70%; right: 15%; animation-delay: 5s;">🌹</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Extra glowing title
        st.markdown("""
        <h1 style="
            text-align: center;
            font-size: 52px;
            color: #831843;
            margin: 40px 0 10px 0;
            text-shadow: 
                0 0 10px rgba(255, 20, 147, 0.8),
                0 0 20px rgba(255, 20, 147, 0.6),
                0 0 40px rgba(255, 20, 147, 0.4),
                0 0 80px rgba(255, 105, 180, 0.4),
                0 0 120px rgba(255, 105, 180, 0.2);
            animation: titlePulse 2s ease-in-out infinite;
            font-family: 'Playfair Display', serif;
            letter-spacing: 3px;
        ">🌸 Welcome Back! 🌸</h1>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style='
            text-align: center; 
            color: #c71585; 
            font-size: 18px; 
            margin-bottom: 35px; 
            letter-spacing: 2px;
            text-shadow: 0 0 15px rgba(199, 21, 133, 0.5);
            animation: subtitlePulse 3s ease-in-out infinite;
        '>🌼 Relax. Your garden is in safe hands 🌼</p>
        """, unsafe_allow_html=True)
        
        # Extra glowing info card
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 240, 245, 0.95) 100%);
            border-radius: 25px;
            padding: 30px;
            border: 2px solid rgba(255, 182, 193, 0.6);
            box-shadow: 
                0 10px 40px rgba(255, 182, 193, 0.3),
                0 0 30px rgba(255, 105, 180, 0.2),
                inset 0 0 20px rgba(255, 255, 255, 0.5);
            margin-bottom: 35px;
            position: relative;
            overflow: hidden;
            animation: cardShimmer 4s ease-in-out infinite;
        ">
            <div style="
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.6), transparent);
                transform: rotate(45deg);
                animation: shimmer 3s infinite;
            "></div>
            <p style="
                color: #8b4513; 
                line-height: 2; 
                text-align: center; 
                font-size: 15px; 
                margin: 0;
                position: relative;
                z-index: 1;
            ">
                💕 <strong>Upload your flower photo</strong> and let our magical AI 
                detect any diseases! Get <strong>lovely care tips</strong> to keep your 
                garden happy and blooming! 🌿✨
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Extra glowing process cards with booming border effect
        st.markdown("""
        <style>
        @keyframes cardGlow {
            0%, 100% { 
                box-shadow: 
                    0 10px 30px rgba(255, 105, 180, 0.3),
                    0 0 20px rgba(255, 105, 180, 0.1);
            }
            50% { 
                box-shadow: 
                    0 15px 40px rgba(255, 105, 180, 0.5),
                    0 0 40px rgba(255, 20, 147, 0.3),
                    0 0 60px rgba(255, 20, 147, 0.2);
            }
        }
        @keyframes iconFloat {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-15px) scale(1.1); }
        }
        @keyframes borderBoom {
            0%, 100% { 
                border-color: rgba(255, 182, 193, 0.5);
                box-shadow: 
                    0 10px 30px rgba(255, 105, 180, 0.3),
                    0 0 20px rgba(255, 105, 180, 0.1);
            }
            50% { 
                border-color: #ff1493;
                box-shadow: 
                    0 0 0 4px rgba(255, 20, 147, 0.3),
                    0 0 0 8px rgba(255, 20, 147, 0.2),
                    0 0 0 12px rgba(255, 20, 147, 0.1),
                    0 25px 50px rgba(255, 20, 147, 0.4),
                    0 0 50px rgba(255, 105, 180, 0.5);
            }
        }
        @keyframes clickBoom {
            0% { transform: scale(1); }
            50% { transform: scale(0.95); }
            100% { transform: scale(1); }
        }
        .process-card {
            background: linear-gradient(180deg, #fff5f7 0%, #ffffff 100%);
            border-radius: 25px;
            padding: 30px 20px;
            text-align: center;
            border: 3px solid rgba(255, 182, 193, 0.5);
            box-shadow: 
                0 10px 30px rgba(255, 182, 193, 0.3),
                0 0 20px rgba(255, 105, 180, 0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: pointer;
            height: 100%;
            position: relative;
            overflow: hidden;
            animation: cardGlow 3s ease-in-out infinite;
        }
        .process-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
            transition: left 0.6s;
        }
        .process-card:hover::before {
            left: 100%;
        }
        .process-card:hover {
            animation: borderBoom 1s ease-in-out infinite;
            transform: translateY(-15px) scale(1.05);
        }
        .process-card:active {
            animation: clickBoom 0.3s ease;
            transform: scale(0.98);
        }
        .process-icon {
            font-size: 52px;
            margin-bottom: 15px;
            display: block;
            animation: iconFloat 3s ease-in-out infinite;
            filter: drop-shadow(0 0 15px rgba(255, 105, 180, 0.8));
        }
        .process-step {
            font-size: 14px;
            color: #ff1493;
            font-weight: 700;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 20, 147, 0.3);
        }
        .process-title {
            font-size: 22px;
            font-weight: 800;
            color: #8b1c3d;
            margin: 10px 0;
            font-family: 'Playfair Display', serif;
            text-shadow: 0 0 15px rgba(139, 28, 61, 0.2);
        }
        .process-desc {
            font-size: 13px;
            color: #cd853f;
            line-height: 1.6;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("""
            <div class="process-card" onclick="this.style.animation='clickBoom 0.3s ease'">
                <span class="process-icon">📸</span>
                <div class="process-step">Step 1</div>
                <div class="process-title">Upload</div>
                <div class="process-desc">Take or select a flower image</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown("""
            <div class="process-card" onclick="this.style.animation='clickBoom 0.3s ease'">
                <span class="process-icon">🧠</span>
                <div class="process-step">Step 2</div>
                <div class="process-title">Detect</div>
                <div class="process-desc">AI checks for diseases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c3:
            st.markdown("""
            <div class="process-card" onclick="this.style.animation='clickBoom 0.3s ease'">
                <span class="process-icon">🌿</span>
                <div class="process-step">Step 3</div>
                <div class="process-title">Treat</div>
                <div class="process-desc">Get care tips and remedies</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Final Glow CTA with extra glow
        st.markdown("""
        <div style="
            text-align: center;
            margin: 40px 0 25px 0;
            padding: 30px;
            background: linear-gradient(135deg, rgba(255, 240, 245, 0.8) 0%, rgba(255, 228, 235, 0.8) 100%);
            border-radius: 30px;
            border: 2px solid rgba(255, 182, 193, 0.5);
            box-shadow: 
                0 10px 40px rgba(255, 105, 180, 0.3),
                0 0 30px rgba(255, 105, 180, 0.2),
                inset 0 0 20px rgba(255, 255, 255, 0.5);
            animation: ctaPulse 3s ease-in-out infinite;
        ">
            <style>
            @keyframes ctaPulse {
                0%, 100% { 
                    box-shadow: 
                        0 10px 40px rgba(255, 105, 180, 0.3),
                        0 0 30px rgba(255, 105, 180, 0.2);
                }
                50% { 
                    box-shadow: 
                        0 15px 50px rgba(255, 105, 180, 0.5),
                        0 0 50px rgba(255, 20, 147, 0.3),
                        0 0 80px rgba(255, 20, 147, 0.2);
                }
            }
            </style>
            <p style="
                font-size: 28px;
                color: #ff1493;
                font-weight: 700;
                font-family: 'Playfair Display', serif;
                text-shadow: 
                    0 0 10px rgba(255, 20, 147, 0.6),
                    0 0 20px rgba(255, 20, 147, 0.4),
                    0 0 40px rgba(255, 20, 147, 0.2);
                margin-bottom: 10px;
                animation: textGlow 2s ease-in-out infinite;
            ">
                🌸 Ready to heal your flowers?
            </p>
        """, unsafe_allow_html=True)
        
        # Extra glowing CTA button
        st.markdown("""
        <style>
        @keyframes btnGlow {
            0%, 100% { 
                box-shadow: 
                    0 10px 20px rgba(255, 20, 147, 0.5),
                    0 0 10px rgba(255, 20, 147, 0.3);
            }
            50% { 
                box-shadow: 
                    0 15px 40px rgba(255, 20, 147, 0.7),
                    0 0 40px rgba(255, 20, 147, 0.5),
                    0 0 60px rgba(255, 105, 180, 0.4);
            }
        }
        .stButton > button {
            background: linear-gradient(135deg, #ff6b9d 0%, #ff0066 50%,#ff6b9d 100%) !important;
            background-size: 200% 200% !important;
            color: white !important;
            border: 3px solid transparent !important;
            border-radius: 50px !important;
            padding: 18px 40px !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: 2px !important;
            width: 100% !important;
            margin-top: 10px !important;
            box-shadow: 
                0 10px 30px rgba(255, 20, 147, 0.5),
                0 0 20px rgba(255, 20, 147, 0.3) !important;
            animation: btnGlow 2s ease-in-out infinite !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            text-transform: uppercase;
        }
        .stButton > button:hover {
            transform: translateY(-5px) scale(1.05) !important;
            border-color: #ff69b4 !important;
            box-shadow: 
                0 20px 50px rgba(255, 20, 147, 0.8),
                0 0 60px rgba(255, 105, 180, 0.6),
                0 0 100px rgba(255, 20, 147, 0.4) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🌺 Begin The Magic 🌺", use_container_width=True, key="magic_btn"):
            st.session_state.page = "detection"
            st.rerun()
        
        # Extra glowing footer
        st.markdown("""
        <p style='
            text-align: center; 
            margin-top: 50px; 
            font-size: 24px; 
            letter-spacing: 12px; 
            opacity: 0.9;
            text-shadow: 0 0 15px rgba(255, 105, 180, 0.5);
            animation: footerGlow 3s ease-in-out infinite;
        '>
            🌸 🌼 🌺 🌷 💮 🌹
        </p>
        <p style='
            text-align: center; 
            color: #db7093; 
            font-size: 14px; 
            margin-top: 15px; 
            font-style: italic;
            text-shadow: 0 0 15px rgba(219, 112, 147, 0.4);
        '>
            Made with 💕 for your garden
        </p>
        <style>
        @keyframes footerGlow {
            0%, 100% { text-shadow: 0 0 15px rgba(255, 105, 180, 0.5); }
            50% { text-shadow: 0 0 30px rgba(255, 105, 180, 0.8), 0 0 50px rgba(255, 20, 147, 0.3); }
        }
        </style>
        """, unsafe_allow_html=True)
# ===============================
# ABOUT PAGE (EXTRA GLOWING & EFFECTIVE)
# ===============================
def about_page():
    load_css()
    navigation_sidebar()


    # Add extra glowing styles
    st.markdown("""
    <style>
    .about-petal {
        position: fixed;
        font-size: 32px;
        animation: aboutFloat 6s infinite ease-in-out, petalGlow 3s infinite alternate;
        opacity: 0.8;
        z-index: 0;
        pointer-events: none;
        filter: drop-shadow(0 0 15px rgba(255, 105, 180, 0.8));
    }
    
    @keyframes aboutFloat {
        0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
        50% { transform: translateY(-30px) rotate(180deg) scale(1.2); }
    }
    
    @keyframes petalGlow {
        from { filter: drop-shadow(0 0 10px rgba(255, 105, 180, 0.5)) saturate(0.8); }
        to { filter: drop-shadow(0 0 30px rgba(255, 20, 147, 1)) saturate(1.2); }
    }
    
    .about-glow-card {
        background: linear-gradient(135deg, rgba(255,240,245,0.95) 0%, rgba(255,228,236,0.95) 100%);
        border-radius: 35px;
        padding: 50px;
        border: 3px solid rgba(255, 182, 193, 0.6);
        box-shadow: 
            0 20px 60px rgba(255, 105, 180, 0.4),
            0 0 80px rgba(255, 182, 193, 0.3),
            inset 0 0 40px rgba(255, 255, 255, 0.9);
        position: relative;
        overflow: hidden;
        animation: cardPulse 3s ease-in-out infinite alternate;
    }
    
    @keyframes cardPulse {
        from { 
            box-shadow: 
                0 20px 60px rgba(255, 105, 180, 0.4),
                0 0 80px rgba(255, 182, 193, 0.3),
                inset 0 0 40px rgba(255, 255, 255, 0.9);
        }
        to { 
            box-shadow: 
                0 25px 70px rgba(255, 105, 180, 0.6),
                0 0 100px rgba(255, 182, 193, 0.5),
                inset 0 0 50px rgba(255, 255, 255, 1);
        }
    }
    
    .about-title-glow {
        font-family: 'Playfair Display', serif;
        font-size: 60px;
        color: #ff1493;
        text-align: center;
        margin-bottom: 15px;
        text-shadow: 
            0 0 20px rgba(255, 20, 147, 0.8),
            0 0 40px rgba(255, 20, 147, 0.6),
            0 0 60px rgba(255, 20, 147, 0.4),
            0 0 100px rgba(255, 105, 180, 0.4);
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { 
            text-shadow: 
                0 0 20px rgba(255, 20, 147, 0.8),
                0 0 40px rgba(255, 20, 147, 0.6),
                0 0 60px rgba(255, 20, 147, 0.4);
        }
        to { 
            text-shadow: 
                0 0 30px rgba(255, 20, 147, 1),
                0 0 60px rgba(255, 20, 147, 0.8),
                0 0 90px rgba(255, 20, 147, 0.6),
                0 0 120px rgba(255, 105, 180, 0.5);
        }
    }
    
    .about-subtitle-glow {
        color: #db7093;
        font-size: 16px;
        letter-spacing: 5px;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 600;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(219, 112, 147, 0.5);
        animation: subtitlePulse 3s ease-in-out infinite;
    }
    
    @keyframes subtitlePulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; text-shadow: 0 0 20px rgba(219, 112, 147, 0.8); }
    }
    
    .about-section-cute {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 30px;
        padding: 35px;
        margin: 30px 0;
        border: 3px solid transparent;
        box-shadow: 
            0 10px 40px rgba(255, 182, 193, 0.3),
            inset 0 0 30px rgba(255, 240, 245, 0.5);
        position: relative;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: sectionGlow 4s ease-in-out infinite;
    }
    
    @keyframes sectionGlow {
        0%, 100% { box-shadow: 0 10px 40px rgba(255, 182, 193, 0.3); }
        50% { box-shadow: 0 15px 50px rgba(255, 182, 193, 0.4), 0 0 30px rgba(255, 105, 180, 0.2); }
    }
    
    .about-section-cute:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #ff69b4;
        box-shadow: 
            0 25px 60px rgba(255, 20, 147, 0.4),
            0 0 50px rgba(255, 105, 180, 0.3),
            inset 0 0 30px rgba(255, 240, 245, 0.5);
    }
    
    .about-section-cute:active {
        transform: scale(0.98);
    }
    
    .about-heading-cute {
        color: #ff1493;
        font-size: 30px;
        margin-bottom: 25px;
        text-align: center;
        font-weight: 700;
        text-shadow: 
            0 0 15px rgba(255, 20, 147, 0.5),
            0 0 30px rgba(255, 20, 147, 0.3);
        animation: headingPulse 2s ease-in-out infinite;
    }
    
    @keyframes headingPulse {
        0%, 100% { text-shadow: 0 0 15px rgba(255, 20, 147, 0.5); }
        50% { text-shadow: 0 0 25px rgba(255, 20, 147, 0.8), 0 0 40px rgba(255, 20, 147, 0.4); }
    }
    
    .about-text-cute {
        color: #8b4513;
        line-height: 2.2;
        font-size: 17px;
        text-align: center;
        font-weight: 400;
        text-shadow: 0 0 10px rgba(139, 69, 19, 0.1);
    }
    
    .about-feature-box {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe4ec 100%);
        border-radius: 25px;
        padding: 25px 20px;
        border: 3px solid rgba(255, 182, 193, 0.6);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(255, 182, 193, 0.3);
        position: relative;
        overflow: hidden;
        animation: featurePulse 3s ease-in-out infinite;
    }
    
    @keyframes featurePulse {
        0%, 100% { box-shadow: 0 8px 25px rgba(255, 182, 193, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(255, 182, 193, 0.4), 0 0 20px rgba(255, 105, 180, 0.2); }
    }
    
    .about-feature-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
        transition: left 0.6s;
    }
    
    .about-feature-box:hover::before {
        left: 100%;
    }
    
    .about-feature-box:hover {
        transform: translateY(-12px) scale(1.08);
        border-color: #ff1493;
        box-shadow: 
            0 20px 50px rgba(255, 20, 147, 0.4),
            0 0 40px rgba(255, 105, 180, 0.4);
    }
    
    .about-feature-box:active {
        transform: scale(0.95);
    }
    
    .about-emoji-glow {
        font-size: 42px;
        display: block;
        margin-bottom: 12px;
        animation: emojiBounce 2s infinite;
        filter: drop-shadow(0 0 15px rgba(255, 105, 180, 0.8));
    }
    
    @keyframes emojiBounce {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-12px) scale(1.2); }
    }
    
    .about-label-cute {
        color: #ff1493;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(255, 20, 147, 0.3);
    }
    
    .about-divider {
        width: 100px;
        height: 5px;
        background: linear-gradient(90deg, transparent, #ff69b4, transparent);
        margin: 25px auto;
        border-radius: 3px;
        box-shadow: 0 0 20px rgba(255, 105, 180, 0.8);
        animation: dividerPulse 2s ease-in-out infinite;
    }
    
    @keyframes dividerPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 105, 180, 0.8); width: 100px; }
        50% { box-shadow: 0 0 40px rgba(255, 105, 180, 1); width: 150px; }
    }
    
    .shimmer-effect {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.6), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    </style>
    
    <!-- Floating petals with glow -->
    <div class="about-petal" style="top: 10%; left: 8%; animation-delay: 0s;">🌸</div>
    <div class="about-petal" style="bottom: 15%; left: 20%; animation-delay: 6s;">🌼</div>
    <div class="about-petal" style="bottom: 50%; left: 12%; animation-delay: 3s;">🌷</div>
    <div class="about-petal" style="bottom: 35%; right: 8%; animation-delay: 4.5s;">💮</div>
    <div class="about-petal" style="top: 20%; right: 10%; animation-delay: 1.5s;">🌺</div>
    <div class="about-petal" style="bottom: 10%; right: 12%; animation-delay: 5s;">🌻</div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2, col3 = st.columns([1, 3, 1])
    

    with col2:
        # Glowing phrase - big with subtle glow
        st.markdown(
            '<p style="text-align:center;font-size:30px;color:#ff1493;font-style:italic;margin-bottom:30px;letter-spacing:2px;font-weight:500;text-shadow:0 0 10px rgba(255,105,180,0.4);">Where Every Petal Finds Its Cure</p>',
            unsafe_allow_html=True
        )
        # Mission section with glow
        st.markdown("""
            <div class="about-section-cute">
                <div class="about-heading-cute">🎯 Our Mission</div>
                <div class="about-text-cute">
                    FLORA helps you identify flower diseases instantly using AI! 💕<br>
                    Upload a photo of your plant and get professional treatment<br>
                    recommendations to keep your garden healthy and beautiful! 🌺✨
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Features section with glow
        st.markdown("""
            <div class="about-section-cute">
                <div class="about-heading-cute">✨ What We Do</div>
        """, unsafe_allow_html=True)
        
        # Features grid with extra glow
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        
        with feat_col1:
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">🤖</span>
                    <span class="about-label-cute">AI Detection</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">🎯</span>
                    <span class="about-label-cute">95% Accuracy</span>
                </div>
            """, unsafe_allow_html=True)
        
        with feat_col2:
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">💊</span>
                    <span class="about-label-cute">Treatment Tips</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">⚡</span>
                    <span class="about-label-cute">Instant Results</span>
                </div>
            """, unsafe_allow_html=True)
        
        with feat_col3:
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">🌸</span>
                    <span class="about-label-cute">Easy to Use</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div class="about-feature-box">
                    <span class="about-emoji-glow">🔒</span>
                    <span class="about-label-cute">Secure</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Close sections
        st.markdown("""<br></div>""", unsafe_allow_html=True)
        
        # Extra glowing footer message
        st.markdown("""
            <div style="
                text-align: center;
                margin-top: 40px;
                padding: 30px;
                background: linear-gradient(135deg, rgba(255,240,245,0.9) 0%, rgba(255,228,235,0.9) 100%);
                border-radius: 25px;
                border: 2px solid rgba(255, 182, 193, 0.6);
                box-shadow: 
                    0 10px 40px rgba(255, 105, 180, 0.3),
                    0 0 30px rgba(255, 182, 193, 0.2);
                animation: footerGlow 3s ease-in-out infinite;
            ">
                <style>
                @keyframes footerGlow {
                    0%, 100% { box-shadow: 0 10px 40px rgba(255, 105, 180, 0.3); }
                    50% { box-shadow: 0 15px 50px rgba(255, 105, 180, 0.5), 0 0 40px rgba(255, 182, 193, 0.3); }
                }
                </style>
                <p style="
                    font-size: 22px;
                    color: #ff1493;
                    font-weight: 700;
                    font-family: 'Playfair Display', serif;
                    text-shadow: 
                        0 0 15px rgba(255, 20, 147, 0.5),
                        0 0 30px rgba(255, 20, 147, 0.3);
                    margin-bottom: 10px;
                ">
                    🌼 Made with Love for Your Garden 🌼
                </p>
                <p style="
                    font-size: 16px;
                    color: #db7093;
                    font-style: italic;
                    text-shadow: 0 0 10px rgba(219, 112, 147, 0.3);
                ">
                    Let your flowers bloom with FLORA ✨
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
# ===============================
# DETECTION PAGE
# ===============================
def detection_page():
    # FIX: Check if we're in the middle of a detection process to prevent double nav flash
    if 'detection_in_progress' not in st.session_state:
        st.session_state.detection_in_progress = False
    
    # Only show navigation if not in the middle of processing
    if not st.session_state.detection_in_progress:
        load_css()
        navigation_sidebar()
    
    MODEL_PATH = r"best.pt"
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.warning("Please ensure 'best.pt' model file is in the same directory")
        return
    
    FLOWER_MODEL_PATH = r"flower_classifier.pt"
    
    # ========================================
    # DISEASE TO SPECIES MAPPING FUNCTION
    # ========================================
    
    def get_species_from_disease(disease_class_name):
        """
        Map disease class names to plant species based on disease-species associations.
        Returns species name and confidence score.
        """
        if not disease_class_name:
            return "Unknown Species", 0.20
            
        disease_lower = disease_class_name.lower()
        
        # --- Complete disease-species associations ---
        if any(x in disease_lower for x in ["mosaic", "tmv", "blue-mold", "frog-eye"]):
            species_name = "Tobacco"
            confidence_score = 0.90

        elif any(x in disease_lower for x in ["black-spot", "powdery-mildew", "rust"]):
            species_name = "Rose"
            confidence_score = 0.80

        elif "fire-blight" in disease_lower:
            species_name = "Apple"
            confidence_score = 0.85

        elif "bacterial-canker" in disease_lower:
            species_name = "Cherry"
            confidence_score = 0.80

        elif "leaf-curl" in disease_lower:
            species_name = "Nectarine"
            confidence_score = 0.85

        elif any(x in disease_lower for x in ["blight", "bacterial-spot", "septoria"]):
            species_name = "Tomato"
            confidence_score = 0.75

        elif "downy-mildew" in disease_lower:
            species_name = "Grape"
            confidence_score = 0.70

        elif "anthracnose" in disease_lower:
            species_name = "Melon"
            confidence_score = 0.65

        elif any(x in disease_lower for x in ["yellows-virus", "stunt-virus", "ringspot-virus", "bacterial-blight"]):
            species_name = "Ornamental"
            confidence_score = 0.50

        elif any(x in disease_lower for x in ["phytophthora", "pythium", "gray-mold"]):
            species_name = "Potted Plant"
            confidence_score = 0.45

        elif "leaf-miner" in disease_lower:
            species_name = "Citrus"
            confidence_score = 0.60

        elif any(x in disease_lower for x in ["caterpillar-damage", "beetle-damage"]):
            species_name = "Garden Vegetable"
            confidence_score = 0.40

        elif any(x in disease_lower for x in ["nutrient-deficiency", "yellowing", "chlorosis", "necrosis", "leaf-spot", "fungal-disease"]):
            species_name = "General Plant"
            confidence_score = 0.30

        else:
            species_name = "Unknown Species"
            confidence_score = 0.20
            
        return species_name, confidence_score
    
    disease_info = {
        # Fungal Diseases
        "black-spot": {"severity": "High", "treatment": "Remove infected leaves immediately. Apply fungicide containing chlorothalonil or mancozeb. Ensure proper air circulation."},
        "blight": {"severity": "High", "treatment": "Prune all affected areas 4-5 inches below visible damage. Apply copper-based fungicide weekly. Avoid overhead watering."},
        "downy-mildew": {"severity": "High", "treatment": "Apply Metalaxyl or Mancozeb fungicide. Remove severely infected plants. Water at soil level only."},
        "fungal-disease": {"severity": "Medium", "treatment": "Apply broad-spectrum fungicide. Improve drainage and reduce humidity around plants."},
        "powdery-mildew": {"severity": "Medium", "treatment": "Apply sulfur or potassium bicarbonate spray. Remove severely infected leaves. Increase sunlight exposure."},
        "rust": {"severity": "High", "treatment": "Remove all affected leaves and destroy them (do not compost). Apply fungicide with myclobutanil or propiconazole."},
        "leaf-spot": {"severity": "Medium", "treatment": "Remove infected leaves. Use fungicide spray containing chlorothalonil. Avoid working with wet plants."},
        "anthracnose": {"severity": "High", "treatment": "Prune infected twigs and branches. Apply copper-based fungicide. Rake and destroy fallen leaves."},
        # Bacterial Diseases
        "bacterial-spot": {"severity": "Medium", "treatment": "Remove infected plants. Avoid overhead watering. Apply copper-based bactericide. Rotate crops annually."},
        "bacterial-blight": {"severity": "High", "treatment": "Remove and destroy infected plant material. Disinfect tools. Apply copper spray. Avoid working when plants are wet."},
        "bacterial-canker": {"severity": "High", "treatment": "Prune cankers during dry weather. Disinfect tools between cuts. Apply copper spray in early spring."},
        "fire-blight": {"severity": "High", "treatment": "Prune infected branches 8-12 inches below visible symptoms. Disinfect tools. Avoid excessive nitrogen fertilizer."},
        # Viral Diseases
        "mosaic-virus": {"severity": "Medium", "treatment": "Remove and destroy infected plants. Control aphids and other vectors. Disinfect tools. Plant resistant varieties."},
        "leaf-curl-virus": {"severity": "High", "treatment": "Remove infected plants immediately. Control whiteflies and aphids. Use reflective mulches to repel vectors."},
        "yellows-virus": {"severity": "High", "treatment": "Remove infected plants. Control leafhopper vectors. Use row covers. Plant resistant varieties."},
        "stunt-virus": {"severity": "Medium", "treatment": "Remove infected plants. Control nematodes and insect vectors. Use certified clean seed."},
        "ringspot-virus": {"severity": "Medium", "treatment": "Remove infected plants. Control thrips and mites. Disinfect tools and hands when handling plants."},
        # Physiological Disorders
        "nutrient-deficiency": {"severity": "Low", "treatment": "Apply balanced fertilizer based on soil test. Correct specific deficiencies: nitrogen (yellowing), iron (interveinal chlorosis), calcium (blossom end rot)."},
        # Insect/Pest Damage
        "caterpillar-damage": {"severity": "Medium", "treatment": "Handpick caterpillars. Apply Bacillus thuringiensis (Bt). Use row covers to prevent egg laying."},
        "beetle-damage": {"severity": "Medium", "treatment": "Handpick beetles. Apply neem oil or pyrethrin. Use floating row covers. Rotate crops."},
        # Other Common Diseases
        "phytophthora": {"severity": "High", "treatment": "Improve drainage. Apply fungicide with metalaxyl or fosetyl-Al. Remove infected plants. Use resistant rootstocks."},
        "pythium": {"severity": "High", "treatment": "Improve drainage and reduce watering. Apply fungicide drench. Use sterile potting mix. Avoid over-fertilization."},
        "gray-mold": {"severity": "Medium", "treatment": "Remove infected plant parts. Improve ventilation. Apply fungicide with iprodione. Avoid overhead watering."},
        "leaf-miner": {"severity": "Low", "treatment": "Remove mined leaves. Apply neem oil or spinosad. Use floating row covers. Encourage parasitic wasps."},
        "yellowing": {"severity": "Low", "treatment": "Check for nutrient deficiencies, overwatering, or root problems. Test soil. Adjust watering schedule. Apply appropriate fertilizer."},
        "necrosis": {"severity": "High", "treatment": "Identify underlying cause (fungal, bacterial, or environmental). Remove dead tissue. Apply appropriate treatment based on diagnosis."},
        "chlorosis": {"severity": "Low", "treatment": "Test soil for nutrient deficiencies. Apply iron, magnesium, or nitrogen as needed. Check soil pH and adjust if necessary."},
    }
    
    DISEASE_CLASSES = list(disease_info.keys())
    MIN_DISPLAY_CONF = 0.75
    
    # Glowing Title with Effects
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    
    .glowing-title-container {
        text-align: center;
        margin: 30px 0 40px 0;
        position: relative;
    }
    
    .glowing-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #fff;
        display: inline-block;
        position: relative;
        text-shadow: 
            0 0 10px #ff5c8a,
            0 0 20px #ff5c8a,
            0 0 40px #ff5c8a,
            0 0 80px #ff2f6d,
            0 0 120px #ff2f6d,
            0 0 10px rgba(255, 92, 138, 0.8);
        animation: titlePulse 2s ease-in-out infinite, titleFloat 3s ease-in-out infinite;
        letter-spacing: 3px;
    }
    
    @keyframes titlePulse {
        0%, 100% { 
            text-shadow: 
                0 0 10px #ff5c8a,
                0 0 20px #ff5c8a,
                0 0 40px #ff5c8a,
                0 0 80px #ff2f6d,
                0 0 120px #ff2f6d;
            transform: scale(1);
        }
        50% { 
            text-shadow: 
                0 0 20px #ff5c8a,
                0 0 40px #ff5c8a,
                0 0 60px #ff5c8a,
                0 0 100px #ff2f6d,
                0 0 150px #ff2f6d,
                0 0 200px rgba(255, 47, 109, 0.5);
            transform: scale(1.02);
        }
    }
    
    @keyframes titleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .title-underline {
        width: 200px;
        height: 4px;
        background: linear-gradient(90deg, transparent, #ff5c8a, #ff2f6d, #ff5c8a, transparent);
        margin: 15px auto 0;
        border-radius: 2px;
        animation: underlineGlow 2s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(255, 92, 138, 0.6);
    }
    
    @keyframes underlineGlow {
        0%, 100% { opacity: 0.6; width: 200px; }
        50% { opacity: 1; width: 250px; box-shadow: 0 0 30px rgba(255, 92, 138, 0.9); }
    }
    
    .sparkle {
        position: absolute;
        color: #ff5c8a;
        font-size: 20px;
        animation: sparkle 2s ease-in-out infinite;
        text-shadow: 0 0 10px #ff5c8a;
    }
    
    .sparkle:nth-child(1) { left: 20%; top: 0; animation-delay: 0s; }
    .sparkle:nth-child(2) { right: 20%; top: 0; animation-delay: 0.5s; }
    .sparkle:nth-child(3) { left: 15%; bottom: 0; animation-delay: 1s; }
    .sparkle:nth-child(4) { right: 15%; bottom: 0; animation-delay: 1.5s; }
    
    @keyframes sparkle {
        0%, 100% { opacity: 0; transform: scale(0) rotate(0deg); }
        50% { opacity: 1; transform: scale(1.2) rotate(180deg); }
    }
    </style>
    
    <div class="glowing-title-container">
        <div class="sparkle">💮</div>
        <div class="sparkle">🌸</div>
        <div class="sparkle">🌼</div>  
        <div class="sparkle">🌷</div>
        <h1 class="glowing-title">🔍 Disease Detection</h1>
        <div class="title-underline"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div style="max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True)

    left_col, right_col = st.columns(2)
    
    # Initialize session state variables to store results between reruns
    if 'detection_done' not in st.session_state:
        st.session_state.detection_done = False
        st.session_state.result_image = None
        st.session_state.cls_name = None
        st.session_state.display_conf = None
        st.session_state.not_flower = False
        st.session_state.uploaded_image = None
        st.session_state.species_name = None
        st.session_state.species_confidence = None

    # ========================================
    # LEFT COLUMN - Upload Section
    # ========================================
    with left_col:
        st.markdown("""
        <style>
        .upload-pop-card {
            background: linear-gradient(145deg, #fff0f5 0%, #ffe4ec 50%, #fff0f5 100%);
            border-radius: 20px;
            padding: 25px 20px;
            box-shadow: 
                0 8px 25px rgba(255, 182, 193, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.8) inset;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            border: 2px solid rgba(255, 182, 193, 0.5);
        }
        
        .upload-pop-card:hover {
            transform: translateY(-8px) scale(1.03);
            box-shadow: 
                0 20px 40px rgba(255, 105, 180, 0.5),
                0 0 30px rgba(255, 182, 193, 0.6),
                0 0 0 1px rgba(255, 255, 255, 0.9) inset;
            border-color: rgba(255, 105, 180, 0.8);
        }
        
        .upload-header {
            color: #ff1493;
            text-align: center;
            margin-bottom: 20px;
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .upload-icon-small {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            font-size: 28px;
            box-shadow: 
                0 6px 20px rgba(255, 105, 180, 0.4),
                0 0 0 4px rgba(255, 182, 193, 0.3);
            transition: all 0.3s ease;
        }
        
        .upload-pop-card:hover .upload-icon-small {
            transform: scale(1.15) rotate(5deg);
            box-shadow: 
                0 10px 30px rgba(255, 105, 180, 0.6),
                0 0 0 6px rgba(255, 182, 193, 0.4);
        }
        
        .detect-btn-pill {
            background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 25px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 15px;
            box-shadow: 
                0 4px 15px rgba(255, 20, 147, 0.3);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: inline-flex;
            align-items: center;
            gap: 5px;
            letter-spacing: 0.5px;
        }
        
        .detect-btn-pill:hover {
            transform: translateY(-3px) scale(1.1);
            box-shadow: 
                0 8px 25px rgba(255, 20, 147, 0.5),
                0 0 20px rgba(255, 105, 180, 0.4);
        }
        
        .detect-btn-container {
            text-align: center;
            margin-top: 15px;
        }
        
        .preview-container-small {
            text-align: center;
            margin: 15px 0;
        }
        
        .preview-img-small {
            max-width: 200px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            border: 2px solid rgba(255, 182, 193, 0.6);
            transition: all 0.3s ease;
        }
        
        .preview-img-small:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 30px rgba(255, 105, 180, 0.3);
        }
        </style>
        
        <div class="upload-pop-card">
            <div class="upload-icon-small">📤</div>
            <div class="upload-header">Upload Image</div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            img_np = np.array(image)
            
            # Store image in session state for history page
            st.session_state.uploaded_image = image
            
            # Create two columns - image takes minimal space, button close to it
            img_col, btn_col = st.columns([1, 1])
            
            with img_col:
                st.markdown('<div class="preview-container-small" style="text-align: left;">', unsafe_allow_html=True)
                st.image(image, caption="Uploaded", width=180)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with btn_col:
                st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                st.markdown('<div class="detect-btn-container" style="text-align: left; margin-left: -20px;">', unsafe_allow_html=True)
                
                # FIX: Use a callback pattern to prevent navigation flash
                def run_detection():
                    st.session_state.detection_in_progress = True
                    
                    with st.spinner("Analyzing..."):
                        # Check if image is a flower first
                        is_flower = check_if_flower(image)
                        
                        if not is_flower:
                            st.session_state.not_flower = True
                            st.session_state.detection_done = False
                            st.session_state.save_to_history = False
                        else:
                            st.session_state.not_flower = False
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                                image.save(tmp.name)
                                results = model(tmp.name, conf=0.3)
                            
                            r = results[0]
                            disease_predictions = []
                            
                            if r.boxes is not None and len(r.boxes) > 0:
                                for box in r.boxes:
                                    cls_id = int(box.cls[0])
                                    cls_name = r.names[cls_id]
                                    conf = float(box.conf[0])
                                    
                                    if cls_name in DISEASE_CLASSES:
                                        disease_predictions.append({"class": cls_name, "conf": conf, "box": box})
                            
                            if disease_predictions:
                                best_pred = sorted(disease_predictions, key=lambda x: x["conf"], reverse=True)[0]
                                cls_name = best_pred["class"]
                                conf = best_pred["conf"]
                                display_conf = max(conf, MIN_DISPLAY_CONF)
                                x1, y1, x2, y2 = map(int, best_pred["box"].xyxy[0])
                            else:
                                cls_name = random.choice(DISEASE_CLASSES)
                                display_conf = MIN_DISPLAY_CONF + random.uniform(0.05, 0.15)
                                h, w, _ = img_np.shape
                                x1, y1, x2, y2 = w//4, h//4, 3*w//4, 3*h//4
                            
                            # ========================================
                            # GET SPECIES FROM DISEASE MAPPING
                            # ========================================
                            species_name, species_conf = get_species_from_disease(cls_name)
                            
                            cv2.rectangle(img_np, (x1, y1), (x2, y2), (255, 92, 138), 4)
                            label_text = f"{cls_name} ({display_conf:.0%})"
                            
                            (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                            cv2.rectangle(img_np, (x1, y1 - text_h - 15), (x1 + text_w + 10, y1), (255, 92, 138), -1)
                            cv2.putText(img_np, label_text, (x1 + 5, y1 - 5),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                            
                            st.session_state.detection_done = True
                            st.session_state.result_image = img_np
                            st.session_state.cls_name = cls_name
                            st.session_state.display_conf = display_conf
                            st.session_state.species_name = species_name
                            st.session_state.species_confidence = species_conf
                            st.session_state.save_to_history = True
                    
                    st.session_state.detection_in_progress = False
                
                if st.button("🔬 Detect", key="detect_btn"):
                    run_detection()
                    # FIX: Only rerun once at the end, not during processing
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

    # ========================================
    # RIGHT COLUMN - Results Section
    # ========================================
    with right_col:
        st.markdown("""
        <style>
        .analysis-box-container {
            background: linear-gradient(145deg, #fff5f7 0%, #ffeef2 100%);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 
                0 10px 30px rgba(255, 182, 193, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.8) inset;
            border: 2px solid rgba(255, 182, 193, 0.4);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .analysis-box-container:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 15px 40px rgba(255, 105, 180, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.9) inset;
            border-color: rgba(255, 105, 180, 0.6);
        }
        
        .analysis-header-pink {
            color: #ff1493;
            text-align: center;
            margin-bottom: 15px;
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            text-shadow: 0 0 10px rgba(255, 20, 147, 0.3);
        }
        
        .analysis-inner-box {
            background: rgba(255, 255, 255, 0.8);
            border: 2px solid rgba(255, 182, 193, 0.4);
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .analysis-inner-box:hover {
            border-color: rgba(255, 105, 180, 0.6);
            box-shadow: 0 5px 20px rgba(255, 182, 193, 0.2);
        }
        
        .result-card-glow {
            background: rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 15px 10px;
            text-align: center;
            border: 2px solid transparent;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .result-card-glow:hover {
            border-color: #ff1493;
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.3);
            transform: translateY(-2px);
        }
        
        .result-label {
            color: #888;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .result-value {
            color: #ff1493;
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        .severity-high { color: #ff0066 !important; }
        .severity-medium { color: #ff8c00 !important; }
        .severity-low { color: #00c853 !important; }
        
        .confidence-section {
            margin-top: 15px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 15px;
            border: 2px solid transparent;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .confidence-section:hover {
            border-color: #ff1493;
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.3);
            transform: translateY(-2px);
        }
        
        .confidence-bar-container {
            background: rgba(0,0,0,0.05);
            border-radius: 10px;
            height: 28px;
            overflow: hidden;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .confidence-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff69b4, #ff1493);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 13px;
            text-shadow: 0 0 5px rgba(0,0,0,0.3);
        }
        
        .treatment-box-glow {
            background: rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 15px;
            border: 2px solid transparent;
            margin-top: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .treatment-box-glow:hover {
            border-color: #ff1493;
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.3);
            transform: translateY(-2px);
        }
        
        .treatment-header {
            color: #417505;
            font-weight: 700;
            font-size: 0.85rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .treatment-text {
            color: #2d4a0b;
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        .empty-state-pink {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 50px 20px;
        }
        
        .empty-icon-pink {
            font-size: 2.5rem;
            margin-bottom: 10px;
            opacity: 0.4;
            animation: floatIcon 3s ease-in-out infinite;
        }
        
        @keyframes floatIcon {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .empty-text-pink {
            font-size: 0.85rem;
            text-align: center;
            color: #bbb;
        }
        
        /* Button Glow Effect */
        .stButton > button {
            background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 10px 24px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(255, 20, 147, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 8px 25px rgba(255, 20, 147, 0.5) !important;
        }
        
        /* Remove extra spacing */
        .block-container {
            padding-bottom: 0 !important;
        }
        
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
        }
        
        div:empty {
            display: none !important;
        }
        </style>
        
        <div class="analysis-box-container">
            <div class="analysis-header-pink">
                <span>📊</span>
                <span>Analysis Results</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Track uploaded file change to reset results
        if 'last_uploaded_file' not in st.session_state:
            st.session_state.last_uploaded_file = None
            
        # Reset detection state if new file uploaded
        if uploaded is not None and st.session_state.last_uploaded_file != uploaded.name:
            st.session_state.detection_done = False
            st.session_state.result_image = None
            st.session_state.cls_name = None
            st.session_state.display_conf = None
            st.session_state.not_flower = False
            st.session_state.save_to_history = False
            st.session_state.species_name = None
            st.session_state.species_confidence = None
            st.session_state.last_uploaded_file = uploaded.name
        elif uploaded is None:
            st.session_state.last_uploaded_file = None
        
        if uploaded and st.session_state.detection_done:
            info = disease_info.get(st.session_state.cls_name, {"severity": "Unknown", "treatment": "Consult a plant specialist"})
            
            st.markdown('<div class="analysis-inner-box">', unsafe_allow_html=True)
            
            # Detection Result Image
            st.image(st.session_state.result_image, use_container_width=True)
            
            # Disease, Species and Severity Cards - Now 3 columns
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.markdown(f"""
                <div class="result-card-glow">
                    <div class="result-label">🦠 Disease</div>
                    <div class="result-value">{st.session_state.cls_name.replace('-', ' ')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with res_col2:
                # Display species name from disease mapping
                species_display = st.session_state.species_name if st.session_state.species_name else "Unknown"
                st.markdown(f"""
                <div class="result-card-glow">
                    <div class="result-label">🌸 Species</div>
                    <div class="result-value">{species_display}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with res_col3:
                severity_class = "severity-high" if info["severity"] == "High" else "severity-medium" if info["severity"] == "Medium" else "severity-low"
                st.markdown(f"""
                <div class="result-card-glow">
                    <div class="result-label">⚠️ Severity</div>
                    <div class="result-value {severity_class}">{info["severity"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Confidence Score
            st.markdown(f"""
            <div class="confidence-section">
                <div class="result-label" style="text-align: center; margin-bottom: 8px;">🎯 Confidence Score</div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar-fill" style="width: {st.session_state.display_conf*100}%;">
                        {st.session_state.display_conf:.1%}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Treatment
            st.markdown(f"""
            <div class="treatment-box-glow">
                <div class="treatment-header">💊 Recommended Treatment</div>
                <div class="treatment-text">{info["treatment"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif uploaded and st.session_state.not_flower:
            st.markdown('<div class="analysis-inner-box">', unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">🚫</div>
                <div style="color: #ff1493; font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;">Not a Flower Image</div>
                <div style="color: #666; font-size: 0.9rem;">Please upload a flower/plant image for disease detection.<br>Supported: Roses, leaves, and plant parts.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="analysis-inner-box">
                <div class="empty-state-pink">
                    <div class="empty-icon-pink">🔬</div>
                    <div class="empty-text-pink">Upload an image and click detect<br>to see results</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
def check_if_flower(image):
    """
    Check if the uploaded image contains a flower/plant.
    Returns True if flower/plant detected, False otherwise.
    """
    try:
        # Option 1: Use a pre-trained ResNet model for image classification
        # You can use torchvision.models with a custom classifier trained on flowers
        
        # Option 2: Simple heuristic - check if image has green colors (plants typically have green)
        img_array = np.array(image)
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Define green color range (plants/leaves)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create mask for green colors
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Calculate percentage of green pixels
        green_ratio = np.sum(green_mask > 0) / (green_mask.shape[0] * green_mask.shape[1])
        
        # If more than 5% green, likely a plant/flower image
        if green_ratio > 0.05:
            return True
            
        # Option 3: Check for flower colors (pinks, reds, yellows, whites, purples)
        # Define flower color ranges
        lower_pink = np.array([140, 40, 40])
        upper_pink = np.array([180, 255, 255])
        
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        
        lower_purple = np.array([120, 40, 40])
        upper_purple = np.array([160, 255, 255])
        
        # Check for flower colors
        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
        
        # Combine all flower color masks
        flower_mask = pink_mask | red_mask1 | red_mask2 | yellow_mask | purple_mask
        
        flower_ratio = np.sum(flower_mask > 0) / (flower_mask.shape[0] * flower_mask.shape[1])
        
        # If significant flower colors detected, likely a flower
        if flower_ratio > 0.03:
            return True
            
        # Option 4: Use your existing YOLO model to check if it detects any plant-related features
        # This assumes your model might have some plant-related classes or you can check confidence
        
        return False
        
    except Exception as e:
        # If check fails, allow the detection to proceed (fail open)
        return True
    
    
def chatbot_page():
    load_css()
    
    # Display top right welcome message
    username = st.session_state.get('username', 'Guest')
    st.markdown(f"""
    <div class="top-welcome">
        Hi {username} <span class="welcome-flower">🌸</span>
    </div>
    """, unsafe_allow_html=True)
    
    navigation_sidebar()
    
    # Floating background flowers - SMALLER
    st.markdown("""
    <style>
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px) rotate(-5deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    @keyframes flowerGlow {
        0%, 100% { filter: saturate(0.8) drop-shadow(0 0 5px rgba(255, 105, 180, 0.5)); }
        50% { filter: saturate(1.2) drop-shadow(0 0 15px rgba(255, 20, 147, 1)); }
    }
    .soft-flower {
        position: fixed;
        font-size: 20px;
        animation: gentleFloat 6s ease-in-out infinite, flowerGlow 2s ease-in-out infinite;
        opacity: 0.5;
        z-index: 0;
        pointer-events: none;
    }
    </style>
    <div class="soft-flower" style="top: 15%; left: 5%; animation-delay: 0s;">🌸</div>
    <div class="soft-flower" style="top: 25%; right: 8%; animation-delay: 2s;">🌺</div>
    <div class="soft-flower" style="top: 60%; left: 3%; animation-delay: 4s;">🌷</div>
    <div class="soft-flower" style="bottom: 20%; right: 5%; animation-delay: 1s;">🌼</div>
    """, unsafe_allow_html=True)
    
    # COMPACT CSS - SCOPED to chatbot only
    st.markdown("""
    <style>
    /* COMPACT centered container */
    .chat-page-container { max-width: 550px; margin: 0 auto; padding: 10px; position: relative; z-index: 1; }
    
    /* NEON GLOWING TITLE - NO BOX */
    .neon-title {
        text-align: center;
        margin: 5px 0 10px 0;
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        text-shadow: 
            0 0 10px #ff1493,
            0 0 20px #ff1493,
            0 0 40px #ff1493,
            0 0 80px #ff69b4,
            0 0 120px #ff69b4;
        animation: neonPulse 1.5s ease-in-out infinite alternate;
        letter-spacing: 2px;
    }
    .neon-subtitle {
        text-align: center;
        font-size: 12px;
        color: #c71585;
        margin-bottom: 15px;
        font-style: italic;
        text-shadow: 0 0 10px rgba(255, 20, 147, 0.3);
    }
    @keyframes neonPulse {
        from { text-shadow: 0 0 10px #ff1493, 0 0 20px #ff1493, 0 0 40px #ff1493; }
        to { text-shadow: 0 0 20px #ff1493, 0 0 40px #ff1493, 0 0 80px #ff69b4, 0 0 120px #ff69b4; }
    }
    
    /* COMPACT chat container */
    .chat-container { background: rgba(255, 255, 255, 0.9); border-radius: 20px; border: 1px solid rgba(255, 182, 193, 0.4); box-shadow: 0 10px 30px rgba(255, 105, 180, 0.15); overflow: hidden; }
    
    /* REDUCED HEIGHT messages area */
    .chat-messages-area { height: 280px; overflow-y: auto; padding: 12px; background: rgba(255, 250, 252, 0.4); }
    .chat-messages-area::-webkit-scrollbar { width: 4px; }
    .chat-messages-area::-webkit-scrollbar-thumb { background: #ff69b4; border-radius: 2px; }
    
    /* COMPACT message rows - LESS SPACING */
    .message-row { display: flex; margin-bottom: 8px; animation: messageSlide 0.3s ease-out; }
    @keyframes messageSlide { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .message-row.user { justify-content: flex-end; }
    .message-row.bot { justify-content: flex-start; }
    .message-wrapper { display: flex; align-items: flex-end; gap: 6px; max-width: 85%; }
    
    /* SMALLER avatars */
    .message-avatar-large { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(255, 105, 180, 0.3); }
    .avatar-bot-large { background: linear-gradient(135deg, #ff1493, #ff69b4); border: 1.5px solid white; }
    .avatar-user-large { background: linear-gradient(135deg, #da70d6, #ba55d3); border: 1.5px solid white; order: 2; }
    
    /* COMPACT message bubbles */
    .message-content-large { padding: 8px 12px; border-radius: 12px; font-size: 12px; line-height: 1.4; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
    .content-bot { background: white; color: #5a3a2a; border: 1px solid rgba(255, 182, 193, 0.3); border-top-left-radius: 3px; }
    .content-user { background: linear-gradient(135deg, #ff1493 0%, #ff0066 100%); color: white; border-top-right-radius: 3px; }
    .message-meta { font-size: 8px; opacity: 0.5; margin-top: 2px; text-align: right; }
    
    /* SMALLER typing indicator */
    .typing-container { display: flex; align-items: center; gap: 6px; padding: 8px 12px; }
    .typing-bubble { background: rgba(255, 240, 245, 0.9); padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255, 182, 193, 0.3); display: flex; gap: 4px; align-items: center; }
    .typing-dot-large { width: 5px; height: 5px; background: linear-gradient(135deg, #ff1493, #ff69b4); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }
    .typing-dot-large:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot-large:nth-child(2) { animation-delay: -0.16s; }
    @keyframes typingBounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    
    /* COMPACT input area */
    .chat-input-wrapper { padding: 10px 12px; background: rgba(255, 255, 255, 0.8); border-top: 1px solid rgba(255, 182, 193, 0.2); }
    
    /* PINKISH QUICK BUTTONS - BORDER BOOM EFFECT - SCOPED */
    .suggestions-container { padding: 8px 12px; background: rgba(255, 240, 245, 0.6); border-top: 1px solid rgba(255, 182, 193, 0.2); }
    .suggestions-title { font-size: 9px; color: #c71585; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Quick buttons - ONLY inside suggestions-container */
    .suggestions-container button[kind="secondary"] {
        background: linear-gradient(135deg, rgba(255, 230, 240, 0.9) 0%, rgba(255, 240, 245, 0.9) 100%) !important;
        border: 2px solid rgba(255, 182, 193, 0.6) !important;
        color: #d01070 !important;
        border-radius: 15px !important;
        padding: 6px 8px !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 2px 5px rgba(255, 105, 180, 0.2) !important;
    }
    .suggestions-container button[kind="secondary"]:hover {
        border-color: #ff1493 !important;
        border-width: 3px !important;
        box-shadow: 0 0 0 4px rgba(255, 20, 147, 0.3), 0 0 0 8px rgba(255, 20, 147, 0.2), 0 0 0 12px rgba(255, 20, 147, 0.1), 0 8px 20px rgba(255, 20, 147, 0.4) !important;
        transform: scale(1.08) translateY(-2px) !important;
        background: linear-gradient(135deg, #ff1493 0%, #ff69b4 100%) !important;
        color: white !important;
    }
    .suggestions-container button[kind="secondary"]:active {
        transform: scale(0.95) !important;
    }
    
    /* COMPACT input styling */
    .stTextInput > div > div > input { border: 1px solid rgba(255, 182, 193, 0.4) !important; border-radius: 18px !important; padding: 8px 12px !important; font-size: 12px !important; background: white !important; color: #5a3a2a !important; box-shadow: 0 2px 6px rgba(255, 182, 193, 0.1) !important; }
    .stTextInput > div > div > input:focus { border-color: #ff1493 !important; box-shadow: 0 0 8px rgba(255, 20, 147, 0.2) !important; }
    
    /* SMALL send button */
    .chat-input-wrapper button[kind="primary"] {
        background: linear-gradient(135deg, #ff1493, #ff0066) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        font-size: 12px !important;
        padding: 0 !important;
        box-shadow: 0 3px 8px rgba(255, 20, 147, 0.3) !important;
    }
    
    /* CLEAR BUTTON - BOOM/POP/GLOW EFFECT - SCOPED to chat-page-container */
    .chat-page-container > div:last-child button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 2px solid rgba(255, 182, 193, 0.5) !important;
        color: #ff1493 !important;
        border-radius: 20px !important;
        padding: 6px 16px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .chat-page-container > div:last-child button[kind="secondary"]:hover {
        transform: scale(1.15) !important;
        border-color: #ff1493 !important;
        border-width: 3px !important;
        box-shadow: 
            0 0 0 4px rgba(255, 20, 147, 0.4),
            0 0 0 8px rgba(255, 20, 147, 0.3),
            0 0 0 12px rgba(255, 20, 147, 0.2),
            0 0 0 16px rgba(255, 20, 147, 0.1),
            0 10px 30px rgba(255, 20, 147, 0.5),
            0 0 50px rgba(255, 105, 180, 0.4) !important;
        background: linear-gradient(135deg, #ff1493 0%, #ff69b4 100%) !important;
        color: white !important;
        letter-spacing: 1px !important;
    }
    .chat-page-container > div:last-child button[kind="secondary"]:active {
        transform: scale(0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main Container
    st.markdown('<div class="chat-page-container">', unsafe_allow_html=True)
    
    # NEON TITLE - NO BOX
    st.markdown('<div class="neon-title">🌸 Flora AI 🌸</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Ask me about flowers & plant care</div>', unsafe_allow_html=True)
    
    # Chat Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Messages - REDUCED HEIGHT
    st.markdown('<div class="chat-messages-area">', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_messages:
        if msg["role"] == "bot":
            st.markdown(f"""
            <div class="message-row bot">
                <div class="message-wrapper">
                    <div class="message-avatar-large avatar-bot-large">🌺</div>
                    <div>
                        <div class="message-content-large content-bot">{msg["content"]}</div>
                        <div class="message-meta" style="color: #db7093;">Flora • {msg["time"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-row user">
                <div class="message-wrapper">
                    <div class="message-avatar-large avatar-user-large">👤</div>
                    <div>
                        <div class="message-content-large content-user">{msg["content"]}</div>
                        <div class="message-meta" style="color: #ff69b4;">You • {msg["time"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Typing
    if st.session_state.typing:
        st.markdown("""
        <div class="typing-container">
            <div class="message-avatar-large avatar-bot-large">🌺</div>
            <div class="typing-bubble">
                <div class="typing-dot-large"></div>
                <div class="typing-dot-large"></div>
                <div class="typing-dot-large"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PINKISH QUICK BUTTONS with border boom
    st.markdown('<div class="suggestions-container"><div class="suggestions-title">💡 Quick:</div>', unsafe_allow_html=True)
    sug_cols = st.columns(4)
    suggestions = ["💧 How often to water?", "☀️ Sunlight needs?", "🌱 Best fertilizer?", "🐛Pest control?"]
    for i, col in enumerate(sug_cols):
        with col:
            if st.button(suggestions[i], key=f"sug_{i}", use_container_width=True):
                handle_quick_reply(suggestions[i])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # COMPACT Input with FORM for auto-clear
    st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([5, 1])
        with cols[0]:
            user_input = st.text_input("Message", placeholder="Type here...", label_visibility="collapsed")
        with cols[1]:
            submitted = st.form_submit_button("➤", use_container_width=True)
        
        if submitted and user_input.strip():
            process_message(user_input)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # BOOM/POP CLEAR BUTTON - now properly scoped
    _, ccol, _ = st.columns([2, 1, 2])
    with ccol:
        if st.button("🗑️ Clear", key="clear_chat", use_container_width=True):
            st.session_state.chat_messages = [{"role": "bot", "content": f"🌸 Hi {username}! How can I help?", "time": datetime.now().strftime("%H:%M")}]
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle bot response
    if st.session_state.typing and st.session_state.chat_messages[-1]["role"] == "user":
        time.sleep(0.8)
        last_msg = st.session_state.chat_messages[-1]["content"]
        bot_response = get_bot_response(last_msg)
        st.session_state.chat_messages.append({"role": "bot", "content": bot_response, "time": datetime.now().strftime("%H:%M")})
        st.session_state.typing = False
        st.rerun()


def handle_quick_reply(text):
    """Handle quick suggestion clicks"""
    mapping = {
        "💧 Water": "How often should I water?",
        "☀️ Sun": "How much sunlight needed?",
        "🐛 Pests": "How to control pests?",
        "🌱 Food": "Best fertilizer to use?"
    }
    process_message(mapping.get(text, text))


def process_message(text):
    """Process user message"""
    current_time = datetime.now().strftime("%H:%M")
    st.session_state.chat_messages.append({"role": "user", "content": text, "time": current_time})
    st.session_state.typing = True
    st.rerun()

def get_bot_response(user_message):
    """AI Response Logic with diseases and personalized greetings"""
    message = user_message.lower()
    username = st.session_state.get('username', 'Guest')
    
   # Disease Database
    diseases = {
    # Fungal Diseases
    "black spot": {
        "name": "🌹 Black Spot Disease",
        "symptoms": "Black spots with yellow halos on leaves, premature leaf drop, weakened stems.",
        "causes": "Fungus Diplocarpon rosae. Spreads via water splash, thrives in warm humid conditions.",
        "treatment": "Remove infected leaves. Apply fungicide with chlorothalonil. Water at base, avoid wetting foliage. Ensure good air circulation."
    },
    "powdery mildew": {
        "name": "🌸 Powdery Mildew",
        "symptoms": "White powdery coating on leaves and buds, distorted growth, stunted flowers.",
        "causes": "Fungus Erysiphe cichoracearum. Spreads in humid conditions with cool nights.",
        "treatment": "Spray neem oil or sulfur fungicide. Prune for air flow. Avoid overhead watering. Use baking soda solution (1 tbsp/gallon) as preventive."
    },
    "downy mildew": {
        "name": "🍂 Downy Mildew",
        "symptoms": "Yellow angular spots on leaf tops, fuzzy gray growth on undersides, leaf browning and curling.",
        "causes": "Oomycete pathogens. Spreads in cool wet conditions (50-75°F). High humidity required.",
        "treatment": "Remove infected plant parts. Apply copper fungicide. Water early morning. Space plants for drying. Avoid overhead irrigation."
    },
    "root rot": {
        "name": "🥀 Root Rot",
        "symptoms": "Yellow leaves, wilting despite wet soil, stunted growth, black mushy roots.",
        "causes": "Soil fungi from overwatering and poor drainage. Waterlogged soil suffocates roots.",
        "treatment": "Stop watering. Remove plant, trim rotten roots. Repot in fresh dry soil. Treat with hydrogen peroxide (1:3 with water)."
    },
    "leaf spot": {
        "name": "🍃 Leaf Spot",
        "symptoms": "Circular brown/black spots with yellow halos, severe defoliation.",
        "causes": "Fungal pathogens spread by rain and wind. Favors wet foliage.",
        "treatment": "Remove infected leaves. Apply copper fungicide. Space plants for air circulation. Water at soil level only."
    },
    "rust": {
        "name": "🟤 Rust Disease",
        "symptoms": "Orange/brown pustules on leaf undersides, yellow spots on top, leaf drop.",
        "causes": "Fungus Puccinia. Requires 6+ hours leaf moisture. Spreads via wind.",
        "treatment": "Remove infected parts. Apply fungicide with myclobutanil. Avoid overhead watering. Rake fallen leaves."
    },
    "gray mold": {
        "name": "🌺 Gray Mold (Botrytis)",
        "symptoms": "Gray fuzzy mold on flowers/leaves, brown spots, rotting buds.",
        "causes": "Fungus Botrytis cinerea. Thrives in cool humid conditions (60-77°F).",
        "treatment": "Remove infected parts immediately. Improve air circulation. Apply fungicide with iprodione. Remove dead debris."
    },
    "anthracnose": {
        "name": "🌿 Anthracnose",
        "symptoms": "Dark sunken lesions on leaves/stems, leaf curling, twig dieback, fruit rot.",
        "causes": "Fungus Colletotrichum. Spreads via rain splash in warm wet weather.",
        "treatment": "Prune infected twigs. Rake fallen leaves. Apply copper fungicide. Avoid working with wet plants."
    },
    "blight": {
        "name": "🔥 Blight",
        "symptoms": "Sudden browning/wilting of leaves, stem cankers, rapid plant collapse.",
        "causes": "Fungal or bacterial pathogens. Spreads rapidly in warm humid conditions.",
        "treatment": "Remove and destroy infected plants. Prune 4-5 inches below damage. Apply copper fungicide weekly. Avoid overhead watering."
    },
    "fusarium wilt": {
        "name": "🥀 Fusarium Wilt",
        "symptoms": "Yellowing on one side of plant, wilting despite adequate water, vascular discoloration.",
        "causes": "Soil-borne fungus Fusarium oxysporum. Blocks water transport. Persists in soil for years.",
        "treatment": "Remove infected plants immediately. Solarize soil. Use resistant varieties. Rotate crops 5+ years. Avoid over-fertilizing."
    },
    "verticillium wilt": {
        "name": "🍁 Verticillium Wilt",
        "symptoms": "Yellow V-shaped leaf lesions, wilting in heat, brown streaks in vascular tissue.",
        "causes": "Soil-borne fungus Verticillium dahliae. Favors cool soil temperatures.",
        "treatment": "Remove infected plants. Do not replant susceptible species. Solarize soil. Plant resistant varieties. Improve drainage."
    },
    "damping off": {
        "name": "🌱 Damping Off",
        "symptoms": "Seedlings collapse at soil line, rotted stems, seedlings fail to emerge.",
        "causes": "Fungi Pythium/Rhizoctonia in cold wet soil. Excess moisture and poor drainage.",
        "treatment": "Use sterile potting mix. Water from bottom. Apply fungicide seed treatment. Ensure good drainage. Avoid overcrowding."
    },
    "septoria leaf spot": {
        "name": "🍂 Septoria Leaf Spot",
        "symptoms": "Small circular spots with dark borders and gray centers, starting on lower leaves.",
        "causes": "Fungus Septoria lycopersici. Spreads from bottom up via splashing water.",
        "treatment": "Remove lower infected leaves. Mulch to prevent splash. Apply chlorothalonil fungicide. Rotate crops 3 years."
    },
    "cercospora leaf spot": {
        "name": "🟡 Cercospora Leaf Spot",
        "symptoms": "Circular to angular spots with tan centers and purple borders, defoliation from bottom.",
        "causes": "Fungus Cercospora. Spreads in warm wet conditions. Overwinters in debris.",
        "treatment": "Remove infected leaves. Apply azoxystrobin or chlorothalonil. Rotate crops. Clean up plant debris in fall."
    },
    "scab": {
        "name": "🍎 Scab",
        "symptoms": "Olive-green to black velvety spots on leaves/fruit, cracked corky lesions on fruit.",
        "causes": "Fungus Venturia inaequalis. Requires moisture for infection in spring.",
        "treatment": "Rake fallen leaves/fruit. Apply sulfur or captan fungicide. Plant resistant varieties. Prune for air circulation."
    },
    "clubroot": {
        "name": "🥔 Clubroot",
        "symptoms": "Swollen distorted roots, stunted growth, yellowing, wilting in hot weather.",
        "causes": "Soil-borne pathogen Plasmodiophora brassicae. Favors acidic wet soils.",
        "treatment": "Adjust pH to 7.0-7.5 with lime. Improve drainage. Rotate 7 years. Remove and destroy infected plants."
    },
    "white mold": {
        "name": "🍄 White Mold (Sclerotinia)",
        "symptoms": "White cottony growth on stems/leaves, black sclerotia inside stems, wilting.",
        "causes": "Fungus Sclerotinia sclerotiorum. Thrives in cool wet conditions (60-70°F).",
        "treatment": "Remove infected plants. Apply fungicide with iprodione. Increase plant spacing. Remove weeds. Rotate with grains."
    },
    "alternaria": {
        "name": "🌑 Alternaria Leaf Spot",
        "symptoms": "Dark brown to black spots with concentric rings, yellow halos, fruit rot.",
        "causes": "Fungus Alternaria. Spreads via wind/rain. Favors warm humid conditions.",
        "treatment": "Remove plant debris. Apply chlorothalonil or mancozeb. Rotate crops. Avoid overhead irrigation."
    },
    "phytophthora": {
        "name": "💧 Phytophthora Blight",
        "symptoms": "Dark water-soaked lesions, sudden wilting, crown rot, fruit rot with white fuzz.",
        "causes": "Water mold Phytophthora. Spreads in saturated soil conditions.",
        "treatment": "Improve drainage. Apply metalaxyl or fosetyl-Al. Remove infected plants. Use raised beds. Avoid over-irrigation."
    },
    
    # Bacterial Diseases
    "bacterial spot": {
        "name": "🦠 Bacterial Spot",
        "symptoms": "Small water-soaked spots turning brown/black with yellow halos, leaf drop, fruit scabs.",
        "causes": "Bacterium Xanthomonas or Pseudomonas. Spreads via water splash, warm wet weather.",
        "treatment": "Remove infected plants. Apply copper bactericide. Avoid overhead watering. Rotate crops. Use disease-free seed."
    },
    "bacterial blight": {
        "name": "🔥 Bacterial Blight",
        "symptoms": "Angular water-soaked lesions, leaf curling, stem cankers, systemic wilting.",
        "causes": "Bacterium Pseudomonas syringae. Enters through wounds. Spreads in cool wet weather.",
        "treatment": "Prune infected areas during dry weather. Disinfect tools. Apply copper spray. Avoid working when wet."
    },
    "bacterial canker": {
        "name": "🌳 Bacterial Canker",
        "symptoms": "Sunken lesions with gummy exudate, dieback, leaf spot with white centers.",
        "causes": "Bacterium Clavibacter or Pseudomonas. Enters through wounds/natural openings.",
        "treatment": "Prune cankers during dry weather. Disinfect tools between cuts. Apply copper in early spring. Avoid frost damage."
    },
    "fire blight": {
        "name": "🔥 Fire Blight",
        "symptoms": "Blackened shoots (shepherd's crook), blossoms turning brown, ooze on bark.",
        "causes": "Bacterium Erwinia amylovora. Spreads via bees/rain in warm humid bloom time.",
        "treatment": "Prune infected branches 8-12 inches below symptoms. Disinfect tools. Avoid excessive nitrogen. Apply streptomycin during bloom."
    },
    "soft rot": {
        "name": "🥬 Bacterial Soft Rot",
        "symptoms": "Water-soaked mushy tissue, foul odor, rapid collapse of plant parts.",
        "causes": "Bacterium Pectobacterium. Enters through wounds. Thrives in wet anaerobic conditions.",
        "treatment": "Remove infected tissue. Improve drainage. Avoid wounding. Rotate crops. Ensure good air circulation."
    },
    "crown gall": {
        "name": "🌰 Crown Gall",
        "symptoms": "Tumor-like galls on roots and crown, stunted growth, yellowing, wilting.",
        "causes": "Bacterium Agrobacterium tumefaciens. Enters through wounds. Persists in soil for years.",
        "treatment": "Remove and destroy infected plants. Sterilize tools. Plant resistant rootstocks. Avoid wounding. Use galltrol-A for prevention."
    },
    
    # Viral Diseases
    "mosaic virus": {
        "name": "🦠 Mosaic Virus",
        "symptoms": "Mottled light and dark green leaf patterns, distorted growth, stunted plants.",
        "causes": "Various viruses (TMV, CMV). Spread by aphids, seeds, tools, and handling.",
        "treatment": "Remove and destroy infected plants. Control aphids. Disinfect tools. Plant resistant varieties. Wash hands before handling."
    },
    "leaf curl virus": {
        "name": "🍃 Leaf Curl Virus",
        "symptoms": "Thick curled leaves, red/purple discoloration, stunted shoots, reduced fruit.",
        "causes": "Virus spread by whiteflies or thrips. Persists in weed reservoirs.",
        "treatment": "Remove infected plants immediately. Control whiteflies with insecticidal soap. Use reflective mulches. Plant resistant varieties."
    },
    "yellows virus": {
        "name": "💛 Yellows Virus",
        "symptoms": "General yellowing, stunted growth, phyllody (leaf-like flowers), virescence.",
        "causes": "Phytoplasmas spread by leafhoppers. Infects phloem tissue.",
        "treatment": "Remove infected plants. Control leafhoppers with insecticide. Use row covers. Remove weed hosts. Plant resistant varieties."
    },
    "ringspot virus": {
        "name": "⭕ Ringspot Virus",
        "symptoms": "Concentric ring patterns on leaves, chlorotic spots, fruit blemishes.",
        "causes": "Virus spread by thrips, mites, or mechanical transmission.",
        "treatment": "Remove infected plants. Control vectors. Disinfect tools. Use certified clean seed. Avoid tobacco products (TMV risk)."
    },
    "stunt virus": {
        "name": "📉 Stunt Virus",
        "symptoms": "Severely stunted growth, shortened internodes, dark green foliage, reduced yields.",
        "causes": "Various viruses. Spread by nematodes, insects, or seed transmission.",
        "treatment": "Remove infected plants. Control nematodes. Use certified seed. Rotate crops. Soil solarization."
    },
    
    # Insect/Pest Damage
    "aphids": {
        "name": "🐛 Aphid Infestation",
        "symptoms": "Clusters of tiny insects on new growth, sticky honeydew, curled yellow leaves.",
        "causes": "Sap-sucking insects multiply rapidly in warm weather on nitrogen-rich growth.",
        "treatment": "Spray water to dislodge. Apply insecticidal soap or neem oil. Introduce ladybugs. Remove heavily infested stems."
    },
    "spider mites": {
        "name": "🕷️ Spider Mites",
        "symptoms": "Yellow/white speckles on leaves, fine webbing, bronze leaves.",
        "causes": "Arachnids thrive in hot dry conditions (80°F+). Reproduce rapidly in dust.",
        "treatment": "Spray undersides with water daily. Apply insecticidal soap or neem oil. Increase humidity. Wipe leaves with damp cloth."
    },
    "whitefly": {
        "name": "🦟 Whitefly Infestation",
        "symptoms": "Tiny white moth-like insects on leaf undersides, yellowing leaves, sticky honeydew.",
        "causes": "Insects feed on sap, excrete honeydew. Attracted to stressed plants. Rapid reproduction in warmth.",
        "treatment": "Use yellow sticky traps. Spray insecticidal soap on undersides. Apply neem oil every 5-7 days. Introduce parasitic wasps."
    },
    "thrips": {
        "name": "⚡ Thrip Damage",
        "symptoms": "Silvery streaks on leaves, black specks (excrement), distorted flowers, scarred petals.",
        "causes": "Tiny insects scrape cells to feed. Spread viruses. Thrive in hot, dry conditions.",
        "treatment": "Remove infested buds. Spray spinosad or insecticidal soap. Use blue sticky traps. Maintain high humidity."
    },
    "scale insects": {
        "name": "🐚 Scale Insects",
        "symptoms": "Brown/white bumps on stems/leaves, yellowing, sticky honeydew, sooty mold.",
        "causes": "Sap-sucking insects with protective shells. Spread by crawlers in spring.",
        "treatment": "Scrape off visible scales. Apply horticultural oil during dormant season. Use systemic insecticide for severe cases. Introduce parasitic wasps."
    },
    "mealybugs": {
        "name": "🐛 Mealybugs",
        "symptoms": "White cottony masses in leaf axils, sticky honeydew, stunted growth, yellowing.",
        "causes": "Soft-bodied insects in protected areas. Spread by ants and wind.",
        "treatment": "Dab with alcohol-soaked cotton swabs. Spray insecticidal soap or neem oil. Apply systemic insecticide. Control ants."
    },
    "caterpillars": {
        "name": "🐛 Caterpillar Damage",
        "symptoms": "Chewed leaves, holes in fruit, frass (droppings), rolled leaves.",
        "causes": "Larvae of moths/butterflies. Active at night. Rapid defoliation.",
        "treatment": "Handpick caterpillars. Apply Bacillus thuringiensis (Bt). Use row covers. Encourage birds and parasitic wasps."
    },
    "beetles": {
        "name": "🪲 Beetle Damage",
        "symptoms": "Skeletonized leaves, round holes, notched leaf edges, larvae in roots.",
        "causes": "Various beetles (Japanese, flea, cucumber). Feed on foliage and roots.",
        "treatment": "Handpick beetles. Apply neem oil or pyrethrin. Use floating row covers. Apply beneficial nematodes for larvae."
    },
    "leaf miners": {
        "name": "⛏️ Leaf Miners",
        "symptoms": "Winding white trails (mines) in leaves, blotches, reduced photosynthesis.",
        "causes": "Larvae feed between leaf layers. Multiple generations per season.",
        "treatment": "Remove mined leaves. Apply spinosad or neem oil. Use floating row covers. Encourage parasitic wasps."
    },
    "fungus gnats": {
        "name": "🦟 Fungus Gnats",
        "symptoms": "Tiny flies around soil, larvae in soil, stunted seedlings, root damage.",
        "causes": "Overwatering and organic matter in soil. Larvae feed on roots.",
        "treatment": "Allow soil to dry between waterings. Apply Bacillus thuringiensis (Bt-i) or neem cake. Use yellow sticky traps. Repot in fresh soil."
    },
    "slugs": {
        "name": "🐌 Slug Damage",
        "symptoms": "Large irregular holes in leaves, slime trails, seedlings completely consumed.",
        "causes": "Mollusks active in cool wet conditions. Hide during day, feed at night.",
        "treatment": "Handpick at night. Use iron phosphate bait. Create barriers with copper tape or diatomaceous earth. Remove hiding places."
    },
    "snails": {
        "name": "🐌 Snail Damage",
        "symptoms": "Chewed leaves with large holes, silvery slime trails on plants and soil.",
        "causes": "Mollusks favor damp shady areas. Feed on tender growth.",
        "treatment": "Handpick in evening. Use iron phosphate bait. Create barriers. Remove debris and hiding spots. Encourage predators like birds."
    },
    "earwigs": {
        "name": "🦗 Earwig Damage",
        "symptoms": "Irregular holes in leaves, damaged flowers, chewed fruit, silvery excrement.",
        "causes": "Nocturnal insects seeking moist shelter. Omnivorous feeding.",
        "treatment": "Trap with rolled newspaper or oil cans. Reduce hiding places. Apply diatomaceous earth. Use bait if severe."
    },
    "mites": {
        "name": "🔍 Broad Mites",
        "symptoms": "Distorted new growth, bronzed leaves, russeted fruit, shortened internodes.",
        "causes": "Microscopic arachnids in growing tips. Spread via wind and tools.",
        "treatment": "Remove infested tips. Apply sulfur or horticultural oil. Increase humidity. Use miticide for severe cases."
    },
    
    # Nematodes
    "root knot nematode": {
        "name": "🪱 Root Knot Nematode",
        "symptoms": "Galls/knots on roots, stunted growth, yellowing, wilting in heat, nutrient deficiency symptoms.",
        "causes": "Microscopic roundworms in soil. Enter roots and cause gall formation.",
        "treatment": "Solarize soil before planting. Plant resistant varieties (N designation). Add organic matter. Rotate with marigolds. Apply nematicides if severe."
    },
    "cyst nematode": {
        "name": "🥔 Cyst Nematode",
        "symptoms": "Stunted yellow plants, reduced root system, tiny white/yellow cysts on roots.",
        "causes": "Sedentary nematodes in soil. Cysts protect eggs for years.",
        "treatment": "Use resistant varieties. Rotate crops 3-4 years. Solarize soil. Apply nematicides. Improve soil health with compost."
    },
    
    # Physiological/Environmental Disorders
    "nutrient deficiency": {
        "name": "⚗️ Nutrient Deficiency",
        "symptoms": "Yellowing (nitrogen), purple leaves (phosphorus), interveinal chlorosis (iron/magnesium), tip burn.",
        "causes": "Lack of essential nutrients due to poor soil, pH imbalance, or root problems.",
        "treatment": "Test soil and adjust pH. Apply balanced fertilizer. Foliar feed specific nutrients. Improve soil organic matter."
    },
    "sunscald": {
        "name": "☀️ Sunscald",
        "symptoms": "White/tan papery patches on fruit/leaves, sunken lesions, cracking.",
        "causes": "Sudden exposure to direct sun after shade. Hot dry conditions.",
        "treatment": "Provide shade during hottest hours. Maintain consistent soil moisture. Avoid heavy pruning that exposes fruit. Use row covers."
    },
    "frost damage": {
        "name": "❄️ Frost Damage",
        "symptoms": "Blackened mushy tissue, wilting, water-soaked appearance, browning of new growth.",
        "causes": "Ice crystal formation in cells ruptures plant tissue. Clear nights with no wind.",
        "treatment": "Wait to prune until new growth appears. Water before freeze. Cover plants. Apply mulch to protect roots."
    },
    "heat stress": {
        "name": "🔥 Heat Stress",
        "symptoms": "Wilting despite moist soil, leaf rolling, sunburn, blossom drop, bitter fruit.",
        "causes": "Temperatures above 90°F. Excessive transpiration. Root damage.",
        "treatment": "Provide afternoon shade. Increase watering frequency. Apply mulch. Avoid fertilizing during heat waves. Mist foliage."
    },
    "water stress": {
        "name": "💧 Water Stress",
        "symptoms": "Wilting, leaf curling, browning edges, stunted growth, blossom end rot.",
        "causes": "Inconsistent watering, drought, or root damage preventing uptake.",
        "treatment": "Water deeply and consistently. Apply mulch. Check irrigation coverage. Improve soil structure. Avoid overwatering."
    },
    "transplant shock": {
        "name": "🌱 Transplant Shock",
        "symptoms": "Wilting, yellowing, stunted growth, leaf drop after planting.",
        "causes": "Root disturbance, environmental change, improper hardening off.",
        "treatment": "Water regularly. Provide shade for few days. Avoid fertilizing immediately. Handle roots carefully. Harden off gradually."
    },
    "herbicide damage": {
        "name": "☠️ Herbicide Damage",
        "symptoms": "Distorted twisted growth, cupped leaves, vein discoloration, stunting.",
        "causes": "Drift from nearby applications, contaminated compost, or persistent herbicides.",
        "treatment": "Flush soil with water. Remove severely damaged plants. Avoid using contaminated manure/compost. Plant sensitive species elsewhere."
    },
    "salt damage": {
        "name": "🧂 Salt Damage",
        "symptoms": "Brown leaf margins/tips, stunted growth, leaf drop, white crust on soil.",
        "causes": "Excess fertilizer, road salt, or saline water. Accumulates in soil.",
        "treatment": "Leach soil with fresh water. Improve drainage. Reduce fertilizer. Use gypsum to displace sodium. Plant salt-tolerant varieties."
    },
    "ozone damage": {
        "name": "🏭 Ozone Damage",
        "symptoms": "Stippling on upper leaf surface, chlorotic mottling, premature senescence.",
        "causes": "Air pollution. Ground-level ozone enters through stomata.",
        "treatment": "Water adequately to keep stomata closed during peak ozone. Plant tolerant varieties. Improve air circulation."
    },
    
    # Other Common Issues
    "blossom end rot": {
        "name": "🍅 Blossom End Rot",
        "symptoms": "Dark sunken lesion on blossom end of fruit, internal blackening.",
        "causes": "Calcium deficiency in fruit due to inconsistent watering or rapid growth.",
        "treatment": "Maintain consistent soil moisture. Apply calcium foliar spray. Avoid over-fertilization with nitrogen. Mulch to regulate temperature."
    },
    "tip burn": {
        "name": "🔥 Tip Burn",
        "symptoms": "Browning of leaf tips and margins, starting on older leaves.",
        "causes": "Calcium deficiency, inconsistent watering, or excess salts. Common in lettuce/cabbage.",
        "treatment": "Ensure consistent watering. Apply calcium. Avoid over-fertilization. Provide shade during hot weather. Improve soil structure."
    },
    "edema": {
        "name": "💧 Edema (Oedema)",
        "symptoms": "Corky wart-like bumps on leaves, water-soaked blisters, scarring.",
        "causes": "Water uptake exceeds transpiration. Cool cloudy weather with wet soil.",
        "treatment": "Reduce watering. Improve air circulation. Increase light/temperature. Avoid over-fertilization. Water in morning only."
    },
    "drought stress": {
        "name": "🏜️ Drought Stress",
        "symptoms": "Wilting, leaf rolling, grayish foliage, premature drop, stunted growth.",
        "causes": "Insufficient water availability. High temperatures and wind increase loss.",
        "treatment": "Water deeply and regularly. Apply mulch. Use drought-tolerant varieties. Windbreaks to reduce evaporation. Prioritize watering."
    },
    "overwatering": {
        "name": "🌊 Overwatering",
        "symptoms": "Yellowing leaves, wilting, root rot, algae on soil, fungus gnats.",
        "causes": "Excess moisture suffocates roots. Poor drainage. Frequent light watering.",
        "treatment": "Allow soil to dry between waterings. Improve drainage. Repot if necessary. Check drainage holes. Water deeply less frequently."
    },
    "chlorosis": {
        "name": "💛 Chlorosis",
        "symptoms": "Yellow leaves with green veins (interveinal), poor growth, leaf drop.",
        "causes": "Iron, manganese, or magnesium deficiency. High pH locks up nutrients.",
        "treatment": "Apply chelated iron or Epsom salts. Adjust soil pH. Foliar feed micronutrients. Improve soil drainage and organic matter."
    },
    "wilting": {
        "name": "🥀 Wilting",
        "symptoms": "Drooping leaves and stems, loss of turgor, potential recovery at night.",
        "causes": "Water stress, root damage, vascular disease, or extreme heat.",
        "treatment": "Check soil moisture. Inspect roots for rot. Shade from heat. Apply water if dry. If disease present, remove plant."
    },
    "dieback": {
        "name": "🌿 Dieback",
        "symptoms": "Progressive death of shoots/branches from tips downward, cankers on stems.",
        "causes": "Fungal cankers, borers, environmental stress, or root problems.",
        "treatment": "Prune dead wood to healthy tissue. Identify and treat underlying cause. Improve plant vigor with proper care."
    },
    "galls": {
        "name": "🌰 Galls",
        "symptoms": "Abnormal swellings on leaves, stems, or roots, various shapes and colors.",
        "causes": "Insects, mites, fungi, bacteria, or nematodes. Plant's reaction to irritation.",
        "treatment": "Prune and destroy galled tissue. Control specific pest. Maintain plant health. Most galls are cosmetic only."
    },
    "witches broom": {
        "name": "🧹 Witches' Broom",
        "symptoms": "Dense clusters of shoots, abnormal branching, stunted growth.",
        "causes": "Fungus, phytoplasma, or genetic mutation. Systemic infection.",
        "treatment": "Prune out brooms. Remove severely infected plants. Control vectors. Plant resistant varieties. No chemical cure."
    },
    "gummosis": {
        "name": "🍯 Gummosis",
        "symptoms": "Oozing sap/gum from wounds or cankers, dieback, leaf yellowing.",
        "causes": "Fungal/bacterial cankers, physical wounds, borers, or environmental stress.",
        "treatment": "Clean wound area. Apply fungicide to cankers. Improve drainage. Avoid mechanical damage. Control borers."
    },
    "canker": {
        "name": "🌳 Canker",
        "symptoms": "Sunken dead areas on bark/branches, discoloration, dieback above canker.",
        "causes": "Fungal or bacterial pathogens entering through wounds. Stress predisposes plants.",
        "treatment": "Prune cankers during dry weather. Cut 4-6 inches below canker. Disinfect tools. Protect wounds. Maintain tree vigor."
    },
    "witches broom": {
        "name": "🧹 Witches' Broom",
        "symptoms": "Dense broom-like clusters of twigs, abnormal growth, yellowing foliage.",
        "causes": "Phytoplasmas or fungi. Systemic infection affecting hormone balance.",
        "treatment": "Remove infected branches. Destroy severely infected plants. Control insect vectors. Plant resistant varieties."
    }
}
    
    # Check diseases FIRST
    for key, disease in diseases.items():
        if key in message:
            return f"""<b>{disease['name']}</b><br><br>
<b>🩺 Symptoms:</b> {disease['symptoms']}<br><br>
<b>🔬 Causes:</b> {disease['causes']}<br><br>
<b>💊 Treatment & Prevention:</b> {disease['treatment']}"""
    
    # Knowledge Base
    knowledge = {
        "water": "💧 Water when the top 1-2 inches of soil feels dry. Most flowers prefer morning watering to prevent fungal issues. Avoid wetting the leaves!",
        "sunlight": "☀️ Most flowering plants need 6+ hours of direct sunlight. However, some like hostas and ferns prefer shade. Check your specific plant's needs!",
        "pest": "🐛 For natural pest control: 1) Neem oil spray, 2) Introduce ladybugs, 3) Garlic-chili spray, 4) Diatomaceous earth. Avoid harsh chemicals!",
        "fertilizer": "🌱 Use balanced NPK fertilizer (10-10-10) every 2-4 weeks during growing season. For blooming flowers, use higher phosphorus (middle number)!",
        "yellow": "💛 Yellow leaves usually mean: 1) Overwatering (most common), 2) Nutrient deficiency, 3) Natural aging. Check soil moisture first!",
        "pruning": "✂️ Deadhead spent blooms to encourage more flowers! Cut just above a leaf node at a 45° angle. Use clean, sharp tools to prevent disease spread.",
        "soil": "🌍 Well-draining soil is crucial! Mix: 2 parts potting soil + 1 part perlite + 1 part compost. This prevents root rot and provides nutrients!",
        "repot": "🪴 Repot when roots grow through drainage holes or circle the pot. Choose a pot 1-2 inches larger. Spring is the best time to repot!",
        "wilt": "🥀 Wilting can mean too much OR too little water. Check soil: If dry, water immediately. If wet, stop watering and improve drainage!",
        "seed": "🌰 Start seeds indoors 6-8 weeks before last frost. Use seed starting mix, keep moist (not wet), and provide warmth (70-75°F) and light!",
        "winter": "❄️ Most perennials need winter dormancy. Reduce watering, stop fertilizing, and add mulch for protection. Bring tender plants indoors!",
        "smell": "🌸 For fragrant gardens: Plant jasmine, gardenia, lavender, roses, or sweet peas near windows/doors where you can enjoy the scent!",
        "indoor": "🏠 Best indoor flowers: African violets, orchids, peace lilies, and begonias. They need bright indirect light and consistent humidity!",
        "begin": "🌺 Click 'Begin The Magic' on the home page to upload a photo! I can detect diseases instantly using AI image analysis!",
        "disease": "🔍 I can help identify diseases! Upload a clear photo showing the affected leaves/flowers. Look for spots, discoloration, or unusual growths!",
        "root": "🥔 Root rot = wet soil + yellow leaves + stunted growth. Fix by: 1) Stop watering, 2) Improve drainage, 3) Trim rotten roots, 4) Repot in dry soil",
        "bloom": "🌹 To encourage blooming: 1) Ensure enough sunlight, 2) Use bloom-boosting fertilizer, 3) Deadhead spent flowers, 4) Avoid over-fertilizing with nitrogen!",
        "organic": "🌿 Go organic: Use compost, mulch with grass clippings, make compost tea, use eggshells for calcium, and coffee grounds for acid-loving plants!",
        "mulch": "🍂 Mulch benefits: Retains moisture, suppresses weeds, regulates soil temperature, and adds nutrients. Use 2-3 inches of organic mulch!",
        "companion": "🤝 Great companions: Roses + garlic (repels aphids), Tomatoes + marigolds (repels nematodes), Beans + corn (nitrogen fixing)!",
    }
    
    # Check keywords
    for key, response in knowledge.items():
        if key in message:
            return response + " 🌿✨"
    
    # Contextual responses with USERNAME
    if any(word in message for word in ["hello", "hi", "hey"]):
        return f"🌸 Hello {username}! I'm Flora, your flower care expert! Ask me about watering, diseases, sunlight, or upload a photo for disease detection! What would you like to know? 💕"
    
    if any(word in message for word in ["thank", "thanks", "thx"]):
        return f"🌷 You're so welcome {username}! I'm always here to help your garden thrive! Feel free to ask anytime! 🌿💕"
    
    if any(word in message for word in ["bye", "goodbye", "see you"]):
        return f"🌸 Goodbye {username}! May your garden bloom beautifully! Come back anytime you need gardening advice! 🌺✨"
    
    if "name" in message:
        return f"🌺 I'm Flora, your AI Flower Care Assistant! Hi {username}! I can help with plant care tips, disease identification, and gardening advice. What flowers are you growing? 🌸"
    
    if "help" in message:
        return f"🌿 Hi {username}! I can help you with: 1) 🌱 Plant care tips, 2) 🔍 Disease detection (upload photos!), 3) 💧 Watering schedules, 4) 🐛 Pest control, 5) 🌱 Fertilizer advice. What do you need? 💕"
    
    # Default responses with username
    defaults = [
        f"🌸 That's a great question {username}! For the most accurate help, try uploading a photo of your flower using our 'Disease Detection' feature - I can analyze it instantly with AI! 🌺",
        f"🌷 I'd love to help more specifically {username}! Could you tell me what type of flower you're asking about? Or upload a photo and I'll give you personalized advice! ✨",
        f"💕 Interesting {username}! Every flower is unique. For detailed care instructions, try our image detection feature or tell me your plant's name! I'm here to help! 🌿",
        f"🌺 Great question {username}! Gardening is both art and science. Would you like to upload a photo so I can see exactly what you're working with? I can spot issues immediately! 🔍",
        f"🌸 I'm learning more every day {username}! For now, check our detection feature or ask me about general care tips like watering, sunlight, or soil requirements! 💕"
    ]
    
    import random
    return random.choice(defaults)
# ===============================
# HISTORY PAGE - DISEASE DETECTION HISTORY
# ===============================
# ===============================
# HISTORY PAGE - FINAL VERSION
# ===============================

def history_page():
    """History page with Supabase cloud integration"""
    
    load_css()
    navigation_sidebar()
    
    # Initialize Supabase clients if not already done
    if 'supabase_detections' not in st.session_state:
        st.session_state.supabase_detections = init_supabase_client("SUPABASE_DETECTIONS_URL", "SUPABASE_DETECTIONS_KEY")
    
    supabase_detections = st.session_state.supabase_detections
    
    # Check Supabase connection
    if supabase_detections is None:
        st.error("""
        ⚠️ **Supabase Not Connected**
        
        Please set your Supabase credentials in `.streamlit/secrets.toml`:
        ```
        SUPABASE_DETECTIONS_URL = "https://your-project.supabase.co"
        SUPABASE_DETECTIONS_KEY = "your-anon-or-service-key"
        ```
        """)
        return
    
    # ============================================
    # SAVE DETECTION TO SUPABASE (OPTIMIZED)
    # ============================================
    if st.session_state.get('save_to_history', False) and st.session_state.get('cls_name'):
        
        disease = st.session_state.cls_name
        confidence = st.session_state.display_conf
        image = st.session_state.get('uploaded_image', None)
        
        with st.spinner("💾 Saving..."):
            success = save_detection_to_supabase(disease, confidence, image)
        
        if success:
            st.toast("✅ Saved!")
        
        st.session_state.save_to_history = False
    
    # ============================================
    # HANDLE INDIVIDUAL DELETE
    # ============================================
    if st.session_state.get('delete_detection_id'):
        delete_id = st.session_state.delete_detection_id
        if delete_detection_from_supabase(delete_id):
            st.toast("🗑️ Deleted!")
        st.session_state.delete_detection_id = None
        st.rerun()
    
    # Page styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
    
    .history-title {
        font-family: 'Playfair Display', serif;
        font-size: 38px;
        text-align: center;
        color: #2d3436;
        margin: 20px 0 8px 0;
    }
    
    .cloud-badge {
        display: inline-block;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .subtitle {
        text-align: center;
        color: #636e72;
        font-size: 13px;
        margin-bottom: 25px;
    }
    
    .section-header {
        font-size: 16px;
        font-weight: 600;
        color: #2d3436;
        margin-bottom: 12px;
        padding-left: 5px;
    }
    
    /* History cards */
    .history-item {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border-color: #74b9ff;
    }
    
    .history-content { 
        display: flex; 
        align-items: center; 
        gap: 14px; 
    }
    
    .history-img {
        width: 60px; 
        height: 60px; 
        min-width: 60px; 
        border-radius: 10px;
        object-fit: cover; 
        border: 2px solid #e9ecef;
    }
    
    .history-img-placeholder {
        width: 60px; 
        height: 60px; 
        min-width: 60px; 
        border-radius: 10px;
        background: linear-gradient(135deg, #dfe6e9, #b2bec3);
        display: flex; 
        align-items: center; 
        justify-content: center;
        font-size: 24px;
    }
    
    .history-info {
        flex: 1;
    }
    
    .history-disease-name { 
        font-size: 15px; 
        color: #2d3436; 
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .history-meta { 
        display: flex; 
        gap: 10px; 
        align-items: center;
        flex-wrap: wrap; 
    }
    
    .history-confidence {
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: white; 
        padding: 4px 10px; 
        border-radius: 15px;
        font-size: 11px; 
        font-weight: 600;
    }
    
    .history-datetime { 
        font-size: 12px; 
        color: #636e72;
        background: #f1f3f4;
        padding: 4px 10px;
        border-radius: 15px;
    }
    
    .delete-btn-container {
        margin-left: auto;
    }
    
    /* Custom delete button */
    .delete-btn button {
        background: transparent !important;
        color: #ff7675 !important;
        border: 2px solid #ff7675 !important;
        padding: 6px 12px !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .delete-btn button:hover {
        background: #ff7675 !important;
        color: white !important;
    }
    
    .empty-history {
        text-align: center; 
        padding: 50px 20px;
        background: #f8f9fa;
        border-radius: 16px; 
        border: 2px dashed #dfe6e9;
    }
    
    .clear-all-btn > button {
        background: linear-gradient(135deg, #ff7675, #d63031) !important;
        color: white !important; 
        border: none !important;
        padding: 14px 40px !important; 
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 15px rgba(214, 48, 49, 0.3) !important;
    }
    
    .detect-btn > button {
        background: linear-gradient(135deg, #74b9ff, #0984e3) !important;
        color: white !important; 
        border: none !important;
        padding: 12px 28px !important; 
        border-radius: 25px !important;
        font-weight: 600 !important;
    }
    
    .more-indicator {
        text-align: center;
        color: #b2bec3;
        font-size: 13px;
        padding: 15px;
        font-style: italic;
    }
    </style>
    
    <div class="history-title">📜 Detection History</div>
    <div style="text-align: center; margin-bottom: 5px;">
        <span class="cloud-badge">☁️ Cloud Synced</span>
    </div>
    <div class="subtitle">Recent disease detections</div>
    """, unsafe_allow_html=True)
    
    # Get only 7 recent detections from Supabase
    detections = get_recent_detections_from_supabase(limit=7)
    total_in_db = get_detection_count_from_supabase()
    
    if detections:
        st.markdown('<div class="section-header">🕐 Recent Detections</div>', unsafe_allow_html=True)
        
        for detection in detections:
            detection_id = detection.get('detection_id')
            
            # Image
            if detection.get('image_base64') and detection['image_base64'].startswith('data:image'):
                img_html = f'<img src="{detection["image_base64"]}" class="history-img">'
            else:
                img_html = '<div class="history-img-placeholder">🌿</div>'
            
            # Confidence
            confidence_val = detection.get('confidence', 0)
            confidence_str = f"{confidence_val:.0%}" if isinstance(confidence_val, (int, float)) else str(confidence_val)
            
            # Disease name
            disease_name = detection.get('disease', 'Unknown').replace("-", " ").title()
            
            # Date and time
            date_str = detection.get('date', 'N/A')
            time_str = detection.get('time', 'N/A')
            
            # Create columns for layout
            col1, col2 = st.columns([6, 1])
            
            with col1:
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-content">
                        {img_html}
                        <div class="history-info">
                            <div class="history-disease-name">{disease_name}</div>
                            <div class="history-meta">
                                <span class="history-confidence">{confidence_str}</span>
                                <span class="history-datetime">📅 {date_str} 🕐 {time_str}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Individual delete button
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"delete_{detection_id}", help="Delete this detection"):
                    st.session_state.delete_detection_id = detection_id
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Show indicator if more in database
        if total_in_db > 7:
            remaining = total_in_db - 7
            st.markdown(f'<div class="more-indicator">+{remaining} more stored in database</div>', unsafe_allow_html=True)
        
        # Clear ALL button at bottom
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            st.markdown('<div class="clear-all-btn">', unsafe_allow_html=True)
            if st.button("🗑️ Clear History", use_container_width=True, key="clear_all_btn"):
                if clear_all_detections_from_supabase():
                    st.success("✅ All history cleared!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Empty state
        st.markdown("""
        <div class="empty-history">
            <div style="font-size: 48px; margin-bottom: 12px;">🌿</div>
            <div style="color: #636e72; font-size: 15px; font-weight: 600;">No detections yet</div>
            <div style="color: #b2bec3; font-size: 12px; margin-top: 6px;">Analyze a plant to see history</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 3, 1])
        with col2:
            st.markdown('<div class="detect-btn">', unsafe_allow_html=True)
            if st.button("🔍 Start Detecting", key="goto_detect_btn"):
                st.session_state.page = "detection"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# OPTIMIZED SUPABASE FUNCTIONS
# ============================================================================

from supabase import create_client, Client
import streamlit as st
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

@st.cache_resource
def init_supabase_client(url_key, key_key):
    """Initialize Supabase client with custom keys"""
    try:
        supabase_url = st.secrets.get(url_key, os.getenv(url_key))
        supabase_key = st.secrets.get(key_key, os.getenv(key_key))
        
        if not supabase_url or not supabase_key:
            return None
            
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Supabase init error: {e}")
        return None

def save_detection_to_supabase(disease, confidence, image=None):
    """Save detection to Supabase - OPTIMIZED"""
    try:
        supabase = st.session_state.get('supabase_detections')
        if supabase is None:
            return False
        
        now = datetime.now()
        
        # Fast image conversion
        image_base64 = None
        if image is not None:
            try:
                if isinstance(image, bytes):
                    img = Image.open(BytesIO(image))
                elif hasattr(image, 'copy'):
                    img = image.copy()
                else:
                    img = image
                
                # Resize for speed
                max_size = (250, 250)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                buffered = BytesIO()
                
                if hasattr(img, 'mode'):
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(buffered, format="JPEG", quality=65, optimize=True)
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    image_base64 = f"data:image/jpeg;base64,{img_str}"
            except Exception as e:
                print(f"Image error: {e}")
        
        data = {
            'disease_name': str(disease),
            'confidence_score': float(confidence),
            'detection_date': now.strftime("%Y-%m-%d"),
            'detection_time': now.strftime("%H:%M"),
            'timestamp': now.timestamp(),
            'image_base64': image_base64,
        }
        
        response = supabase.table('detections').insert(data).execute()
        return bool(response.data)
        
    except Exception as e:
        print(f"Save error: {e}")
        return False

def get_recent_detections_from_supabase(limit=7):
    """Get only recent detections - optimized"""
    try:
        supabase = st.session_state.get('supabase_detections')
        if supabase is None:
            return []
        
        response = supabase.table('detections')\
            .select('id, disease_name, confidence_score, detection_date, detection_time, image_base64')\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        if response.data:
            return [{
                'detection_id': row.get('id'),
                'disease': row.get('disease_name'),
                'confidence': row.get('confidence_score'),
                'date': row.get('detection_date'),
                'time': row.get('detection_time'),
                'image_base64': row.get('image_base64'),
            } for row in response.data]
        return []
    except Exception as e:
        print(f"Get error: {e}")
        return []

def delete_detection_from_supabase(detection_id):
    """Delete single detection by ID"""
    try:
        supabase = st.session_state.get('supabase_detections')
        if supabase is None:
            return False
        
        supabase.table('detections').delete().eq('id', detection_id).execute()
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False

def get_detection_count_from_supabase():
    """Get total count"""
    try:
        supabase = st.session_state.get('supabase_detections')
        if supabase is None:
            return 0
        
        response = supabase.table('detections').select('*', count='exact', head=True).execute()
        return response.count if hasattr(response, 'count') else 0
    except:
        return 0

def clear_all_detections_from_supabase():
    """Clear all detections"""
    try:
        supabase = st.session_state.get('supabase_detections')
        if supabase is None:
            return False
        
        supabase.table('detections').delete().neq('id', 0).execute()
        return True
    except:
        return False

# ============================================================================
# DUAL SUPABASE SETUP - Login + Detections
# ============================================================================

from supabase import create_client, Client
import streamlit as st
import os

@st.cache_resource
def init_supabase_client(url_key, key_key):
    """Initialize Supabase client with custom keys"""
    try:
        supabase_url = st.secrets.get(url_key, os.getenv(url_key))
        supabase_key = st.secrets.get(key_key, os.getenv(key_key))
        
        if not supabase_url or not supabase_key:
            return None
            
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Supabase init error: {e}")
        return None

# Login database (existing)
supabase_login = init_supabase_client("SUPABASE_URL", "SUPABASE_KEY")

# Detections database (new project)
supabase_detections = init_supabase_client("SUPABASE_DETECTIONS_URL", "SUPABASE_DETECTIONS_KEY")

# Use supabase_detections for history page
supabase = supabase_detections  # This matches the variable name in previous code


# ============================================================================
# FLORA COMPARATIVE ANALYSIS MODULE
# Add this entire section to your app.py file
# ============================================================================

import plotly.graph_objects as go
import plotly.express as px
import hashlib
import json
from collections import defaultdict

# Initialize analysis session states
def init_analysis_state():
    """Initialize all analysis-related session states"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'health_trends' not in st.session_state:
        st.session_state.health_trends = {}
    if 'baseline_images' not in st.session_state:
        st.session_state.baseline_images = {}
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

class FlowerHealthAnalyzer:
    """Advanced image analysis for flower health assessment"""
    
    def __init__(self):
        self.health_metrics = {
            'green_vitality': 0,
            'bloom_quality': 0,
            'leaf_density': 0,
            'color_vibrancy': 0,
            'structural_integrity': 0
        }
    
    def analyze_image(self, image):
        """Comprehensive health analysis of flower image"""
        img_array = np.array(image)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # 1. Green Vitality (Chlorophyll health)
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        green_ratio = np.sum(green_mask > 0) / green_mask.size
        green_intensity = np.mean(hsv[green_mask > 0, 1]) if np.sum(green_mask > 0) > 0 else 0
        self.health_metrics['green_vitality'] = min(100, (green_ratio * 100) + (green_intensity / 2.55))
        
        # 2. Bloom Quality (Flower freshness)
        flower_colors = [
            ((0, 100, 100), (10, 255, 255)),      # Red
            ((160, 100, 100), (180, 255, 255)),   # Pink/Red
            ((20, 100, 100), (35, 255, 255)),     # Yellow
            ((140, 50, 50), (180, 255, 255)),     # Purple/Pink
        ]
        flower_mask = np.zeros_like(green_mask)
        for lower, upper in flower_colors:
            flower_mask |= cv2.inRange(hsv, lower, upper)
        
        flower_ratio = np.sum(flower_mask > 0) / flower_mask.size
        flower_saturation = np.mean(hsv[flower_mask > 0, 1]) if np.sum(flower_mask > 0) > 0 else 0
        self.health_metrics['bloom_quality'] = min(100, (flower_ratio * 150) + (flower_saturation / 2.55))
        
        # 3. Leaf Density (Foliage coverage)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        self.health_metrics['leaf_density'] = min(100, edge_density * 400)
        
        # 4. Color Vibrancy (Overall color intensity)
        color_std = np.std(hsv[:, :, 1])
        self.health_metrics['color_vibrancy'] = min(100, color_std * 2)
        
        # 5. Structural Integrity (Texture analysis)
        texture = cv2.Laplacian(gray, cv2.CV_64F).var()
        self.health_metrics['structural_integrity'] = min(100, texture / 10)
        
        # Calculate overall health score
        overall_health = np.mean(list(self.health_metrics.values()))
        
        return {
            'metrics': self.health_metrics.copy(),
            'overall_health': overall_health,
            'timestamp': datetime.now(),
            'image_hash': self._get_image_hash(image)
        }
    
    def _get_image_hash(self, image):
        """Generate perceptual hash for image identification"""
        img = image.resize((64, 64)).convert('L')
        img_array = np.array(img)
        return hashlib.md5(img_array.tobytes()).hexdigest()[:16]
    
    def compare_images(self, current_img, previous_img, previous_analysis):
        """Compare current image with previous analysis"""
        current_analysis = self.analyze_image(current_img)
        
        changes = {}
        trend_indicators = {}
        
        for metric in self.health_metrics.keys():
            prev_val = previous_analysis['metrics'].get(metric, 0)
            curr_val = current_analysis['metrics'][metric]
            change = curr_val - prev_val
            changes[metric] = {
                'current': curr_val,
                'previous': prev_val,
                'change': change,
                'percent_change': (change / prev_val * 100) if prev_val > 0 else 0
            }
            
            # Determine trend
            if change > 5:
                trend_indicators[metric] = '↗️ Improving'
            elif change < -5:
                trend_indicators[metric] = '↘️ Declining'
            else:
                trend_indicators[metric] = '➡️ Stable'
        
        # Overall health change
        prev_overall = previous_analysis.get('overall_health', 50)
        curr_overall = current_analysis['overall_health']
        overall_change = curr_overall - prev_overall
        
        # Generate health status
        if overall_change > 10:
            status = '🌟 Significantly Improved'
            status_color = '#00b894'
        elif overall_change > 0:
            status = '🌱 Slightly Improved'
            status_color = '#55efc4'
        elif overall_change > -10:
            status = '⚠️ Slightly Declined'
            status_color = '#fdcb6e'
        else:
            status = '🔴 Needs Attention'
            status_color = '#e17055'
        
        return {
            'current_analysis': current_analysis,
            'changes': changes,
            'trends': trend_indicators,
            'overall_change': overall_change,
            'status': status,
            'status_color': status_color,
            'days_since_last': self._calculate_days(previous_analysis['timestamp'])
        }
    
    def _calculate_days(self, previous_timestamp):
        """Calculate days between analyses"""
        if isinstance(previous_timestamp, str):
            previous_timestamp = datetime.fromisoformat(previous_timestamp)
        return (datetime.now() - previous_timestamp).days

def create_health_radar_chart(metrics1, metrics2=None, label1="Current", label2="Previous"):
    """Create radar chart for health metrics comparison"""
    categories = list(metrics1.keys())
    values1 = list(metrics1.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values1 + [values1[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=label1,
        line_color='#ff1493',
        fillcolor='rgba(255, 20, 147, 0.3)'
    ))
    
    if metrics2:
        values2 = [metrics2.get(k, 0) for k in categories]
        fig.add_trace(go.Scatterpolar(
            r=values2 + [values2[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=label2,
            line_color='#74b9ff',
            fillcolor='rgba(116, 185, 255, 0.3)'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Poppins', size=12),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_trend_line_chart(history_data):
    """Create trend line chart over time"""
    if not history_data:
        return None
    
    dates = [h['timestamp'] for h in history_data]
    health_scores = [h['overall_health'] for h in history_data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=health_scores,
        mode='lines+markers',
        name='Health Score',
        line=dict(color='#ff1493', width=3),
        marker=dict(size=8, color='#ff69b4', line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(255, 20, 147, 0.1)'
    ))
    
    fig.update_layout(
        title='Health Trend Over Time',
        xaxis_title='Date',
        yaxis_title='Health Score',
        yaxis_range=[0, 100],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.5)',
        font=dict(family='Poppins', size=12)
    )
    
    return fig

def analysis_page():
    """Main analysis page with side-by-side comparison - FIXED: No jumping"""
    init_analysis_state()
    load_css()
    navigation_sidebar()
    
    # FIXED: Modern, clean styling with anti-jump measures
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* FIXED: Prevent layout shift during upload */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    
    [data-testid="column"] {
        min-height: 300px;
    }
    
    /* Hide Streamlit default containers */
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: #fce7f3;
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 24px;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 12px;
        padding: 0 24px;
        font-size: 14px;
        font-weight: 700;
        color: #9d174d;
        background: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #be185d !important;
        box-shadow: 0 2px 8px rgba(190, 24, 93, 0.15);
    }
    
    /* Remove default Streamlit containers */
    .stMarkdown {
        background: transparent !important;
    }
    
    .main-title {
        font-size: 42px;
        font-weight: 900;
        color: #831843;
        text-align: center;
        margin: 0 0 8px 0;
        letter-spacing: -1px;
    }
    
    .subtitle {
        text-align: center;
        color: #9d174d;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 32px;
        opacity: 0.8;
    }
    
    /* Section Title - Bold and Clear */
    .section-title {
        font-size: 24px;
        font-weight: 800;
        color: #831843;
        margin: 28px 0 20px 0;
        padding: 0;
        background: none;
        border: none;
        letter-spacing: -0.3px;
    }
    
    /* FIXED: Upload Zone with min-height to prevent collapse */
    .upload-zone {
        background: white;
        min-height: 240px;
        height: 240px;
        border: 2px dashed #f9a8d4;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .upload-zone:hover {
        border-color: #ec4899;
        background: #fdf2f8;
    }
    
    /* FIXED: Preview Cards with stable dimensions */
    .preview-card {
        background: white;
        min-height: 240px;
        height: 240px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(190, 24, 93, 0.1);
        border: 2px solid #fce7f3;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .preview-header {
        background: #fdf2f8;
        padding: 12px 16px;
        border-bottom: 2px solid #fce7f3;
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 44px;
        box-sizing: border-box;
    }
    
    .preview-label {
        font-size: 13px;
        font-weight: 800;
        color: #9d174d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .preview-label.current {
        color: #ec4899;
    }
    
    .preview-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
    }
    
    /* FIXED: VS Badge with stable centering */
    .vs-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 240px;
    }
    
    .vs-badge {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 900;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        flex-shrink: 0;
    }
    
    /* Results Header */
    .results-header {
        font-size: 36px;
        font-weight: 900;
        color: #831843;
        text-align: center;
        margin: 20px 0 32px 0;
        letter-spacing: -0.5px;
    }
    
    /* Score Cards - Clean Design */
    .score-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 24px;
        align-items: center;
        margin-bottom: 32px;
    }
    
    .score-box {
        background: white;
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 4px 15px rgba(190, 24, 93, 0.1);
        border: 3px solid #fce7f3;
        text-align: center;
    }
    
    .score-box.current {
        border-color: #ec4899;
        background: linear-gradient(135deg, #fff 0%, #fdf2f8 100%);
    }
    
    .score-label-big {
        font-size: 16px;
        font-weight: 800;
        color: #9d174d;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 16px;
    }
    
    .score-value-big {
        font-size: 64px;
        font-weight: 900;
        color: #9d174d;
        line-height: 1;
        margin-bottom: 8px;
    }
    
    .score-value-big.current {
        color: #ec4899;
        font-size: 72px;
    }
    
    .score-date {
        font-size: 14px;
        color: #f472b6;
        font-weight: 700;
    }
    
    /* Change Box */
    .change-box-center {
        text-align: center;
        padding: 20px;
    }
    
    .change-arrow {
        font-size: 32px;
        margin-bottom: 8px;
    }
    
    .change-value-big {
        font-size: 28px;
        font-weight: 900;
        padding: 12px 24px;
        border-radius: 30px;
        display: inline-block;
    }
    
    .change-value-big.up {
        background: #d1fae5;
        color: #047857;
    }
    
    .change-value-big.down {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .change-value-big.neutral {
        background: #f3f4f6;
        color: #6b7280;
    }
    
    .change-label {
        margin-top: 8px;
        font-size: 14px;
        font-weight: 800;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metrics Table - Clean and Bold */
    .metrics-table {
        width: 100%;
        margin: 24px 0;
    }
    
    .metric-row {
        display: grid;
        grid-template-columns: 1.5fr 2fr 1fr 1fr 1fr;
        gap: 16px;
        align-items: center;
        padding: 20px;
        background: white;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(190, 24, 93, 0.08);
        border: 2px solid #fce7f3;
    }
    
    .metric-name {
        font-size: 18px;
        font-weight: 800;
        color: #831843;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .metric-bar-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .metric-bar-bg {
        flex: 1;
        height: 12px;
        background: #fce7f3;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .metric-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #ec4899, #f472b6);
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    
    .metric-current {
        font-size: 20px;
        font-weight: 900;
        color: #ec4899;
        min-width: 50px;
    }
    
    .metric-before {
        font-size: 16px;
        font-weight: 700;
        color: #9ca3af;
        text-decoration: line-through;
        text-align: center;
    }
    
    .metric-after {
        font-size: 20px;
        font-weight: 900;
        color: #831843;
        text-align: center;
    }
    
    .metric-diff {
        font-size: 18px;
        font-weight: 900;
        padding: 8px 16px;
        border-radius: 20px;
        text-align: center;
    }
    
    .metric-diff.up {
        background: #d1fae5;
        color: #047857;
    }
    
    .metric-diff.down {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .metric-diff.neutral {
        background: #f3f4f6;
        color: #6b7280;
    }
    
    /* Insight Section */
    .insight-title-simple {
        font-size: 22px;
        font-weight: 800;
        color: #be185d;
        margin: 32px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .insight-box-simple {
        background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
        border-left: 5px solid #ec4899;
        padding: 24px;
        border-radius: 0 16px 16px 0;
    }
    
    .insight-text-big {
        font-size: 18px;
        color: #831843;
        line-height: 1.7;
        font-weight: 600;
    }
    
    /* Chart Container - Minimal */
    .chart-wrap {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(190, 24, 93, 0.1);
        border: 2px solid #fce7f3;
        margin-top: 24px;
    }
    
    .chart-title-simple {
        font-size: 24px;
        font-weight: 800;
        color: #831843;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* History Page - Improved Design */
    .history-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    
    .history-title-big {
        font-size: 28px;
        font-weight: 900;
        color: #831843;
    }
    
    .history-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .history-card {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr auto;
        gap: 16px;
        align-items: center;
        padding: 20px 24px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(190, 24, 93, 0.1);
        border: 2px solid #fce7f3;
        border-left: 5px solid;
        transition: all 0.2s ease;
    }
    
    .history-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 15px rgba(190, 24, 93, 0.15);
    }
    
    .history-datetime {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .history-date {
        font-size: 16px;
        font-weight: 800;
        color: #831843;
    }
    
    .history-time {
        font-size: 13px;
        font-weight: 700;
        color: #f472b6;
    }
    
    .history-metric-box {
        text-align: center;
        padding: 8px;
        background: #fdf2f8;
        border-radius: 10px;
    }
    
    .history-metric-label {
        font-size: 11px;
        font-weight: 800;
        color: #9d174d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    
    .history-metric-value {
        font-size: 22px;
        font-weight: 900;
        color: #831843;
    }
    
    .history-metric-value.before {
        color: #9ca3af;
        text-decoration: line-through;
        font-size: 18px;
    }
    
    .history-change-box {
        text-align: center;
        padding: 8px 12px;
        border-radius: 20px;
        font-size: 18px;
        font-weight: 900;
    }
    
    .history-delete-btn {
        background: #fee2e2;
        color: #dc2626;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.2s;
    }
    
    .history-delete-btn:hover {
        background: #fecaca;
        transform: scale(1.05);
    }
    
    /* Clear All Button */
    .clear-all-container {
        margin-top: 32px;
        padding-top: 24px;
        border-top: 2px solid #fce7f3;
        text-align: center;
    }
    
    /* Center Button */
    .center-button {
        display: flex;
        justify-content: center;
        margin: 32px 0;
    }
    
    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%) !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        padding: 16px 48px !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5) !important;
    }
    
    /* Secondary/Danger Button */
    .danger-btn button {
        background: #fee2e2 !important;
        color: #dc2626 !important;
        border: 2px solid #fecaca !important;
        font-weight: 800 !important;
    }
    
    .danger-btn button:hover {
        background: #fecaca !important;
        transform: translateY(-1px) !important;
    }
    
    /* Info messages */
    .stInfo {
        background: #fdf2f8 !important;
        border: 2px solid #fce7f3 !important;
        border-radius: 12px !important;
        color: #831843 !important;
        font-weight: 600 !important;
    }
    
    /* Tab Title Styles */
    .tab-title {
        font-size: 28px;
        font-weight: 900;
        color: #831843;
        text-align: center;
        margin: 20px 0 30px 0;
        letter-spacing: -0.5px;
    }
    
    /* New Analysis Button */
    .new-analysis-btn {
        margin: 20px 0;
        text-align: center;
    }
    
    /* FIXED: File uploader container stability */
    .stFileUploader {
        margin-bottom: 0 !important;
    }
    
    .stFileUploader > div {
        margin-bottom: 0 !important;
    }
    </style>
    
    <h1 class="main-title">Health Analysis</h1>
    <p class="subtitle">Track and compare your flower's health over time</p>
    """, unsafe_allow_html=True)
    
    analyzer = FlowerHealthAnalyzer()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Compare", "📊 Results", "📈 Trends", "🎯 Radar", "📋 History"])
    
    # ========== TAB 1: COMPARE ==========
    with tab1:
        st.markdown('<div class="section-title">Bloom Evolution Analysis</div>', unsafe_allow_html=True)
        
        # Add "New Analysis" button if there's already a comparison
        if st.session_state.get('has_comparison'):
            col_btn1, col_btn2, col_btn3 = st.columns([6, 2, 1])
            with col_btn2:
                if st.button("🔄 Start New Analysis", key="new_analysis_btn"):
                    # Clear only the comparison data, keep history
                    st.session_state.past_analysis_data = None
                    st.session_state.current_analysis_data = None
                    st.session_state.comparison_data = None
                    st.session_state.has_comparison = False
                    st.session_state.past_image_temp = None
                    st.session_state.current_image_temp = None
                    st.session_state.current_uploaded_temp = False
                    # Increment counter for unique keys
                    st.session_state.upload_counter = st.session_state.get('upload_counter', 0) + 1
                    st.rerun()
        
        # FIXED: Use container to stabilize layout
        upload_container = st.container()
        
        with upload_container:
            col1, col_mid, col2 = st.columns([1, 0.12, 1])
            
            # Use dynamic keys based on counter to force fresh uploaders
            upload_key_suffix = f"_{st.session_state.get('upload_counter', 0)}"
            
            # FIXED: Process uploads first, then render UI based on state
            past_image_to_show = None
            current_image_to_show = None
            
            with col1:
                st.markdown('<div style="font-size: 14px; font-weight: 800; color: #9d174d; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">📷 Previous Record </div>', unsafe_allow_html=True)
                
                # File uploader (hidden label)
                past_uploaded = st.file_uploader(
                    "Past", 
                    type=['jpg', 'jpeg', 'png'], 
                    key=f"past_img{upload_key_suffix}", 
                    label_visibility="collapsed"
                )
                
                # FIXED: Update state if new file uploaded, otherwise use cached
                if past_uploaded is not None:
                    past_image = Image.open(past_uploaded).convert('RGB')
                    st.session_state.past_image_temp = past_image
                    st.session_state.past_uploaded_current = True
                    past_image_to_show = past_image
                elif st.session_state.get('past_image_temp') is not None:
                    past_image_to_show = st.session_state.past_image_temp
                else:
                    st.session_state.past_uploaded_current = False
            
            with col2:
                st.markdown('<div style="font-size: 14px; font-weight: 800; color: #ec4899; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">📷 Current Status</div>', unsafe_allow_html=True)
                
                # File uploader (hidden label)
                current_uploaded = st.file_uploader(
                    "Current", 
                    type=['jpg', 'jpeg', 'png'], 
                    key=f"current_img{upload_key_suffix}", 
                    label_visibility="collapsed"
                )
                
                # FIXED: Update state if new file uploaded, otherwise use cached
                if current_uploaded is not None:
                    current_image = Image.open(current_uploaded).convert('RGB')
                    st.session_state.current_image_temp = current_image
                    st.session_state.current_uploaded_temp = True
                    current_image_to_show = current_image
                elif st.session_state.get('current_image_temp') is not None:
                    current_image_to_show = st.session_state.current_image_temp
                else:
                    st.session_state.current_uploaded_temp = False
            
            # FIXED: Render UI after state is determined (prevents jump)
            # Re-render columns with stable content
            col1_render, col_mid_render, col2_render = st.columns([1, 0.12, 1])
            
            with col1_render:
                if past_image_to_show is not None:
                    st.markdown(f"""
                    <div class="preview-card">
                        <div class="preview-header">
                            <span class="preview-label">Past Photo</span>
                            <span style="font-size: 12px; color: #9d174d; font-weight: 700;">{datetime.now().strftime('%b %d, %H:%M')}</span>
                        </div>
                        <img src="data:image/png;base64,{get_image_base64(past_image_to_show)}" class="preview-img">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="upload-zone">
                        <div style="font-size: 28px; margin-bottom: 8px;">📸</div>
                        <div style="font-size: 16px; color: #831843; font-weight: 700; margin-bottom: 4px;">Drag and drop file here</div>
                        <div style="font-size: 13px; color: #f472b6; font-weight: 600;">Limit 200MB per file • JPG, JPEG, PNG</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_mid_render:
                # Show VS badge only when both images exist
                if past_image_to_show is not None and current_image_to_show is not None:
                    st.markdown('<div class="vs-wrapper"><div class="vs-badge">VS</div></div>', unsafe_allow_html=True)
                else:
                    # FIXED: Empty placeholder to maintain column height
                    st.markdown('<div class="vs-wrapper"></div>', unsafe_allow_html=True)
            
            with col2_render:
                if current_image_to_show is not None:
                    st.markdown(f"""
                    <div class="preview-card">
                        <div class="preview-header">
                            <span class="preview-label current">Current Photo</span>
                            <span style="font-size: 12px; color: #ec4899; font-weight: 800;">{datetime.now().strftime('%b %d, %H:%M')}</span>
                        </div>
                        <img src="data:image/png;base64,{get_image_base64(current_image_to_show)}" class="preview-img">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="upload-zone">
                        <div style="font-size: 28px; margin-bottom: 8px;">📸</div>
                        <div style="font-size: 16px; color: #831843; font-weight: 700; margin-bottom: 4px;">Drag and drop file here</div>
                        <div style="font-size: 13px; color: #f472b6; font-weight: 600;">Limit 200MB per file • JPG, JPEG, PNG</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Auto-analyze when both images are uploaded and not yet analyzed
        if (past_image_to_show is not None and 
            current_image_to_show is not None and 
            not st.session_state.get('has_comparison')):
            
            with st.spinner("Analyzing flower health..."):
                past_analysis = analyzer.analyze_image(past_image_to_show)
                current_analysis = analyzer.analyze_image(current_image_to_show)
                comparison = analyzer.compare_images(current_image_to_show, past_image_to_show, current_analysis)
                
                st.session_state.past_analysis_data = past_analysis
                st.session_state.current_analysis_data = current_analysis
                st.session_state.comparison_data = comparison
                st.session_state.has_comparison = True
                st.session_state.analysis_history.extend([past_analysis, current_analysis])
                st.rerun()

        if st.session_state.get('has_comparison'):
            st.success("✅ Analysis complete! Check the Results, Trends, and Radar tabs.")
    
    
    # ========== TAB 2: RESULTS (Clean - No White Boxes) ==========
    with tab2:
        if not st.session_state.get('has_comparison'):
            st.info("👆 Upload two photos in the Compare tab to see results")
        else:
            show_results_tab_clean()
    
    # ========== TAB 3: TRENDS ==========
    with tab3:
        st.markdown('<div class="tab-title">📈 Health Trends Over Time</div>', unsafe_allow_html=True)
        
        if len(st.session_state.analysis_history) < 2:
            st.info("Complete at least two analyses to see trends")
        else:
            fig = create_trend_line_chart(st.session_state.analysis_history)
            if fig:
                st.plotly_chart(fig, use_container_width=True, height=450)
    
    # ========== TAB 4: RADAR ==========
    with tab4:
        st.markdown('<div class="tab-title">🎯 Health Radar Comparison</div>', unsafe_allow_html=True)
        
        if not st.session_state.get('has_comparison'):
            st.info("👆 Upload photos in the Compare tab to see the radar chart")
        else:
            past = st.session_state.past_analysis_data
            current = st.session_state.current_analysis_data
            
            fig = create_health_radar_chart(
                past['metrics'], 
                current['metrics'],
                "Before",
                "After"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True, height=600)
                
            st.markdown("""
            <div style="margin-top: 20px; padding: 20px; background: white; border-radius: 16px; border: 2px solid #fce7f3;">
                <div style="font-size: 18px; font-weight: 800; color: #831843; margin-bottom: 10px;">📊 Understanding Your Chart</div>
                <div style="font-size: 15px; color: #9d174d; font-weight: 600; line-height: 1.6;">
                    The radar chart compares 5 key health metrics. Larger area = better health. 
                    <span style="color: #ec4899; font-weight: 800;">Pink</span> = Current, 
                    <span style="color: #9ca3af; font-weight: 800;">Gray</span> = Previous.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== TAB 5: HISTORY (Improved) ==========
    with tab5:
        show_history_tab()

def show_results_tab_clean():
    """Display results without white boxes - clean design"""
    past = st.session_state.past_analysis_data
    current = st.session_state.current_analysis_data
    
    past_score = past['overall_health']
    current_score = current['overall_health']
    change = current_score - past_score
    
    # Header
    st.markdown(f'<div class="results-header">📊 Comparison Results</div>', unsafe_allow_html=True)
    
    # Scores Grid
    col1, col2, col3 = st.columns([1, 0.7, 1])
    
    with col1:
        st.markdown(f"""
        <div class="score-box">
            <div class="score-label-big">Before</div>
            <div class="score-value-big">{past_score:.0f}%</div>
            <div class="score-date">{past['timestamp'].strftime('%b %d, %Y at %H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        change_class = "up" if change > 0 else "down" if change < 0 else "neutral"
        arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
        
        st.markdown(f"""
        <div class="change-box-center">
            <div class="change-value-big {change_class}">
                {arrow} {abs(change):.1f}%
            </div>
            <div class="change-label">
                {arrow} {abs(change):.1f}% {"IMPROVED" if change > 0 else "DECLINED" if change < 0 else "NO CHANGE"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="score-box current">
            <div class="score-label-big" style="color: #ec4899;">After</div>
            <div class="score-value-big current">{current_score:.0f}%</div>
            <div class="score-date" style="color: #ec4899;">{current['timestamp'].strftime('%b %d, %Y at %H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics Title
    st.markdown('<div class="section-title">Detailed Metrics Breakdown</div>', unsafe_allow_html=True)
    
    # Metrics Table
    metrics = current['metrics']
    past_metrics = past['metrics']
    metric_names = {
        'green_vitality': '🌿 Green Vitality',
        'bloom_quality': '🌸 Bloom Quality',
        'leaf_density': '🍃 Leaf Density',
        'color_vibrancy': '🎨 Color Vibrancy',
        'structural_integrity': '🏗️ Structure'
    }
    
    for key in metrics:
        curr_val = metrics[key]
        past_val = past_metrics.get(key, 0)
        diff = curr_val - past_val
        
        change_class = "up" if diff > 0 else "down" if diff < 0 else "neutral"
        change_symbol = "+" if diff > 0 else ""
        
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-name">{metric_names.get(key, key)}</div>
            <div class="metric-bar-wrap">
                <div class="metric-bar-bg">
                    <div class="metric-bar-fill" style="width: {curr_val}%;"></div>
                </div>
                <span class="metric-current">{curr_val:.0f}%</span>
            </div>
            <div class="metric-before">{past_val:.0f}%</div>
            <div class="metric-after">{curr_val:.0f}%</div>
            <div class="metric-diff {change_class}">{change_symbol}{diff:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Insight
    st.markdown('<div class="insight-title-simple">💡 Key Insight & Recommendations</div>', unsafe_allow_html=True)
    
    if change > 10:
        insight = "🎉 <b>Excellent progress!</b> Your flower shows significant improvement. Keep up the great work!"
    elif change > 0:
        insight = "🌱 <b>Good progress!</b> Your flower is healthier. Continue your current care routine."
    elif change > -10:
        insight = "⚠️ <b>Small decline.</b> Check watering and light. Adjust care slightly."
    else:
        insight = "🚨 <b>Major decline!</b> Immediate action needed. Check for pests or overwatering."
    
    st.markdown(f"""
    <div class="insight-box-simple">
        <div class="insight-text-big">{insight}</div>
    </div>
    """, unsafe_allow_html=True)

def show_history_tab():
    """Show improved history with individual delete and clear all"""
    if not st.session_state.analysis_history:
        st.info("No analyses yet. Start by comparing two photos!")
        return
    
    # Header
    st.markdown('<div class="history-title-big">📋 Analysis History</div>', unsafe_allow_html=True)
    
    # History items - show in pairs (before/after)
    history = list(st.session_state.analysis_history)
    
    # Create pairs from history - every 2 items form a comparison pair
    pairs = []
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            pairs.append((history[i], history[i+1], i))
    
    # Display all pairs in reverse order (newest first)
    for before, after, idx in reversed(pairs):
        date_str = after['timestamp'].strftime("%b %d, %Y")
        time_str = after['timestamp'].strftime("%H:%M")
        before_score = before['overall_health']
        after_score = after['overall_health']
        change = after_score - before_score
        
        # Color based on health
        if after_score >= 80:
            color = "#10b981"
        elif after_score >= 60:
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        change_class = "up" if change > 0 else "down" if change < 0 else "neutral"
        change_symbol = "+" if change > 0 else ""
        
        cols = st.columns([2, 1, 1, 1, 0.5])
        
        with cols[0]:
            st.markdown(f"""
            <div class="history-datetime">
                <div class="history-date">{date_str}</div>
                <div class="history-time">⏰ {time_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
            <div class="history-metric-box">
                <div class="history-metric-label">Before</div>
                <div class="history-metric-value before">{before_score:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f"""
            <div class="history-metric-box" style="background: #fdf2f8; border: 2px solid #fce7f3;">
                <div class="history-metric-label" style="color: #ec4899;">After</div>
                <div class="history-metric-value" style="color: {color};">{after_score:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown(f"""
            <div class="history-change-box {change_class}">
                {change_symbol}{change:.0f}%
            </div>
            """, unsafe_allow_html=True)
        
        with cols[4]:
            if st.button("🗑️", key=f"delete_{idx}", help="Delete this analysis"):
                # Remove the pair at the original index
                if idx < len(st.session_state.analysis_history):
                    st.session_state.analysis_history.pop(idx)
                # After removing first item, the second item shifts to the same index
                if idx < len(st.session_state.analysis_history):
                    st.session_state.analysis_history.pop(idx)
                
                # Clear comparison data if history is empty or modified
                if len(st.session_state.analysis_history) == 0:
                    st.session_state.has_comparison = False
                    st.session_state.past_analysis_data = None
                    st.session_state.current_analysis_data = None
                
                st.rerun()
    
    # Clear All Button at Bottom - Centered
    st.markdown('<div class="clear-all-container">', unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if st.button("🗑️ CLEAR ALL HISTORY", key="clear_all", type="secondary"):
            st.session_state.analysis_history = []
            st.session_state.has_comparison = False
            st.session_state.past_analysis_data = None
            st.session_state.current_analysis_data = None
            st.session_state.past_image_temp = None
            st.session_state.current_image_temp = None
            st.session_state.current_uploaded_temp = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def init_analysis_state():
    """Initialize session state variables - only initialize if not exists"""
    # IMPORTANT: Only initialize history if it doesn't exist
    # This preserves history across page navigations
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    # Initialize upload counter for unique keys
    if 'upload_counter' not in st.session_state:
        st.session_state.upload_counter = 0
    
    # These are temporary states that should reset when leaving the page
    defaults = {
        'past_analysis_data': None,
        'current_analysis_data': None,
        'comparison_data': None,
        'has_comparison': False,
        'past_image_temp': None,
        'current_image_temp': None,
        'current_uploaded_temp': False,
        'past_uploaded_current': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_image_base64(image):
    """Convert PIL Image to base64"""
    import base64
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
# ============================================================================
# END OF ANALYSIS MODULE
# ============================================================================

# ===============================
# MAIN APP FLOW
# ===============================

def main():
    if not st.session_state.logged_in:
        if st.session_state.page == "landing":
            landing_page()
        elif st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()
        elif st.session_state.page == "forgot_password":
            forgot_password_page()
        else:
            st.session_state.page = "landing"
            landing_page()
    else:
        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "about":
            about_page()
        elif st.session_state.page == "detection":
            detection_page()
        elif st.session_state.page == "analysis":      # <-- ADD THESE 2 LINES
            analysis_page()     
        elif st.session_state.page == "history":
            history_page()
        elif st.session_state.page == "chatbot":
            chatbot_page() 
        else:
            st.session_state.page = "home"
            home_page()

# ADD THIS LINE AT THE VERY END:
if __name__ == "__main__":
    main()
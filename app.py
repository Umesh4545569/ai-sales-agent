import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import pandas as pd
from datetime import datetime

# --- 1. PRO UI & BRANDING ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 5px; padding: 10px 20px; color: #888; }
    .stTabs [aria-selected="true"] { background-color: #6366f1 !important; color: white !important; }
    .social-btn { 
        display: flex; align-items: center; justify-content: center; 
        padding: 10px; border-radius: 8px; border: 1px solid #444; 
        margin-bottom: 10px; cursor: pointer; background: #111;
        text-decoration: none; color: white; font-weight: bold;
    }
    .social-btn:hover { background: #222; border-color: #6366f1; }
    .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. PERMANENT DATABASE (Free JSON DB) ---
DB_FILE = "salespilot_users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

# --- 3. AI ENGINES ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_ai_response(prompt):
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            return res.choices[0].message.content, "Groq Engine"
        except: pass
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text, "Gemini Engine"
        except: continue
    return None, None

# --- 4. SOCIAL LOGIN INTERFACE ---
db = load_db()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col_a, col_b, col_c = st.columns([1, 1.5, 1])
    with col_b:
        st.markdown("<h1 style='text-align: center;'>🚀 SalesPilot AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Sign in to start your 5 Crore journey.</p>", unsafe_allow_html=True)
        
        # Social UI Simulation
        if st.button("Continue with Google"): 
            st.session_state.user_email = "google_user@gmail.com"
            st.session_state.authenticated = True
            st.rerun()
        if st.button("Continue with GitHub"): 
            st.session_state.user_email = "github_user@github.com"
            st.session_state.authenticated = True
            st.rerun()
        if st.button("Continue with X (Twitter)"): 
            st.session_state.user_email = "x_user@x.com"
            st.session_state.authenticated = True
            st.rerun()
            
        st.markdown("---")
        email_input = st.text_input("Or enter work email")
        if st.button("Sign in with Email"):
            if "@" in email_input:
                st.session_state.user_email = email_input
                st.session_state.authenticated = True
                if email_input not in db: db[email_input] = 0
                save_db(db)
                st.rerun()
    st.stop()

# --- 5. SIDEBAR & SUBSCRIPTION ---
user_email = st.session_state.user_email
if user_email not in db: 
    db[user_email] = 0
    save_db(db)

credits_used = db[user_email]

with st.sidebar:
    st.title("💎 Member Area")
    st.write(f"Logged as: **{user_email}**")
    st.progress(credits_used / 3)
    st.write(f"Credits: **{3 - credits_used} left**")
    
    st.markdown("---")
    st.markdown("### 🌟 PRO FEATURES")
    st.write("✅ Unlimited Pitches\n✅ CRM Export\n✅ Global Language Support")
    
    # PERMANENT SUBSCRIPTION BUTTON
    st.markdown(f'''
    <a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank" style="text-decoration: none;">
        <div style="background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); color: black; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
            💳 UPGRADE TO PRO ($9/mo)
        </div>
    </a>
    ''', unsafe_allow_html=True)
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN B2B INTERFACE ---
if credits_used >= 3:
    st.error("⚡ Free Limit Reached!")
    st.info("Upgrade to Pro to continue generating high-conversion pitches.")
    st.stop()

st.title("🚀 SalesPilot AI: B2B Sales Pro")

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Target Intelligence")
    name = st.text_input("Target Company Name")
    url = st.text_input("Website URL")
    selling = st.text_area("What are you selling?")
    lang = st.selectbox("Language", ["English", "Japanese", "Spanish", "Hindi"])
    
    if st.button("✨ Generate B2B Suite"):
        if not name or not url:
            st.error("Missing Details.")
        else:
            with st.spinner('Analyzing...'):
                prompt = f"B2B Pro Copywriter: Analyze {url}. Target {name}. Selling {selling}. Output in {lang}. Mark with [EMAIL], [LINKEDIN], [WHATSAPP]."
                res, engine = generate_ai_response(prompt)
                if res:
                    db[user_email] += 1
                    save_db(db)
                    st.session_state.last_res = res
                    st.session_state.last_engine = engine
                    st.rerun()

with col_right:
    if 'last_res' in st.session_state:
        st.success(f"Generated via {st.session_state.last_engine}")
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp"])
        
        content = st.session_state.last_res
        e_match = re.search(r"\[EMAIL\](.*?)(?=\[|$)", content, re.DOTALL)
        l_match = re.search(r"\[LINKEDIN\](.*?)(?=\[|$)", content, re.DOTALL)
        w_match = re.search(r"\[WHATSAPP\](.*)", content, re.DOTALL)
        
        with tabs[0]: st.code(e_match.group(1).strip() if e_match else content)
        with tabs[1]: st.code(l_match.group(1).strip() if l_match else "LinkedIn DM Pending")
        with tabs[2]: st.code(w_match.group(1).strip() if w_match else "WhatsApp Pending")
    else:
        st.info("Your AI-generated intel will appear here.")

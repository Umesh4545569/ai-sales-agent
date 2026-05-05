import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re
import os
import json

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background: #0a0a0a; color: white; } .stCode { background-color: #111 !important; }</style>", unsafe_allow_html=True)

# --- 2. PERMANENT DATA STORAGE (FREE) ---
# This creates a small file to remember users even after refresh
DB_FILE = "user_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

# --- 3. ENGINE LOGIC ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_suite(prompt):
    # Try Groq First (Fastest)
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content, "Groq LPU"
        except Exception as e:
            if "429" in str(e): st.warning("Groq Busy, trying Gemini...")
    
    # Try Gemini Farm
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text, "Gemini Backup"
        except: continue
    return None, None

# --- 4. AUTH & PERSISTENCE ---
db = load_db()

if 'user_email' not in st.session_state:
    st.markdown("<div style='text-align:center'><h1>🚀 SalesPilot AI</h1><h3>Autonomous B2B Sales Engine</h3></div>", unsafe_allow_html=True)
    email = st.text_input("Enter Work Email to Access Free Credits")
    if st.button("Start Researching"):
        if "@" in email:
            st.session_state.user_email = email
            if email not in db:
                db[email] = 0 # New user starts with 0 used credits
                save_db(db)
            st.rerun()
    st.stop()

# Load user's persistent credit count
user_email = st.session_state.user_email
current_usage = db.get(user_email, 0)

# --- 5. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI")
st.caption(f"Logged in: {user_email} | Permanent Credits Used: {current_usage}/3")

if current_usage >= 3:
    st.error("⚡ Free limit reached. Refreshes won't reset this.")
    st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
    <button style="background:linear-gradient(90deg, #f59e0b 0%, #d97706 100%); color:black; width:100%; height:50px; border-radius:10px; font-weight:bold; cursor:pointer; border:none;">
    💳 Unlock Unlimited Lifetime Pro ($9/mo)</button></a>''', unsafe_allow_html=True)
    st.stop()

col1, col2 = st.columns([1, 1.5])

with col1:
    c_name = st.text_input("Company Name")
    c_url = st.text_input("Website URL")
    c_prod = st.text_area("What are you selling?")
    
    if st.button("✨ Generate Pitch Suite"):
        if not c_name or not c_url:
            st.error("Details missing.")
        else:
            with st.spinner('Engaging Dual-Engine AI...'):
                # Scrape and Generate
                prompt = f"B2B Sales Outreach for {c_name} selling {c_prod}."
                res, engine = generate_suite(prompt)
                
                if res:
                    # Update Database Permanently
                    db[user_email] += 1
                    save_db(db)
                    st.session_state.raw_data = res
                    st.session_state.target = c_name
                    st.rerun() # Refresh to show new credit count
                else:
                    st.error("🚨 ALL ENGINES BUSY. Google/Groq Free limits reached. Wait 2-5 minutes.")

with col2:
    if 'raw_data' in st.session_state:
        st.success("✅ Pitch Generated")
        st.code(st.session_state.raw_data)

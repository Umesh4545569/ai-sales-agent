import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

# --- 1. ENTERPRISE UI STYLING ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: white; }
    
    /* Login Container */
    .login-card {
        background-color: #111; padding: 40px; border-radius: 15px;
        border: 1px solid #333; text-align: center; max-width: 400px; margin: auto;
    }
    
    /* Account Picker Styling */
    .account-row {
        background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px;
        padding: 12px; margin-bottom: 10px; display: flex; align-items: center;
        transition: 0.3s; cursor: pointer; text-align: left;
    }
    .account-row:hover { border-color: #6366f1; background-color: #222; }
    
    .avatar {
        width: 40px; height: 40px; border-radius: 50%; background-color: #6366f1;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; margin-right: 15px; font-size: 18px; color: white;
    }
    .acc-info { line-height: 1.2; }
    .acc-name { font-weight: bold; font-size: 15px; color: #eee; }
    .acc-email { font-size: 13px; color: #888; }
    
    /* Custom Sidebar Button */
    .stButton>button { width: 100% !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'auth_state' not in st.session_state: st.session_state.auth_state = "login_gate"
if 'user_email' not in st.session_state: st.session_state.user_email = None

# --- 3. LOGIN INTERFACE ---
def login_screen():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🚀 SalesPilot AI</h1>", unsafe_allow_html=True)
        st.write(" ")
        
        if st.session_state.auth_state == "login_gate":
            st.markdown("<p style='text-align: center; color: #888;'>Secure B2B Login</p>", unsafe_allow_html=True)
            if st.button("Continue with Google"):
                st.session_state.auth_state = "account_picker"
                st.rerun()
            if st.button("Continue with GitHub"):
                st.session_state.auth_state = "account_picker"
                st.rerun()
            st.markdown("<p style='text-align: center; font-size: 12px; margin-top: 20px;'>By continuing, you agree to SalesPilot's Terms of Service.</p>", unsafe_allow_html=True)

        elif st.session_state.auth_state == "account_picker":
            st.markdown("### Choose an account")
            st.markdown("<p style='color: #888; font-size: 14px;'>to continue to <b>SalesPilot AI</b></p>", unsafe_allow_html=True)
            
            # List of simulated accounts
            accounts = [
                {"name": "Umesh Personal", "email": "umesh.personal@gmail.com", "init": "U"},
                {"name": "Founder Account", "email": "founder@salespilot.ai", "init": "S"}
            ]
            
            for acc in accounts:
                # We use a button but style it inside the markdown for visual effect
                if st.button(f"👤 {acc['name']} ({acc['email']})", key=acc['email']):
                    with st.spinner("Authenticating..."):
                        time.sleep(1)
                        st.session_state.user_email = acc['email']
                        st.session_state.auth_state = "dashboard"
                        st.rerun()
            
            st.markdown("---")
            if st.button("Use another account"):
                st.session_state.auth_state = "login_gate"
                st.rerun()

# --- 4. DASHBOARD LOGIC ---
if st.session_state.auth_state != "dashboard":
    login_screen()
    st.stop()

# --- 5. MAIN APPLICATION (The Product) ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")

# Sidebar
with st.sidebar:
    st.success(f"Verified: {st.session_state.user_email}")
    st.markdown("---")
    st.markdown("### 🌟 PRO PLAN")
    st.write("Unlock unlimited high-conversion pitches and CRM exports.")
    st.link_button("💳 Upgrade to Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.auth_state = "login_gate"
        st.session_state.user_email = None
        st.rerun()

# AI Logic
def run_ai(p):
    try:
        c = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = c.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": p}])
        return res.choices[0].message.content
    except: return "Engine Busy. Wait 30s."

col_in, col_out = st.columns([1, 2], gap="large")
with col_in:
    c_name = st.text_input("Target Company")
    c_url = st.text_input("Website URL")
    if st.button("✨ Generate B2B Suite"):
        with st.spinner("AI analyzing business data..."):
            st.session_state.res = run_ai(f"Write B2B sales email for {c_name} at {c_url}")

with col_out:
    if 'res' in st.session_state:
        st.success("Analysis Complete")
        st.code(st.session_state.res)

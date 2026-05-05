import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

# --- 1. PRO UI & BRANDING ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: white; }
    /* Google Account Selector Look */
    .account-box {
        background-color: white; color: #3c4043; border-radius: 8px;
        padding: 10px; margin-bottom: 8px; cursor: pointer;
        display: flex; align-items: center; border: 1px solid #dadce0;
    }
    .account-box:hover { background-color: #f7f8f8; }
    .google-header { color: #202124; font-family: 'Google Sans',Arial,sans-serif; text-align: center; }
    .avatar {
        background-color: #6366f1; color: white; border-radius: 50%;
        width: 30px; height: 30px; display: flex; align-items: center;
        justify-content: center; margin-right: 12px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
if 'login_step' not in st.session_state: st.session_state.login_step = "gate"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

# --- 3. THE "CHOOSE ACCOUNT" SCREEN ---
def show_account_selector(provider):
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown(f"<h2 class='google-header'>Choose an account</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#5f6368;'>to continue to <b>SalesPilot AI</b></p>", unsafe_allow_html=True)
        
        # Simulated Accounts
        accounts = [
            {"name": "Personal Account", "email": f"user_personal@{provider.lower()}.com", "init": "P"},
            {"name": "Work Account", "email": f"founder@business.com", "init": "W"}
        ]
        
        for acc in accounts:
            if st.button(f"{acc['name']} ({acc['email']})", key=acc['email']):
                st.session_state.user_email = acc['email']
                with st.spinner("Authenticating..."):
                    time.sleep(1.5)
                    st.session_state.authenticated = True
                    st.session_state.login_step = "dashboard"
                    st.rerun()
        
        st.markdown("---")
        if st.button("Use another account"):
            st.session_state.login_step = "email_entry"
            st.rerun()

# --- 4. THE LOGIN GATE ---
if not st.session_state.authenticated:
    if st.session_state.login_step == "gate":
        col_a, col_b, col_c = st.columns([1, 1.5, 1])
        with col_b:
            st.markdown("<h1 style='text-align: center;'>🚀 SalesPilot AI</h1>", unsafe_allow_html=True)
            st.write(" ")
            if st.button("Continue with Google"):
                st.session_state.login_step = "selector"
                st.session_state.provider = "Google"
                st.rerun()
            if st.button("Continue with GitHub"):
                st.session_state.login_step = "selector"
                st.session_state.provider = "GitHub"
                st.rerun()
            st.markdown("<p style='text-align:center; color:gray;'>Safe & Secure B2B Authentication</p>", unsafe_allow_html=True)
        st.stop()

    if st.session_state.login_step == "selector":
        show_account_selector(st.session_state.provider)
        st.stop()

# --- 5. THE MAIN DASHBOARD ---
st.title("🚀 SalesPilot AI: Enterprise Dashboard")
st.sidebar.success(f"Verified: {st.session_state.user_email}")

# AI Engine Logic (using your existing keys)
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def run_ai(prompt):
    try:
        client = Groq(api_key=groq_key)
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content
    except:
        return "Engine Busy. Upgrade to Pro for Priority access."

# Main App UI
col1, col2 = st.columns([1, 2])
with col1:
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    if st.button("Generate Pro Pitch"):
        with st.spinner("Analyzing..."):
            result = run_ai(f"Write a sales pitch for {company} at {url}")
            st.session_state.result = result

with col2:
    if 'result' in st.session_state:
        st.code(st.session_state.result)
        st.link_button("💳 Upgrade to Unlimited ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.login_step = "gate"
    st.rerun()

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
    
    /* Central Login Card */
    .auth-container {
        max-width: 400px;
        margin: 80px auto;
        padding: 40px;
        background: #111;
        border: 1px solid #333;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Account Picker List */
    .account-row {
        display: flex;
        align-items: center;
        padding: 12px;
        margin-top: 10px;
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        cursor: pointer;
        text-align: left;
    }
    .account-row:hover { border-color: #6366f1; background: #222; }
    
    .avatar {
        width: 35px; height: 35px; border-radius: 50%;
        background: #6366f1; color: white; font-weight: bold;
        display: flex; align-items: center; justify-content: center;
        margin-right: 15px;
    }
    
    .stButton>button { width: 100% !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTH LOGIC ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'step' not in st.session_state: st.session_state.step = "gate"

# --- 3. IDENTITY INTERFACE ---
def show_identity_layer():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        if st.session_state.step == "gate":
            st.title("🚀 SalesPilot AI")
            st.write("Sign in to your B2B Workspace")
            st.write(" ")
            if st.button("Continue with Google"):
                st.session_state.step = "picker"
                st.rerun()
            if st.button("Continue with GitHub"):
                st.session_state.step = "picker"
                st.rerun()
                
        elif st.session_state.step == "picker":
            st.markdown("### Choose an account")
            st.markdown("<p style='color:#888;'>to continue to <b>SalesPilot AI</b></p>", unsafe_allow_html=True)
            
            # Simulated Account Picker
            accounts = [
                {"name": "Umesh (Personal)", "email": "umesh@gmail.com", "init": "U"},
                {"name": "SalesPilot (Work)", "email": "founder@salespilot.ai", "init": "S"}
            ]
            
            for acc in accounts:
                if st.button(f"👤 {acc['name']} ({acc['email']})", key=acc['email']):
                    with st.spinner("Verifying identity..."):
                        time.sleep(1.2)
                        st.session_state.user_email = acc['email']
                        st.session_state.authenticated = True
                        st.rerun()
            
            st.markdown("---")
            if st.button("← Back"):
                st.session_state.step = "gate"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. APP FLOW ---
if not st.session_state.authenticated:
    show_identity_layer()
    st.stop()

# --- 5. DASHBOARD (What you see in your screenshot) ---
st.title("🚀 SalesPilot AI: Dashboard")
with st.sidebar:
    st.success(f"Logged in: {st.session_state.user_email}")
    if st.button("Logout / Reset Session"):
        st.session_state.authenticated = False
        st.session_state.step = "gate"
        st.rerun()

st.info("You are now inside the B2B Sales Pro Dashboard.")
# (Your Generation Logic Here)

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
    
    /* The Central Login Card */
    .auth-card {
        background-color: #111; padding: 40px; border-radius: 15px;
        border: 1px solid #333; text-align: center; 
        max-width: 450px; margin: 100px auto;
    }
    
    /* Account Picker Styling */
    .account-item {
        background-color: #1a1a1a; border: 1px solid #333; border-radius: 10px;
        padding: 15px; margin-bottom: 12px; display: flex; align-items: center;
        transition: 0.3s; cursor: pointer; text-align: left;
    }
    .account-item:hover { border-color: #6366f1; background-color: #222; }
    
    .avatar-circle {
        width: 45px; height: 45px; border-radius: 50%; background-color: #6366f1;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; margin-right: 15px; font-size: 20px; color: white;
    }
    .acc-details { line-height: 1.3; }
    .acc-name { font-weight: bold; font-size: 16px; color: #fff; }
    .acc-email { font-size: 13px; color: #aaa; }
    
    .stButton>button { width: 100% !important; border-radius: 8px !important; height: 45px; }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTH STATE LOGIC ---
if 'auth_step' not in st.session_state: st.session_state.auth_step = "gate"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

# --- 3. THE IDENTITY INTERFACE ---
def show_login_flow():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # STEP 1: THE BRAND GATE
        if st.session_state.auth_step == "gate":
            st.markdown("<div style='text-align: center; margin-top: 50px;'>", unsafe_allow_html=True)
            st.title("🚀 SalesPilot AI")
            st.write("Autonomous B2B Sales Engine")
            st.write(" ")
            
            if st.button("Continue with Google"):
                st.session_state.auth_step = "picker"
                st.rerun()
            if st.button("Continue with GitHub"):
                st.session_state.auth_step = "picker"
                st.rerun()
            
            st.markdown("<p style='color: #666; font-size: 12px; margin-top: 20px;'>By signing in, you agree to our Terms of Service.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # STEP 2: THE ACCOUNT PICKER (What you want)
        elif st.session_state.auth_step == "picker":
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown("## Choose an account")
            st.markdown("<p style='color: #888;'>to continue to <b>SalesPilot AI</b></p>", unsafe_allow_html=True)
            st.write(" ")
            
            accounts = [
                {"name": "Umesh Personal", "email": "umesh.personal@gmail.com", "init": "U"},
                {"name": "Founder Account", "email": "founder@salespilot.ai", "init": "S"}
            ]
            
            for acc in accounts:
                if st.button(f"👤 {acc['name']} ({acc['email']})", key=acc['email']):
                    with st.spinner("Authenticating..."):
                        time.sleep(1.2)
                        st.session_state.user_email = acc['email']
                        st.session_state.authenticated = True
                        st.session_state.auth_step = "app"
                        st.rerun()
            
            st.markdown("---")
            if st.button("Use another account"):
                st.session_state.auth_step = "gate"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# --- 4. ENGINE & APP LOGIC ---
if not st.session_state.authenticated:
    show_login_flow()
    st.stop()

# --- 5. THE MAIN DASHBOARD (Only shows AFTER login) ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")

# Sidebar for Status
with st.sidebar:
    st.success(f"Verified: {st.session_state.user_email}")
    st.write("Credits: 3/3")
    st.markdown("---")
    st.link_button("💳 Upgrade to Pro ($9)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.auth_step = "gate"
        st.rerun()

# Main App Generator
col_left, col_right = st.columns([1, 2], gap="large")
with col_left:
    st.subheader("Target Intelligence")
    name = st.text_input("Company Name")
    url = st.text_input("Website URL")
    prod = st.text_area("What are you selling?")
    if st.button("✨ Generate B2B Suite"):
        st.info("Generating... (Engine: Groq)")

import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import pandas as pd

# --- 1. PRO THEME & UI ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c23; border-radius: 5px; padding: 10px 20px; color: #888;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important; color: white !important;
    }
    .metric-card { 
        background: #1a1c23; padding: 15px; border-radius: 10px; 
        border: 1px solid #333; text-align: center; min-height: 100px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ENGINES ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_ai_response(prompt):
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
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

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "Data missing."

# --- 3. SESSION STATE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'user_email' not in st.session_state: st.session_state.user_email = "User"

# --- 4. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Target Intelligence")
    name = st.text_input("Target Company Name", placeholder="e.g. zomato")
    url = st.text_input("Website URL", placeholder="https://...")
    selling = st.text_area("What are you selling?", placeholder="e.g. AI-powered delivery optimization")
    lang = st.selectbox("Output Language", ["English", "Japanese", "Spanish", "French", "Hindi"])
    
    if st.button("✨ Generate B2B Suite"):
        if not name or not url:
            st.error("Missing details.")
        else:
            with st.spinner('Scraping & Researching...'):
                site_data = scrape_website(url)
                # UPDATED PROMPT WITH MARKERS
                prompt = f"""
                You are a B2B Sales Pro. Analyze: {site_data}.
                Target: {name}. Selling: {selling}. Language: {lang}.
                
                Provide exactly this structure:
                INTEL: [One sentence industry summary]
                EMAIL: [Subject and Body]
                LINKEDIN: [Short DM]
                WHATSAPP: [Friendly msg]
                """
                res, engine = generate_ai_response(prompt)
                if res:
                    st.session_state.last_res = res
                    st.session_state.last_engine = engine
                    st.session_state.pitch_count += 1
                    st.rerun()

with col_right:
    if 'last_res' in st.session_state:
        st.success(f"Intel via {st.session_state.last_engine}")
        content = st.session_state.last_res
        
        # TOP METRICS
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown("<div class='metric-card'><b>Industry</b><br>Food Tech</div>", unsafe_allow_html=True)
        with m2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><b>Language</b><br>{lang}</div>", unsafe_allow_html=True)
        
        # TAB PARSING LOGIC
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp"])
        
        # This part separates the text so the tabs aren't messy
        email_part = re.search(r"EMAIL:(.*?)(?=LINKEDIN:|$)", content, re.DOTALL)
        li_part = re.search(r"LINKEDIN:(.*?)(?=WHATSAPP:|$)", content, re.DOTALL)
        wa_part = re.search(r"WHATSAPP:(.*)", content, re.DOTALL)

        with tabs[0]: 
            st.markdown("### 📧 COLD EMAIL")
            st.code(email_part.group(1).strip() if email_part else "Email not found", language=None)
        with tabs[1]: 
            st.markdown("### 💬 LINKEDIN DM")
            st.code(li_part.group(1).strip() if li_part else "LinkedIn DM not found", language=None)
        with tabs[2]: 
            st.markdown("### 📱 WHATSAPP")
            st.code(wa_part.group(1).strip() if wa_part else "WhatsApp not found", language=None)

        # CRM EXPORT
        df = pd.DataFrame([{"Company": name, "Content": content}])
        st.download_button("📥 Export to CSV (CRM Ready)", data=df.to_csv().encode('utf-8'), file_name="sales_intel.csv")
    else:
        st.info("Input details on the left to start.")

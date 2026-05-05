import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os
import pandas as pd

# --- 1. PREMIUM UI ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0e1117; color: white; }
    .stTabs [aria-selected="true"] { background-color: #6366f1 !important; }
    .metric-card { background: #1a1c23; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ---
DB_FILE = "user_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

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

# --- 3. APP FLOW ---
db = load_db()
if 'user_email' not in st.session_state:
    st.title("🚀 SalesPilot AI")
    email = st.text_input("Enter Work Email to start")
    if st.button("Login"):
        if "@" in email:
            st.session_state.user_email = email
            if email not in db: db[email] = 0
            save_db(db)
            st.rerun()
    st.stop()

user_email = st.session_state.user_email
credits_used = db.get(user_email, 0)

# PAYWALL
if credits_used >= 3:
    st.error("⚡ Free limit reached. Upgrade to Pro!")
    st.link_button("💳 Unlock Unlimited Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    st.stop()

# --- 4. INTERFACE ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Target Intelligence")
    name = st.text_input("Target Company Name")
    url = st.text_input("Website URL")
    
    # YOUR PLACEHOLDER REQUEST
    selling = st.text_area(
        "What are you selling?", 
        height=120,
        placeholder="e.g. AI-powered route optimization software that reduces delivery costs by 40%"
    )
    
    # MULTI-LANGUAGE FEATURE
    lang = st.selectbox("Output Language", ["English", "Spanish", "German", "French", "Hindi", "Japanese"])
    
    if st.button("✨ Generate B2B Suite"):
        if not name or not url:
            st.error("Missing info.")
        else:
            with st.spinner('Scraping & Analyzing...'):
                data = scrape_website(url)
                prompt = f"""
                You are a Global Sales Expert. Analyze this data: {data}.
                Target: {name}. Selling: {selling}. Language: {lang}.
                Provide: [INDUSTRY], [SIZE_EST], [PAIN_SCORE], [EMAIL], [LINKEDIN], [WHATSAPP].
                """
                res, engine = generate_ai_response(prompt)
                if res:
                    db[user_email] += 1
                    save_db(db)
                    st.session_state.last_res = res
                    st.session_state.last_engine = engine
                    st.rerun()

with col_right:
    if 'last_res' in st.session_state:
        st.success(f"Intel via {st.session_state.last_engine}")
        content = st.session_state.last_res
        
        # AUTO-INTELLIGENCE METRICS
        m1, m2, m3 = st.columns(3)
        ind = re.search(r"\[INDUSTRY\](.*)", content)
        with m1: st.markdown(f"<div class='metric-card'><b>Industry</b><br>{ind.group(1)[:15] if ind else 'SaaS'}</div>", unsafe_allow_html=True)
        with m2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><b>Language</b><br>{lang}</div>", unsafe_allow_html=True)
        
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp"])
        
        # EXTRACT AND DISPLAY
        email_match = re.search(r"\[EMAIL\](.*?)(?=\[|$)", content, re.DOTALL)
        with tabs[0]: st.code(email_match.group(1) if email_match else content)
        
        # CRM EXPORT FEATURE
        df = pd.DataFrame([{"Company": name, "Email_Pitch": content}])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export to CSV (CRM Ready)", data=csv, file_name=f"{name}_intel.csv")
    else:
        st.info("Generating intelligence for your next deal...")

import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os

# --- 1. PREMIUM UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730; color: white; border-radius: 5px;
    }
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c23; border-radius: 5px; padding: 10px 20px; color: #888;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important; color: white !important;
    }
    /* The Gold Upgrade Button */
    .upgrade-btn {
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        color: white !important;
        padding: 15px 30px;
        text-decoration: none;
        border-radius: 10px;
        font-weight: bold;
        display: inline-block;
        text-align: center;
        margin-top: 20px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. PERMANENT DATABASE ---
DB_FILE = "user_db.json"
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

# --- 4. APP FLOW ---
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

# --- 5. THE PAYWALL (Fixed Visibility) ---
if credits_used >= 3:
    st.title("🚀 SalesPilot AI Pro")
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.warning("⚡ Free limit reached (3/3 Credits Used)")
        st.markdown("""
        ### Upgrade to SalesPilot Pro
        Join 500+ sales professionals closing deals with AI.
        - **Unlimited** high-conversion pitches
        - **Priority** AI server access (No wait time)
        - **Advanced** Company Intelligence reports
        - **Export** to PDF and CRM
        """)
        
        # LEMON SQUEEZY SUBSCRIPTION BUTTON
        st.markdown(f'''
        <a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" class="upgrade-btn">
            💳 UNLOCK UNLIMITED PRO ACCESS ($9/mo)
        </a>
        ''', unsafe_allow_html=True)
        
        st.info("Your business email is registered. Pro features will activate instantly after payment.")
    st.stop()

# --- 6. MAIN INTERFACE (Credits Remaining) ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")
st.sidebar.write(f"👤 {user_email}")
st.sidebar.write(f"📊 Credits: {3 - credits_used}/3")

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Target Business")
    name = st.text_input("Target Company Name")
    url = st.text_input("Website URL")
    selling = st.text_area("What are you selling?", height=150)
    
    if st.button("✨ Generate B2B Suite"):
        if not name or not url:
            st.error("Please fill all fields.")
        else:
            with st.spinner('Generating...'):
                prompt = f"B2B Sales Outreach for {name} selling {selling}. Headers: [EMAIL], [LINKEDIN], [WHATSAPP], [PITCH], [PAIN]"
                res, engine = generate_ai_response(prompt)
                if res:
                    db[user_email] += 1
                    save_db(db)
                    st.session_state.last_res = res
                    st.session_state.last_engine = engine
                    st.rerun()
                else:
                    st.error("Engines busy. Wait 60s.")

with col_right:
    if 'last_res' in st.session_state:
        st.success(f"Generated via {st.session_state.last_engine}")
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🎙️ Pitch", "🔍 Pain Points"])
        
        content = st.session_state.last_res
        sections = {"Email": r"\[EMAIL\](.*?)(?=\[|$)", "LinkedIn": r"\[LINKEDIN\](.*?)(?=\[|$)", "WhatsApp": r"\[WHATSAPP\](.*?)(?=\[|$)", "Pitch": r"\[PITCH\](.*?)(?=\[|$)", "Pain Points": r"\[PAIN\](.*?)(?=\[|$)"}

        for i, (label, pattern) in enumerate(sections.items()):
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            text = match.group(1).strip() if match else content
            with tabs[i]:
                st.code(text, language=None)
    else:
        st.info("Input details on the left to start.")

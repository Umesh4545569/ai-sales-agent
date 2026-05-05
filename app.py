import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
import re
import json
import os

# --- 1. INTERFACE STYLING (The Screenshot Look) ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    /* Dark Background */
    .main { background-color: #0e1117; color: white; }
    
    /* Input Boxes */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730; color: white; border-radius: 5px; border: 1px solid #444;
    }
    
    /* The Generate Button */
    .stButton>button {
        background-color: transparent; color: white; border: 1px solid #444;
        border-radius: 5px; width: 100%; padding: 10px; transition: 0.3s;
    }
    .stButton>button:hover { border-color: #6366f1; color: #6366f1; }

    /* Tabs Styling (Indigo Color) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c23; border-radius: 5px; padding: 10px 20px; color: #888;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important; color: white !important;
    }
    
    /* Success Banner */
    .stAlert { background-color: #112b1d; color: #4ade80; border: 1px solid #22543d; }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND LOGIC (Database & Engines) ---
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
    # Try Groq First
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content, "Groq Engine"
        except: pass
    
    # Try Gemini Backup
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text, "Gemini Engine"
        except: continue
    return None, None

# --- 3. THE INTERFACE LAYOUT ---
st.title("🚀 SalesPilot AI: B2B Sales Pro")

# Login / Persistence
db = load_db()
if 'user_email' not in st.session_state:
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

# TWO COLUMN LAYOUT
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("Target Business")
    name = st.text_input("Target Company Name", placeholder="e.g. zomato")
    url = st.text_input("Website URL", placeholder="https://www.zomato.com")
    selling = st.text_area("What are you selling?", height=150, placeholder="e.g. AI-powered delivery route optimization software.")
    
    if st.button("✨ Generate B2B Suite"):
        if credits_used >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        elif not name or not url:
            st.error("Please fill all fields.")
        else:
            with st.spinner('Generating...'):
                prompt = f"""
                You are a B2B Sales Expert. Generate outreach for {name} selling {selling}.
                Provide 5 distinct sections starting with these exact headers:
                [EMAIL]
                [LINKEDIN]
                [WHATSAPP]
                [PITCH]
                [PAIN]
                """
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
        
        # TABBED NAVIGATION
        tab_list = ["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🎙️ Pitch", "🔍 Pain Points"]
        tabs = st.tabs(tab_list)
        
        content = st.session_state.last_res
        sections = {
            "Email": r"\[EMAIL\](.*?)(?=\[|$)",
            "LinkedIn": r"\[LINKEDIN\](.*?)(?=\[|$)",
            "WhatsApp": r"\[WHATSAPP\](.*?)(?=\[|$)",
            "Pitch": r"\[PITCH\](.*?)(?=\[|$)",
            "Pain Points": r"\[PAIN\](.*?)(?=\[|$)"
        }

        for i, (label, pattern) in enumerate(sections.items()):
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            text = match.group(1).strip() if match else "Content not found."
            with tabs[i]:
                st.markdown(f"### {label.upper()}")
                st.code(text, language=None) # Built-in COPY button
    else:
        st.info("Input business details on the left to generate your sales suite.")

st.sidebar.caption(f"Logged in: {user_email} | Credits: {3 - credits_used}/3")
if credits_used >= 3:
    st.sidebar.link_button("💳 Upgrade to Pro ($9)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")

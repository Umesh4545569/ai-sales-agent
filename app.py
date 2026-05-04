import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time
import random

# --- 1. PRO THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background-color: #0a0a0a; color: white; } .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
keys_list = st.secrets.get("GEMINI_KEYS", [])

# --- 3. THE "ULTRA-STABLE" ENGINE ---
def smart_generate(prompt):
    # Models to try in order of efficiency
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.0-pro']
    
    # Shuffle keys to avoid hitting the same one repeatedly
    shuffled_keys = list(keys_list)
    random.shuffle(shuffled_keys)

    for key in shuffled_keys:
        try:
            genai.configure(api_key=key)
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response:
                        return response.text, model_name
                except Exception as e:
                    if "429" in str(e): continue # Rate limit, try next model
                    else: return f"Error: {e}", None
        except: continue
    return None, None

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "No data found."

def create_pdf_data(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"SalesPilot AI Pitch Report: {company}", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S')

# --- 4. LANDING & EMAIL GATE ---
if not st.session_state.user_email:
    st.markdown("<div style='text-align:center;'><h1>🚀 SalesPilot AI</h1><h3>The World's Fastest AI SDR</h3></div>", unsafe_allow_html=True)
    st.markdown("---")
    email = st.text_input("Work Email Address")
    if st.button("Start Free — No Credit Card"):
        if "@" in email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("📚 Dashboard")
    st.write(f"Credits: {3 - st.session_state.pitch_count}/3")
    st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
    <button style="background:#f59e0b; color:black; padding:12px; border:none; border-radius:8px; width:100%; font-weight:bold; cursor:pointer;">
    💳 Subscribe Pro ($9/mo)</button></a>''', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Recent Pitches")
    for item in st.session_state.history:
        st.caption(f"🏢 {item['company']}")

# --- 6. MAIN APP ---
st.title("🚀 Sales Generator")
col_in, col_out = st.columns([1, 1.5])

with col_in:
    company_name = st.text_input("Target Company")
    website = st.text_input("Website (https://...)")
    product = st.text_area("What are you selling?")
    tone = st.selectbox("Select Tone", ["Professional", "Aggressive", "Friendly", "Consultative", "Urgent"])
    
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Limit reached. Upgrade to Pro!")
        elif not company_name or not website:
            st.error("Missing info.")
        else:
            with st.spinner('Scraping Intel & Crafting Pitches...'):
                raw_data = scrape_website(website)
                prompt = f"Company: {company_name} | Website Data: {raw_data} | Selling: {product} | Tone: {tone}. Generate: 1. Cold Email 2. LinkedIn DM 3. WhatsApp 4. Elevator Pitch 5. Pain Points."
                full_pitch, model_used = smart_generate(prompt)
                
                if full_pitch:
                    st.session_state.pitch_count += 1
                    st.session_state.history.append({'company': company_name, 'date': datetime.now().strftime("%d %b"), 'pitch': full_pitch})
                    st.session_state.current_pitch = full_pitch
                    st.session_state.current_model = model_used
                else:
                    st.error("🚨 All free slots are busy. Google is rate-limiting this server. Please wait 60 seconds.")

with col_out:
    if 'current_pitch' in st.session_state:
        st.subheader("🔍 Intelligence")
        ci1, ci2, ci3 = st.columns(3)
        with ci1: st.markdown("<div class='metric-card'><b>Industry</b><br>Tech/SaaS</div>", unsafe_allow_html=True)
        with ci2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with ci3: st.markdown("<div class='metric-card'><b>Model</b><br>"+st.session_state.current_model+"</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.code(st.session_state.current_pitch, language=None)
        pdf_bytes = create_pdf_data(company_name, st.session_state.current_pitch)
        st.download_button("📄 Download PDF Report", pdf_bytes, f"{company_name}_pitch.pdf", "application/pdf")
    else:
        st.info("Your AI-generated pitch suite will appear here.")

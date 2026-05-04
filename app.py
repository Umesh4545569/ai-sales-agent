import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a1a; color: white; border-radius: 8px; }
    .stButton>button { 
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); 
        color: white; border: none; border-radius: 8px; padding: 0.7rem 2rem; width: 100%; font-weight: bold;
    }
    footer {visibility: hidden;}
    .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; min-height: 80px;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'current_model' not in st.session_state: st.session_state.current_model = "None"
keys_list = st.secrets.get("GEMINI_KEYS", [])

# --- 3. HELPER FUNCTIONS ---
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
    # Remove non-latin characters for simple FPDF
    safe_text = content.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S')

def smart_generate(prompt):
    for key in keys_list:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Gemini 1.5 Flash"
        except Exception as e:
            if "429" in str(e): continue
            else: return None, None
    return None, None

# --- 4. AUTH GATE ---
if not st.session_state.user_email:
    st.title("🚀 SalesPilot AI")
    st.write("Generate winning B2B pitches in 10 seconds.")
    email = st.text_input("Work Email Address", placeholder="name@company.com")
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
    st.subheader("History")
    for item in st.session_state.history[-5:]:
        st.caption(f"🏢 {item['company']}")

# --- 6. MAIN APP ---
st.title("🚀 Sales Generator")

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.subheader("Target Details")
    c_name = st.text_input("Target Company Name")
    c_url = st.text_input("Website (https://...)")
    c_prod = st.text_area("What are you selling?")
    c_tone = st.selectbox("Tone", ["Professional", "Urgent", "Friendly"])
    
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        elif not c_name or not c_url:
            st.error("Fill all fields.")
        else:
            with st.spinner('Scraping & Researching...'):
                raw_data = scrape_website(c_url)
                prompt = f"Company: {c_name} | Info: {raw_data} | Sell: {c_prod} | Tone: {c_tone}. Generate Cold Email, LinkedIn DM, WhatsApp, Elevator Pitch, and 3 Pain Points."
                full_pitch, model_used = smart_generate(prompt)
                
                if full_pitch:
                    st.session_state.pitch_count += 1
                    st.session_state.current_model = str(model_used)
                    st.session_state.current_company = str(c_name)
                    st.session_state.current_pitch = str(full_pitch)
                    st.session_state.history.append({'company': c_name})
                else:
                    time.sleep(10)
                    st.info("🔄 Servers busy, retrying automatically...")
                    full_pitch, model_used = smart_generate(prompt)

with col_out:
    if 'current_pitch' in st.session_state:
        st.subheader("🔍 Intelligence")
        ci1, ci2, ci3 = st.columns(3)
        with ci1: st.markdown(f"<div class='metric-card'><b>Industry</b><br>SaaS/Tech</div>", unsafe_allow_html=True)
        with ci2: st.markdown(f"<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with ci3: st.markdown(f"<div class='metric-card'><b>Model</b><br>{st.session_state.current_model}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.code(st.session_state.current_pitch, language=None)
        
        pdf_bytes = create_pdf_data(st.session_state.current_company, st.session_state.current_pitch)
        st.download_button("📄 Download PDF Report", pdf_bytes, f"pitch_report.pdf", "application/pdf")
    else:
        st.info("Your AI-generated pitch suite will appear here.")

import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re

# --- 1. UI CONFIG ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    .main { background: #0a0a0a; color: white; }
    .stCode { background-color: #111 !important; border: 1px solid #333; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 8px 8px 0px 0px; padding: 12px 24px; color: #888; }
    .stTabs [aria-selected="true"] { background-color: #6366f1 !important; color: white !important; }
    .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE LOGIC ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_suite(prompt):
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content, "Groq LPU (Priority)"
        except: pass
    
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text, "Gemini (Backup)"
        except: continue
    return None, None

# --- 3. HELPERS ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'user_email' not in st.session_state: st.session_state.user_email = None

def create_pdf(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, f"SALESPILOT AI REPORT: {company.upper()}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10)
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text)
    return bytes(pdf.output())

# --- 4. AUTH GATE ---
if not st.session_state.user_email:
    st.markdown("<div style='text-align:center'><h1>🚀 SalesPilot AI</h1><h3>The B2B SDR Engine</h3></div>", unsafe_allow_html=True)
    email = st.text_input("Enter business email to unlock 3 free credits", placeholder="you@company.com")
    if st.button("Start Researching"):
        if "@" in email and "." in email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- 5. MAIN APP ---
st.title("🚀 SalesPilot AI")
st.caption(f"Credits: {3 - st.session_state.pitch_count}/3")

if st.session_state.pitch_count >= 3:
    st.warning("⚡ Free limit reached.")
    st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
    <button style="background:linear-gradient(90deg, #f59e0b 0%, #d97706 100%); color:black; width:100%; height:50px; border-radius:10px; font-weight:bold; cursor:pointer; border:none;">
    💳 Unlock Unlimited Pro Access ($9/mo)</button></a>''', unsafe_allow_html=True)
    st.stop()

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Research Target")
    c_name = st.text_input("Company Name", placeholder="e.g. Zomato")
    c_url = st.text_input("Website URL", placeholder="https://...")
    c_prod = st.text_area("What are you selling?", placeholder="e.g. AI-powered route optimization")
    
    if st.button("✨ Generate Expert Suite"):
        if not c_name or not c_url or not c_prod:
            st.error("Fill all fields.")
        else:
            with st.spinner('Writing Pitches...'):
                prompt = f"""
                You are a B2B Sales Expert. Generate outreach for {c_name} selling {c_prod}.
                Use these exact markers: 
                [SECTION: EMAIL]
                [SECTION: LINKEDIN]
                [SECTION: WHATSAPP]
                [SECTION: PITCH]
                [SECTION: PAIN]
                """
                res, engine = generate_suite(prompt)
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.raw_data = res
                    st.session_state.current_company = c_name
                    st.session_state.engine = engine
                else:
                    st.error("Engines busy. Wait 30s.")

with col2:
    if 'raw_data' in st.session_state:
        st.success(f"✅ Generated via {st.session_state.engine}")
        
        # UI Metrics
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown("<div class='metric-card'><b>Industry</b><br>Tech/B2B</div>", unsafe_allow_html=True)
        with m2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with m3: st.markdown("<div class='metric-card'><b>Fit</b><br>Excellent</div>", unsafe_allow_html=True)
        
        # IMPROVED PARSING LOGIC
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🎙️ Pitch", "🔍 Intel"])
        sections = ["EMAIL", "LINKEDIN", "WHATSAPP", "PITCH", "PAIN"]
        
        raw_text = st.session_state.raw_data
        for i, section in enumerate(sections):
            pattern = rf"\[SECTION: {section}\](.*?)(\[SECTION:|$)"
            match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            content = match.group(1).strip() if match else raw_text # Fallback to raw if match fails
            with tabs[i]:
                st.markdown(content)
                st.code(content, language=None)
        
        st.markdown("---")
        pdf_bytes = create_pdf(st.session_state.current_company, st.session_state.raw_data)
        st.download_button("📄 Download PDF Report", pdf_bytes, f"report.pdf", "application/pdf")

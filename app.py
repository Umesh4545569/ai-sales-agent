import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF

# --- PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a1a; color: white; border-radius: 8px; }
    .stButton>button { background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%; }
    .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- ENGINE LOGIC ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'user_email' not in st.session_state: st.session_state.user_email = None
keys_list = st.secrets.get("GEMINI_KEYS", [])

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "Company data not accessible."

def create_pdf(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "SALESPILOT AI: STRATEGIC PITCH REPORT", 0, 1, 'C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Target: {company} | Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Filter for PDF safety
    safe_text = content.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S')

def smart_generate(prompt):
    for i, key in enumerate(keys_list):
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, f"Engine {i+1} Active"
        except: continue
    return None, None

# --- APP FLOW ---
if not st.session_state.user_email:
    st.title("🚀 SalesPilot AI")
    st.write("Generate Billion-Dollar Pitches in Seconds.")
    email = st.text_input("Work Email to Start")
    if st.button("Get Started"):
        if "@" in email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

st.sidebar.title("💎 Pro Dashboard")
st.sidebar.write(f"Credits: {3 - st.session_state.pitch_count}/3")
st.sidebar.link_button("🚀 GO PRO ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")

st.title("🚀 Sales Generator")
col_in, col_out = st.columns([1, 1.5])

with col_in:
    name = st.text_input("Target Company")
    url = st.text_input("Website URL")
    prod = st.text_area("What are you selling?")
    if st.button("Generate Pro Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        elif not name or not url:
            st.error("Details missing.")
        else:
            with st.spinner('AI Agent Researching...'):
                raw = scrape_website(url)
                prompt = f"Analyze: {raw}. Generate for {name} selling {prod}: 1. Pain Points, 2. Email, 3. LinkedIn DM, 4. WhatsApp Message."
                res, status = smart_generate(prompt)
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.res = res
                    st.session_state.status = status
                    st.session_state.name = name
                else:
                    st.error("All engines busy. Wait 60s or go Pro.")

with col_out:
    if 'res' in st.session_state:
        st.subheader("🔍 Strategic Intel")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown("<div class='metric-card'><b>Industry</b><br>Tech/SaaS</div>", unsafe_allow_html=True)
        with c2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Status</b><br>{st.session_state.status}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.code(st.session_state.res)
        pdf_data = create_pdf(st.session_state.name, st.session_state.res)
        st.download_button("📄 Download Pro PDF Report", pdf_data, f"report.pdf", "application/pdf")

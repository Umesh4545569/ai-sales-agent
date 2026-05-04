import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background-color: #0a0a0a; color: white; }</style>", unsafe_allow_html=True)

# --- 2. ENGINE CONFIG ---
keys_list = st.secrets.get("GEMINI_KEYS", [])

def smart_generate(prompt):
    """Retries with different keys and adds a small delay to bypass IP blocks."""
    for i, key in enumerate(keys_list):
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            # The Magic: Small wait between keys to let Google's IP block cool down
            time.sleep(1) 
            response = model.generate_content(prompt)
            return response.text, f"Engine Slot {i+1} Active"
        except Exception as e:
            if "429" in str(e):
                continue # Try next key immediately
            else:
                return None, f"Error: {str(e)}"
    return None, "ALL SLOTS BUSY: Google is limiting the Streamlit IP."

# --- [Rest of your scraping and PDF functions stay the same] ---
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "No data found."

def create_pdf(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Strategic Pitch: {company}", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, content.encode('ascii', 'ignore').decode('ascii'))
    return pdf.output(dest='S')

# --- 3. APP INTERFACE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0

st.title("🚀 SalesPilot AI: v2.2 Hyper-Engine")
col1, col2 = st.columns([1, 1.5])

with col1:
    name = st.text_input("Target Company")
    url = st.text_input("Website URL")
    prod = st.text_area("What are you selling?")
    if st.button("Generate Pro Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. [Go Pro for $9](https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d)")
        else:
            with st.spinner('Engaging AI Clusters...'):
                raw = scrape_website(url)
                prompt = f"Target: {name} | URL: {url} | Selling: {prod}. Write 5 formats: Email, LinkedIn, WhatsApp, Elevator Pitch, Pain Points."
                res, status = smart_generate(prompt)
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.res = res
                    st.session_state.status = status
                    st.session_state.name = name
                else:
                    st.warning("⚠️ ENGINE HEAT-UP: Free tier is crowded. Retrying in 10s...")
                    time.sleep(10)
                    st.info("🔄 Retrying now... please wait.")

with col2:
    if 'res' in st.session_state:
        st.success(f"✅ {st.session_state.status}")
        st.code(st.session_state.res)
        pdf_data = create_pdf(st.session_state.name, st.session_state.res)
        st.download_button("📄 Download PDF Report", pdf_data, "report.pdf")

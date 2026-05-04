import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background-color: #0a0a0a; color: white; } .stCode { background-color: #111 !important; }</style>", unsafe_allow_html=True)

# --- 2. ENGINE CONFIG ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_with_groq(prompt):
    if not groq_key: return None, "Groq Key missing"
    try:
        client = Groq(api_key=groq_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content, "Groq LPU Engine (Ultra-Fast)"
    except Exception as e:
        return None, str(e)

def generate_with_gemini(prompt):
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Gemini Backup"
        except: continue
    return None, "All Engines Throttled"

# --- 3. SCRAPING & PDF ---
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "Data not available."

def create_pdf(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, f"SALESPILOT AI REPORT: {company.upper()}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    # Clean text to avoid encoding errors
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output()

# --- 4. APP INTERFACE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0

st.title("🚀 SalesPilot AI: Enterprise v2.4")
col1, col2 = st.columns([1, 1.5])

with col1:
    name = st.text_input("Target Company Name")
    url = st.text_input("Website URL")
    prod = st.text_area("What are you selling?")
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        elif not name or not url:
            st.error("Please enter Name and URL.")
        else:
            with st.spinner('Engaging AI Engines...'):
                raw = scrape_website(url)
                prompt = f"Write a professional sales email, LinkedIn DM, and WhatsApp message for {name} selling {prod} using this data: {raw}. Keep it high-conversion."
                
                res, status = generate_with_groq(prompt)
                if not res:
                    res, status = generate_with_gemini(prompt)
                
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.res, st.session_state.status, st.session_state.name = res, status, name
                else:
                    st.error("Engines busy. Please retry in 30s.")

with col2:
    if 'res' in st.session_state:
        st.success(f"✅ {st.session_state.status}")
        st.markdown("### Generated Outreach")
        st.code(st.session_state.res, language=None)
        
        # FIXED PDF DOWNLOAD LOGIC
        try:
            pdf_output = create_pdf(st.session_state.name, st.session_state.res)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_output,
                file_name=f"SalesPilot_{st.session_state.name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF Error: {e}")
        
        st.markdown("---")
        st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
        <button style="background:orange; color:black; width:100%; height:50px; border-radius:10px; font-weight:bold; cursor:pointer;">
        💳 Upgrade to Pro for Unlimited PDF Reports ($9/mo)</button></a>''', unsafe_allow_html=True)

import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background-color: #0a0a0a; color: white; }</style>", unsafe_allow_html=True)

# --- 2. ENGINE CONFIG ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_with_groq(prompt):
    if not groq_key: return None, "Groq Key missing in secrets"
    try:
        client = Groq(api_key=groq_key)
        # UPDATED: Using Llama 3.1 8B (Fastest & currently active)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content, "Groq LPU Engine (Ultra-Fast)"
    except Exception as e:
        return None, f"Groq Error: {str(e)}"

def generate_with_gemini(prompt):
    if not gemini_keys: return None, "Gemini Keys missing"
    for i, key in enumerate(gemini_keys):
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, f"Gemini Slot {i+1}"
        except Exception:
            continue
    return None, "All Gemini keys throttled."

# --- 3. SCRAPING & PDF ---
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return "Data unavailable."

def create_pdf(company, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Strategic Report: {company}", ln=True, align='C')
    pdf.ln(10)
    # Filter for PDF safety
    safe_text = content.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S')

# --- 4. APP INTERFACE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0

st.title("🚀 SalesPilot AI: v2.3 High-Uptime")
col1, col2 = st.columns([1, 1.5])

with col1:
    name = st.text_input("Target Company")
    url = st.text_input("Website URL")
    prod = st.text_area("What are you selling?")
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        else:
            with st.spinner('Engaging High-Speed LPUs...'):
                raw = scrape_website(url)
                prompt = f"Analyze {raw}. Write a 3-sentence sales email for {name} selling {prod}."
                
                # TRY GROQ FIRST
                res, g_status = generate_with_groq(prompt)
                
                if not res:
                    st.warning(f"Groq primary engine unavailable. Trying backup...")
                    res, gem_status = generate_with_gemini(prompt)
                    status = gem_status
                else:
                    status = g_status
                
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.res, st.session_state.status, st.session_state.name = res, status, name
                else:
                    st.error("🚨 Both AI providers are currently rate-limited. Please wait 2 minutes.")

with col2:
    if 'res' in st.session_state:
        st.success(f"✅ Active: {st.session_state.status}")
        st.code(st.session_state.res)
        pdf_data = create_pdf(st.session_state.name, st.session_state.res)
        st.download_button("📄 Download PDF Report", pdf_data, "report.pdf")

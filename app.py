import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF

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
    safe_text = content.encode('ascii', 'ignore').decode('ascii')
    pdf.multi_cell(0, 10, safe_text)
    return pdf.output(dest='S')

def smart_generate(prompt):
    if not keys_list:
        return None, "No API Keys found."
    
    for i, key in enumerate(keys_list):
        try:
            genai.configure(api_key=key.strip()) # strip() removes accidental spaces
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, f"Key {i+1} Active"
        except Exception as e:
            # If the key is invalid or rate-limited, try the next one
            continue 
            
    return None, "All keys failed. Check if they are valid in Google AI Studio."

# --- 4. AUTH GATE ---
if not st.session_state.user_email:
    st.title("🚀 SalesPilot AI")
    email = st.text_input("Work Email Address")
    if st.button("Start Free"):
        if "@" in email:
            st.session_state.user_email = email
            st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("📚 Dashboard")
    st.write(f"Credits: {3 - st.session_state.pitch_count}/3")
    st.link_button("🚀 Upgrade Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")

# --- 6. MAIN APP ---
st.title("🚀 Sales Generator")

col_in, col_out = st.columns([1, 1.5])

with col_in:
    c_name = st.text_input("Company Name")
    c_url = st.text_input("Website (https://...)")
    c_prod = st.text_area("What are you selling?")
    
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached.")
        elif not c_name or not c_url:
            st.error("Fill all fields.")
        else:
            with st.spinner('Checking Key Farm...'):
                raw_data = scrape_website(c_url)
                prompt = f"Write a 3-sentence sales email for {c_name} selling {c_prod} based on: {raw_data}"
                full_pitch, status = smart_generate(prompt)
                
                if full_pitch:
                    st.session_state.pitch_count += 1
                    st.session_state.current_model = status
                    st.session_state.current_company = c_name
                    st.session_state.current_pitch = full_pitch
                    st.session_state.history.append({'company': c_name})
                else:
                    st.error(f"⚠️ {status}")

with col_out:
    if 'current_pitch' in st.session_state:
        st.subheader("🔍 Intelligence")
        ci1, ci2, ci3 = st.columns(3)
        with ci1: st.markdown(f"<div class='metric-card'><b>Industry</b><br>Tech</div>", unsafe_allow_html=True)
        with ci2: st.markdown(f"<div class='metric-card'><b>Pain</b><br>🔴 High</div>", unsafe_allow_html=True)
        with ci3: st.markdown(f"<div class='metric-card'><b>Status</b><br>{st.session_state.current_model}</div>", unsafe_allow_html=True)
        
        st.code(st.session_state.current_pitch, language=None)
        
        pdf_bytes = create_pdf_data(st.session_state.current_company, st.session_state.current_pitch)
        st.download_button("📄 Download PDF Report", pdf_bytes, f"report.pdf", "application/pdf")

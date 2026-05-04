import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import time

# --- 1. PRO THEME & UI ---
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
    .metric-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE & DATA ---
if 'history' not in st.session_state: st.session_state.history = []
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
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
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S')

def smart_generate(prompt):
    for key in keys_list:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except: continue
    return None

# --- 4. LANDING PAGE & EMAIL CAPTURE ---
if not st.session_state.user_email:
    st.markdown("""
    <div style='text-align:center; padding:20px'>
        <h1>🚀 SalesPilot AI</h1>
        <h3>Generate winning B2B pitches in 10 seconds</h3>
        <p style='color:gray'>Used by 500+ sales teams worldwide</p>
        <div style='display:flex; justify-content:center; gap:40px; margin-top:20px'>
            <div>⚡ 10s Gen</div><div>🌍 50+ Countries</div><div>💰 3x Reply Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    email = st.text_input("Work Email Address", placeholder="name@company.com")
    if st.button("Start Free — No Credit Card"):
        if "@" in email:
            st.session_state.user_email = email
            st.rerun()
        else: st.error("Valid email required.")
    st.stop()

# --- 5. SIDEBAR (HISTORY & SUBSCRIPTION) ---
with st.sidebar:
    st.title("📚 Dashboard")
    st.write(f"User: {st.session_state.user_email}")
    st.write(f"Credits: {3 - st.session_state.pitch_count}/3")
    
    st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
    <button style="background:#f59e0b; color:black; padding:12px; border:none; border-radius:8px; width:100%; font-weight:bold; cursor:pointer;">
    💳 Subscribe Pro ($9/mo)</button></a>''', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Recent Pitches")
    for item in st.session_state.history:
        st.caption(f"🏢 {item['company']} ({item['date']})")

# --- 6. MAIN APP INTERFACE ---
st.title("🚀 Sales Generator")

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.subheader("Target Details")
    company_name = st.text_input("Target Company Name")
    website = st.text_input("Website (https://...)")
    product = st.text_area("What are you selling?")
    tone = st.selectbox("Select Pitch Tone", ["Professional", "Aggressive", "Friendly", "Consultative", "Urgent"])
    
    if st.button("✨ Generate Full Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Free limit reached. Upgrade to Pro!")
        elif not company_name or not website:
            st.error("Missing info.")
        else:
            with st.spinner('Scraping Intel & Crafting Pitches...'):
                raw_data = scrape_website(website)
                prompt = f"""
                Company: {company_name} | Website Data: {raw_data} | Selling: {product} | Tone: {tone}
                Generate exactly:
                1. COLD EMAIL: Subject and 3 paragraph body.
                2. LINKEDIN DM: Under 300 chars.
                3. WHATSAPP: Friendly and short.
                4. ELEVATOR PITCH: 30s script.
                5. PAIN POINTS: 3 bullet points.
                """
                full_pitch = smart_generate(prompt)
                
                if full_pitch:
                    st.session_state.pitch_count += 1
                    st.session_state.history.append({
                        'company': company_name, 'date': datetime.now().strftime("%d %b"), 'pitch': full_pitch
                    })
                    st.session_state.current_pitch = full_pitch
                else:
                    st.error("Engine busy. Try again in 60s.")

with col_out:
    if 'current_pitch' in st.session_state:
        st.subheader("🔍 Company Intelligence")
        ci1, ci2, ci3 = st.columns(3)
        with ci1: st.markdown("<div class='metric-card'><b>Industry</b><br>SaaS/Tech</div>", unsafe_allow_html=True)
        with ci2: st.markdown("<div class='metric-card'><b>Pain Score</b><br>🔴 High</div>", unsafe_allow_html=True)
        with ci3: st.markdown("<div class='metric-card'><b>Fit</b><br>Strong</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📄 Generated Pitch Suite")
        st.code(st.session_state.current_pitch, language=None)
        
        pdf_bytes = create_pdf_data(company_name, st.session_state.current_pitch)
        st.download_button("📄 Download PDF Report", pdf_bytes, f"{company_name}_pitch.pdf", "application/pdf")
    else:
        st.info("Your AI-generated pitch suite will appear here.")

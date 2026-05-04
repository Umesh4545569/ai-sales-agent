import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# --- 1. PRO THEME & UI ---
st.set_page_config(page_title="SalesPilot AI", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border-radius: 8px; }
    .stButton>button { 
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); 
        color: white; border: none; border-radius: 8px; padding: 0.7rem 2rem; width: 100%;
        font-weight: bold;
    }
    .stExpander { background-color: #111; border: 1px solid #333; border-radius: 10px; }
    .pitch-box { background-color: #161616; padding: 20px; border-radius: 12px; border-left: 5px solid #6366f1; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & LIMITS ---
if 'pitch_count' not in st.session_state:
    st.session_state.pitch_count = 0
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

api_key = st.secrets.get("GEMINI_API_KEY")

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): script.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return None

# --- 3. AUTH & EMAIL GATE ---
if not st.session_state.authenticated:
    st.title("🚀 SalesPilot AI")
    st.write("The Enterprise AI Sales SDR. Turn URLs into high-conversion revenue.")
    email = st.text_input("Enter business email to access free credits")
    if st.button("Start Building Pitches"):
        if "@" in email:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Please enter a valid email.")
    st.stop()

# --- 4. PAYWALL ---
if st.session_state.pitch_count >= 3:
    st.title("⚡ Limit Reached")
    st.warning("You've used your 3 free daily pitches.")
    st.markdown("### Upgrade to Pro for unlimited leads & CRM export.")
    st.link_button("🚀 Upgrade to SalesPilot Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    st.stop()

# --- 5. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI")
st.caption(f"Credits: {3 - st.session_state.pitch_count} remaining")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### Target Intel")
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    service = st.text_area("What are you selling?")
    gen_btn = st.button("Generate Pitch Suite")

with col2:
    if gen_btn:
        if not company or not url:
            st.error("Missing details.")
        else:
            with st.spinner('Scraping & Researching...'):
                genai.configure(api_key=api_key)
                data = scrape_website(url)
                if data:
                    prompt = f"Analyze: {data}. Target: {company}. Sell: {service}. Output: 1. Pain Points 2. Cold Email 3. LinkedIn DM 4. WhatsApp 5. Elevator Pitch."
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt).text
                    
                    st.session_state.pitch_count += 1
                    
                    st.success("✅ Pitch Suite Generated")
                    tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🔍 Analysis"])
                    
                    with tabs[0]: st.code(response)
                    with tabs[1]: st.info("Perfect for LinkedIn InMail")
                    with tabs[3]: st.write(response)
                else:
                    st.error("Scraping failed.")

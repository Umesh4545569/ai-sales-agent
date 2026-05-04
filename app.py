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
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [aria-selected="true"] { color: #6366f1 !important; border-bottom-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & LIMITS ---
if 'pitch_count' not in st.session_state:
    st.session_state.pitch_count = 0
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# API Key from Secrets
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

# --- 4. PAYWALL (LEMON SQUEEZY) ---
if st.session_state.pitch_count >= 3:
    st.title("⚡ Limit Reached")
    st.warning("You've used your 3 free daily pitches.")
    st.markdown("### Upgrade to SalesPilot Pro for unlimited pitches.")
    st.link_button("🚀 Upgrade to Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    st.stop()

# --- 5. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI")
st.caption(f"Status: Pro Simulation | Free Credits: {3 - st.session_state.pitch_count} left")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### Target Research")
    company = st.text_input("Company Name (e.g. Zomato)")
    url = st.text_input("Website URL (https://...)")
    service = st.text_area("What are you selling?", placeholder="e.g. Logistics software...")
    gen_btn = st.button("Generate Pro Pitch Suite")

with col2:
    if gen_btn:
        if not company or not url:
            st.error("Please provide both company name and URL.")
        else:
            with st.spinner('Scraping Intel & Detecting AI Engine...'):
                try:
                    genai.configure(api_key=api_key)
                    
                    # DYNAMIC MODEL DISCOVERY (FIXES THE 404 ERROR)
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = next((m for m in models if "1.5-flash" in m), models[0])
                    
                    data = scrape_website(url)
                    if data:
                        prompt = f"""
                        Analyze data: {data}. Target: {company}. Service: {service}.
                        Create:
                        1. Pain Points: Identify 3.
                        2. Email: Catchy subject + 3 sentence body.
                        3. LinkedIn: Short DM (200 chars).
                        4. WhatsApp: Direct casual message.
                        """
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt).text
                        
                        st.session_state.pitch_count += 1
                        
                        st.success(f"✅ Success! (Engine: {model_name})")
                        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🔍 Full Analysis"])
                        with tabs[0]: st.code(response)
                        with tabs[1]: st.info("Copy this for LinkedIn InMail")
                        with tabs[3]: st.write(response)
                        
                        st.download_button("Download Suite (.txt)", response, file_name=f"{company}_SalesPilot.txt")
                    else:
                        st.error("Scraping failed. Is the URL correct?")
                except Exception as e:
                    st.error(f"Engine Error: {e}")

st.markdown("---")
st.markdown("<center>Powered by SalesPilot AI | Targeted B2B Outreach at Scale</center>", unsafe_allow_html=True)

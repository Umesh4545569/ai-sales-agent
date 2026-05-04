import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# --- 1. PRO UI THEME ---
st.set_page_config(page_title="SalesPilot AI", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a1a; color: white; border-radius: 8px; }
    
    /* Button Styling */
    .normal-btn button { background-color: #4b5563 !important; color: white !important; border-radius: 8px !important; width: 100%; }
    .pro-btn button { background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important; color: white !important; border-radius: 8px !important; width: 100%; font-weight: bold; }
    .sub-btn a { 
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important; 
        color: white !important; padding: 12px 20px; text-decoration: none; border-radius: 8px;
        display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & STATE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

api_key = st.secrets.get("GEMINI_API_KEY")

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): script.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return None

# --- 3. AUTH GATE ---
if not st.session_state.authenticated:
    st.title("🚀 SalesPilot AI")
    st.write("The Enterprise AI Sales SDR. Generate high-conversion pitches in seconds.")
    email = st.text_input("Enter business email to start")
    if st.button("Access Free Credits"):
        if "@" in email:
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 4. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI")
st.caption(f"Credits Used: {st.session_state.pitch_count}/3")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### Target Input")
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    service = st.text_area("What are you selling?")
    
    st.markdown("---")
    st.markdown('<div class="normal-btn">', unsafe_allow_html=True)
    normal_gen = st.button("Generate Normal Pitch (Free)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="pro-btn">', unsafe_allow_html=True)
    pro_gen = st.button("✨ Generate Full Pro Suite")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" class="sub-btn">💳 Subscribe to Unlimited Pro ($9/mo)</a>', unsafe_allow_html=True)

with col2:
    if st.session_state.pitch_count >= 3 and (normal_gen or pro_gen):
        st.error("⚡ Free limit reached. Please use the Subscription button to continue.")
        st.stop()

    if normal_gen or pro_gen:
        if not company or not url:
            st.error("Missing company info.")
        else:
            with st.spinner('AI Agent is discovering best model and researching...'):
                try:
                    genai.configure(api_key=api_key)
                    
                    # DYNAMIC MODEL DISCOVERY to fix 404 error
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = ""
                    if any("1.5-flash" in m for m in available_models):
                        model_name = [m for m in available_models if "1.5-flash" in m][0]
                    else:
                        model_name = available_models[0]
                    
                    data = scrape_website(url)
                    if data:
                        if normal_gen:
                            prompt = f"Write a simple 3-line sales email for {company} selling {service} based on {data}."
                            st.success(f"✅ Normal Pitch Ready (Model: {model_name})")
                        else:
                            prompt = f"Analyze: {data}. Write: 1. Pain Points 2. Pro Email 3. LinkedIn DM 4. WhatsApp DM for {company} selling {service}."
                            st.success(f"✨ Pro Suite Generated (Model: {model_name})")
                        
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        
                        st.session_state.pitch_count += 1
                        st.write(response.text)
                    else:
                        st.error("Could not read website. Try a different URL.")
                except Exception as e:
                    st.error(f"Technical Error: {e}")
                    st.info("Tip: If you see a Quota error, wait 30 seconds.")

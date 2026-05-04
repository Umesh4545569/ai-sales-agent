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
    .sidebar .stButton>button {
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); /* Gold color for Pro */
    }
    .stExpander { background-color: #111; border: 1px solid #333; border-radius: 10px; }
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

# --- 3. SIDEBAR (ALWAYS VISIBLE UPGRADE) ---
with st.sidebar:
    st.title("🛡️ SalesPilot Control")
    if st.session_state.authenticated:
        st.write(f"📊 Credits: **{3 - st.session_state.pitch_count}/3**")
        st.markdown("---")
        st.write("🌟 **Unlock Pro Features**")
        st.write("- Unlimited Pitches\n- CRM Export\n- Custom AI Tones")
        st.link_button("🚀 Upgrade to Pro ($9/mo)", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")

# --- 4. AUTH & EMAIL GATE ---
if not st.session_state.authenticated:
    st.title("🚀 SalesPilot AI")
    st.write("The Enterprise AI Sales SDR. Turn URLs into revenue.")
    email = st.text_input("Enter business email to start")
    if st.button("Access Terminal"):
        if "@" in email:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid email.")
    st.stop()

# --- 5. PAYWALL (BLOCKS GENERATION AFTER 3) ---
if st.session_state.pitch_count >= 3:
    st.title("⚡ Free Limit Reached")
    st.warning("You have used all 3 free pitches for today.")
    st.markdown("### Join 500+ Sales Pros using SalesPilot Pro")
    st.link_button("🚀 Get Unlimited Access — $9/mo", "https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d")
    st.stop()

# --- 6. MAIN INTERFACE ---
st.title("🚀 SalesPilot AI")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### Research Target")
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    service = st.text_area("What are you selling?")
    gen_btn = st.button("Generate Pro Pitch Suite")

with col2:
    if gen_btn:
        if not company or not url:
            st.error("Provide details.")
        else:
            with st.spinner('AI Researching...'):
                try:
                    genai.configure(api_key=api_key)
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = next((m for m in models if "1.5-flash" in m), models[0])
                    
                    data = scrape_website(url)
                    if data:
                        prompt = f"Analyze: {data}. Target: {company}. Sell: {service}. Write: 1. Pain Points 2. Email 3. LinkedIn 4. WhatsApp."
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt).text
                        
                        st.session_state.pitch_count += 1
                        st.success(f"✅ Pitch Ready!")
                        st.write(response)
                        
                        st.markdown("---")
                        st.info("💡 Want unlimited pitches? [Upgrade to Pro here](https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d)")
                    else:
                        st.error("Scrape failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

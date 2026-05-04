import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="SalesPilot AI", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: #ffffff; }
    .stButton>button { background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    .sub-btn a { background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important; color: white !important; padding: 12px 20px; text-decoration: none; border-radius: 8px; display: block; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. MULTI-KEY ROTATION LOGIC ---
# Load the list of keys from secrets
keys_list = st.secrets.get("GEMINI_KEYS", [])

if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]): script.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return None

# --- 3. THE "UNLIMITED" GENERATOR FUNCTION ---
def generate_with_rotation(prompt):
    # Try every key in your list until one works
    for key in keys_list:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, key # Success!
        except Exception as e:
            if "429" in str(e):
                continue # Try the next key
            else:
                return f"Error: {e}", None
    return "All API keys are currently exhausted. Please wait 60 seconds.", None

# --- 4. APP INTERFACE ---
if not st.session_state.authenticated:
    st.title("🚀 SalesPilot AI")
    email = st.text_input("Enter business email to start")
    if st.button("Access Free Credits"):
        if "@" in email:
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

st.title("🚀 SalesPilot AI")
st.caption(f"Status: High-Volume Engine Active | Credits Used: {st.session_state.pitch_count}/3")

col1, col2 = st.columns([1, 1.5])

with col1:
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    service = st.text_area("What are you selling?")
    
    st.markdown("---")
    pro_gen = st.button("✨ Generate Full Pro Suite")
    st.markdown(f'<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" class="sub-btn">💳 Subscribe to Unlimited Pro ($9/mo)</a>', unsafe_allow_html=True)

with col2:
    if st.session_state.pitch_count >= 3 and pro_gen:
        st.error("Free limit reached. Upgrade to Pro for business use.")
        st.stop()

    if pro_gen:
        if not company or not url:
            st.error("Missing details.")
        else:
            with st.spinner('Rotating keys and researching...'):
                data = scrape_website(url)
                if data:
                    prompt = f"Analyze: {data}. Write a 3-sentence sales email and LinkedIn DM for {company} selling {service}."
                    result, used_key = generate_with_rotation(prompt)
                    
                    if used_key:
                        st.session_state.pitch_count += 1
                        st.success("✅ Success!")
                        st.write(result)
                    else:
                        st.warning(result) # Show the exhausted message
                else:
                    st.error("Scrape failed.")

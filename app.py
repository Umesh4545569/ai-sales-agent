import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time

# --- 1. UI ---
st.set_page_config(page_title="SalesPilot AI", page_icon="🚀", layout="wide")
st.markdown("<style>.main { background-color: #0a0a0a; color: white; }</style>", unsafe_allow_html=True)

# --- 2. THE KEY FARM ---
keys_list = st.secrets.get("GEMINI_KEYS", [])

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:3000]
    except: return None

# --- 3. THE SMART ROTATOR ---
def smart_generate(prompt):
    models_to_try = ['gemini-1.5-flash', 'gemini-1.0-pro'] # Try both versions
    
    for key in keys_list:
        genai.configure(api_key=key)
        for model_variant in models_to_try:
            try:
                model = genai.GenerativeModel(model_variant)
                response = model.generate_content(prompt)
                return response.text, f"{model_variant} (Key Active)"
            except Exception as e:
                if "429" in str(e):
                    continue # Try next model or next key
                else:
                    pass 
    return None, None

# --- 4. APP ---
st.title("🚀 SalesPilot AI: High-Volume Engine")

if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0

col1, col2 = st.columns([1, 1.5])

with col1:
    company = st.text_input("Company Name")
    url = st.text_input("Website URL")
    service = st.text_area("What are you selling?")
    gen_btn = st.button("✨ Generate Pro Pitch Suite")
    st.markdown(f'<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" style="background:orange; color:white; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center; font-weight:bold;">💳 Subscribe for Priority Servers ($9/mo)</a>', unsafe_allow_html=True)

with col2:
    if gen_btn:
        if not company or not url:
            st.error("Enter details.")
        else:
            with st.spinner('Scanning Engine Farm for available slot...'):
                data = scrape_website(url)
                if data:
                    prompt = f"Analyze: {data}. Write a 3-sentence sales email for {company} selling {service}."
                    result, status = smart_generate(prompt)
                    
                    if result:
                        st.session_state.pitch_count += 1
                        st.success(f"✅ Success! Generated via {status}")
                        st.write(result)
                    else:
                        st.error("🚨 ALL FREE SLOTS BUSY. Google is rate-limiting your IP. Please wait 60 seconds or Upgrade to Pro.")
                else:
                    st.error("Website unreachable.")

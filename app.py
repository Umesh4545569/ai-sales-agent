import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Agent Pro", page_icon="🚀")
st.title("🚀 Professional AI Sales Agent")

# Secure API Key Loading
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        return " ".join(text.split())[:3000] 
    except Exception as e:
        return None

with st.form("agent_form"):
    company = st.text_input("Target Company Name")
    url = st.text_input("Target Website URL (https://...)")
    service = st.text_input("What are you selling?")
    submit = st.form_submit_button("Generate Professional Pitch")

if submit:
    if not api_key:
        st.error("❌ API Key not found. Please add it to Secrets or Sidebar.")
    else:
        with st.spinner('Connecting to your AI engine...'):
            try:
                genai.configure(api_key=api_key)
                
                # DYNAMIC DISCOVERY: Ask Google what models you have
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Pick the best one (prefer 1.5-flash for speed)
                model_name = ""
                for m in models:
                    if "1.5-flash" in m:
                        model_name = m
                        break
                if not model_name:
                    model_name = models[0] # Fallback to first available

                data = scrape_website(url)
                if data:
                    prompt = f"Analyze this data: {data}. Write a 3-sentence sales email for {company} selling {service}."
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    
                    st.success(f"✅ Success! Generated using {model_name}")
                    st.markdown("### Your Personalized Pitch:")
                    st.info(response.text)
                else:
                    st.error("Could not read website. Check the URL.")
            except Exception as e:
                if "429" in str(e):
                    st.error("Quota Exceeded! Wait 60 seconds. (Free Tier limit)")
                else:
                    st.error(f"Error: {e}")

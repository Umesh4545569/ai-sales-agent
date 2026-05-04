import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Agent Pro", page_icon="🚀")
st.title("🚀 Professional AI Sales Agent")

# 1. Secure API Key Loading
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
        st.error("❌ API Key not found. Please add GEMINI_API_KEY to Streamlit Secrets.")
    else:
        with st.spinner('AI is researching and selecting best model...'):
            try:
                genai.configure(api_key=api_key)
                
                # 2. AUTO-DETECT WORKING MODEL
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Try to find Flash first, then Pro
                model_to_use = "models/gemini-1.5-flash" # Default
                if any("gemini-1.5-flash" in m for m in available_models):
                    model_to_use = [m for m in available_models if "gemini-1.5-flash" in m][0]
                elif any("gemini-pro" in m for m in available_models):
                    model_to_use = [m for m in available_models if "gemini-pro" in m][0]

                data = scrape_website(url)
                if data:
                    prompt = f"Write a professional 3-sentence sales email for {company} selling {service}. Use this data: {data}. Focus on ROI."
                    model = genai.GenerativeModel(model_to_use)
                    response = model.generate_content(prompt)
                    
                    st.success(f"✅ Success! (Using {model_to_use})")
                    st.markdown("### Your Personalized Pitch:")
                    st.info(response.text)
                else:
                    st.error("Could not read website. Ensure URL is correct.")
            except Exception as e:
                st.error(f"Technical Error: {e}")

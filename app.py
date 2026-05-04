import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time

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
        st.error("❌ Please configure your API Key.")
    else:
        with st.spinner('AI is researching...'):
            try:
                genai.configure(api_key=api_key)
                # Forced to use 'gemini-1.5-flash' for highest free-tier limits
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                data = scrape_website(url)
                if data:
                    prompt = f"Analyze this data: {data}. Write a 3-sentence sales email for {company} selling {service}. Focus on how they save money."
                    response = model.generate_content(prompt)
                    
                    st.success("✅ Success!")
                    st.markdown("### Your Personalized Pitch:")
                    st.info(response.text)
                else:
                    st.error("Could not read website. Try again.")
            except Exception as e:
                if "429" in str(e):
                    st.error("Too many requests! Please wait 60 seconds and try again. This is a limit of the Free Tier.")
                else:
                    st.error(f"Technical Error: {e}")

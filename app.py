import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# CHANGE THE NAME HERE
st.set_page_config(page_title="AgenticSales", page_icon="🚀")
st.title("🚀 AgenticSales: Autonomous Sales SDR")
st.subheader("High-performance AI agents for Logistics & SaaS")

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
        st.error("❌ API Key not found.")
    else:
        with st.spinner('AgenticSales is researching the target...'):
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = [m for m in models if "1.5-flash" in m][0] if any("1.5-flash" in m for m in models) else models[0]
                
                data = scrape_website(url)
                if data:
                    prompt = f"Analyze website data: {data}. Write a 3-sentence high-conversion sales email for {company} selling {service}. Focus on ROI and efficiency."
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    st.success("✅ Success!")
                    st.info(response.text)
                else:
                    st.error("Could not read website.")
            except Exception as e:
                st.error(f"Error: {e}")

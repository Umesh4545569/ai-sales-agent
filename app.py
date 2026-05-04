import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Agent Pro", page_icon="🚀")
st.title("🚀 Professional AI Sales Agent")

# Automatically get the API Key from Streamlit Secrets
# If not found in secrets, it falls back to the sidebar (for safety)
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
        st.error("❌ API Key not configured!")
    else:
        with st.spinner('AI Agent is researching...'):
            try:
                genai.configure(api_key=api_key)
                data = scrape_website(url)
                if data:
                    prompt = f"Write a 3-sentence sales email for {company} selling {service} based on this: {data}"
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.success("✅ Analysis Complete!")
                    st.write(response.text)
                else:
                    st.error("Could not read website.")
            except Exception as e:
                st.error(f"Error: {e}")

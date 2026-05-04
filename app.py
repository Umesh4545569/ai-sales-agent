import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Zero-Cost AI Agent", page_icon="🚀")
st.title("🚀 AI Sales Agent (Bulletproof Version)")

# Sidebar for Setup
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

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

# Form
with st.form("agent_form"):
    company = st.text_input("Target Company Name")
    url = st.text_input("Target Website URL (https://...)")
    service = st.text_input("What are you selling?")
    submit = st.form_submit_button("Generate Pitch")

if submit:
    if not api_key:
        st.error("❌ Please enter your API Key in the sidebar!")
    else:
        with st.spinner('Scanning available AI models...'):
            try:
                genai.configure(api_key=api_key)
                
                # Get ALL models and strip the 'models/' prefix to be safe
                raw_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Filter for the best ones
                working_model = None
                
                # List of models to try in order of quality
                to_try = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-pro", "models/gemini-pro"]
                
                # Add any other models discovered from the API list
                for m in raw_models:
                    if m not in to_try:
                        to_try.append(m)

                data = scrape_website(url)
                if not data:
                    st.error("Could not read website.")
                    st.stop()

                prompt = f"Write a 3-sentence sales email for {company} selling {service} based on this data: {data}"

                # TRY EACH MODEL UNTIL ONE WORKS
                for model_name in to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response.text:
                            st.success(f"✅ Success using {model_name}!")
                            st.write("### Your Personalized Pitch:")
                            st.info(response.text)
                            working_model = model_name
                            break
                    except Exception:
                        continue # If it fails, try the next one in the list
                
                if not working_model:
                    st.error("Could not find a working model. Please check your API Key permissions at aistudio.google.com")

            except Exception as e:
                st.error(f"Setup Error: {e}")

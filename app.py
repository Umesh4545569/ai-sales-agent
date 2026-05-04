import streamlit as st
import google.generativeai as genai
from groq import Groq
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re

# --- 1. UI CONFIG ---
st.set_page_config(page_title="SalesPilot AI Pro", page_icon="🚀", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0a0a0a; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a; border-radius: 4px 4px 0px 0px; padding: 10px 20px; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #6366f1 !important; }
    .stCode { background-color: #111 !important; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE LOGIC ---
gemini_keys = st.secrets.get("GEMINI_KEYS", [])
groq_key = st.secrets.get("GROQ_API_KEY", "")

def generate_output(prompt):
    # Try Groq First
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content, "Groq Engine"
        except: pass
    
    # Fallback to Gemini
    for key in gemini_keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            return res.text, "Gemini Engine"
        except: continue
    return None, None

# --- 3. SCRAPING ---
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return " ".join(soup.get_text().split())[:4000]
    except: return "No website data available."

# --- 4. APP INTERFACE ---
if 'pitch_count' not in st.session_state: st.session_state.pitch_count = 0

st.title("🚀 SalesPilot AI: B2B Sales Pro")
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Target Business")
    name = st.text_input("Target Company Name", placeholder="e.g. Zomato")
    url = st.text_input("Website URL", placeholder="https://...")
    prod = st.text_area("What are you selling?", placeholder="e.g. AI-powered route optimization")
    
    if st.button("✨ Generate B2B Suite"):
        if st.session_state.pitch_count >= 3:
            st.error("Limit reached. Upgrade to Pro below.")
        elif not name or not url or not prod:
            st.error("Please fill all fields.")
        else:
            with st.spinner('Expert Copywriter is thinking...'):
                site_data = scrape_website(url)
                # THE FIXED PROMPT
                prompt = f"""
                You are an expert B2B sales copywriter.
                USER ROLE: Salesperson trying to SELL.
                TARGET CLIENT: {name} ({url})
                PRODUCT BEING SOLD: {prod}
                RESEARCH DATA: {site_data}

                TASK: Write outreach FROM salesperson TO {name}.
                ===COLD EMAIL===
                Subject: Selling {prod} to {name}
                Body: 3 paragraphs referencing {name}'s context.
                ===LINKEDIN DM===
                Under 300 chars referencing {name}.
                ===WHATSAPP===
                Short and friendly.
                ===ELEVATOR PITCH===
                30-second verbal script.
                ===PAIN POINTS===
                3 specific bullets.
                """
                
                res, engine = generate_output(prompt)
                if res:
                    st.session_state.pitch_count += 1
                    st.session_state.raw_res = res
                    st.session_state.target_name = name
                    st.session_state.engine_info = engine
                else:
                    st.error("Engines busy. Retry in 30s.")

with col2:
    if 'raw_res' in st.session_state:
        st.success(f"✅ Generated via {st.session_state.engine_info}")
        
        # Split logic to create tabs
        content = st.session_state.raw_res
        
        tabs = st.tabs(["📧 Email", "💬 LinkedIn", "📱 WhatsApp", "🎙️ Pitch", "🔍 Pain Points"])
        
        sections = {
            "Email": r"===COLD EMAIL===(.*?)===",
            "LinkedIn": r"===LINKEDIN DM===(.*?)===",
            "WhatsApp": r"===WHATSAPP===(.*?)===",
            "Pitch": r"===ELEVATOR PITCH===(.*?)===",
            "Pain": r"===PAIN POINTS===(.*)"
        }

        for i, (label, pattern) in enumerate(sections.items()):
            match = re.search(pattern, content, re.DOTALL)
            text = match.group(1).strip() if match else content
            with tabs[i]:
                st.markdown(text)
                st.code(text, language=None) # Auto-copy button

        st.markdown("---")
        st.markdown(f'''<a href="https://salespilotai.lemonsqueezy.com/checkout/buy/5a3cf1a7-0418-4e8b-b389-a1a57621f28d" target="_blank">
        <button style="background:linear-gradient(90deg, #f59e0b 0%, #d97706 100%); color:black; width:100%; height:50px; border-radius:10px; font-weight:bold; cursor:pointer; border:none;">
        💳 Upgrade to Pro ($9/mo)</button></a>''', unsafe_allow_html=True)

import streamlit as st
import json
import re
import requests
from bs4 import BeautifulSoup
import trafilatura
from google import genai
from google.genai import types

st.set_page_config(
    page_title="VeritasLens • Gemini AI Claim Forensic Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .verdict-banner {
        padding: 16px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 20px;
        text-align: center;
        letter-spacing: 0.5px;
        margin-bottom: 20px;
    }
    .verdict-real {
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.35);
    }
    .verdict-fake {
        background: linear-gradient(135deg, #b71c1c, #d32f2f);
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.35);
    }
    .verdict-sensational {
        background: linear-gradient(135deg, #e65100, #f57c00);
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(245, 124, 0, 0.35);
    }
    .tag-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        background-color: rgba(255, 75, 75, 0.15);
        color: #ff4b4b;
        margin-right: 6px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 75, 75, 0.3);
    }
    .claim-box {
        background: rgba(33, 150, 243, 0.08);
        border-left: 4px solid #2196f3;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
    }
    .bias-card {
        background: rgba(255, 193, 7, 0.08);
        border-left: 4px solid #ffc107;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- LIVE URL SCRAPER -----------------
def scrape_article(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(downloaded)
            soup = BeautifulSoup(downloaded, 'html.parser')
            title = soup.title.string if soup.title else "Extracted News Article"
            if extracted_text and len(extracted_text) > 80:
                return title.strip(), extracted_text.strip()
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string if soup.title else "Extracted News Article"
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        text = " ".join(paragraphs)
        return title.strip(), text[:4000]
    except Exception as e:
        return None, str(e)

# ----------------- GEMINI AI FORENSIC AUDIT -----------------
def run_gemini_audit(headline, body, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert investigative journalist, fact-checker, and forensic NLP linguist.
    Audit the following news claim/article for authenticity, manipulation, factual grounding, and rhetoric:

    ARTICLE HEADLINE / CORE CLAIM:
    {headline}

    ARTICLE CONTENT:
    {body[:3500]}

    Evaluate the content strictly and respond in JSON matching this schema:
    {{
      "verdict": "<GENUINE | SENSATIONALIZED | FAKE>",
      "credibility_score": <integer from 0 to 100>,
      "verdict_summary": "<2-3 sentence clear, objective explanation explaining the score and verdict>",
      "key_claims_extracted": ["<Atomic claim 1>", "<Atomic claim 2>"],
      "manipulative_phrases": ["<Specific suspicious, emotionally charged, or clickbait phrases found in text>"],
      "fallacies_and_biases": [
        {{
          "name": "<Name of Logical Fallacy / Cognitive Bias, e.g. Appeal to Emotion, Cherry-Picking, False Dilemma, Anonymous Authority>",
          "explanation": "<Short explanation of how this technique was used in the article>"
        }}
      ],
      "verification_search_query": "<An optimal 4-6 word search query to verify this story on Google/Reuters/AP>"
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    return json.loads(response.text)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("VeritasLens AI")
    st.caption("Powered by Google Gemini 2.5 Flash")
    
    api_key_input = st.text_input(
        "Enter Gemini API Key", 
        type="password", 
        placeholder="AIzaSy...",
        help="Get a free key from Google AI Studio (aistudio.google.com)"
    )
    
    st.divider()
    st.markdown("### 🧪 Quick Demo Presets")
    preset_choice = st.selectbox(
        "Load test scenario:",
        ["Select a scenario...", "1. Verified Science & Space News", "2. Fabricated Miracle Cure", "3. Sensational Clickbait"]
    )
    
    st.divider()
    st.markdown("### 🧬 AI Inspection Pipeline")
    st.write("• **Article Scraper:** Strips ads, scripts & boilerplates")
    st.write("• **Neural Verification:** Gemini 2.5 Flash Reasoning")
    st.write("• **Forensic Layer:** Bias & Cognitive Fallacy Radar")

# Preset Samples
default_title = "ISRO conducts successful test of indigenous cryogenic stage"
default_body = "The Indian Space Research Organisation (ISRO) successfully conducted the hot test of the CE-20 cryogenic engine. The engine was tested in a multi-restart configuration at the Propulsion Complex in Mahendragiri, meeting all performance benchmarks."

if preset_choice == "2. Fabricated Miracle Cure":
    default_title = "SHOCKING secret cure leaked online cures all illnesses in 24 hours!"
    default_body = "URGENT! Corrupt doctors are furious after a leaked miracle herb exposes the entire medical industry. This secret remedy cures all diseases overnight and billionaires are actively trying to ban it from the public!"
elif preset_choice == "3. Sensational Clickbait":
    default_title = "Mind-blowing tax change that will shock every citizen tomorrow"
    default_body = "Authorities have announced a minor procedural update in tax documentation filing dates, but financial bloggers claim this unexpected move will alter personal budgeting plans across the country."

# ----------------- MAIN UI -----------------
st.title("🛡️ VeritasLens: Autonomous AI Claim Forensic Engine")
st.markdown("Paste a **Live News URL** or enter text manually to perform a deep neural authenticity audit.")

tab_url, tab_text = st.tabs(["🌐 Extract from Live News URL", "✍️ Custom Text Input"])

target_title = default_title
target_body = default_body

with tab_url:
    col_u1, col_u2 = st.columns([4, 1])
    with col_u1:
        input_url = st.text_input("Paste News Article URL", placeholder="https://www.thehindu.com/news/... or BBC / NDTV link")
    with col_u2:
        fetch_btn = st.button("Fetch & Parse", use_container_width=True)
        
    if fetch_btn and input_url:
        with st.spinner("Scraping clean article body from source..."):
            extracted_title, extracted_body = scrape_article(input_url)
            if extracted_title and len(extracted_body) > 40:
                target_title = extracted_title
                target_body = extracted_body
                st.success(f"Extracted: **{extracted_title}**")
            else:
                st.error("Could not extract clean text from this URL. Try pasting manually in the next tab.")

with tab_text:
    target_title = st.text_input("Headline / Key Assertion", value=target_title)
    target_body = st.text_area("Article Body / Summary", height=160, value=target_body)

run_audit_btn = st.button("🚀 Run Comprehensive Gemini AI Audit", type="primary", use_container_width=True)

# ----------------- RESULTS DASHBOARD -----------------
if run_audit_btn:
    if not api_key_input:
        st.error("⚠️ Please enter your Gemini API Key in the left sidebar to run the AI verification.")
    elif not target_body.strip():
        st.error("⚠️ Please enter an article body or scrape a valid URL first.")
    else:
        with st.spinner("Gemini 2.5 Flash is analyzing claims, rhetoric, and logical validity..."):
            try:
                result = run_gemini_audit(target_title, target_body, api_key_input)
                
                verdict = result.get("verdict", "SENSATIONALIZED").upper()
                score = result.get("credibility_score", 50)
                summary = result.get("verdict_summary", "Audit completed.")
                claims = result.get("key_claims_extracted", [])
                buzzwords = result.get("manipulative_phrases", [])
                fallacies = result.get("fallacies_and_biases", [])
                search_query = result.get("verification_search_query", target_title)
                
                st.write("---")
                col_left, col_right = st.columns([1.15, 0.85], gap="large")
                
                with col_left:
                    # Dynamic Verdict Banner
                    if verdict == "GENUINE":
                        st.markdown('<div class="verdict-banner verdict-real">✅ AI VERDICT: VERIFIED / CREDIBLE CONTENT</div>', unsafe_allow_html=True)
                    elif verdict == "FAKE":
                        st.markdown('<div class="verdict-banner verdict-fake">🚨 AI VERDICT: UNRELIABLE / FABRICATED CLAIM</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="verdict-banner verdict-sensational">⚠️ AI VERDICT: SENSATIONALIZED / MISLEADING</div>', unsafe_allow_html=True)
                        
                    st.markdown("### 📋 AI Forensic Reasoning")
                    st.info(summary)
                    
                    st.markdown("### 🎯 Core Factual Claims Identified")
                    for c in claims:
                        st.markdown(f'<div class="claim-box">📌 {c}</div>', unsafe_allow_html=True)
                        
                    st.markdown("### 🧬 Cognitive Bias & Fallacy Matrix")
                    if fallacies:
                        for item in fallacies:
                            f_name = item.get("name", "Cognitive Bias")
                            f_desc = item.get("explanation", "")
                            st.markdown(f"""
                            <div class="bias-card">
                                <strong>⚠️ {f_name}</strong><br>
                                <small style="opacity:0.9;">{f_desc}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("No logical fallacies or manipulative biases detected.")

                with col_right:
                    st.markdown("### 📊 Credibility Score")
                    st.metric(label="Calculated Authenticity Index", value=f"{score} / 100")
                    st.progress(score / 100)
                    
                    st.write("---")
                    st.markdown("### 🚩 Manipulative / Deceptive Phrases")
                    if buzzwords:
                        for b in buzzwords:
                            st.markdown(f'<span class="tag-badge">⚠️ "{b}"</span>', unsafe_allow_html=True)
                    else:
                        st.success("Clean linguistic structure. No suspicious phrases flagged.")
                        
                    st.write("---")
                    st.markdown("### 🔍 Live Fact-Check Triangulation")
                    st.write("Cross-verify the core assertions on global databases:")
                    
                    factcheck_url = f"https://toolbox.google.com/factcheck/explorer/search/{requests.utils.quote(search_query)}"
                    st.link_button("🌐 Check Google Fact Check Explorer", factcheck_url, use_container_width=True)
                    
                    google_news_url = f"https://news.google.com/search?q={requests.utils.quote(search_query)}"
                    st.link_button("📰 Cross-Reference Live News Outlets", google_news_url, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error during AI analysis: {str(e)}")

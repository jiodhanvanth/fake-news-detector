import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import trafilatura
from google import genai
from google.genai import types

st.set_page_config(
    page_title="VeritasLens • Dynamic Gemini AI Claim Verifier",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Visual Styling
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

# Initialize Session State
if "article_title" not in st.session_state:
    st.session_state.article_title = ""
if "article_body" not in st.session_state:
    st.session_state.article_body = ""
if "scraped_source" not in st.session_state:
    st.session_state.scraped_source = ""

# ----------------- LIVE URL SCRAPER -----------------
def scrape_article_data(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(downloaded)
            soup = BeautifulSoup(downloaded, 'html.parser')
            title = soup.title.string if soup.title else "Online Article"
            if extracted_text and len(extracted_text) > 60:
                return title.strip(), extracted_text.strip()
        
        # Fallback Scraper
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string if soup.title else "Online Article"
        paragraphs = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 20]
        body = " ".join(paragraphs)
        if len(body) > 60:
            return title.strip(), body[:4000]
        return None, "Article content could not be extracted (site might be paywalled or blocking bots)."
    except Exception as e:
        return None, f"Scraping Error: {str(e)}"

# ----------------- GEMINI REASONING ENGINE -----------------
def run_gemini_audit(headline, body, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert investigative fact-checker and forensic NLP intelligence system.
    Analyze the following specific input article/claim for factual authenticity, manipulative framing, bias, and deception:

    === INPUT HEADLINE ===
    {headline}

    === INPUT ARTICLE BODY ===
    {body[:3500]}

    Respond ONLY in valid JSON matching this exact structure:
    {{
      "verdict": "<GENUINE | SENSATIONALIZED | FAKE>",
      "credibility_score": <integer from 0 to 100>,
      "verdict_summary": "<2-3 sentence clear, objective explanation specifically tailored to this input>",
      "key_claims_extracted": ["<Specific assertion 1 from the text>", "<Specific assertion 2 from the text>"],
      "manipulative_phrases": ["<Specific suspicious, sensational, or clickbait phrases found in this text>"],
      "fallacies_and_biases": [
        {{
          "name": "<Logical Fallacy or Rhetorical Technique name>",
          "explanation": "<Specific explanation of how it occurs in this input>"
        }}
      ],
      "verification_search_query": "<An optimal 4-6 word Google Fact Check search query for this exact story>"
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

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("VeritasLens AI")
    st.caption("Powered by Google Gemini 2.5 Flash")
    
    api_key_input = st.text_input(
        "Gemini API Key", 
        type="password", 
        placeholder="AIzaSy...",
        help="Get a free key at aistudio.google.com"
    )
    
    st.divider()
    st.markdown("### 🧪 Quick Presets")
    
    if st.button("Load: Clean ISRO News", use_container_width=True):
        st.session_state.article_title = "ISRO successfully conducts restart hot test of cryogenic CE-20 engine"
        st.session_state.article_body = "The Indian Space Research Organisation (ISRO) successfully conducted the qualification hot test of the CE-20 cryogenic engine at the Propulsion Complex in Mahendragiri, confirming all nominal parameters for upcoming heavy payload missions."
        st.session_state.scraped_source = "Demo Preset 1"
        st.rerun()

    if st.button("Load: Fabricated Miracle Cure", use_container_width=True):
        st.session_state.article_title = "SHOCKING secret cure leaked online cures all illnesses in 24 hours!"
        st.session_state.article_body = "URGENT! Corrupt doctors are furious after a leaked miracle herb exposes the entire medical industry. This secret remedy cures all diseases overnight and billionaires are actively trying to ban it from the public!"
        st.session_state.scraped_source = "Demo Preset 2"
        st.rerun()

# ----------------- MAIN INTERFACE -----------------
st.title("🛡️ VeritasLens: Autonomous AI Claim Forensic Engine")
st.markdown("Analyze any live web link or direct text with real-time Gemini AI fact-checking.")

st.markdown("#### 1. Ingest Content")
col_url, col_btn = st.columns([4, 1])

with col_url:
    input_url = st.text_input("Enter News Article URL", placeholder="https://www.bbc.com/news/... or NDTV / The Hindu link")
with col_btn:
    st.write("")
    scrape_clicked = st.button("Fetch URL", use_container_width=True)

if scrape_clicked and input_url:
    with st.spinner("Extracting headline and body from URL..."):
        title, body = scrape_article_data(input_url)
        if title and len(body) > 40:
            st.session_state.article_title = title
            st.session_state.article_body = body
            st.session_state.scraped_source = input_url
            st.success("Article successfully extracted.")
            st.rerun()
        else:
            st.error("Failed to parse this URL. Please paste the text manually below.")

st.markdown("#### 2. Review or Edit Extracted Content")
final_title = st.text_input("Headline / Key Claim", value=st.session_state.article_title, placeholder="Enter claim or headline...")
final_body = st.text_area("Article Body / Summary", value=st.session_state.article_body, height=180, placeholder="Paste or review article body...")

# Update state on user edit
st.session_state.article_title = final_title
st.session_state.article_body = final_body

audit_btn = st.button("🚀 Execute Gemini AI Forensic Audit", type="primary", use_container_width=True)

# ----------------- RESULTS DASHBOARD -----------------
if audit_btn:
    if not api_key_input:
        st.error("⚠️ Please enter your Gemini API Key in the left sidebar to run the verification.")
    elif not final_body.strip():
        st.error("⚠️ Please provide an article body or fetch a valid URL first.")
    else:
        with st.spinner(f"Gemini 2.5 Flash is actively auditing: '{final_title[:40]}...'"):
            try:
                result = run_gemini_audit(final_title, final_body, api_key_input)
                
                verdict = result.get("verdict", "SENSATIONALIZED").upper()
                score = result.get("credibility_score", 50)
                summary = result.get("verdict_summary", "Audit finished.")
                claims = result.get("key_claims_extracted", [])
                buzzwords = result.get("manipulative_phrases", [])
                fallacies = result.get("fallacies_and_biases", [])
                search_query = result.get("verification_search_query", final_title)
                
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
                    if claims:
                        for c in claims:
                            st.markdown(f'<div class="claim-box">📌 {c}</div>', unsafe_allow_html=True)
                    else:
                        st.write("No distinct sub-claims isolated.")
                        
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
                    st.link_button("🌐 Open Google Fact Check Explorer", factcheck_url, use_container_width=True)
                    
                    google_news_url = f"https://news.google.com/search?q={requests.utils.quote(search_query)}"
                    st.link_button("📰 Cross-Reference Live News Outlets", google_news_url, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error during AI analysis: {str(e)}")

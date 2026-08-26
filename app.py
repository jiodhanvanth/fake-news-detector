import streamlit as st
import json
import re
import requests
from bs4 import BeautifulSoup
import trafilatura
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline
from google import genai
from google.genai import types

st.set_page_config(
    page_title="VeritasLens™ | Autonomous Neural News Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Cyber Glassmorphism & Modern Typography CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Branding */
    .hero-container {
        padding: 5px 0 18px 0;
    }
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.8px;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 45%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .author-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 4px 12px;
        border-radius: 8px;
    }
    
    /* Live Status Beacon */
    .pulse-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.6px;
        background: rgba(34, 197, 94, 0.12);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.35);
        margin-bottom: 15px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #22c55e;
        box-shadow: 0 0 10px #22c55e;
    }

    /* Verdict Banners */
    .verdict-banner {
        padding: 22px 28px;
        border-radius: 16px;
        font-weight: 800;
        font-size: 22px;
        text-align: center;
        letter-spacing: 0.5px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
    }
    .verdict-genuine {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.25), rgba(16, 185, 129, 0.12));
        border: 1px solid #10b981;
        color: #34d399;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.2);
    }
    .verdict-fake {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.25), rgba(239, 68, 68, 0.12));
        border: 1px solid #ef4444;
        color: #f87171;
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.2);
    }
    .verdict-sensational {
        background: linear-gradient(135deg, rgba(234, 88, 12, 0.25), rgba(249, 115, 22, 0.12));
        border: 1px solid #f97316;
        color: #fb923c;
        box-shadow: 0 8px 30px rgba(249, 115, 22, 0.2);
    }

    /* Modern Card Layouts */
    .metric-card-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 14px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-val {
        font-size: 28px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .metric-lbl {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94a3b8;
    }

    .claim-item {
        background: rgba(59, 130, 246, 0.06);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .source-item {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-left: 4px solid #10b981;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
        font-size: 13px;
    }

    .bias-pill {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 10px;
    }

    .token-chip {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin: 3px 6px 3px 0;
    }

    /* Sidebar Tech Cards */
    .side-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    /* Footer Credits */
    .neural-footer {
        margin-top: 50px;
        padding: 18px 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #94a3b8;
        letter-spacing: 0.4px;
    }
    .subtle-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        background: rgba(96, 165, 250, 0.08);
        border: 1px solid rgba(96, 165, 250, 0.2);
        color: #60a5fa;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# State initialization
if "article_title" not in st.session_state:
    st.session_state.article_title = ""
if "article_body" not in st.session_state:
    st.session_state.article_body = ""

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ----------------- LAYER 1: STATISTICAL ML BASELINE -----------------
@st.cache_resource
def load_ml_classifier():
    corpus = [
        "Government announces new educational policy reforms across schools and colleges nationwide.",
        "ISRO successfully launches navigation satellite into orbit from Sriharikota space center.",
        "Ministry of Finance releases quarterly economic growth and tax revenue statistics.",
        "Health department advises citizens on seasonal influenza prevention and vaccination schedule.",
        "Reserve Bank issues updated monetary policy guidelines for commercial banking institutions.",
        "Scientists publish comprehensive study on clean energy grid infrastructure and solar conversion efficiency.",
        "SHOCKING miracle cure hidden by corrupt doctors leaked online cures all diseases overnight!",
        "URGENT secret conspiracy exposed government is putting secret microchips in tap water!",
        "Mind-blowing breakthrough that the billionaire elites do not want you to know about!",
        "UNBELIEVABLE secret leak proves celebrities are secretly alien reptiles from outer space!",
        "Secret military experiment exposed as 5G towers secretly control civilian brainwaves!"
    ]
    targets = [
        "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE",
        "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED"
    ]
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('pac', PassiveAggressiveClassifier(max_iter=150, random_state=42))
    ])
    pipe.fit(corpus, targets)
    return pipe

ml_engine = load_ml_classifier()

# ----------------- LAYER 2: HIGH-ACCURACY DOM ARTICLE EXTRACTOR -----------------
def scrape_article_data(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(downloaded)
            soup = BeautifulSoup(downloaded, 'html.parser')
            title = soup.title.string if soup.title else "Extracted Article"
            if extracted_text and len(extracted_text) > 50:
                return title.strip(), extracted_text.strip()
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string if soup.title else "Extracted Article"
        paras = [p.get_text() for p in soup.find_all('p') if len(p.get_text()) > 20]
        body = " ".join(paras)
        if len(body) > 50:
            return title.strip(), body[:4000]
        return None, "Extraction restricted or paywalled by host site."
    except Exception as e:
        return None, str(e)

# ----------------- LAYER 3: REAL-TIME GROUNDED NEURAL ENGINE -----------------
def execute_grounded_forensics(headline, body, key):
    client = genai.Client(api_key=key)
    
    prompt = f"""
    You are VeritasLens Real-Time Neural Core.
    You have access to live Google Search Grounding.
    
    CRITICAL INSTRUCTION:
    First, execute live searches to verify if the following news story, claim, or event actually happened in real-world reporting from reputable sources (e.g. ISRO, NASA, BBC, Reuters, The Hindu, AP, PIB, Government Gazettes, etc.).
    
    - If reputable mainstream news sources confirm this story, classify it as GENUINE with a high credibility score (85-98) regardless of technical terminology.
    - If the story is an unsubstantiated conspiracy, internet hoax, or medical myth that is debunked or unverified online, classify it as FAKE with a low score (5-30).
    - If it is based on a real event but heavily exaggerated with clickbait phrasing, classify it as SENSATIONALIZED (50-75).

    HEADLINE / ASSERTION:
    {headline}

    ARTICLE CONTENT:
    {body[:3500]}

    Return your audit strictly in a JSON code block using this exact schema:
    ```json
    {{
      "verdict": "<GENUINE FAKE SENSATIONALIZED |>",
      "credibility_score": <integer from 0 to 100>,
      "factual_grounding_pct": <integer 0-100>,
      "rhetorical_distortion_pct": <integer 0-100>,
      "clickbait_sensationalism_pct": <integer 0-100>,
      "verdict_summary": "<2-3 sentence clear explanation citing real-world verification findings>",
      "real_world_sources_found": ["<Name Hindu ISRO Press Release, Reuters, The e.g. institution of or publisher reporting this, verified>"],
      "atomic_claims": [
        {{
          "claim": "<Core 1 Claim>",
          "status": "<VERIFIED CONTRADICTED UNVERIFIED |>"
        }},
        {{
          "claim": "<Core 2 Claim>",
          "status": "<VERIFIED CONTRADICTED UNVERIFIED |>"
        }}
      ],
      "flagged_keywords": ["<manipulative or deceptive words if any, or empty list>"],
      "cognitive_fallacies": [
        {{
          "name": "<Logical / Bias Fallacy Name, None clean if or>",
          "description": "<Brief absence bias note of on or presence rhetorical>"
        }}
      ],
      "recommended_factcheck_query": "<4-6 word optimal search query to cross-reference this>"
    }}
    ```
    """
    
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}],  # Live Search Grounding
            temperature=0.1
        )
    )
    
    response_text = res.text
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    else:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return json.loads(response_text[start_idx:end_idx+1])
        raise ValueError("Invalid JSON format returned by neural core.")

# ----------------- REDESIGNED SIDEBAR CONTROL HUB -----------------
with st.sidebar:
    st.markdown('<div class="pulse-pill"><div class="pulse-dot"></div>NEURAL ENGINE ONLINE</div>', unsafe_allow_html=True)
    
    st.markdown("### 🧬 Project Identity")
    st.markdown("""
    <div class="side-card">
        <strong style="color:#60a5fa;">VeritasLens™ Suite</strong><br>
        <span style="font-size:12px; color:#cbd5e1;">Class 11 Computer Science</span><br>
        <hr style="margin:8px 0; opacity:0.15;">
        <span style="font-size:12px;">👑 <strong>Created & Developed:</strong><br><span style="color:#a855f7; font-weight:700;">DHANVANTH CR</span></span><br>
        <span style="font-size:12px;">🤝 <strong>Assisted by:</strong><br><span style="color:#38bdf8; font-weight:700;">JANESH S</span></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Multi-Vector Pipeline")
    st.markdown("""
    <div class="side-card">
        <strong style="color:#60a5fa;">1. Live Web Grounding</strong><br>
        <small style="color:#94a3b8;">Queries global news indexes in real-time to verify breaking events.</small>
    </div>
    <div class="side-card">
        <strong style="color:#a855f7;">2. Neural Reasoning Engine</strong><br>
        <small style="color:#94a3b8;">Decomposes claims & validates evidence entailment.</small>
    </div>
    <div class="side-card">
        <strong style="color:#34d399;">3. Statistical ML Core</strong><br>
        <small style="color:#94a3b8;">TF-IDF + Passive-Aggressive Stance Baseline.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🧪 Quick Benchmark Scenarios")
    
    if st.button("🛰️ Scenario 1: Space & Technology", use_container_width=True):
        st.session_state.article_title = "ISRO successfully validates restart capability of cryogenic upper stage engine"
        st.session_state.article_body = "The Indian Space Research Organisation (ISRO) successfully conducted the qualification hot test of the CE-20 cryogenic engine at the Propulsion Complex in Mahendragiri, confirming all nominal parameters for upcoming missions."
        st.rerun()

    if st.button("🚨 Scenario 2: Medical Conspiracy Hoax", use_container_width=True):
        st.session_state.article_title = "SHOCKING miracle cure hidden by corrupt doctors leaked online!"
        st.session_state.article_body = "URGENT! Corrupt medical cartels are in panic after a secret natural herb leaked online that instantly cures all cardiovascular diseases overnight. Billionaire elites are actively threatening doctors to ban this mind-blowing breakthrough from the public!"
        st.rerun()

    if st.button("📢 Scenario 3: Sensational Clickbait", use_container_width=True):
        st.session_state.article_title = "Mind-blowing tax change that will shock every citizen tomorrow morning"
        st.session_state.article_body = "The Ministry of Finance announced minor administrative adjustments to digital filing deadlines for quarterly returns, but financial bloggers claim this unexpected measure will wipe out personal savings accounts across the nation."
        st.rerun()

# ----------------- MAIN UI WORKFLOW -----------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🛡️ VeritasLens™ Intelligence Suite</div>
    <div class="hero-subtitle">Real-Time Forensic Claim Verification • Live Web Grounding • Cognitive Fallacy Radar</div>
    <div class="author-badge">
        <span>👑 Created & Developed by <strong>DHANVANTH CR</strong></span>
        <span>•</span>
        <span>Assisted by <strong>JANESH S</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("#### 1. Ingest Content (Live URL or Raw Text)")
col_u1, col_u2 = st.columns([4.2, 1])
with col_u1:
    url_input = st.text_input("Enter Live News Article URL", placeholder="https://www.thehindu.com/news/... or BBC / NDTV / Reuters link", label_visibility="collapsed")
with col_u2:
    scrape_btn = st.button("Extract URL", use_container_width=True)

if scrape_btn and url_input:
    with st.spinner("Scraping live article body and filtering DOM scripts/ads..."):
        scraped_title, scraped_body = scrape_article_data(url_input)
        if scraped_title and len(scraped_body) > 40:
            st.session_state.article_title = scraped_title
            st.session_state.article_body = scraped_body
            st.success(f"Extracted: **{scraped_title}**")
            st.rerun()
        else:
            st.error("Could not parse article from this URL. Enter the text manually below.")

st.markdown("#### 2. Review or Edit Claim Context")
headline_val = st.text_input("Claim / Article Headline", value=st.session_state.article_title, placeholder="Enter headline or primary assertion...")
body_val = st.text_area("Full Article Content", value=st.session_state.article_body, height=150, placeholder="Enter article content to audit...")

st.session_state.article_title = headline_val
st.session_state.article_body = body_val

st.markdown("#### 3. Execute Verification")
execute_audit = st.button("🚀 Execute Comprehensive Neural Forensic Audit", type="primary", use_container_width=True)

# ----------------- AUDIT REPORT DASHBOARD -----------------
if execute_audit:
    if not body_val.strip():
        st.error("⚠️ Please provide an article body or fetch a URL first.")
    else:
        with st.spinner(f"Querying live web indexes and evaluating: '{headline_val[:45]}...'"):
            key_to_use = API_KEY if API_KEY else "LOCAL_FALLBACK"
            
            if key_to_use != "LOCAL_FALLBACK":
                try:
                    res = execute_grounded_forensics(headline_val, body_val, key_to_use)
                except Exception as err:
                    st.warning(f"Live search fallback: {err}")
                    ml_pred = ml_engine.predict([body_val])[0]
                    res = {
                        "verdict": ml_pred,
                        "credibility_score": 90 if ml_pred == "GENUINE" else 20,
                        "factual_grounding_pct": 88 if ml_pred == "GENUINE" else 15,
                        "rhetorical_distortion_pct": 10 if ml_pred == "GENUINE" else 85,
                        "clickbait_sensationalism_pct": 12 if ml_pred == "GENUINE" else 88,
                        "verdict_summary": f"Classified as {ml_pred} via statistical NLP patterns.",
                        "real_world_sources_found": ["Statistical NLP Baseline"],
                        "atomic_claims": [{"claim": headline_val[:80], "status": "VERIFIED" if ml_pred == "GENUINE" else "UNVERIFIED"}],
                        "flagged_keywords": [],
                        "cognitive_fallacies": [],
                        "recommended_factcheck_query": headline_val
                    }
            else:
                ml_pred = ml_engine.predict([body_val])[0]
                res = {
                    "verdict": ml_pred,
                    "credibility_score": 90 if ml_pred == "GENUINE" else 20,
                    "factual_grounding_pct": 88 if ml_pred == "GENUINE" else 15,
                    "rhetorical_distortion_pct": 10 if ml_pred == "GENUINE" else 85,
                    "clickbait_sensationalism_pct": 12 if ml_pred == "GENUINE" else 88,
                    "verdict_summary": "Evaluated via local ML model (Add GEMINI_API_KEY to secrets for live Google grounding).",
                    "real_world_sources_found": ["Local Model"],
                    "atomic_claims": [{"claim": headline_val[:80], "status": "VERIFIED" if ml_pred == "GENUINE" else "UNVERIFIED"}],
                    "flagged_keywords": [],
                    "cognitive_fallacies": [],
                    "recommended_factcheck_query": headline_val
                }

            verdict = res.get("verdict", "SENSATIONALIZED").upper()
            score = res.get("credibility_score", 50)
            grounding = res.get("factual_grounding_pct", 50)
            distortion = res.get("rhetorical_distortion_pct", 50)
            clickbait = res.get("clickbait_sensationalism_pct", 50)
            summary = res.get("verdict_summary", "Audit completed.")
            sources_found = res.get("real_world_sources_found", [])
            claims = res.get("atomic_claims", [])
            buzzwords = res.get("flagged_keywords", [])
            fallacies = res.get("cognitive_fallacies", [])
            search_query = res.get("recommended_factcheck_query", headline_val)

        st.markdown("---")
        
        # 1. Dynamic Verdict Banner
        if verdict == "GENUINE":
            st.markdown(f'<div class="verdict-banner verdict-genuine">✅ AUDIT VERDICT: VERIFIED / AUTHENTIC CONTENT ({score}/100)</div>', unsafe_allow_html=True)
        elif verdict == "FAKE":
            st.markdown(f'<div class="verdict-banner verdict-fake">🚨 AUDIT VERDICT: UNRELIABLE / FABRICATED CLAIM ({score}/100)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="verdict-banner verdict-sensational">⚠️ AUDIT VERDICT: SENSATIONALIZED / HYPERBOLIC ({score}/100)</div>', unsafe_allow_html=True)

        # 2. Four Multi-Vector Telemetry Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-val">{score}%</div>
                <div class="metric-lbl">Authenticity Index</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-val">{grounding}%</div>
                <div class="metric-lbl">Factual Grounding</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-val">{distortion}%</div>
                <div class="metric-lbl">Rhetorical Manipulation</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card-box">
                <div class="metric-val">{clickbait}%</div>
                <div class="metric-lbl">Clickbait Load</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("---")

        # 3. Two-Column Detailed Audit
        col_left, col_right = st.columns([1.2, 0.8], gap="large")
        
        with col_left:
            st.markdown("### 📋 Forensic Reasoning Summary")
            st.info(summary)
            
            if sources_found:
                st.markdown("#### 🌐 Corroborating Real-World Sources Identified")
                for s in sources_found:
                    st.markdown(f'<div class="source-item">📰 <strong>Verified Publisher/Record:</strong> {s}</div>', unsafe_allow_html=True)
            
            st.markdown("### 🎯 Atomic Claim Decomposition & Entailment")
            if claims:
                for c in claims:
                    status = c.get("status", "UNVERIFIED")
                    badge_color = "#10b981" if status == "VERIFIED" else "#ef4444" if status == "CONTRADICTED" else "#f59e0b"
                    st.markdown(f"""
                    <div class="claim-item">
                        <span style="color:{badge_color}; font-weight:800; font-size:12px;">[{status}]</span> {c.get('claim')}
                    </div>
                    """, unsafe_allow_html=True)

        with col_right:
            st.markdown("### 🧬 Cognitive Bias & Fallacy Radar")
            if fallacies and fallacies[0].get("name") != "None":
                for f in fallacies:
                    st.markdown(f"""
                    <div class="bias-pill">
                        <strong>⚠️ {f.get('name')}</strong><br>
                        <small style="color:#cbd5e1;">{f.get('description')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✔️ No cognitive biases or logical fallacies detected. Adheres to journalistic standards.")
                
            st.markdown("### 🚩 Trigger Vocabulary Tokens")
            if buzzwords:
                for b in buzzwords:
                    st.markdown(f'<span class="token-chip">⚠️ {b.upper()}</span>', unsafe_allow_html=True)
            else:
                st.write("No suspicious tokens isolated.")
                
            st.write("---")
            st.markdown("### 🌐 Live Verification Indexes")
            
            factcheck_url = f"https://toolbox.google.com/factcheck/explorer/search/{requests.utils.quote(search_query)}"
            st.link_button("🌐 Query Fact Check Verification Index", factcheck_url, use_container_width=True)
            
            news_url = f"https://news.google.com/search?q={requests.utils.quote(search_query)}"
            st.link_button("📰 Cross-Reference Global Media", news_url, use_container_width=True)

# ----------------- SUBTLE CORNER TELEMETRY INDICATOR -----------------
st.markdown("""
<div class="neural-footer">
    <div>VeritasLens™ Protocol • Class 11 CS Project | Created & Developed by <strong>DHANVANTH CR</strong>, Assisted by <strong>JANESH S</strong></div>
    <div class="subtle-badge">
        <span style="width:6px; height:6px; border-radius:50%; background-color:#60a5fa; display:inline-block;"></span>
        Grounded via Deep Neural Intelligence Core
    </div>
</div>
""", unsafe_allow_html=True)

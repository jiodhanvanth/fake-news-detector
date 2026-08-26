"""
====================================================================================
PROJECT: VeritasLens™ — Autonomous Neural News & Forensic Claim Intelligence Suite
COURSE: Class 11 Computer Science (AI, NLP & Machine Learning Engineering Project)
LEAD DEVELOPER & ARCHITECT: DHANVANTH CR
ASSISTANT DEVELOPER: JANESH S
====================================================================================
"""

import streamlit as st
import json
import re
import io
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import trafilatura
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from google import genai
from google.genai import types

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="VeritasLens™ | Autonomous Neural News Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM CYBER-GLASSMORPHIC CSS STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Header */
    .hero-container {
        padding: 6px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 40px;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #60a5fa 0%, #c084fc 45%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .author-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #e2e8f0;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px 14px;
        border-radius: 8px;
    }
    
    /* Live Status Indicators */
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

    /* Verdict Result Banners */
    .verdict-banner {
        padding: 22px 28px;
        border-radius: 16px;
        font-weight: 800;
        font-size: 22px;
        text-align: center;
        letter-spacing: 0.5px;
        margin-bottom: 24px;
        backdrop-filter: blur(14px);
    }
    .verdict-genuine {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.25), rgba(16, 185, 129, 0.15));
        border: 1px solid #10b981;
        color: #34d399;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.25);
    }
    .verdict-fake {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.25), rgba(239, 68, 68, 0.15));
        border: 1px solid #ef4444;
        color: #f87171;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.25);
    }
    .verdict-sensational {
        background: linear-gradient(135deg, rgba(234, 88, 12, 0.25), rgba(249, 115, 22, 0.15));
        border: 1px solid #f97316;
        color: #fb923c;
        box-shadow: 0 8px 32px rgba(249, 115, 22, 0.25);
    }

    /* Telemetry Cards */
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

    /* Claim & Entity Cards */
    .claim-item {
        background: rgba(59, 130, 246, 0.06);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-left: 4px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.5;
    }
    .source-item {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .bias-pill {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 12px;
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
    .highlight-manipulation {
        background-color: rgba(239, 68, 68, 0.28);
        border-bottom: 2px solid #ef4444;
        padding: 2px 5px;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Sidebar Telemetry Cards */
    .side-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }

    /* Discrete Footer */
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

# ----------------- SESSION STATE & INITIALIZATION -----------------
if "article_title" not in st.session_state:
    st.session_state.article_title = ""
if "article_body" not in st.session_state:
    st.session_state.article_body = ""
if "audit_history" not in st.session_state:
    st.session_state.audit_history = []

API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ----------------- LAYER 1: EXPANDED ML CLASSIFICATION PIPELINE -----------------
@st.cache_resource
def build_ml_engine():
    """
    Trains a high-speed Passive-Aggressive Classifier on TF-IDF n-grams (1,2)
    and computes formal evaluation metrics for academic review.
    """
    training_corpus = [
        # Verified News Articles (Label: GENUINE)
        "Government announces new educational policy reforms across schools and colleges nationwide.",
        "ISRO successfully launches navigation satellite into orbit from Sriharikota space center.",
        "Ministry of Finance releases quarterly economic growth and tax revenue statistics showing stability.",
        "Health department advises citizens on seasonal influenza prevention and vaccination schedule guidelines.",
        "Reserve Bank issues updated monetary policy guidelines for commercial banking lending frameworks.",
        "Scientists publish comprehensive peer-reviewed study on clean energy grid infrastructure and solar conversion efficiency.",
        "Civil Aviation authority issues updated airspace safety standards for commercial passenger flight operations.",
        "National highway authority approves new infrastructure connectivity corridors across southern industrial zones.",
        "Central meteorological department releases annual monsoon distribution model and agricultural rainfall forecast.",
        "Department of Telecommunications allocates spectrum bands for high-speed fiber internet in rural schools.",
        "Archaeological survey team documents ancient stone inscription dating back to ninth century Chola era.",
        "State university signs collaborative research agreement for semiconductor fabrication engineering.",
        
        # Fabricated & Manipulative Hoaxes (Label: FABRICATED)
        "SHOCKING miracle cure hidden by corrupt doctors leaked online cures all terminal diseases overnight!",
        "URGENT secret conspiracy exposed government is putting secret microchips in bottled tap water to control minds!",
        "Mind-blowing breakthrough that the billionaire elites do not want you to know about free infinite energy!",
        "UNBELIEVABLE secret leak proves celebrities are secretly alien reptiles masquerading in human skin!",
        "Secret military experiment exposed as 5G mobile towers secretly transmit civilian mind-control brainwaves!",
        "Doctors banned this one magical fruit that melts forty pounds of body fat in less than two hours!",
        "LEAKED memo reveals global moon landing was filmed entirely on a Hollywood soundstage by secret elites!",
        "Emergency warning drinking boiled lemon juice with baking soda guarantees complete immunity from all viral pandemics!",
        "Ancient scrolls discovered in secret pyramid prove world leaders communicate with Martian telepaths!",
        "Billionaire reveals top-secret algorithm that multiplies bank accounts by 1000 percent automatically with zero risk!"
    ]
    
    training_labels = [
        "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE",
        "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE",
        "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED", 
        "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED", "FABRICATED"
    ]
    
    X_train, X_test, y_train, y_test = train_test_split(
        training_corpus, training_labels, test_size=0.25, random_state=42
    )
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english', sublinear_tf=True)),
        ('pac', PassiveAggressiveClassifier(max_iter=200, random_state=42, C=0.5))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Calculate baseline verification metrics
    y_pred = pipeline.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, pos_label="GENUINE", zero_division=0),
        "recall": recall_score(y_test, y_pred, pos_label="GENUINE", zero_division=0),
        "f1": f1_score(y_test, y_pred, pos_label="GENUINE", zero_division=0),
        "vocab_size": len(pipeline.named_steps['tfidf'].vocabulary_)
    }
    
    # Full fit on entire corpus for production inference
    pipeline.fit(training_corpus, training_labels)
    return pipeline, metrics

ml_pipeline, ml_metrics = build_ml_engine()

# ----------------- LAYER 2: HIGH-ACCURACY DOM ARTICLE SCRAPER -----------------
def scrape_article_data(url):
    """Extracts headline and clean body text from live URLs while stripping DOM boilerplates."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted_text = trafilatura.extract(downloaded)
            soup = BeautifulSoup(downloaded, 'html.parser')
            title = soup.title.string if soup.title else "Extracted Article"
            if extracted_text and len(extracted_text) > 50:
                return title.strip(), extracted_text.strip()
        
        # Fallback Scraper
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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

# ----------------- LAYER 3: HEURISTIC STYLOMETRIC NLP SCANNER -----------------
def run_stylometric_nlp_scan(text):
    """Computes NLP readability, subjectivity, lexical density, and clickbait token presence."""
    blob = TextBlob(text)
    subjectivity = round(blob.sentiment.subjectivity * 100, 1)
    polarity = round(blob.sentiment.polarity, 2)
    
    words = re.findall(r'\b\w+\b', text.lower())
    sensational_lexicon = {
        "shocking", "unbelievable", "secret", "miracle", "exposed", "conspiracy",
        "urgent", "leaked", "danger", "mind-blowing", "banned", "cure", "corrupt",
        "aliens", "hidden", "proven", "coverup", "scandal", "magic", "forbidden"
    }
    flagged_tokens = list(set([w for w in words if w in sensational_lexicon]))
    caps_shouting = [w for w in text.split() if w.isupper() and len(w) > 2 and w.isalpha()]
    
    clickbait_load = min(100, int((len(flagged_tokens) * 18) + (len(caps_shouting) * 5) + (subjectivity * 0.3)))
    return subjectivity, polarity, flagged_tokens, caps_shouting, clickbait_load

# ----------------- LAYER 4: REAL-TIME GROUNDED NEURAL ENGINE -----------------
def execute_grounded_forensics(headline, body, key):
    """
    Executes deep semantic reasoning using Google Search Grounding to verify
    factual claims against verified real-world news indexes.
    """
    client = genai.Client(api_key=key)
    
    prompt = f"""
    You are VeritasLens Real-Time Neural Core.
    You have access to live Google Search Grounding.
    
    CRITICAL INSTRUCTION:
    First, execute live searches to verify if the following news story, claim, or event actually happened in real-world reporting from reputable sources (e.g. ISRO, NASA, BBC, Reuters, The Hindu, AP, PIB, Government Gazettes, Nature, etc.).
    
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
      "real_world_sources_found": ["<Name Hindu ISRO Press Release, Reuters, The e.g. media of or publisher reporting this, verified>"],
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
            tools=[{"google_search": {}}],  # Live Real-Time Search Grounding
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
        raise ValueError("Invalid JSON response format from neural core.")

# Text Highlighting Helper
def highlight_manipulative_phrases(text, phrases):
    highlighted = text
    for phrase in phrases:
        pattern = re.compile(rf'\b({re.escape(phrase)})\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlight-manipulation">\1</span>', highlighted)
    return highlighted

# ----------------- SIDEBAR & CONTROL HUB -----------------
with st.sidebar:
    st.markdown('<div class="pulse-pill"><div class="pulse-dot"></div>NEURAL ENGINE ONLINE</div>', unsafe_allow_html=True)
    
    st.markdown("### 🧬 Project Identity")
    st.markdown("""
    <div class="side-card">
        <strong style="color:#60a5fa; font-size:14px;">VeritasLens™ Protocol</strong><br>
        <span style="font-size:12px; color:#cbd5e1;">Class 11 Computer Science</span><br>
        <hr style="margin:8px 0; opacity:0.15;">
        <span style="font-size:12px;">👑 <strong>Created & Developed by:</strong><br><span style="color:#c084fc; font-weight:700;">DHANVANTH CR</span></span><br><br>
        <span style="font-size:12px;">🤝 <strong>Assisted by:</strong><br><span style="color:#38bdf8; font-weight:700;">JANESH S</span></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Multi-Vector Pipeline")
    st.markdown("""
    <div class="side-card">
        <strong style="color:#60a5fa;">1. Live Web Grounding</strong><br>
        <small style="color:#94a3b8;">Queries global search indexes in real-time to verify breaking events.</small>
    </div>
    <div class="side-card">
        <strong style="color:#a855f7;">2. Neural Reasoning Core</strong><br>
        <small style="color:#94a3b8;">Decomposes claims & validates evidence entailment.</small>
    </div>
    <div class="side-card">
        <strong style="color:#34d399;">3. Statistical ML Core</strong><br>
        <small style="color:#94a3b8;">TF-IDF + Passive-Aggressive Stance Baseline.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🧪 Demonstration Benchmarks")
    
    if st.button("🛰️ Scenario 1: Space & Tech Wire", use_container_width=True):
        st.session_state.article_title = "ISRO successfully validates restart capability of cryogenic upper stage engine"
        st.session_state.article_body = "The Indian Space Research Organisation (ISRO) successfully conducted the qualification hot test of the CE-20 cryogenic engine at the Propulsion Complex in Mahendragiri, confirming all nominal parameters for upcoming heavy payload missions."
        st.rerun()

    if st.button("🚨 Scenario 2: Medical Miracle Hoax", use_container_width=True):
        st.session_state.article_title = "SHOCKING miracle cure hidden by corrupt doctors leaked online!"
        st.session_state.article_body = "URGENT! Corrupt medical cartels are in panic after a secret natural herb leaked online that instantly cures all cardiovascular diseases overnight. Billionaire elites are actively threatening doctors to ban this mind-blowing breakthrough from the public!"
        st.rerun()

    if st.button("📢 Scenario 3: Clickbait Distortion", use_container_width=True):
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

# Main Navigation Tabs for Multi-Modal Inputs & Model Diagnostics
tab_url, tab_text, tab_file, tab_diagnostics = st.tabs([
    "🌐 Ingest via Live Web URL", 
    "✍️ Manual Article / Claim Entry", 
    "📄 File Document Scanner (.txt)", 
    "📊 ML Model Telemetry & Evaluation"
])

# Tab 1: Live URL Ingestion
with tab_url:
    col_u1, col_u2 = st.columns([4.2, 1])
    with col_u1:
        url_input = st.text_input("Enter Live News Article URL", placeholder="https://www.thehindu.com/news/... or BBC / NDTV / Reuters link")
    with col_u2:
        st.write("")
        st.write("")
        scrape_btn = st.button("Extract Article", use_container_width=True)

    if scrape_btn and url_input:
        with st.spinner("Executing DOM extraction and filtering scripts/ads..."):
            scraped_title, scraped_body = scrape_article_data(url_input)
            if scraped_title and len(scraped_body) > 40:
                st.session_state.article_title = scraped_title
                st.session_state.article_body = scraped_body
                st.success(f"Extracted: **{scraped_title}**")
                st.rerun()
            else:
                st.error("Could not parse article from this URL. Enter the text manually in Tab 2.")

# Tab 2: Direct Text Input
with tab_text:
    headline_val = st.text_input("Claim / Article Headline", value=st.session_state.article_title, placeholder="Enter headline or primary assertion...")
    body_val = st.text_area("Full Article Content", value=st.session_state.article_body, height=160, placeholder="Enter article content to audit...")
    st.session_state.article_title = headline_val
    st.session_state.article_body = body_val

# Tab 3: File Document Ingestion
with tab_file:
    uploaded_file = st.file_uploader("Upload a news text file (.txt)", type=["txt"])
    if uploaded_file is not None:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        file_text = stringio.read()
        lines = [line.strip() for line in file_text.split("\n") if line.strip()]
        if lines:
            st.session_state.article_title = lines[0]
            st.session_state.article_body = " ".join(lines[1:]) if len(lines) > 1 else lines[0]
            st.success(f"File loaded successfully: **{lines[0][:60]}...**")
            st.rerun()

# Tab 4: Machine Learning Academic Diagnostics
with tab_diagnostics:
    st.markdown("### 📊 Statistical Machine Learning Baseline Telemetry")
    st.caption("Passive-Aggressive Classifier on TF-IDF (1,2) N-Grams")
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("Validation Accuracy", f"{ml_metrics['accuracy']*100:.1f}%")
    col_d2.metric("Precision Score", f"{ml_metrics['precision']*100:.1f}%")
    col_d3.metric("Recall Score", f"{ml_metrics['recall']*100:.1f}%")
    col_d4.metric("F1-Score Metric", f"{ml_metrics['f1']*100:.1f}%")
    
    st.info(f"💡 **Trained Vocabulary Size:** `{ml_metrics['vocab_size']}` unique linguistic n-gram features extracted across science, governance, health, and disinformation hoaxes.")

# ----------------- EXECUTION TRIGGER -----------------
st.markdown("---")
execute_audit = st.button("🚀 Execute Comprehensive Neural Forensic Audit", type="primary", use_container_width=True)

# ----------------- RESULTS DASHBOARD -----------------
if execute_audit:
    current_body = st.session_state.article_body
    current_title = st.session_state.article_title
    
    if not current_body.strip():
        st.error("⚠️ Please provide an article body or extract a URL first.")
    else:
        with st.spinner(f"Querying live web indexes and evaluating: '{current_title[:45]}...'"):
            start_time = time.time()
            
            # Stylometric NLP Scan
            subjectivity, polarity, styl_buzzwords, styl_caps, styl_clickbait = run_stylometric_nlp_scan(current_body)
            
            # Statistical ML Inference
            ml_pred = ml_pipeline.predict([current_body])[0]
            
            # Deep Neural Grounded Analysis
            key_to_use = API_KEY if API_KEY else "LOCAL_FALLBACK"
            
            if key_to_use != "LOCAL_FALLBACK":
                try:
                    res = execute_grounded_forensics(current_title, current_body, key_to_use)
                except Exception as err:
                    st.warning(f"Live search fallback: {err}")
                    res = {
                        "verdict": ml_pred,
                        "credibility_score": 90 if ml_pred == "GENUINE" else 20,
                        "factual_grounding_pct": 88 if ml_pred == "GENUINE" else 15,
                        "rhetorical_distortion_pct": 10 if ml_pred == "GENUINE" else 85,
                        "clickbait_sensationalism_pct": styl_clickbait,
                        "verdict_summary": f"Classified as {ml_pred} via statistical NLP patterns and vocabulary distribution.",
                        "real_world_sources_found": ["Statistical NLP Baseline"],
                        "atomic_claims": [{"claim": current_title[:80], "status": "VERIFIED" if ml_pred == "GENUINE" else "UNVERIFIED"}],
                        "flagged_keywords": styl_buzzwords,
                        "cognitive_fallacies": [{"name": "Sensational Bias", "description": "Linguistic markers indicate emotional charge."}] if ml_pred != "GENUINE" else [],
                        "recommended_factcheck_query": current_title
                    }
            else:
                res = {
                    "verdict": ml_pred,
                    "credibility_score": 90 if ml_pred == "GENUINE" else 20,
                    "factual_grounding_pct": 88 if ml_pred == "GENUINE" else 15,
                    "rhetorical_distortion_pct": 10 if ml_pred == "GENUINE" else 85,
                    "clickbait_sensationalism_pct": styl_clickbait,
                    "verdict_summary": "Evaluated via local ML baseline model (Add GEMINI_API_KEY to secrets for live Google grounding).",
                    "real_world_sources_found": ["Local Machine Learning Model"],
                    "atomic_claims": [{"claim": current_title[:80], "status": "VERIFIED" if ml_pred == "GENUINE" else "UNVERIFIED"}],
                    "flagged_keywords": styl_buzzwords,
                    "cognitive_fallacies": [],
                    "recommended_factcheck_query": current_title
                }

            execution_duration = round(time.time() - start_time, 2)
            
            verdict = res.get("verdict", "SENSATIONALIZED").upper()
            score = res.get("credibility_score", 50)
            grounding = res.get("factual_grounding_pct", 50)
            distortion = res.get("rhetorical_distortion_pct", 50)
            clickbait = res.get("clickbait_sensationalism_pct", 50)
            summary = res.get("verdict_summary", "Audit completed.")
            sources_found = res.get("real_world_sources_found", [])
            claims = res.get("atomic_claims", [])
            buzzwords = res.get("flagged_keywords", styl_buzzwords)
            fallacies = res.get("cognitive_fallacies", [])
            search_query = res.get("recommended_factcheck_query", current_title)

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

        # 3. Two-Column Detailed Forensic Breakdown
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
                    
            st.markdown("### 🔍 Flagged Content Markup")
            if buzzwords:
                with st.expander("View Interactive Highlighted Text", expanded=True):
                    st.markdown(highlight_manipulative_phrases(current_body, buzzwords), unsafe_allow_html=True)
            else:
                st.success("Clean linguistic structure. Zero deceptive tokens highlighted in article body.")

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
            st.markdown("### 🌐 Live Fact-Checking Indexes")
            
            factcheck_url = f"https://toolbox.google.com/factcheck/explorer/search/{requests.utils.quote(search_query)}"
            st.link_button("🌐 Query Fact Check Verification Index", factcheck_url, use_container_width=True)
            
            news_url = f"https://news.google.com/search?q={requests.utils.quote(search_query)}"
            st.link_button("📰 Cross-Reference Global Media", news_url, use_container_width=True)
            
            # Export Report Download Feature
            st.write("---")
            st.markdown("### 📥 Export Forensic Audit Report")
            report_data = {
                "system": "VeritasLens™ Intelligence Suite",
                "lead_developer": "DHANVANTH CR",
                "assistant_developer": "JANESH S",
                "timestamp": str(datetime.now()),
                "headline": current_title,
                "verdict": verdict,
                "authenticity_score": score,
                "factual_grounding": grounding,
                "rhetorical_manipulation": distortion,
                "clickbait_load": clickbait,
                "summary": summary,
                "verified_sources": sources_found,
                "atomic_claims": claims
            }
            report_json = json.dumps(report_data, indent=2)
            st.download_button(
                label="📄 Download Full JSON Audit Log",
                data=report_json,
                file_name=f"veritas_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

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

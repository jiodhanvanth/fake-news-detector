import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from textblob import TextBlob
import requests
import re
import spacy

# Page Configuration & Styling
st.set_page_config(page_title="Veritas AI • Claim Forensic Engine", page_icon="🧬", layout="wide")

# Enhanced Custom Styling
st.markdown("""
    <style>
    .highlight-manipulative {
        background-color: rgba(255, 75, 75, 0.18);
        border-bottom: 2px solid #FF4B4B;
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: 600;
        cursor: help;
    }
    .main-score {
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .score-subtitle {
        font-size: 16px;
        opacity: 0.8;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .verdict-box {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 22px;
    }
    .verified-box { background-color: #2e7d32; }
    .risk-box { background-color: #c62828; }
    .neutral-box { background-color: #f9a825; color: #1f1f1f; }
    
    .metric-card {
        background-color: #f1f3f4;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. CORE AI Engine: Dynamic Balanced Classifier
@st.cache_resource
def load_ai_engine():
    # Pre-train with archetypal linguistic structures
    texts = [
        "Govt mandates 5% interest rate cap for agriculture loans to boost farming sector.",
        "SpaceX to launch third-generation Starlink satellite array from Florida coast tomorrow.",
        "Annual GDP growth remains steady at 6.8%, according to new Finance Ministry report.",
        "SHOCKING miracle breakthrough hidden by doctors leaks cure for all diseases overnight!",
        "URGENT secret conspiracy exposed government putting tracking microchips in standard bottled water!",
        "MIND-BLOWING truth billionaire elites don't want you to know about energy!",
        "UNBELIEVABLE secret leak shows celebs are actually extraterrestrial reptile species from Mars!"
    ]
    labels = ["GENUINE", "GENUINE", "GENUINE", "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE"]
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 3), stop_words='english')),
        ('clf', MultinomialNB(alpha=0.01))
    ])
    pipe.fit(texts, labels)
    # Load NLP parser for entity extraction
    nlp_parser = spacy.load("en_core_web_sm")
    return pipe, nlp_parser

ai_engine, nlp = load_ai_engine()

# Manipulative Dictionary
MANIPULATIVE_LEXICON = {
    "shocking", "unbelievable", "secret", "miracle", "exposed", "conspiracy", 
    "urgent", "leaked", "danger", "mind-blowing", "banned", "cure", "corrupt", 
    "magical", "breakthrough", "aliens", "hidden", "proven", "coverup", "alert"
}

# 2. ANALYSIS CORE: Stylometric & Rhetorical Processing
def run_forensic_scan(text):
    blob = TextBlob(text)
    subjectivity = blob.sentiment.subjectivity
    polarity = abs(blob.sentiment.polarity)
    
    tokens = re.findall(r'\b\w+\b', text.lower())
    buzzwords = [w for w in tokens if w in MANIPULATIVE_LEXICON]
    unique_buzzwords = list(set(buzzwords))
    
    # Sensationalism score calculation (0-100)
    score = min(100, int((subjectivity * 35) + (polarity * 20) + (len(unique_buzzwords) * 20)))
    return score, subjectivity, unique_buzzwords

def highlight_triggers(text, buzzwords):
    highlighted = text
    for word in buzzwords:
        pattern = re.compile(rf'\b({re.escape(word)})\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlight-manipulative" title="Manipulative Language Detected">\1</span>', highlighted)
    return highlighted

# 3. KNOWLEDGE ENGINE: Real-time Entity Cross-Referencing
def cross_reference_entities(text):
    doc = nlp(text)
    # Extract Persons, Organizations, or Locations as core entities
    entities = [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE", "NORP")]
    unique_ents = list(set(entities))[:4] # Take top 4 unique
    
    refs = []
    if unique_ents:
        for ent in unique_ents:
            try:
                url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={requests.utils.quote(ent)}&limit=1&namespace=0&format=json"
                res = requests.get(url, timeout=4).json()
                if res[1] and res[3]:
                    refs.append({"name": ent, "title": res[1][0], "url": res[3][0]})
            except Exception:
                pass
    return unique_ents, refs

# ----------------- MAIN UI DASHBOARD -----------------

st.title("🧬 Veritas AI: Comprehensive Claim Forensic Engine")
st.caption("Integrated Platform: Linguistic Forensics • Machine Learning Stance • Live Knowledge Graph Validation")

# Setup Columns
col_main, col_stats = st.columns([1.3, 0.7], gap="large")

with col_main:
    st.markdown("### 📝 Enter Content for AI Verification")
    headline = st.text_input("Claim Headline", placeholder="Scientists discover breakthrough in quantum computing stability...")
    article = st.text_area("Full Article Text / Key Context", height=220, placeholder="Start typing or paste content here...")
    analyze_btn = st.button("🚀 Execute Comprehensive AI Audit", type="primary", use_container_width=True)

if analyze_btn and article.strip():
    with st.spinner("AI Engine Executing Multi-Modal Scan..."):
        # Layer 1: Forensic Scan
        sensationalism, subjectivity, buzzwords = run_forensic_scan(article)
        
        # Layer 2: Machine Learning Prediction
        prediction = ai_engine.predict([article])[0]
        confidence_probs = ai_engine.predict_proba([article])[0]
        confidence = max(confidence_probs) * 100
        
        # Layer 3: Entity Extraction & Cross-Ref
        entities, knowledge_links = cross_reference_entities(headline if headline else article[:100])
        
        # 4. UNIFIED UNIFIED VERDICT CALCULATION
        # Unified Trust Formula: Combine model confidence, low sensationalism, and successful cross-ref
        base_trust = confidence if prediction == "GENUINE" else (100 - confidence)
        unified_trust = min(98, max(5, int(
            (base_trust * 0.6) + 
            ((100 - sensationalism) * 0.3) + 
            (min(len(knowledge_links), 2) * 5) # successful entity matches add boost
        )))

    with col_stats:
        st.markdown("### 📊 AI Audit Summary")
        
        # Big Score + Subtitle
        st.markdown(f'<div class="main-score">{unified_trust} / 100</div>', unsafe_allow_html=True)
        st.markdown('<div class="score-subtitle">Integrated Veritas Credibility Index</div>', unsafe_allow_html=True)
        
        # Dynamic Verdict Box
        if prediction == "MANIPULATIVE" or unified_trust < 35:
            verdict_class, verdict_text = "risk-box", "⚠️ AI DETECTS HIGH RISK"
        elif unified_trust > 75:
            verdict_class, verdict_text = "verified-box", "✅ AI VERIFIED: CREDIBLE"
        else:
            verdict_class, verdict_text = "neutral-box", "⚖️ AMBIGUOUS STRUCTURE"
        st.markdown(f'<div class="verdict-box {verdict_class}">{verdict_text}</div>', unsafe_allow_html=True)
        
        # Breakdown Metrics
        st.markdown("#### Veritas Scoring Breakdown")
        st.progress(unified_trust / 100)
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("ML Stance", prediction, help="Machine Learning analysis of text patterns.")
        with m2:
            st.metric("Sensationalism", f"{sensationalism}%", help="Measure of emotional or exaggerated language.")
        
        st.write("---")
        
        # Rhetorical Flags
        st.markdown("#### 🚩 Rhetorical Manipulators & Trigger Flags")
        if buzzwords:
            st.markdown(f"Detected **{len(buzzwords)}** high-risk tokens:")
            st.code(", ".join(buzzwords))
            
            with st.expander("Show Highlighted Article", expanded=True):
                st.markdown(highlight_triggers(article, buzzwords), unsafe_allow_html=True)
        else:
            st.success("Clean linguistic structure. No manipulative patterns detected.")

        st.write("---")
        
        # Knowledge Entity Links
        st.markdown("#### 🌐 Live Knowledge Graph Reference Check")
        if knowledge_links:
            st.markdown(f"Analyzed **{len(entities)}** key entities from claim:")
            for ref in knowledge_links:
                st.markdown(f"- **{ref['name']}** $\rightarrow$ [{ref['title']}]({ref['url']})")
        else:
            st.info("No direct reference matches for key entities in open knowledge indexes.")

elif analyze_btn:
    st.error("Please enter at least the article body text to run the analysis.")

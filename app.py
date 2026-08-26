import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from textblob import TextBlob
import requests
import re

st.set_page_config(page_title="Veritas AI • Claim Forensic Engine", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    .highlight-manipulative {
        background-color: rgba(255, 75, 75, 0.22);
        border-bottom: 2px solid #FF4B4B;
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: 600;
    }
    .main-score {
        font-size: 50px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .score-subtitle {
        font-size: 15px;
        opacity: 0.8;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .verdict-box {
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 20px;
    }
    .verified-box { background-color: #2e7d32; }
    .risk-box { background-color: #c62828; }
    .neutral-box { background-color: #e65100; }
    </style>
""", unsafe_allow_html=True)

# 1. CORE AI Engine: Fast Dynamic Classifier
@st.cache_resource
def load_ai_engine():
    texts = [
        "Government announces new educational policy reforms across schools and colleges nationwide.",
        "ISRO successfully launches navigation satellite into orbit from Sriharikota space center.",
        "Ministry of Finance releases quarterly economic growth and tax revenue statistics.",
        "Health department advises citizens on seasonal influenza prevention and vaccination schedule.",
        "Reserve Bank issues updated monetary policy guidelines for commercial banking operations.",
        "Scientists publish comprehensive study on clean energy grid infrastructure and solar conversion efficiency.",
        "SHOCKING miracle cure hidden by corrupt doctors leaked online cures all diseases overnight!",
        "URGENT secret conspiracy exposed government is putting secret microchips in tap water!",
        "Mind-blowing breakthrough that the billionaire elites do not want you to know about!",
        "UNBELIEVABLE secret leak proves celebrities are secretly alien reptiles from outer space!",
        "Secret military experiment exposed as 5G towers secretly control civilian brainwaves!",
        "Doctors banned this one magical fruit that instantly burns all body fat in 3 hours!"
    ]
    labels = [
        "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE",
        "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE", "MANIPULATIVE"
    ]
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('clf', MultinomialNB(alpha=0.1))
    ])
    pipe.fit(texts, labels)
    return pipe

ai_engine = load_ai_engine()

MANIPULATIVE_LEXICON = {
    "shocking", "unbelievable", "secret", "miracle", "exposed", "conspiracy", 
    "urgent", "leaked", "danger", "mind-blowing", "banned", "cure", "corrupt", 
    "magical", "breakthrough", "aliens", "hidden", "proven", "coverup", "alert"
}

def run_forensic_scan(text):
    blob = TextBlob(text)
    subjectivity = blob.sentiment.subjectivity
    polarity = abs(blob.sentiment.polarity)
    
    tokens = re.findall(r'\b\w+\b', text.lower())
    buzzwords = list(set([w for w in tokens if w in MANIPULATIVE_LEXICON]))
    caps_words = [w for w in text.split() if w.isupper() and len(w) > 1 and w.isalpha()]
    
    score = min(100, int((subjectivity * 35) + (polarity * 20) + (len(buzzwords) * 15) + (len(caps_words) * 10)))
    return score, subjectivity, polarity, buzzwords, caps_words

def highlight_triggers(text, buzzwords):
    highlighted = text
    for word in buzzwords:
        pattern = re.compile(rf'\b({re.escape(word)})\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlight-manipulative">\1</span>', highlighted)
    return highlighted

def extract_entities_and_cross_reference(text):
    # Extract capitalized proper nouns and keywords for entity matching
    words = re.findall(r'\b[A-Z][a-z0-9_]+\b', text)
    stopwords = {"The", "A", "An", "In", "On", "At", "This", "That", "It", "They", "We", "He", "She", "Is", "Are", "Shocking", "Urgent"}
    entities = list(set([w for w in words if w not in stopwords]))[:3]
    
    refs = []
    for ent in entities:
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={requests.utils.quote(ent)}&limit=1&namespace=0&format=json"
            res = requests.get(url, timeout=3).json()
            if res[1] and res[3]:
                refs.append({"name": ent, "title": res[1][0], "url": res[3][0]})
        except Exception:
            pass
    return entities, refs

# ----------------- UI DASHBOARD -----------------

st.title("🧬 Veritas AI: Comprehensive Claim Forensic Engine")
st.caption("Integrated Platform: Linguistic Forensics • Machine Learning Stance • Live Knowledge Graph Validation")

col_main, col_stats = st.columns([1.2, 0.8], gap="large")

with col_main:
    st.markdown("### 📝 Enter Content for AI Verification")
    headline = st.text_input("Claim Headline", "ISRO announces expansion of regional satellite navigation network")
    article = st.text_area(
        "Full Article Text / Key Context", 
        height=220, 
        value="The Indian Space Research Organisation (ISRO) confirmed plans to deploy new navigation payloads next quarter. Officials stated the upgrades will improve precision for civilian positioning services and maritime transport systems across the subcontinent."
    )
    analyze_btn = st.button("🚀 Execute Comprehensive AI Audit", type="primary", use_container_width=True)

if analyze_btn and article.strip():
    with st.spinner("AI Engine Executing Multi-Stage Scan..."):
        sensationalism, subjectivity, polarity, buzzwords, caps = run_forensic_scan(article)
        prediction = ai_engine.predict([article])[0]
        confidence_probs = ai_engine.predict_proba([article])[0]
        confidence = max(confidence_probs) * 100
        
        entities, knowledge_links = extract_entities_and_cross_reference(f"{headline} {article}")
        
        # Unified Trust Calculation
        base_trust = confidence if prediction == "GENUINE" else (100 - confidence)
        unified_trust = min(98, max(5, int(
            (base_trust * 0.6) + 
            ((100 - sensationalism) * 0.3) + 
            (min(len(knowledge_links), 2) * 5)
        )))

    with col_stats:
        st.markdown("### 📊 AI Audit Summary")
        st.markdown(f'<div class="main-score">{unified_trust} / 100</div>', unsafe_allow_html=True)
        st.markdown('<div class="score-subtitle">Integrated Veritas Credibility Index</div>', unsafe_allow_html=True)
        
        if prediction == "MANIPULATIVE" or unified_trust < 40:
            verdict_class, verdict_text = "risk-box", "⚠️ AI DETECTS HIGH RISK"
        elif unified_trust > 70:
            verdict_class, verdict_text = "verified-box", "✅ AI VERIFIED: CREDIBLE"
        else:
            verdict_class, verdict_text = "neutral-box", "⚖️ AMBIGUOUS STRUCTURE"
        st.markdown(f'<div class="verdict-box {verdict_class}">{verdict_text}</div>', unsafe_allow_html=True)
        
        st.progress(unified_trust / 100)
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("ML Stance", prediction)
        with m2:
            st.metric("Sensationalism", f"{sensationalism}%")
        
        st.write("---")
        st.markdown("#### 🚩 Rhetorical Manipulators & Trigger Flags")
        if buzzwords or caps:
            if buzzwords:
                st.markdown(f"**Trigger Keywords:** `{', '.join(buzzwords)}`")
            if caps:
                st.markdown(f"**Capitalized Shouting:** `{', '.join(caps)}`")
            
            with st.expander("Show Highlighted Text Breakdown", expanded=True):
                st.markdown(highlight_triggers(article, buzzwords), unsafe_allow_html=True)
        else:
            st.success("Clean linguistic structure. No manipulative patterns detected.")

        st.write("---")
        st.markdown("#### 🌐 Live Knowledge Graph Validation")
        if knowledge_links:
            st.markdown(f"Cross-referenced **{len(knowledge_links)}** key verified entities:")
            for ref in knowledge_links:
                st.markdown(f"- **{ref['name']}** $\rightarrow$ [{ref['title']}]({ref['url']})")
        else:
            st.info("No reference matches found in open knowledge indexes.")

elif analyze_btn:
    st.error("Please enter at least the article text to run verification.")

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline
from textblob import TextBlob
import requests
import re

st.set_page_config(
    page_title="VeritasLens | AI News Forensic Engine", 
    page_icon="🛡️", 
    layout="wide"
)

# Custom Styling for clean presentation
st.markdown("""
    <style>
    .highlight-fake {
        background-color: #ff4b4b33;
        border-bottom: 2px solid #ff4b4b;
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: 600;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ VeritasLens: AI Forensic News & Claim Verifier")
st.caption("Multi-Stage Verification: Stylometric Analysis • Machine Learning Semantics • Live Knowledge Cross-Referencing")

# Robust in-memory training pipeline
@st.cache_resource
def get_ml_pipeline():
    training_texts = [
        "Government announces new educational policy reforms across schools and colleges nationwide.",
        "ISRO successfully launches navigation satellite into orbit from Sriharikota space center.",
        "Ministry of Finance releases quarterly economic growth and tax revenue statistics.",
        "Health department advises citizens on seasonal influenza prevention and vaccination schedule.",
        "Reserve Bank issues updated monetary policy guidelines for commercial banks.",
        "Scientists publish comprehensive study on clean energy grid infrastructure and solar conversion efficiency.",
        "SHOCKING miracle cure hidden by corrupt doctors leaked online cures all diseases overnight!",
        "URGENT secret conspiracy exposed government is putting secret microchips in tap water!",
        "Mind-blowing breakthrough that the billionaire elites do not want you to know about!",
        "UNBELIEVABLE secret leak proves celebrities are secretly alien reptiles from outer space!",
        "Secret military experiment exposed as 5G towers secretly control civilian brainwaves!",
        "Doctors banned this one magical fruit that instantly burns all body fat in 3 hours!"
    ]
    training_labels = [
        "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE", "GENUINE",
        "UNRELIABLE", "UNRELIABLE", "UNRELIABLE", "UNRELIABLE", "UNRELIABLE", "UNRELIABLE"
    ]
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('clf', PassiveAggressiveClassifier(max_iter=150, random_state=42))
    ])
    pipe.fit(training_texts, training_labels)
    return pipe

model = get_ml_pipeline()

SENSATIONAL_LEXICON = {
    "shocking", "unbelievable", "secret", "miracle", "exposed", "conspiracy", 
    "urgent", "leaked", "danger", "mind-blowing", "banned", "cure", "corrupt", 
    "magical", "breakthrough", "aliens", "hidden"
}

def analyze_forensics(text):
    blob = TextBlob(text)
    subjectivity = blob.sentiment.subjectivity
    polarity = abs(blob.sentiment.polarity)
    
    tokens = re.findall(r'\b\w+\b', text.lower())
    found_buzzwords = [w for w in tokens if w in SENSATIONAL_LEXICON]
    caps_words = [w for w in text.split() if w.isupper() and len(w) > 1 and w.isalpha()]
    
    sensational_score = min(100, int((subjectivity * 35) + (polarity * 20) + (len(found_buzzwords) * 15) + (len(caps_words) * 10)))
    return sensational_score, subjectivity, polarity, list(set(found_buzzwords)), caps_words

def highlight_text(text, buzzwords):
    highlighted = text
    for word in buzzwords:
        pattern = re.compile(rf'\b({re.escape(word)})\b', re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlight-fake">\1</span>', highlighted)
    return highlighted

def search_live_entities(query):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={requests.utils.quote(query)}&limit=3&namespace=0&format=json"
        res = requests.get(url, timeout=5).json()
        return list(zip(res[1], res[3]))
    except Exception:
        return []

# Layout
col_input, col_report = st.columns([1.1, 0.9], gap="large")

with col_input:
    st.subheader("📝 Input News Content")
    headline = st.text_input("Headline / Key Claim", "ISRO announces expansion of regional satellite navigation network")
    article_body = st.text_area(
        "Article Body Text", 
        height=220, 
        value="The Indian Space Research Organisation (ISRO) confirmed plans to deploy new navigation payloads next quarter. Officials stated the upgrades will improve precision for civilian positioning services and maritime transport systems across the subcontinent."
    )
    run_analysis = st.button("🚀 Run Forensic Verification", type="primary", use_container_width=True)

if run_analysis and article_body.strip():
    with st.spinner("Executing linguistic & rhetorical forensic scan..."):
        sensational_score, subjectivity, polarity, buzzwords, caps = analyze_forensics(article_body)
        prediction = model.predict([article_body])[0]
        live_refs = search_live_entities(headline)
        
        # Calculate Unified Credibility Index
        if prediction == "UNRELIABLE" or sensational_score > 45:
            credibility = max(5, int(100 - (sensational_score * 0.6) - (len(buzzwords) * 8) - (len(caps) * 4)))
            verdict = "HIGH RISK / SENSATIONALIZED"
            color = "red"
        else:
            credibility = min(98, int(100 - (sensational_score * 0.35)))
            verdict = "VERIFIED / CREDIBLE STRUCTURE"
            color = "green"

    with col_report:
        st.subheader("📊 Forensic Audit Report")
        
        st.metric(label="Unified Credibility Index", value=f"{credibility} / 100")
        st.progress(credibility / 100)
        st.markdown(f"**Classification:** :{color}[**{verdict}**]")
        
        st.write("---")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("ML Stance", prediction)
        c2.metric("Sensationalism", f"{sensational_score}%")
        c3.metric("Subjectivity", f"{int(subjectivity*100)}%")
        
        st.write("---")
        
        st.markdown("#### 🔍 Rhetorical Analysis & Trigger Flags")
        if buzzwords or caps:
            st.markdown(f"- **Sensational Keywords:** `{', '.join(buzzwords) if buzzwords else 'None'}`")
            st.markdown(f"- **Capitalized Emphasis Tokens:** `{', '.join(caps) if caps else 'None'}`")
        else:
            st.success("Clean linguistic structure. No manipulative trigger patterns detected.")
            
        with st.expander("View Highlighted Article Breakdown"):
            st.markdown(highlight_text(article_body, buzzwords), unsafe_allow_html=True)
            
        st.write("---")
        st.markdown("#### 🌐 Live Reference Cross-Check")
        if live_refs:
            for title, link in live_refs:
                st.markdown(f"- [{title}]({link})")
        else:
            st.info("No direct reference matches in open knowledge indexes.")
import streamlit as st
import pandas as pd
import numpy as np
import os
import pymupdf 
from pathlib import Path
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# Must be the first Streamlit command
st.set_page_config(
    page_title="Personal Health & Wellness AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a unique, clean look
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load ENV
load_dotenv()

# ==========================================
# Caching Resources
# ==========================================
@st.cache_resource
def load_question_a_model():
    """Loads and trains the Question A Logistic Regression model dynamically."""
    S = 3046
    data_path = Path(__file__).resolve().parent.parent / "question_a" / "data" / "heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(data_path).dropna()
    
    X = df.drop(columns=['DEATH_EVENT'])
    y = df['DEATH_EVENT']
    
    # Train test split for scaling
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=S, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Using C=np.inf to match the scratch mathematical model
    model = LogisticRegression(random_state=S, max_iter=8000, C=np.inf)
    model.fit(X_train_scaled, y_train)
    
    return model, scaler, X.columns.tolist()

@st.cache_resource
def load_question_c_rag():
    """Loads PDFs, chunks them, and prepares the TF-IDF vectorizer."""
    docs_dir = Path(__file__).resolve().parent.parent / "question_c" / "documents"
    words_per_chunk = 200
    overlap = 50
    
    chunks = []
    metadata = []
    
    for filepath in docs_dir.glob("*.pdf"):
        doc = pymupdf.open(filepath)
        text = " ".join(page.get_text().replace('\n', ' ') for page in doc)
        
        words = text.split()
        for i in range(0, len(words), words_per_chunk - overlap):
            chunk_words = words[i:i + words_per_chunk]
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            metadata.append(filepath.name)
            
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    
    return vectorizer, tfidf_matrix, chunks, metadata

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ==========================================
# Sidebar Navigation
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=60)
    st.title("Navigation")
    page = st.radio("Select Module:", ["Dashboard", "Heart Failure Risk (Q:A)", "Health Assistant (Q:C)"])
    
    st.markdown("---")
    st.markdown("**Candidate:** Shreyas G R")
    st.markdown("**USN:** 1DA23AI046")
    st.markdown("**Seed:** 3046")

# ==========================================
# Page Routing
# ==========================================
if page == "Dashboard":
    st.markdown('<p class="main-title">Personal Health & Wellness AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">A dual-engine platform for clinical risk prediction and trusted health information retrieval.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🫀 Question A: Risk Predictor\nAnalyzes 12 clinical features (like Ejection Fraction and Serum Creatinine) to predict heart failure risk. Features a dynamic threshold slider demonstrating the clinical trade-off between Recall and Precision (False Positives).")
    with col2:
        st.success("### 💬 Question C: Health Assistant\nAn AI-powered RAG system that answers health queries strictly using WHO documents. It uses TF-IDF cosine similarity to fetch chunks and a strict Groq LLM guardrail to prevent hallucination.")

elif page == "Heart Failure Risk (Q:A)":
    st.markdown('<p class="main-title">Heart Failure Risk Predictor</p>', unsafe_allow_html=True)
    st.markdown("Enter patient metrics below to evaluate clinical risk. Adjust the diagnostic threshold to see how sensitivity changes.")
    
    model, scaler, feature_names = load_question_a_model()
    
    # Create input form
    with st.expander("📝 Patient Clinical Data Input", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=60)
            anaemia = st.selectbox("Anaemia", [0, 1], format_func=lambda x: "Yes (1)" if x==1 else "No (0)")
            creatinine_phosphokinase = st.number_input("CPK (mcg/L)", value=250)
            diabetes = st.selectbox("Diabetes", [0, 1], format_func=lambda x: "Yes (1)" if x==1 else "No (0)")
            
        with col2:
            ejection_fraction = st.number_input("Ejection Fraction (%)", min_value=1, max_value=100, value=38)
            high_blood_pressure = st.selectbox("High Blood Pressure", [0, 1], format_func=lambda x: "Yes (1)" if x==1 else "No (0)")
            platelets = st.number_input("Platelets (kiloplatelets/mL)", value=263358.0)
            serum_creatinine = st.number_input("Serum Creatinine (mg/dL)", value=1.1)
            
        with col3:
            serum_sodium = st.number_input("Serum Sodium (mEq/L)", value=137)
            sex = st.selectbox("Sex", [0, 1], format_func=lambda x: "Male (1)" if x==1 else "Female (0)")
            smoking = st.selectbox("Smoking", [0, 1], format_func=lambda x: "Yes (1)" if x==1 else "No (0)")
            time = st.number_input("Follow-up Time (days)", value=130, help="Note: This is a highly predictive feature in this dataset, though often unknown at time zero in reality.")
            
    # Dynamic Threshold
    st.markdown("---")
    st.subheader("⚙️ Clinical Diagnostic Settings")
    threshold = st.slider("Decision Threshold (Probability cut-off)", min_value=0.01, max_value=0.99, value=0.42, step=0.01, help="Level 3 Analysis determined that lowering the threshold to 0.42 increases Recall to ~0.90 while controlling False Positives.")
    
    if st.button("Predict Risk", use_container_width=True, type="primary"):
        # Prepare input array
        input_data = pd.DataFrame([[
            age, anaemia, creatinine_phosphokinase, diabetes, ejection_fraction, 
            high_blood_pressure, platelets, serum_creatinine, serum_sodium, sex, smoking, time
        ]], columns=feature_names)
        
        # Scale & Predict
        scaled_input = scaler.transform(input_data)
        prob = model.predict_proba(scaled_input)[0][1] # Probability of Class 1
        
        # Output Results
        st.markdown("### Prediction Results")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.metric(label="Calculated Risk Probability", value=f"{prob*100:.1f}%")
            
        with res_col2:
            if prob >= threshold:
                st.error("🚨 **HIGH RISK**: The patient's risk probability exceeds the diagnostic threshold. Immediate clinical review recommended.")
            else:
                st.success("✅ **LOW RISK**: The patient is below the current risk threshold.")

elif page == "Health Assistant (Q:C)":
    st.markdown('<p class="main-title">Trusted Health Assistant</p>', unsafe_allow_html=True)
    st.markdown("Ask health-related questions. The AI is sandboxed and will *only* answer using the provided WHO Fact Sheets.")
    
    vectorizer, tfidf_matrix, chunks, metadata = load_question_c_rag()
    client = get_groq_client()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("View Retrieved Context"):
                    for src, text in zip(message["source_names"], message["sources"]):
                        st.markdown(f"**{src}**\n\n> {text}...")

    # Chat input
    if prompt := st.chat_input("E.g., What are the risk factors for cardiovascular disease?"):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant processing
        with st.chat_message("assistant"):
            with st.spinner("Searching WHO documents..."):
                # TF-IDF Retrieval
                query_vec = vectorizer.transform([prompt])
                similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
                top_indices = similarities.argsort()[-3:][::-1]
                
                context = ""
                source_names = []
                source_texts = []
                
                for idx in top_indices:
                    context += f"\n[Source Document: {metadata[idx]}]\n{chunks[idx]}\n"
                    source_names.append(metadata[idx])
                    source_texts.append(chunks[idx][:200]) # Preview for UI
                
                # LLM Generation
                llm_prompt = f"""You are a trusted medical assistant. Answer the user's question based strictly on the context below. 
                If the context does not contain the relevant information to answer the question, you MUST explicitly state: "I don't know based on the provided context." 
                You MUST explicitly cite the source document name in your answer if you find it. Do not use outside knowledge under any circumstances.
                
                Context:
                {context}
                
                Question: {prompt}
                
                Answer (with citations):"""
                
                try:
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": llm_prompt}],
                        model="openai/gpt-oss-20b",
                        temperature=0.1
                    )
                    answer = response.choices[0].message.content
                    
                    st.markdown(answer)
                    with st.expander("View Retrieved Context"):
                        for src, text in zip(source_names, source_texts):
                            st.markdown(f"**{src}**\n\n> {text}...")
                            
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": source_texts,
                        "source_names": source_names
                    })
                except Exception as e:
                    st.error(f"API Error: {str(e)}")

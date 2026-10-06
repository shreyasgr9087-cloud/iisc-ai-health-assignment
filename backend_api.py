import os
import pandas as pd
import pymupdf
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

load_dotenv()

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Question A: Model Setup
# ==========================================
S = 3046
data_path = Path(__file__).resolve().parent / "question_a" / "data" / "heart_failure_clinical_records_dataset.csv"
df = pd.read_csv(data_path).dropna()

X = df.drop(columns=['DEATH_EVENT'])
y = df['DEATH_EVENT']

X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=S, stratify=y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Using C=np.inf to match the scratch mathematical model
qa_model = LogisticRegression(random_state=S, max_iter=8000, C=np.inf)
qa_model.fit(X_train_scaled, y_train)
feature_names = X.columns.tolist()

# ==========================================
# Question C: RAG Setup
# ==========================================
docs_dir = Path(__file__).resolve().parent / "question_c" / "documents"
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

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ==========================================
# API Models & Endpoints
# ==========================================

class Features(BaseModel):
    age: float
    anaemia: int
    creatinine_phosphokinase: float
    diabetes: int
    ejection_fraction: float
    high_blood_pressure: int
    platelets: float
    serum_creatinine: float
    serum_sodium: float
    sex: int
    smoking: int
    time: float

class PredictRequest(BaseModel):
    features: Features
    threshold: float

@app.post("/predict")
def predict_risk(req: PredictRequest):
    # Ensure ordered exactly as feature_names
    f = req.features
    input_data = pd.DataFrame([[
        f.age, f.anaemia, f.creatinine_phosphokinase, f.diabetes, f.ejection_fraction,
        f.high_blood_pressure, f.platelets, f.serum_creatinine, f.serum_sodium, f.sex, f.smoking, f.time
    ]], columns=feature_names)
    
    scaled_input = scaler.transform(input_data)
    prob = qa_model.predict_proba(scaled_input)[0][1]
    
    return {"probability": float(prob)}


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[Message]

@app.post("/chat")
def chat_assistant(req: ChatRequest):
    question = req.question
    
    # TF-IDF Retrieval
    query_vec = vectorizer.transform([question])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-3:][::-1]
    
    context = ""
    sources_out = []
    
    for idx in top_indices:
        doc_name = metadata[idx]
        chunk_text = chunks[idx]
        context += f"\n[Source Document: {doc_name}]\n{chunk_text}\n"
        sources_out.append({
            "id": f"chunk-{idx}",
            "document": doc_name,
            "page": None,
            "excerpt": chunk_text[:250] + "..."  # Provide a snippet for UI
        })
    
    llm_prompt = f"""You are a trusted medical assistant. Answer the user's question based strictly on the context below. 
    If the context does not contain the relevant information to answer the question, you MUST explicitly state: "I don't know based on the provided context." 
    You MUST explicitly cite the source document name in your answer if you find it. Do not use outside knowledge under any circumstances.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer (with citations):"""
    
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": llm_prompt}],
        model="openai/gpt-oss-20b",
        temperature=0.1
    )
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources_out
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

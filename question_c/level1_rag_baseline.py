import os
import pymupdf 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Load API key from .env file
load_dotenv()

def load_and_chunk_pdfs(docs_dir, words_per_chunk=200, overlap=50):
    chunks = []
    metadata = []
    
    for filepath in Path(docs_dir).glob("*.pdf"):
        doc = pymupdf.open(filepath)
        text = " ".join(page.get_text().replace('\n', ' ') for page in doc)
        
        words = text.split()
        for i in range(0, len(words), words_per_chunk - overlap):
            chunk_words = words[i:i + words_per_chunk]
            if not chunk_words:
                break
            chunks.append(" ".join(chunk_words))
            metadata.append(filepath.name)
            
    return chunks, metadata

def main():
    print("--- Question C, Level 1: Trusted Health Assistant (Baseline RAG) ---")
    
    # 1. Load and chunk WHO PDFs
    docs_dir = Path(__file__).resolve().parent / "documents"
    chunks, metadata = load_and_chunk_pdfs(docs_dir)
    print(f"Loaded {len(chunks)} text chunks from documents.")
    
    # 2. Build Scikit-Learn TF-IDF Retriever (Baseline for Level 1)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    
    # 3. Define the Question
    question = "What are the common risk factors for cardiovascular diseases?"
    print(f"\n[ User Question ]: {question}")
    
    # 4. Retrieve Top 3 Chunks
    query_vec = vectorizer.transform([question])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-3:][::-1]
    
    context = ""
    sources = set()
    for idx in top_indices:
        context += f"\n[Source Document: {metadata[idx]}]\n{chunks[idx]}\n"
        sources.add(metadata[idx])
        
    # 5. Generate Answer via Groq LLM
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"""You are a trusted medical assistant. Answer the user's question based strictly on the context below. 
    If the context does not contain the relevant information to answer the question, you MUST explicitly state: "I don't know based on the provided context." 
    You MUST explicitly cite the source document name in your answer if you find it. Do not use outside knowledge under any circumstances.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer (with citations):"""
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b",
        temperature=0.1
    )
    
    print("\n[ Assistant Answer ]")
    print(response.choices[0].message.content)
    print(f"\n[ Retrieved Sources Identified ]: {', '.join(sources)}")

if __name__ == "__main__":
    main()
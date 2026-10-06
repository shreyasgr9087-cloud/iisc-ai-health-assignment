import numpy as np
import pymupdf
import math
import re
from collections import Counter
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tokenize(text):
    # Matches scikit-learn's default token_pattern exactly
    return re.findall(r"(?u)\b\w\w+\b", text.lower())

def load_and_chunk_pdfs(docs_dir, words_per_chunk=200, overlap=50):
    chunks = []
    metadata = []
    for filepath in Path(docs_dir).glob("*.pdf"):
        doc = pymupdf.open(filepath)
        text = " ".join(page.get_text().replace('\n', ' ') for page in doc)
        
        # Split naively just for chunk sizing to preserve original text for the LLM later
        raw_words = text.split()
        for i in range(0, len(raw_words), words_per_chunk - overlap):
            chunk_words = raw_words[i:i + words_per_chunk]
            if not chunk_words: break
            chunks.append(" ".join(chunk_words))
            metadata.append(filepath.name)
    return chunks, metadata

class ScratchTFIDF:
    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.num_docs = 0
        
    def fit_transform(self, documents):
        self.num_docs = len(documents)
        
        # 1. Build Vocabulary and Document Frequencies (DF)
        doc_freqs = Counter()
        for doc in documents:
            words = set(tokenize(doc))
            for word in words:
                doc_freqs[word] += 1
                
        sorted_vocab = sorted(list(doc_freqs.keys()))
        self.vocab = {word: idx for idx, word in enumerate(sorted_vocab)}
        
        # 2. Calculate IDF (Scikit-learn smoothed formula)
        for word, df in doc_freqs.items():
            self.idf[word] = math.log((1 + self.num_docs) / (1 + df)) + 1.0
            
        # 3. Calculate TF-IDF matrix
        tfidf_matrix = np.zeros((self.num_docs, len(self.vocab)))
        for i, doc in enumerate(documents):
            word_counts = Counter(tokenize(doc))
            for word, count in word_counts.items():
                if word in self.vocab:
                    j = self.vocab[word]
                    tfidf_matrix[i, j] = count * self.idf[word]
            
            # L2 normalization
            row_norm = np.linalg.norm(tfidf_matrix[i])
            if row_norm > 0:
                tfidf_matrix[i] = tfidf_matrix[i] / row_norm
                
        return tfidf_matrix
        
    def transform(self, query):
        query_vec = np.zeros(len(self.vocab))
        word_counts = Counter(tokenize(query))
        for word, count in word_counts.items():
            if word in self.vocab:
                j = self.vocab[word]
                query_vec[j] = count * self.idf[word]
                
        vec_norm = np.linalg.norm(query_vec)
        if vec_norm > 0:
            query_vec = query_vec / vec_norm
        return query_vec.reshape(1, -1)

def scratch_cosine_similarity(A, B):
    return np.dot(A, B.T)

def main():
    print("--- Question C, Level 2: Pure NumPy TF-IDF Retriever ---")
    
    docs_dir = Path(__file__).resolve().parent / "documents"
    chunks, metadata = load_and_chunk_pdfs(docs_dir)
    
    questions = [
        "What are the common risk factors for cardiovascular diseases?",
        "How is maternal mortality defined by the WHO?",
        "What are the symptoms of severe dengue fever?"
    ]
    
    sk_vectorizer = TfidfVectorizer()
    sk_matrix = sk_vectorizer.fit_transform(chunks)
    
    scratch_vectorizer = ScratchTFIDF()
    scratch_matrix = scratch_vectorizer.fit_transform(chunks)
    
    for idx, question in enumerate(questions):
        print(f"\n[ Question {idx+1} ]: {question}")
        
        # Scikit-Learn
        sk_query = sk_vectorizer.transform([question])
        sk_sims = cosine_similarity(sk_query, sk_matrix).flatten()
        sk_top_idx = sk_sims.argsort()[-3:][::-1]
        
        # Scratch
        scratch_query = scratch_vectorizer.transform(question)
        scratch_sims = scratch_cosine_similarity(scratch_query, scratch_matrix).flatten()
        scratch_top_idx = scratch_sims.argsort()[-3:][::-1]
        
        print(f"Scikit-Learn Top 3 Indices: {sk_top_idx}")
        print(f"Scratch Math Top 3 Indices: {scratch_top_idx}")
        
        max_diff = np.max(np.abs(sk_sims - scratch_sims))
        print(f"Max mathematical deviation for this query: {max_diff:.4e}")

if __name__ == "__main__":
    main()
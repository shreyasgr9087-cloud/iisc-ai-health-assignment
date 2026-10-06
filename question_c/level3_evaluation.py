import json, os, time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from level2_scratch_retriever import load_and_chunk_pdfs, ScratchTFIDF, scratch_cosine_similarity

load_dotenv()
MODEL = "openai/gpt-oss-20b"
QUESTIONS = [
    {"q": "How does the WHO define overweight and obesity in adults?", "gold": [31, 32, 35]},
    {"q": "How many adults aged 30-79 years globally have hypertension?", "gold": [20]},
    {"q": "What percentage of diabetes deaths occur in low- and middle-income countries?", "gold": [11, 12, 18]},
    {"q": "What is the recommended weekly physical activity (in minutes) for adults?", "gold": [49]},
    {"q": "What are the main differences between Type 1 and Type 2 diabetes?", "gold": [14, 15, 17]},
    {"q": "How can high salt and sodium intake impact the risk of cardiovascular diseases?", "gold": [0, 2]},
    {"q": "What is the suggested weekly bodily movement to maintain wellness?", "gold": [49]},
    {"q": "What are the primary motor symptoms of Parkinson's disease?", "gold": []},
    {"q": "How is a torn Anterior Cruciate Ligament (ACL) surgically repaired?", "gold": []},
    {"q": "What is the standard pharmaceutical treatment protocol for malaria?", "gold": []},
]
PROMPT = """You are a trusted medical assistant. Answer the user's question based strictly on the context below.
If the context does not contain the relevant information to answer the question, you MUST explicitly state: "I don't know based on the provided context."
You MUST explicitly cite the source document name in your answer if you find it. Do not use outside knowledge under any circumstances.

Context:
{context}

Question: {question}

Answer (with citations):"""

def ask(client, prompt):
    err = ""
    for attempt in range(3):
        try:
            r = client.chat.completions.create(model=MODEL, temperature=0,
                                               messages=[{"role": "user", "content": prompt}])
            return r.choices[0].message.content
        except Exception as e:
            err = str(e); time.sleep(2 * (attempt + 1))
    return f"ERROR: {err}"

def main():
    docs_dir = Path(__file__).resolve().parent / "documents"
    chunks, meta = load_and_chunk_pdfs(docs_dir)
    vec = ScratchTFIDF()
    mat = vec.fit_transform(chunks)
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    log = []
    
    print("--- Running Level 3 Evaluation ---")
    for n, item in enumerate(QUESTIONS, 1):
        q = item["q"]
        sims = scratch_cosine_similarity(vec.transform(q), mat).flatten()
        top = [int(i) for i in sims.argsort()[-3:][::-1]]
        context = "".join(f"\n[Source Document: {meta[i]}]\n{chunks[i]}\n" for i in top)
        ans = ask(client, PROMPT.format(context=context, question=q))
        
        gold = item["gold"]
        # Check if any of the retrieved chunks match any of the gold chunks
        gold_in_top3 = bool(set(top) & set(gold)) if gold else None
        said_dont_know = "i don't know" in ans.lower()
        
        log.append({
            "n": n, 
            "question": q, 
            "top3": top, 
            "sources": [meta[i] for i in top],
            "scores": [round(float(sims[i]), 4) for i in top],
            "gold": gold, 
            "gold_in_top3": gold_in_top3,
            "said_dont_know": said_dont_know,
            "chunks": [chunks[i] for i in top], 
            "answer": ans
        })
        print(f"Q{n}: top3={top} gold_hit={gold_in_top3} dont_know={said_dont_know}")
        
    out = Path(__file__).resolve().parent / "level3_results.json"
    out.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"\nSaved {out}")

if __name__ == "__main__":
    main()
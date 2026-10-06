import re
from pathlib import Path
from level2_scratch_retriever import load_and_chunk_pdfs

chunks, meta = load_and_chunk_pdfs(Path(__file__).resolve().parent / "documents")
print("--- Checking for percentages in Diabetes PDF ---")
for i, c in enumerate(chunks):
    if meta[i] == "who_diabetes.pdf" and re.search(r"\d+\s?%", c): 
        print(f"Chunk {i}: {c[:250]}...")
        
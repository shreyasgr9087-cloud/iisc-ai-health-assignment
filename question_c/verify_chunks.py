import re
from pathlib import Path
import pymupdf

def load_and_chunk_pdfs_sorted(docs_dir, words_per_chunk=200, overlap=50):
    chunks = []
    metadata = []
    for filepath in sorted(Path(docs_dir).glob("*.pdf")):
        doc = pymupdf.open(filepath)
        text = " ".join(page.get_text().replace('\n', ' ') for page in doc)
        raw_words = text.split()
        for i in range(0, len(raw_words), words_per_chunk - overlap):
            chunk_words = raw_words[i:i + words_per_chunk]
            if not chunk_words: break
            chunks.append(" ".join(chunk_words))
            metadata.append(filepath.name)
    return chunks, metadata

docs_dir = Path(__file__).resolve().parent / "documents"
chunks, meta = load_and_chunk_pdfs_sorted(docs_dir)

checks = [
 ("Q1: Overweight/obesity definition", r"body mass index|BMI", "who_obesity.pdf"),
 ("Q2: Hypertension 30-79", r"30.{0,3}79", "who_hypertension.pdf"),
 ("Q3: Diabetes deaths LMIC", r"low.{0,5}and middle.income", "who_diabetes.pdf"),
 ("Q4: Weekly activity minutes", r"150", "who_physical_activity.pdf"),
 ("Q5: Type 1 / Type 2", r"type 1", "who_diabetes.pdf"),
 ("Q6: Salt/sodium", r"salt|sodium", "who_cardiovascular.pdf"),
]

for label, pat, src in checks:
    hits = [i for i, c in enumerate(chunks) if meta[i] == src and re.search(pat, c, re.I)]
    print(f"\n{label}: {len(hits)} chunks {hits}")

print("\n--- Unanswerable terms (want 0 hits each) ---")
for t in ["parkinson", "cruciate", r"\bACL\b", "malaria"]:
    hits = [i for i, c in enumerate(chunks) if re.search(t, c, re.I)]
    print(f"{t}: {hits}")
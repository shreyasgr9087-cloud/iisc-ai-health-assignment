# Technical Assignment: AI for Personal Health and Wellness

## Candidate Information
* **USN:** `1DA23AI046`
* **Personal Seed ($S$):** `3046`
  * *Derivation:* Numeric sequence from USN (`1DA23AI046`) is `[1, 2, 3, 0, 4, 6]`. The last four digits are `3046`.
  * *Application:* Seed `3046` is strictly used for all train-test splits (`random_state=3046`) and random number generators (`np.random.seed(3046)`).

---

## Questions Attempted
This submission implements **Question A** and **Question C** across all three mandatory tiers (Level 1: Build, Level 2: Code It Yourself from Scratch, Level 3: Reason with Hypotheses & Results):

1. **Question A: Predict a Health Risk**
   * **Dataset:** Heart Failure Clinical Records (UCI / BMC Medical Informatics, 299 instances, 13 features).
   * **Level 1 (Build):** Scikit-learn Logistic Regression and Random Forest baseline classification with precision, recall, and accuracy tracking.
   * **Level 2 (Code it yourself):** Pure NumPy Logistic Regression (Sigmoid, binary cross-entropy loss, vectorized gradient descent $\nabla_w = \frac{1}{m}X^T(\hat{y}-y)$), custom confusion matrix, and feature weight analysis without scikit-learn.
   * **Level 3 (Reason):** Pre-committed hypothesis and empirical evaluation of precision decay when lowering decision thresholds to reach Recall $\ge 0.90$ under clinical class imbalance.

2. **Question C: Build a Trusted Health-Information Assistant**
   * **Corpus:** Official World Health Organization (WHO) fact sheets on Cardiovascular Diseases, Diabetes, Hypertension, and Physical Activity.
   * **Level 1 (Build):** End-to-end RAG pipeline providing trusted answers with strict source attribution.
   * **Level 2 (Code it yourself):** From-scratch tokenization, Term Frequency-Inverse Document Frequency ($TF\text{-}IDF$) matrix construction, and Cosine Similarity ranking ($\frac{u \cdot v}{\|u\|_2 \|v\|_2}$) via pure NumPy.
   * **Level 3 (Reason):** 10 curated test questions (including unanswerable out-of-domain queries) with pre-committed failure mode predictions and root-cause error diagnosis.

---

## Repository Structure

```text
iisc-ai-health-assignment/
├── README.md                          # Project documentation and seed declaration
├── PERSONAL_INTELLIGENCE.md           # Mandatory decision log and AI usage declaration
├── requirements.txt                   # Environment dependencies
├── question_a/
│   ├── data/                          # Heart Failure Clinical Records dataset
│   ├── level1_build.py                # Scikit-learn baseline models
│   ├── level2_scratch_logreg.py       # Pure NumPy Logistic Regression & Confusion Matrix
│   └── level3_threshold_reasoning.py  # Threshold tuning & clinical reasoning
└── question_c/
    ├── documents/                     # Authoritative WHO public health fact sheets
    ├── level1_rag_baseline.py         # Baseline RAG pipeline with source tracking
    ├── level2_scratch_tfidf.py        # From-scratch TF-IDF & Cosine Similarity search
    └── level3_rag_diagnostics.py      # 10-query test suite & failure mode analysis
```

---

## Setup & Reproduction Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd iisc-ai-health-assignment
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Question A:**
   ```bash
   python question_a/level1_build.py
   python question_a/level2_scratch_logreg.py
   python question_a/level3_threshold_reasoning.py
   ```

4. **Run Question C:**
   ```bash
   python question_c/level1_rag_baseline.py
   python question_c/level2_scratch_tfidf.py
   python question_c/level3_rag_diagnostics.py
   ```

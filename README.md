# Personal Health and Wellness AI 

A dual-engine platform for clinical risk prediction and trusted health information retrieval, built as a full-stack web application.

---

## 1. Candidate Information
* **Name:** Shreyas G R
* **USN:** `1DA23AI046`
* **College:** Dr. Ambedkar Institute of Technology
* **Personal Seed ($S$):** `3046`
  * *Derivation:* Numeric sequence from USN (`1DA23AI046`) is `[1, 2, 3, 0, 4, 6]`. The last four digits are `3046`.
  * *Application:* Seed `3046` is strictly used for all train-test splits (`random_state=3046`) and random number generators (`np.random.seed(3046)`) to ensure complete deterministic reproducibility.

---

## 2. Project Overview

This submission implements a complete solution for **Question A (Health Risk Prediction)** and **Question C (Trusted Health Assistant)**. It covers all three mandatory tiers—Level 1 (Build), Level 2 (Scratch Implementation), and Level 3 (Hypothesis & Reasoning)—unified through a modern **React/Vite Frontend** and a **FastAPI Python Backend**.

### Question A: Predict a Health Risk (Clinical Tool)
* **Dataset:** Heart Failure Clinical Records (UCI / BMC Medical Informatics, 299 instances, 12 continuous features).
* **Level 1 (Build):** Scikit-learn Logistic Regression and Random Forest baseline classification with precision, recall, and accuracy tracking.
* **Level 2 (Code it yourself):** Pure NumPy Logistic Regression (Sigmoid, binary cross-entropy loss, vectorized gradient descent $\nabla_w = \frac{1}{m}X^T(\hat{y}-y)$), custom confusion matrix, and feature weight analysis without scikit-learn. Verified against sklearn (`C=np.inf`).
* **Level 3 (Reason):** Pre-committed hypothesis and empirical evaluation of precision decay when lowering decision thresholds to reach Recall $\ge 0.90$ under clinical class imbalance.

### Question C: Trusted Health Assistant (RAG Pipeline)
* **Corpus:** Official World Health Organization (WHO) fact sheets on Cardiovascular Diseases, Diabetes, Hypertension, Physical Activity, and Obesity.
* **Level 1 (Build):** End-to-end RAG pipeline providing trusted answers via Groq API (`openai/gpt-oss-20b`) with strict source attribution.
* **Level 2 (Code it yourself):** From-scratch Term Frequency-Inverse Document Frequency ($TF\text{-}IDF$) matrix construction, and Cosine Similarity ranking ($\frac{u \cdot v}{\|u\|_2 \|v\|_2}$) via pure NumPy matching scikit-learn's vectorizer to the 10⁻¹⁶ decimal.
* **Level 3 (Reason):** 10 curated test questions (including unanswerable out-of-domain queries) with pre-committed failure mode predictions and root-cause error diagnosis.

---

## 3. Project Directory Structure

```
iisc-ai-health-assignment/
├── README.md                          # Project documentation and seed declaration
├── PERSONAL_INTELLIGENCE.md           # Mandatory decision log and AI usage declaration
├── requirements.txt                   # Minimal top-level Python dependencies
├── backend_api.py                     # FastAPI server exposing ML and RAG models to UI
├── frontend/
│   └── clarity-health/                # Minimalist React Single Page App (Vite + Tailwind)
│       ├── src/                       # React components and views
│       ├── package.json               # Frontend dependencies
│       └── .env                       # API configurations (VITE_API_BASE_URL)
├── question_a/
│   ├── data/                          # Heart Failure Clinical Records dataset
│   ├── level1_build.py                # Scikit-learn baseline models
│   ├── level2_scratch_logreg.py       # Pure NumPy Logistic Regression & Confusion Matrix
│   ├── level3_threshold.py            # Threshold tuning logic
│   └── level3_hypothesis.md           # Clinical reasoning and empirical results
└── question_c/
    ├── documents/                     # Authoritative WHO public health PDFs
    ├── level1_rag_baseline.py         # Baseline RAG pipeline with source tracking
    ├── level2_scratch_retriever.py    # From-scratch TF-IDF & Cosine Similarity search
    ├── level3_evaluation.py           # 10-query test suite generator
    ├── level3_predictions.md          # Pre-run hypothesis for the 10 RAG queries
    ├── level3_results_summary.md      # Post-run failure mode analysis and findings
    └── level3_results.json            # Raw logs of the 10 RAG queries
```

---

## 4. Setup & Reproduction Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Groq API Key ([Get a free key at console.groq.com](https://console.groq.com))

### 1. Backend API (Python)
Clone the repository and set up a Python virtual environment:
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Environment Setup:
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

Run the Backend (FastAPI):
```bash
python backend_api.py
# The API will be available at http://localhost:8000
```

### 2. Frontend UI (React + Vite)
Navigate to the frontend directory:
```bash
cd frontend/clarity-health
```

Ensure `.env` exists inside `clarity-health` with the following configuration:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

Install packages and run the development server:
```bash
npm install
npm run dev
# Access the web app at http://localhost:5173
```

### 3. Running Core Analytical Scripts Directly (Optional)
If you wish to view the pure terminal outputs for the Level 2 mathematical proofs or the Level 3 analyses without using the UI, you can execute the core scripts directly from the root folder:

```bash
python question_a/level1_build.py
python question_a/level2_scratch_logreg.py
python question_a/level3_threshold.py

python question_c/level1_rag_baseline.py
python question_c/level2_scratch_retriever.py
python question_c/level3_evaluation.py
```

---

## 5. Author
- **Shreyas G R**
- Dr. Ambedkar Institute of Technology

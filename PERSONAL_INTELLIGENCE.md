# Decision Log & AI Usage Declaration

This document captures the rationale behind my core architectural decisions, the mistakes made along the way, and the lessons learned during this technical assignment. 

## 1. Decision Log

### Question A: Health Risk Predictor
**Decision 1: Dataset Selection**
I went with the **Heart Failure Clinical Records dataset** primarily because all 12 of its features are purely numeric right out of the box. If I had chosen the UCI Heart Disease dataset or the Pima Indians dataset, I would have had to deal with categorical variables and write one-hot encoding logic from scratch. By keeping it to continuous numerical features, I could focus entirely on getting the pure NumPy math right for Level 2—wrestling with gradient descent, matrix multiplication, and the sigmoid function—rather than getting bogged down in tedious data wrangling. I wanted to prove I understood the core math of Logistic Regression, not just pandas dataframe manipulation.

**Decision 2: Stratified Data Splitting**
I specifically chose to use **`stratify=y` during the train/test split instead of a naive random split.** The dataset is highly imbalanced when it comes to actual death events (only about ~32% positive class). When I first tried a standard random shuffle, the model's recall on the minority class was terrible (hovering around 64%) simply because the training set wasn't guaranteed to see enough positive cases. Enforcing a stratified split immediately stabilized the baseline recall at over 84%. I realized that for a medical diagnostic tool, missing a positive case is potentially fatal; keeping the distribution representative across train and test sets was absolutely critical.

### Question C: Trusted Health Assistant
**Decision 1: Model & Infrastructure**
My primary choice was **using the Groq API to serve the `openai/gpt-oss-20b` model rather than trying to host a local model.** Compute constraints and execution speed were the main factors here. Running a sufficiently smart LLM locally on a standard Windows environment is painfully slow and risks memory crashes, especially during a multi-question evaluation loop like in Level 3. Groq provided near-instant inference, and `gpt-oss-20b` has a massive context window that proved incredibly disciplined at extracting facts without hallucinating. It allowed me to focus on the RAG pipeline logic instead of fighting with my GPU.

**Decision 2: Evaluation Methodology (The Regex Trap)**
Initially, I relied on **regex phrase-matching to assign the "gold" labels for my Level 3 evaluation. This turned out to be a massive learning moment.** I assumed that if a WHO text chunk contained the exact keywords from the prompt (like "low- and middle-income"), it naturally held the answer. That logic completely fell apart on Question 3. I learned the hard way that lexical presence does not equal semantic relevance; you cannot fully automate RAG evaluation labels with a simple text search. You have to manually read and verify the text. It was a humbling realization of how evaluation pipelines can silently fail if the ground truth isn't human-verified.

---

## 2. AI Usage Declaration

* **Tools Used:** 
  * Gemini 3.1 Pro for coding assistance and debugging.
  * Claude 5.5 Sonnet for reasoning, architectural solutions, and generating the React UI.
  * Claude Opus 4.6 for final evaluation and drafting the README.md structure.

* **Where AI was weak and how I fixed it:** 
  Gemini initially drafted my Level 3 predictions and confidently stated that Question 3 (asking for the *percentage* of diabetes deaths in LMICs) would "PASS" because the TF-IDF vector search successfully found those exact keywords in the WHO documents. The AI blindly trusted the regex hits and failed to semantically read the text it was analyzing. 
  
  I caught this during the evaluation phase when the LLM stubbornly replied, "I don't know," despite being fed the AI-designated "gold" chunks. Confused, I wrote a manual script to print out those specific chunks. I read them myself and discovered the text explicitly discussed the topic but *never actually stated the percentage*. The AI had completely missed this nuance. 
  
  I fixed it by throwing out the AI's prediction, manually relabeling the evaluation, and documenting the incident as a human labeling error. Honestly, it was a great outcome—it successfully proved that the LLM's strict context guardrails were working exactly as intended, preventing a hallucination when the answer wasn't actually there!

---

## 3. Timestamp Authentication & Rule Compliance

**Rule Compliance: Predictions Before Results**
As required by the assignment guidelines: *"Commit each Level 3 prediction to GitHub before you run the test. The commit time is your proof."* 

This rule was strictly followed to maintain scientific and chronological integrity. My Git history serves as a timestamped record that the hypotheses were formulated prior to seeing the empirical results (though it should be noted that Git commit timestamps are author-set, so this serves as supporting evidence of ordering rather than tamper-proof proof):
* **Prediction Commit:** `docs(qc): log L3 predictions...` (16cce41) was committed **46 minutes prior** to evaluation.
* **Results Commit:** `feat(qc): add L3 evaluation pipeline, empirical results log...` (ed5329e) was committed **after** the evaluation was executed.

**Project Completion Record**
* **Final Evaluation & Submission Date:** 2026-10-06T10:28:20+05:30
* **Status:** Verified and Complete

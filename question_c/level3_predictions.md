# Question C - Level 3 Predictions
**Model Used:** `openai/gpt-oss-20b` (served via Groq API)

## Predictions Table

| # | Question | Predict PASS/FAIL | If FAIL: retrieval or LLM? | One-line reason |
|---|----------|------|------|------|
| 1 | How does the WHO define overweight and obesity in adults? | PASS | N/A | Lexical overlap ("define", "overweight", "obesity") will cleanly pull chunks [31, 32, 35]. |
| 2 | How many adults aged 30-79 years globally have hypertension? | PASS | N/A | Exact numeric match for "30-79" will pull chunk [20] perfectly. |
| 3 | What percentage of diabetes deaths occur in low- and middle-income countries? | PASS | N/A | "low- and middle-income" guarantees retrieval of chunks [11, 12, 18]. |
| 4 | What is the recommended weekly physical activity (in minutes) for adults? | PASS | N/A | "weekly physical activity" and "minutes" will pull chunk [49]. |
| 5 | What are the main differences between Type 1 and Type 2 diabetes? | PASS | N/A | "Type 1" and "Type 2" explicitly match chunks [14, 15, 17]. |
| 6 | How can high salt and sodium intake impact the risk of cardiovascular diseases? | PASS | N/A | "salt", "sodium", and "cardiovascular" clearly point to chunks [0, 2]. |
| 7 | What is the suggested weekly bodily movement to maintain wellness? | FAIL | Retrieval | Paraphrasing Q4 ("bodily movement", "wellness") bypasses TF-IDF lexical matching; wrong chunks will be retrieved. |
| 8 | What are the primary motor symptoms of Parkinson's disease? | PASS | N/A | LLM guardrail will trigger. Irrelevant chunks retrieved, so LLM will say "I don't know." |
| 9 | How is a torn Anterior Cruciate Ligament (ACL) surgically repaired? | PASS | N/A | LLM guardrail will trigger safely due to zero context overlap. |
| 10| What is the standard pharmaceutical treatment protocol for malaria? | PASS | N/A | LLM guardrail will trigger safely due to zero context overlap. |

**Overall Rationale:**
For Questions 1-6, the exact keyword overlap will allow pure NumPy TF-IDF to easily place the "gold" chunks in the top 3, leading to correct LLM answers. Question 7 will fail because TF-IDF cannot map synonyms (wellness/movement) to the document's vocabulary (health/activity), starving the LLM of context. For the unanswerable queries (8-10), retrieval will mathematically pull irrelevant text, but the explicit LLM prompt guardrail will prevent hallucination, resulting in safe "I don't know" responses. The original text was written by me, but i used AI to create a table, prediction is done by me, the user. 


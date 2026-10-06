# Question C - Level 3 Evaluation Results

| # | Question | Predicted | Actual | Grade / Notes |
|---|----------|-----------|--------|---------------|
| 1 | How does the WHO define overweight and obesity in adults? | PASS | PASS | Correct. |
| 2 | How many adults aged 30-79 years globally have hypertension? | PASS | PASS | Correct. |
| 3 | What percentage of diabetes deaths occur in LMICs? | PASS | **FAIL** | **Prediction Wrong (Labeling Error).** Gold label was assigned by phrase match, not by reading the answer. Model behaved correctly by refusing to answer. |
| 4 | What is the recommended weekly physical activity (in minutes) for adults? | PASS | PASS | Correct. |
| 5 | What are the main differences between Type 1 and Type 2 diabetes? | PASS | PASS | Correct (hit 2 of 3 gold chunks). |
| 6 | How can high salt and sodium intake impact the risk of cardiovascular diseases? | PASS | PASS | Correct (hit 1 of 2 gold chunks). |
| 7 | What is the suggested weekly bodily movement to maintain wellness? | FAIL (Retriever) | FAIL (Retriever) | **Retrieval Failure (Predicted).** TF-IDF failed on synonyms (chunk 49 absent from top 3); LLM correctly refused. |
| 8 | What are the primary motor symptoms of Parkinson's disease? | PASS (Safe) | PASS (Safe) | Guardrail held. |
| 9 | How is a torn Anterior Cruciate Ligament (ACL) surgically repaired? | PASS (Safe) | PASS (Safe) | Guardrail held. |
| 10| What is the standard pharmaceutical treatment protocol for malaria? | PASS (Safe) | PASS (Safe) | Guardrail held. |

## Case Study: Question 3 (The Gold-Labeling Error)
**Question:** "What percentage of diabetes deaths occur in low- and middle-income countries?"

**Analysis:**
I originally predicted this would pass, mapping chunks 11 and 12 as the "gold" chunks because they contained the exact phrase "low- and middle-income countries". The retriever successfully pulled these chunks (scores of 0.2903 and 0.2654). However, the LLM output `"I don't know based on the provided context."` 

Upon manual review of chunks 11 and 12, I discovered that while they discuss diabetes in LMICs, they *do not state the percentage*. The failure was not in the LLM or the retriever, but in my methodology for assigning gold labels based purely on regex phrase matching rather than reading the semantic content. The LLM behaved perfectly by refusing to hallucinate a percentage that did not exist in the provided text. This highlights the danger of relying solely on lexical presence to verify answerability in RAG evaluations.

Note: The original text was written by me, but i used AI to create a table and articulate my texts. The prediction is done by me, the user.
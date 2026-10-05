# Question A - Level 3 Prediction
**Seed S:** 3046

## Hypothesis: Threshold Shift to Reach 0.9 Recall
**Prediction before running:**
Our baseline stratified Logistic Regression achieved a recall of 0.8421 at the default 0.5 threshold. To push recall to \(\ge 0.90\), we must lower the decision threshold, making the model more sensitive. 

Because the Heart Failure dataset is naturally imbalanced (~32% positive class), lowering the threshold will force the model to aggressively flag patients as high-risk. Mathematically, this will trigger a surge in False Positives (FP). Since \(\text{Precision} = \frac{TP}{TP + FP}\), the denominator will inflate. 

Therefore, I predict that lowering the threshold to achieve \(\ge 0.90\) recall will cause a disproportionate drop in precision and overall accuracy, proving that accuracy alone is a misleading metric for clinical screening tools.
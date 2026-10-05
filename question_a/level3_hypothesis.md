# Question A - Level 3 Prediction
**Seed S:** 3046

## Hypothesis: Threshold Shift to Reach 0.9 Recall
**Prediction before running:**
Our baseline stratified Logistic Regression achieved a recall of 0.8421 at the default 0.5 threshold. To push recall to \(\ge 0.90\), we must lower the decision threshold, making the model more sensitive. 

Because the Heart Failure dataset is naturally imbalanced (~32% positive class), lowering the threshold will force the model to aggressively flag patients as high-risk. Mathematically, this will trigger a surge in False Positives (FP). Since \(\text{Precision} = \frac{TP}{TP + FP}\), the denominator will inflate. 

Therefore, I predict that lowering the threshold to achieve \(\ge 0.90\) recall will cause a disproportionate drop in precision and overall accuracy, proving that accuracy alone is a misleading metric for clinical screening tools.

## Empirical Results (Using Scikit-Learn with C=inf)
The results aligned with my prediction: pushing recall upward forced a disproportionate drop in precision due to a surge in false positives. 

At the default 0.50 threshold, we caught 16 of 19 deaths (Recall 0.8421) with 7 False Positives. 
* Lowering to **0.42** caught 1 additional death (17/19, Recall 0.8947) at the cost of 3 extra false alarms (FP=10). 
* Lowering further to **0.27** to strictly exceed 0.90 (catching 18/19, Recall 0.9474) cost 4 more false alarms for that single extra catch (FP=14, Precision 0.5625).

## Conclusion for Clinical Application
For a real screening tool, I would use the **0.42 threshold**. The marginal cost of false alarms rises too steeply beyond this point; paying 4 extra hospital false alarms just to catch one additional patient (moving from 0.42 to 0.27) is likely an inefficient use of resources compared to the 3-to-1 tradeoff at 0.42. 

Accuracy is highly misleading here due to the dataset's imbalance. Since 41 out of 60 test patients survived, a trivial model predicting "everyone survives" achieves a 68.3% baseline accuracy. Our model at threshold 0.27 scores 75%—only 6.7 points above a clinically useless baseline—demonstrating that accuracy masks the true performance of predicting the minority risk class.

*Caveats:* This threshold was selected by observing the test set, which risks overfitting; a production model should select it via training cross-validation. Additionally, the dominant `time` feature would not be known at initial screening, requiring a feature ablation for real-world deployment.
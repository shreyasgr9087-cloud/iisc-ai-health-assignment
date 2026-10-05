import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from pathlib import Path

S = 3046

def main():
    print(f"--- Question A, Level 3: Threshold Sweep (Seed: {S}) ---")
    
    # Load and prep data identically to Level 2
    DATA = Path(__file__).resolve().parent / "data" / "heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(DATA).dropna()
    
    X = df.drop(columns=['DEATH_EVENT']).values
    y = df['DEATH_EVENT'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=S, stratify=y)

    X_mean = np.mean(X_train, axis=0)
    X_std = np.std(X_train, axis=0)
    X_train_scaled = (X_train - X_mean) / X_std
    X_test_scaled = (X_test - X_mean) / X_std

    # Train model (Using our primary apples-to-apples configuration)
    model = LogisticRegression(random_state=S, max_iter=8000, C=np.inf)
    model.fit(X_train_scaled, y_train)
    
    # Extract raw probabilities for the positive class (DEATH_EVENT = 1)
    y_probs = model.predict_proba(X_test_scaled)[:, 1]

    print(f"\n{'Threshold':<10} | {'Recall':<10} | {'Precision':<10} | {'Accuracy':<10} | {'FP (False Alarms)'}")
    print("-" * 75)

    target_threshold = None
    target_metrics = None

    # Sweep threshold from 0.50 down to 0.01 in steps of 0.01
    for t in np.arange(0.50, 0.0, -0.01):
        y_pred_t = (y_probs >= t).astype(int)
        
        tp = int(np.sum((y_test == 1) & (y_pred_t == 1)))
        fp = int(np.sum((y_test == 0) & (y_pred_t == 1)))
        fn = int(np.sum((y_test == 1) & (y_pred_t == 0)))
        tn = int(np.sum((y_test == 0) & (y_pred_t == 0)))
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        
        # Log the exact moment we hit 0.90+ recall
        if recall >= 0.90 and target_threshold is None:
            target_threshold = t
            target_metrics = (recall, precision, accuracy, fp, tp, fn)
            print(f"** {t:.2f} **   | ** {recall:.4f} ** | ** {precision:.4f} ** | ** {accuracy:.4f} ** | ** {fp} **  <-- TARGET REACHED")
        else:
            print(f"{t:.2f}       | {recall:.4f}     | {precision:.4f}     | {accuracy:.4f}     | {fp}")

    print("\n[ Final Level 3 Conclusion ]")
    print(f"To achieve >= 0.90 Recall, we must lower the threshold to {target_threshold:.2f}.")
    print(f"At this threshold, Precision dropped to {target_metrics[1]:.4f} because False Positives jumped to {target_metrics[3]}.")
    print(f"Overall Accuracy dropped to {target_metrics[2]:.4f}.")

if __name__ == "__main__":
    main()
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from pathlib import Path

S = 3046

class ScratchLogisticRegression:
    def __init__(self, lr=0.1, n_iters=8000):
        self.lr = lr
        self.n_iters = n_iters
        self.weights = None
        self.bias = None
        self.losses = []

    def _sigmoid(self, z):
        z = np.clip(z, -250, 250)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X, y):
        m, n = X.shape
        np.random.seed(S)
        self.weights = np.random.randn(n) * 0.01
        self.bias = 0.0

        for _ in range(self.n_iters):
            linear_model = np.dot(X, self.weights) + self.bias
            y_pred = self._sigmoid(linear_model)

            dw = (1.0 / m) * np.dot(X.T, (y_pred - y))
            db = (1.0 / m) * np.sum(y_pred - y)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db

            eps = 1e-15
            y_pred_clipped = np.clip(y_pred, eps, 1 - eps)
            loss = - (1.0 / m) * np.sum(y * np.log(y_pred_clipped) + (1 - y) * np.log(1 - y_pred_clipped))
            self.losses.append(loss)

    def predict_proba(self, X):
        linear_model = np.dot(X, self.weights) + self.bias
        return self._sigmoid(linear_model)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

def custom_confusion_matrix(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    return np.array([[tn, fp], [fn, tp]])

def main():
    print(f"--- Question A, Level 2: Pure NumPy Logistic Regression (Seed: {S}) ---")
    
    DATA = Path(__file__).resolve().parent / "data" / "heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(DATA).dropna()
    
    feature_names = df.drop(columns=['DEATH_EVENT']).columns.tolist()
    X = df.drop(columns=['DEATH_EVENT']).values
    y = df['DEATH_EVENT'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=S, stratify=y)

    X_mean = np.mean(X_train, axis=0)
    X_std = np.std(X_train, axis=0)
    X_train_scaled = (X_train - X_mean) / X_std
    X_test_scaled = (X_test - X_mean) / X_std

    scratch_model = ScratchLogisticRegression(lr=0.1, n_iters=8000)
    scratch_model.fit(X_train_scaled, y_train)
    y_pred_scratch = scratch_model.predict(X_test_scaled)

    # Scikit-Learn Model (Apples to Apples using C=np.inf instead of penalty=None)
    sk_model = LogisticRegression(random_state=S, max_iter=8000, C=np.inf)
    sk_model.fit(X_train_scaled, y_train)
    y_pred_sk = sk_model.predict(X_test_scaled)

    cm_scratch = custom_confusion_matrix(y_test, y_pred_scratch)
    acc_scratch = (cm_scratch[0, 0] + cm_scratch[1, 1]) / np.sum(cm_scratch)
    acc_sk = np.mean(y_pred_sk == y_test)
    
    tp = cm_scratch[1, 1]
    fp = cm_scratch[0, 1]
    fn = cm_scratch[1, 0]
    precision_scratch = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall_scratch = tp / (tp + fn) if (tp + fn) > 0 else 0

    L = scratch_model.losses
    print("\n[ Convergence Metrics ]")
    print(f"Loss: {L[-1]:.6f} | Drop over last 100 iters: {L[-101]-L[-1]:.2e}")
    print(f"Max |w_scratch - w_sklearn|: {np.max(np.abs(scratch_model.weights - sk_model.coef_[0])):.2e}")
    print(f"Bias: {scratch_model.bias:.4f} vs {sk_model.intercept_[0]:.4f}")

    print("\n[ Custom Confusion Matrix (NumPy Scratch) ]")
    print(f"[[TN={cm_scratch[0, 0]}, FP={cm_scratch[0, 1]}],")
    print(f" [FN={cm_scratch[1, 0]}, TP={cm_scratch[1, 1]}]]")

    print(f"\nScratch Metrics:      Acc: {acc_scratch:.4f} | Prec: {precision_scratch:.4f} | Rec: {recall_scratch:.4f}")
    print(f"Scikit-Learn Accuracy: {acc_sk:.4f}")
    
    scratch_top_idx = np.argsort(np.abs(scratch_model.weights))[::-1][:3]
    
    print("\n[ Top 3 Feature Weights Comparison (C=np.inf) ]")
    print(f"{'Feature':<28} {'Scratch Weight':<16} {'Scikit-Learn Weight':<16}")
    print("-" * 62)
    for idx in scratch_top_idx:
        fname = feature_names[idx]
        print(f"{fname:<28} {scratch_model.weights[idx]:<16.4f} {sk_model.coef_[0][idx]:<16.4f}")

if __name__ == "__main__":
    main()
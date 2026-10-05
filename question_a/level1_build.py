import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from pathlib import Path

S = 3046

def main():
    print(f"--- Question A, Level 1: Building Baseline Models (Seed: {S}) ---")
    
    DATA = Path(__file__).resolve().parent / "data" / "heart_failure_clinical_records_dataset.csv"
    df = pd.read_csv(DATA).dropna()
    
    X = df.drop(columns=['DEATH_EVENT'])
    y = df['DEATH_EVENT']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=S, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    log_reg = LogisticRegression(random_state=S)
    log_reg.fit(X_train_scaled, y_train)
    y_pred_lr = log_reg.predict(X_test_scaled)
    
    rf_clf = RandomForestClassifier(random_state=S)
    rf_clf.fit(X_train_scaled, y_train)
    y_pred_rf = rf_clf.predict(X_test_scaled)
    
    print("\n[ Logistic Regression Results ]")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_lr):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_lr):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred_lr):.4f}")
    
    print("\n[ Random Forest Results ]")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_rf):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_rf):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred_rf):.4f}")

if __name__ == "__main__":
    main()
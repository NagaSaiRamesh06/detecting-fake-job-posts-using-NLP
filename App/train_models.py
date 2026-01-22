import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from .feature_engineering import prepare_features
import json
import datetime

def evaluate_model(y_test, y_pred, model_name):
    """
    Calculate and print metrics.
    """
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\n📊 {model_name} Performance:")
    print(f"   Accuracy:  {acc:.4f}")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall:    {rec:.4f}")
    print(f"   F1 Score:  {f1:.4f}")
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return acc

def train_and_eval():
    print("🚀 Starting Model Training Component...")
    
    # 1. Get Features and Target
    X, y = prepare_features()
    
    # 2. Train-Test Split
    print("\n✂️ Splitting data (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Model 1: Logistic Regression
    print("\n🧠 Training Logistic Regression...")
    log_model = LogisticRegression(max_iter=1000, class_weight='balanced')
    log_model.fit(X_train, y_train)
    log_pred = log_model.predict(X_test)
    log_acc = evaluate_model(y_test, log_pred, "Logistic Regression")
    
    # 4. Model 2: Naive Bayes
    print("\n🧠 Training Naive Bayes...")
    nb_model = MultinomialNB()
    nb_model.fit(X_train, y_train)
    nb_pred = nb_model.predict(X_test)
    nb_acc = evaluate_model(y_test, nb_pred, "Naive Bayes")
    
    # 6. Model 3: SVM (LinearSVC)
    print("\n🧠 Training SVM (LinearSVC)...")
    svm_model = LinearSVC(dual=False, random_state=42)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    svm_acc = evaluate_model(y_test, svm_pred, "SVM")

    # 7. Comparison & Save Metrics
    metrics = {
        "Logistic Regression": log_acc,
        "Naive Bayes": nb_acc,
        "SVM": svm_acc
    }
    
    best_model_name = max(metrics, key=metrics.get)
    print(f"\n🏆 Best Model: {best_model_name} ({metrics[best_model_name]:.4f})")
    
    # Save Metrics to JSON
    metrics_data = {
        "models": metrics,
        "active_model": best_model_name,
        "accuracy": metrics[best_model_name],
        "trained_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'Model')
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    with open(os.path.join(model_dir, "model_metrics.json"), "w") as f:
        json.dump(metrics_data, f, indent=4)
        print("✅ Metrics saved to model_metrics.json")

    # Save Best Model as 'best_model.pkl' (for App consumption)
    best_model_obj = None
    if best_model_name == "Logistic Regression":
        best_model_obj = log_model
    elif best_model_name == "Naive Bayes":
        best_model_obj = nb_model
    else:
        best_model_obj = svm_model

    with open(os.path.join(model_dir, "best_model.pkl"), "wb") as f:
        pickle.dump(best_model_obj, f)
    
    # Also save TFIDF if not already handled by prepare_features (it implicitly loads/creates it, but good to be sure)
    # Assuming prepare_features handles TFIDF pickling.
        
    print(f"✅ Best Model saved to {model_dir}")

if __name__ == "__main__":
    train_and_eval()

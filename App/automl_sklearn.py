import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from .feature_engineering import prepare_features

def evaluate_model(y_test, y_pred):
    return {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1 Score": f1_score(y_test, y_pred)
    }

def run_automl():
    print("🚀 Starting AutoML...")
    
    # 1. Get Data
    X, y = prepare_features()
    
    # 2. Split
    print("\n✂️ Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Define Models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced'),
        "Naive Bayes": MultinomialNB(),
        "Linear SVM": LinearSVC(max_iter=1000, class_weight='balanced')
    }
    
    results = []
    best_model_name = None
    best_model_obj = None
    best_f1 = 0.0
    
    print("\n🏎️  Training & Comparing Models:")
    print("-" * 60)
    print(f"{'Model':<25} | {'Accuracy':<10} | {'F1 Score':<10}")
    print("-" * 60)
    
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        
        # Evaluate
        metrics = evaluate_model(y_test, preds)
        metrics["Model"] = name
        results.append(metrics)
        
        print(f"{name:<25} | {metrics['Accuracy']:.4f}     | {metrics['F1 Score']:.4f}")
        
        # Track Best Model (criteria: F1 Score)
        if metrics["F1 Score"] > best_f1:
            best_f1 = metrics["F1 Score"]
            best_model_name = name
            best_model_obj = model
            
    print("-" * 60)
    
    # 4. Save Best Model
    print(f"\n🏆 Best Model: {best_model_name} (F1: {best_f1:.4f})")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'Model')
    save_path = os.path.join(model_dir, "best_model.pkl")
    meta_path = os.path.join(model_dir, "model_metadata.json")
    
    print(f"💾 Saving best model to {save_path}...")
    with open(save_path, "wb") as f:
        pickle.dump(best_model_obj, f)
        
    # Save Metadata
    import json
    metadata = {
        "model_name": best_model_name,
        "accuracy": results[results.index(next(filter(lambda x: x["Model"] == best_model_name, results)))]["Accuracy"],
        "f1_score": best_f1,
        "metrics": next(filter(lambda x: x["Model"] == best_model_name, results))
    }
    
    print(f"📝 Saving metadata to {meta_path}...")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)
        
    print("✅ AutoML Complete.")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    results_df = run_automl()
    print("\nFull Results:")
    print(results_df)

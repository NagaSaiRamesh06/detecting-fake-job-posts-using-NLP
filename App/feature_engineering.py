import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from .data_processor import load_and_clean_data

def prepare_features():
    """
    Load data, perform TF-IDF vectorization, and return features and target.
    Saves the fitted TF-IDF vectorizer to the Model directory.
    """
    print("🚀 Starting Feature Engineering...")
    
    # 1. Load Cleaned Data
    df = load_and_clean_data()
    
    # 2. Setup Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, 'Model')
    os.makedirs(model_dir, exist_ok=True)
    tfidf_path = os.path.join(model_dir, 'tfidf.pkl')
    
    # 3. TF-IDF Vectorization
    print("🔠 Applying TF-IDF Vectorization...")
    # Tokenization and Stopwords removal are handled by TfidfVectorizer
    tfidf = TfidfVectorizer(
        stop_words='english', 
        max_features=5000,
        ngram_range=(1, 2) # Unigrams and Bigrams for better context
    )
    
    X = tfidf.fit_transform(df['clean_description'])
    y = df['fraudulent']
    
    print(f"✅ Feature Matrix created. Shape: {X.shape}")
    
    # 4. Save Vectorizer
    print(f"💾 Saving TF-IDF model to {tfidf_path}...")
    with open(tfidf_path, 'wb') as f:
        pickle.dump(tfidf, f)
        
    print("🎉 Feature Engineering Completed.")
    return X, y

if __name__ == "__main__":
    prepare_features()

import pandas as pd
import os
import re

def clean_text(text):
    """
    Normalize text:
    - Lowercase
    - Remove special characters and punctuation
    - Remove extra whitespace
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_and_clean_data():
    """
    Load dataset, handle missing values, and normalize text.
    Returns: Cleaned DataFrame
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, "Dataset", "fake_job_postings.csv")
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    print("⏳ Loading dataset...")
    df = pd.read_csv(dataset_path)

    # Handle missing values
    print("🧹 Handling missing values...")
    text_columns = ['title', 'company_profile', 'description', 'requirements', 'benefits']
    for col in text_columns:
        df[col] = df[col].fillna("")

    # Combine text for analysis (optional but useful)
    df['text'] = df['title'] + " " + df['description']
    
    # Remove empty descriptions (if any remaining after fillna, practically length check)
    df = df[df['description'].str.strip() != ""]

    # Text Normalization
    print("✨ Normalizing text...")
    df['clean_text'] = df['text'].apply(clean_text)
    df['clean_description'] = df['description'].apply(clean_text)

    # Target Column
    # Ensure it's integer 0/1 (Dataset usually has 0/1 but good to be safe)
    df['fraudulent'] = df['fraudulent'].astype(int)

    print(f"✅ Data loaded and cleaned. Shape: {df.shape}")
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    print(df.head())

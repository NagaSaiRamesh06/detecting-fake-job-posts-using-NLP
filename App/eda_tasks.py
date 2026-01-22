import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from .data_processor import load_and_clean_data
from sklearn.feature_extraction.text import CountVectorizer

def perform_eda():
    print("🚀 Starting EDA...")
    
    # Load Data
    df = load_and_clean_data()
    
    # Setup Output Directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'Static')
    eda_dir = os.path.join(static_dir, 'eda_plots')
    os.makedirs(eda_dir, exist_ok=True)
    
    # Set Style
    sns.set(style="whitegrid")
    
    # 1. Fake vs Real Distribution
    plt.figure(figsize=(8, 6))
    sns.countplot(x='fraudulent', data=df, palette='viridis')
    plt.title('Distribution of Real (0) vs Fake (1) Job Posts')
    plt.xlabel('Fraudulent')
    plt.ylabel('Count')
    plt.savefig(os.path.join(eda_dir, 'distribution.png'))
    plt.close()
    print("✅ Saved distribution plot.")

    # 2. Text Length Analysis
    df['desc_length'] = df['clean_description'].apply(len)
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='desc_length', hue='fraudulent', kde=True, bins=50, palette='magma')
    plt.title('Job Description Length Distribution')
    plt.xlabel('Length (characters)')
    plt.ylabel('Count')
    plt.savefig(os.path.join(eda_dir, 'text_length.png'))
    plt.close()
    print("✅ Saved text length plot.")

    # 3. Common Words in Fake Jobs
    fake_jobs = df[df['fraudulent'] == 1]['clean_description']
    
    if not fake_jobs.empty:
        vectorizer = CountVectorizer(stop_words='english', max_features=20)
        X = vectorizer.fit_transform(fake_jobs)
        word_counts = X.toarray().sum(axis=0)
        words = vectorizer.get_feature_names_out()
        
        word_freq = pd.DataFrame({'word': words, 'count': word_counts})
        word_freq = word_freq.sort_values(by='count', ascending=False)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='count', y='word', data=word_freq, palette='coolwarm')
        plt.title('Top 20 Common Words in Fake Job Postings')
        plt.xlabel('Frequency')
        plt.ylabel('Word')
        plt.savefig(os.path.join(eda_dir, 'common_words.png'))
        plt.close()
        print("✅ Saved common words plot.")
    else:
        print("⚠️ No fake jobs found for word analysis.")

    print(f"🎉 EDA Completed. Plots saved to {eda_dir}")

if __name__ == "__main__":
    perform_eda()

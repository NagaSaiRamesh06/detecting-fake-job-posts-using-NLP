import pandas as pd
from pycaret.classification import *

# Load dataset
df = pd.read_csv("../Dataset/fake_job_postings.csv")
df["description"] = df["description"].fillna("")

# Keep only required columns
data = df[["description", "fraudulent"]]

# Initialize AutoML
clf = setup(
    data=data,
    target="fraudulent",
    text_features=["description"],
    session_id=42,
    silent=True
)

# Compare models
best_model = compare_models()

# Display best model
print(best_model)

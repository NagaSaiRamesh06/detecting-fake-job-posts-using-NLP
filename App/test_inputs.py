import requests
import pandas as pd

url = "http://127.0.0.1:5000/predict"

test_jobs = [
    "Work from home and earn money fast. No experience required.",
    "Immediate hiring. Pay registration fee and start earning.",
    "Looking for Python developer with 3 years experience.",
    "Online job opportunity. Limited seats. Apply now.",
    "Software Engineer required with knowledge of Java and SQL."
]

results = []

for text in test_jobs:
    response = requests.post(url, json={"job_description": text})
    results.append({
        "Job Description": text,
        "Prediction": response.json()
    })

df = pd.DataFrame(results)
df.to_csv("prediction_results.csv", index=False)

print(df)

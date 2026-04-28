import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

print("Starting model training...")

# Load dataset
df = pd.read_csv("data/crop_data.csv")

print("Dataset loaded")

X = df.drop("label", axis=1)
y = df["label"]

model = RandomForestClassifier()
model.fit(X, y)

print("Model trained")

with open("backend/model/crop_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained successfully!")
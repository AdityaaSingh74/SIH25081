
"""
backend/ml_models/train_readiness_model.py

Train a simple RandomForestClassifier to predict readiness (binary) using generated mock data.
Saves a sklearn Pipeline to readiness_model.pkl
"""
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

def prepare_and_train(trainsets_csv="../../data/trainsets_mock.csv", out_model="../../backend/ml_models/readiness_model.pkl"):
    df = pd.read_csv(trainsets_csv)
    # create a binary label: readiness = certificate_valid AND critical_jobs_open==0
    df["label"] = ((df.get("certificate_valid",0)==1) & (df.get("critical_jobs_open",0)==0)).astype(int)
    features = ["mileage_km", "cert_days_left_rolling_stock", "cert_days_left_signalling", "cert_days_left_telecom", "branding_hours_today", "shunting_score"]
    X = df[features].fillna(0)
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    os.makedirs(os.path.dirname(out_model), exist_ok=True)
    joblib.dump(pipeline, out_model)
    print("Model saved to", out_model)
    print("Train score:", pipeline.score(X_train, y_train), "Test score:", pipeline.score(X_test, y_test))

if __name__ == "__main__":
    prepare_and_train()

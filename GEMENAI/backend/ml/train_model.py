import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, precision_score, recall_score
import joblib
import os

def train_all_models(data_path='data/processed_schedule_data.csv'):
    """
    Trains and saves both the readiness classifier and the delay regressor.
    """
    print("Starting model training...")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Processed data not found at {data_path}. Please run preprocessing first.")

    df = pd.read_csv(data_path)
    df.dropna(inplace=True)

    # --- 1. Train Readiness Model (Classifier) ---
    print("Training Readiness Classifier...")
    features_readiness = ['hour_of_day', 'is_peak_hour', 'maintenance_level', 'crew_availability', 'scheduled_load_factor']
    target_readiness = 'is_ready'
    X_r, y_r = df[features_readiness], df[target_readiness]

    if len(y_r.unique()) > 1:
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_r, y_r, test_size=0.2, random_state=42, stratify=y_r)
    else:
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_r, y_r, test_size=0.2, random_state=42)

    model_r = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=10)
    model_r.fit(X_train_r, y_train_r)
    y_pred_r = model_r.predict(X_test_r)
    metrics_r = {
        "accuracy": accuracy_score(y_test_r, y_pred_r),
        "precision": precision_score(y_test_r, y_pred_r, zero_division=0),
        "recall": recall_score(y_test_r, y_pred_r, zero_division=0)
    }
    print(f"Readiness Model - Accuracy: {metrics_r['accuracy']:.2f}, Precision: {metrics_r['precision']:.2f}, Recall: {metrics_r['recall']:.2f}")

    # --- 2. Train Delay Model (Regressor) ---
    print("Training Delay Regressor...")
    features_delay = ['hour_of_day', 'is_peak_hour', 'dwell_time_seconds', 'distance_km', 'scheduled_load_factor', 'maintenance_level']
    target_delay = 'delay_minutes'
    X_d, y_d = df[features_delay], df[target_delay]
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_d, y_d, test_size=0.2, random_state=42)

    model_d = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1)
    model_d.fit(X_train_d, y_train_d)
    y_pred_d = model_d.predict(X_test_d)
    mse_d = mean_squared_error(y_test_d, y_pred_d)
    print(f"Delay Model MSE: {mse_d:.2f}")

    # --- Save Models and Features ---
    model_dir = 'backend/ml/saved_models'
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model_r, os.path.join(model_dir, 'readiness_model.pkl'))
    joblib.dump(features_readiness, os.path.join(model_dir, 'readiness_features.pkl'))
    joblib.dump(model_d, os.path.join(model_dir, 'delay_model.pkl'))
    joblib.dump(features_delay, os.path.join(model_dir, 'delay_features.pkl'))

    print("Models and feature lists saved successfully.")
    return {
        "readiness_accuracy": metrics_r['accuracy'],
        "readiness_precision": metrics_r['precision'],
        "readiness_recall": metrics_r['recall'],
        "delay_mse": mse_d
    }

if __name__ == '__main__':
    train_all_models()


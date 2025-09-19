import pandas as pd
import numpy as np
import os

def preprocess_data(input_path='../data/kochi_metro_train_scheduling.csv'):
    """
    Loads raw data, cleans it, and engineers features for ML models.
    This creates the foundational data for the entire pipeline.
    """
    print("Starting data preprocessing...")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input data not found at {input_path}. Please place your CSV file there.")

    df = pd.read_csv(input_path)

    # --- Data Cleaning ---
    df.dropna(subset=['arrival_time', 'dwell_time_seconds', 'scheduled_load_factor', 'train_id'], inplace=True)
    df['arrival_time'] = pd.to_datetime(df['arrival_time'], format='%H:%M:%S').dt.time

    # --- Feature Engineering ---
    df['hour_of_day'] = df['arrival_time'].apply(lambda x: x.hour)
    df['is_peak_hour'] = df['hour_of_day'].apply(lambda x: 1 if (8 <= x <= 10) or (17 <= x <= 19) else 0)

    # Simulated operational features (INNOVATION)
    np.random.seed(42)
    unique_trains = df['train_id'].unique()
    maintenance_map = {train: np.random.choice([0, 1, 2], p=[0.85, 0.1, 0.05]) for train in unique_trains}
    df['maintenance_level'] = df['train_id'].map(maintenance_map) # 0: Good, 1: Minor, 2: Major

    df['crew_availability'] = np.random.choice([0, 1], size=len(df), p=[0.05, 0.95]) # 0: Not available, 1: Available

    # Target Variable 1: Readiness (`is_ready`)
    df['is_ready'] = ((df['maintenance_level'] < 2) & (df['crew_availability'] == 1)).astype(int)

    # Target Variable 2: Delay (`delay_minutes`)
    base_delay = (df['scheduled_load_factor'] * df['dwell_time_seconds'] / 45)
    maintenance_impact = df['maintenance_level'] * np.random.uniform(1, 4, size=len(df))
    random_noise = np.random.normal(0, 0.5, size=len(df))
    df['delay_minutes'] = np.maximum(0, base_delay + maintenance_impact + random_noise).round(2)

    # --- Final Selection ---
    final_cols = [
        'trip_id', 'train_id', 'station_name', 'hour_of_day', 'is_peak_hour',
        'dwell_time_seconds', 'distance_km', 'scheduled_load_factor',
        'maintenance_level', 'crew_availability', 'is_ready', 'delay_minutes'
    ]
    final_cols = [col for col in final_cols if col in df.columns]
    processed_df = df[final_cols].copy()

    # --- Save Processed Data ---
    output_path = 'data/processed_schedule_data.csv'
    processed_df.to_csv(output_path, index=False)
    print(f"Preprocessing complete. Processed data saved to {output_path}")

    return output_path, processed_df.head().to_json(orient='records')

if __name__ == '__main__':
    preprocess_data()


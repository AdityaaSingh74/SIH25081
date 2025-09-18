"""
🚇 KMRL Simple Data Generator - WORKING VERSION
Reliable data generation without complex dependencies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_simple_kmrl_data(num_trains=25):
    """Generate simple but realistic KMRL train data"""
    
    print(f"📊 Generating simple data for {num_trains} trains...")
    
    # Set seed for reproducible results
    np.random.seed(42)
    random.seed(42)
    
    # Real KMRL train names
    train_names = [
        "KRISHNA", "TAPTI", "NILA", "SARAYU", "ARUTH",
        "VAIGAI", "JHANAVI", "DHWANIL", "BHAVANI", "PADMA",
        "MANDAKINI", "YAMUNA", "PERIYAR", "KABANI", "VAAYU",
        "KAVERI", "SHIRIYA", "PAMPA", "NARMADA", "MAHE",
        "MAARUT", "SABARMATHI", "GODHAVARI", "GANGA", "PAVAN"
    ]
    
    train_data = []
    base_date = datetime.now()
    
    for i in range(num_trains):
        train_id = train_names[i] if i < len(train_names) else f"KMRL_{i+1:03d}"
        
        # Generate realistic operational data
        train_record = {
            # Basic Info
            'TrainID': train_id,
            'TrainNumber': f'T{i+1:03d}',
            'Depot': random.choice(['Muttom', 'Kalamassery']),
            'BayPositionID': random.randint(1, 20),
            
            # Fitness Status
            'RollingStockFitnessStatus': random.choice([True, False], p=[0.85, 0.15]),
            'SignallingFitnessStatus': random.choice([True, False], p=[0.90, 0.10]),
            'TelecomFitnessStatus': random.choice([True, False], p=[0.88, 0.12]),
            
            # Job Cards
            'JobCardStatus': random.choice(['close', 'open'], p=[0.7, 0.3]),
            'OpenJobCards': max(0, np.random.poisson(1.2)),
            
            # Branding
            'BrandingActive': random.choice([True, False], p=[0.3, 0.7]),
            'ExposureHoursTarget': random.choice([280, 300, 320, 340]),
            'ExposureHoursAccrued': random.randint(0, 250),
            
            # Mileage
            'TotalMileageKM': random.randint(15000, 50000),
            'MileageSinceLastServiceKM': random.randint(500, 9000),
            'MileageBalanceVariance': np.random.normal(0, 1500),
            
            # Wear and Tear
            'BrakepadWear%': np.random.uniform(15, 95),
            'HVACWear%': np.random.uniform(10, 90),
            'DoorSystemWear%': np.random.uniform(20, 85),
            'BatteryHealth%': np.random.uniform(60, 100),
            'CompressorEfficiency%': np.random.uniform(70, 98),
            
            # Operational Status
            'OperationalStatus': random.choice(['service', 'standby', 'under_maintenance'], p=[0.5, 0.35, 0.15]),
            'CleaningRequired': random.choice([True, False], p=[0.25, 0.75]),
            'ShuntingMovesRequired': max(0, np.random.poisson(1.8)),
            
            # Delay Prediction Features
            'predicted_delay_minutes': max(0, np.random.normal(3, 2)),
            'scheduled_load_factor': np.random.uniform(0.3, 1.0),
            'dwell_time_seconds': np.random.randint(30, 120),
            'distance_km': np.random.uniform(2, 25),
            'passenger_density': np.random.uniform(0.2, 1.0),
            'delay_category': 'Low',  # Will be updated
            
            # Performance Metrics
            'OnTimePerformance%': np.random.uniform(85, 99),
            'ReliabilityScore': np.random.uniform(0.80, 0.98),
            'FuelEfficiency': np.random.uniform(0.8, 1.2),
            
            # Calculated Score (Simple)
            'Score': 0  # Will be calculated
        }
        
        # Calculate delay category
        delay = train_record['predicted_delay_minutes']
        if delay < 5:
            train_record['delay_category'] = 'Low'
        elif delay < 10:
            train_record['delay_category'] = 'Medium'
        else:
            train_record['delay_category'] = 'High'
        
        # Calculate simple score
        score = 50  # Base score
        
        # Fitness bonuses
        if train_record['RollingStockFitnessStatus']:
            score += 15
        if train_record['SignallingFitnessStatus']:
            score += 10
        if train_record['TelecomFitnessStatus']:
            score += 10
        
        # Job card penalties
        if train_record['JobCardStatus'] == 'close':
            score += 10
        score -= train_record['OpenJobCards'] * 3
        
        # Wear penalties
        score -= (train_record['BrakepadWear%'] - 50) * 0.1
        score -= (train_record['HVACWear%'] - 50) * 0.1
        
        # Operational bonus
        if train_record['OperationalStatus'] == 'service':
            score += 5
        elif train_record['OperationalStatus'] == 'standby':
            score += 3
        
        train_record['Score'] = max(0, min(100, score))
        
        train_data.append(train_record)
    
    df = pd.DataFrame(train_data)
    
    print(f"✅ Generated {len(df)} train records successfully")
    print(f"   - Service: {len(df[df['OperationalStatus'] == 'service'])}")
    print(f"   - Standby: {len(df[df['OperationalStatus'] == 'standby'])}")
    print(f"   - Maintenance: {len(df[df['OperationalStatus'] == 'under_maintenance'])}")
    
    return df

def save_data(df, filename='simple_kmrl_data.csv'):
    """Save data to file"""
    try:
        # Ensure directory exists
        os.makedirs('data/sample_data', exist_ok=True)
        
        file_path = f'data/sample_data/{filename}'
        df.to_csv(file_path, index=False)
        
        print(f"📁 Data saved to: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"❌ Error saving data: {str(e)}")
        return None

# Quick test function
if __name__ == "__main__":
    print("🧪 Testing Simple Data Generator")
    print("="*50)
    
    # Generate test data
    test_df = generate_simple_kmrl_data(10)
    
    # Show sample
    print("\nSample Data:")
    print(test_df[['TrainID', 'OperationalStatus', 'Score', 'predicted_delay_minutes']].head())
    
    # Save test data
    save_data(test_df, 'test_data.csv')
    
    print("\n✅ Simple Data Generator Test Complete!")
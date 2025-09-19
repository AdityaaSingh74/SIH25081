"""
🚇 KMRL Train Readiness Model
ML model for assessing train operational readiness

Features:
- Fitness status classification
- Operational readiness scoring
- Maintenance priority prediction
- Multi-factor analysis
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TrainReadinessModel:
    def __init__(self):
        self.models = {}
        self.feature_names = []
        self.is_trained = False
        
        # Key features for readiness assessment
        self.readiness_features = [
            'BrakepadWear%',
            'HVACWear%', 
            'OpenJobCards',
            'TotalMileageKM',
            'MileageSinceLastServiceKM',
            'BatteryHealth%',
            'CompressorEfficiency%'
        ]
    
    def prepare_features(self, df):
        """Prepare features for training/prediction"""
        feature_df = pd.DataFrame()
        
        # Basic wear metrics
        feature_df['brake_wear'] = df.get('BrakepadWear%', 50)
        feature_df['hvac_wear'] = df.get('HVACWear%', 40) 
        feature_df['battery_health'] = df.get('BatteryHealth%', 85)
        feature_df['compressor_efficiency'] = df.get('CompressorEfficiency%', 90)
        
        # Maintenance indicators
        feature_df['open_job_cards'] = df.get('OpenJobCards', 0)
        feature_df['total_mileage'] = df.get('TotalMileageKM', 25000)
        feature_df['service_mileage'] = df.get('MileageSinceLastServiceKM', 3000)
        
        # Derived features
        feature_df['total_wear_score'] = feature_df['brake_wear'] + feature_df['hvac_wear']
        feature_df['health_score'] = (feature_df['battery_health'] + feature_df['compressor_efficiency']) / 2
        feature_df['maintenance_urgency'] = feature_df['open_job_cards'] * 10 + (feature_df['service_mileage'] / 1000)
        
        # Fitness status indicators
        feature_df['rolling_fitness'] = df.get('RollingStockFitnessStatus', True).astype(int)
        feature_df['signalling_fitness'] = df.get('SignallingFitnessStatus', True).astype(int)
        feature_df['telecom_fitness'] = df.get('TelecomFitnessStatus', True).astype(int)
        
        # Operational indicators
        feature_df['cleaning_required'] = df.get('CleaningRequired', False).astype(int)
        feature_df['job_status_open'] = (df.get('JobCardStatus', 'close') == 'open').astype(int)
        
        return feature_df
    
    def create_targets(self, df, features_df):
        """Create target variables for training"""
        targets = {}
        
        # Operational readiness (binary)
        readiness_conditions = [
            features_df['brake_wear'] < 85,
            features_df['hvac_wear'] < 90, 
            features_df['open_job_cards'] < 3,
            features_df['rolling_fitness'] == 1,
            features_df['signalling_fitness'] == 1,
            features_df['telecom_fitness'] == 1
        ]
        targets['operational_ready'] = np.all(readiness_conditions, axis=0).astype(int)
        
        # Readiness score (continuous 0-100)
        readiness_score = (
            (100 - features_df['brake_wear']) * 0.2 +
            (100 - features_df['hvac_wear']) * 0.2 +
            features_df['health_score'] * 0.3 +
            (features_df['rolling_fitness'] * 100) * 0.2 +
            np.maximum(0, 100 - features_df['open_job_cards'] * 10) * 0.1
        )
        targets['readiness_score'] = np.clip(readiness_score, 0, 100)
        
        # Maintenance priority (0=low, 1=medium, 2=high)
        maintenance_priority = np.zeros(len(features_df))
        maintenance_priority[features_df['total_wear_score'] > 150] = 1  # Medium
        maintenance_priority[
            (features_df['brake_wear'] > 85) | 
            (features_df['hvac_wear'] > 90) |
            (features_df['open_job_cards'] >= 3)
        ] = 2  # High
        targets['maintenance_priority'] = maintenance_priority.astype(int)
        
        return targets
    
    def train_model(self, data_path=None, df=None):
        """Train the readiness assessment models"""
        try:
            if df is None:
                if data_path and os.path.exists(data_path):
                    df = pd.read_csv(data_path)
                else:
                    df = self.generate_sample_data()
            
            print("🚇 Training Train Readiness Models...")
            
            # Prepare features and targets
            features_df = self.prepare_features(df)
            targets = self.create_targets(df, features_df)
            
            self.feature_names = list(features_df.columns)
            X = features_df.values
            
            # Split data
            X_train, X_test, y_ready_train, y_ready_test = train_test_split(
                X, targets['operational_ready'], test_size=0.2, random_state=42
            )
            
            # Train operational readiness classifier
            self.models['readiness_classifier'] = RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=10
            )
            self.models['readiness_classifier'].fit(X_train, y_ready_train)
            
            # Train readiness score regressor
            self.models['readiness_regressor'] = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=12
            )
            self.models['readiness_regressor'].fit(X_train, targets['readiness_score'][:len(X_train)])
            
            # Train maintenance priority classifier
            self.models['maintenance_classifier'] = RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=8
            )
            self.models['maintenance_classifier'].fit(X_train, targets['maintenance_priority'][:len(X_train)])
            
            # Evaluate models
            ready_accuracy = accuracy_score(y_ready_test, 
                self.models['readiness_classifier'].predict(X_test))
            
            score_mae = np.mean(np.abs(
                targets['readiness_score'][len(X_train):] - 
                self.models['readiness_regressor'].predict(X_test)
            ))
            
            maint_accuracy = accuracy_score(
                targets['maintenance_priority'][len(X_train):],
                self.models['maintenance_classifier'].predict(X_test)
            )
            
            self.is_trained = True
            
            print(f"✅ Models trained successfully!")
            print(f"   - Readiness Accuracy: {ready_accuracy:.3f}")
            print(f"   - Score MAE: {score_mae:.3f}")
            print(f"   - Maintenance Accuracy: {maint_accuracy:.3f}")
            
            # Save models
            self.save_models()
            
            return {
                'readiness_accuracy': ready_accuracy,
                'score_mae': score_mae,
                'maintenance_accuracy': maint_accuracy,
                'models_count': len(self.models)
            }
            
        except Exception as e:
            print(f"❌ Error training readiness models: {str(e)}")
            return {'error': str(e)}
    
    def predict_readiness(self, train_data):
        """Predict train readiness metrics"""
        if not self.is_trained:
            self.load_models()
        
        try:
            # Prepare features
            if isinstance(train_data, dict):
                train_df = pd.DataFrame([train_data])
            else:
                train_df = train_data
            
            features_df = self.prepare_features(train_df)
            X = features_df.values
            
            predictions = {}
            
            # Operational readiness
            if 'readiness_classifier' in self.models:
                ready_prob = self.models['readiness_classifier'].predict_proba(X)[0]
                predictions['operational_ready'] = bool(self.models['readiness_classifier'].predict(X)[0])
                predictions['readiness_confidence'] = float(max(ready_prob))
            
            # Readiness score
            if 'readiness_regressor' in self.models:
                predictions['readiness_score'] = float(self.models['readiness_regressor'].predict(X)[0])
            
            # Maintenance priority
            if 'maintenance_classifier' in self.models:
                maint_pred = self.models['maintenance_classifier'].predict(X)[0]
                maint_labels = ['Low', 'Medium', 'High']
                predictions['maintenance_priority'] = maint_labels[int(maint_pred)]
                predictions['maintenance_priority_numeric'] = int(maint_pred)
            
            # Add recommendations
            predictions['recommendations'] = self.generate_recommendations(predictions, features_df.iloc[0])
            
            return predictions
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def generate_recommendations(self, predictions, features):
        """Generate actionable recommendations"""
        recommendations = []
        
        readiness_score = predictions.get('readiness_score', 50)
        maintenance_priority = predictions.get('maintenance_priority', 'Low')
        
        if not predictions.get('operational_ready', True):
            recommendations.append("Train not ready for service - address fitness issues")
        
        if readiness_score < 60:
            recommendations.append("Low readiness score - schedule comprehensive inspection")
        
        if maintenance_priority == 'High':
            recommendations.extend([
                "High maintenance priority - immediate action required",
                "Schedule emergency maintenance window"
            ])
        elif maintenance_priority == 'Medium':
            recommendations.append("Medium priority - schedule maintenance within 48 hours")
        
        # Specific component recommendations
        if features['brake_wear'] > 80:
            recommendations.append("Brake pad replacement recommended")
        
        if features['hvac_wear'] > 85:
            recommendations.append("HVAC system maintenance required")
        
        if features['battery_health'] < 70:
            recommendations.append("Battery health check and possible replacement")
        
        if features['open_job_cards'] >= 2:
            recommendations.append(f"Address {int(features['open_job_cards'])} open job cards")
        
        if not recommendations:
            recommendations.append("Train in good condition - routine monitoring sufficient")
        
        return recommendations
    
    def get_feature_importance(self):
        """Get feature importance from trained models"""
        if not self.is_trained:
            return {}
        
        importance_dict = {}
        
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance_dict[model_name] = dict(zip(
                    self.feature_names,
                    model.feature_importances_
                ))
        
        return importance_dict
    
    def save_models(self):
        """Save trained models"""
        model_dir = 'backend/models/saved_models'
        os.makedirs(model_dir, exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, f'{model_dir}/readiness_{name}.pkl')
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'models': list(self.models.keys()),
            'trained_at': datetime.now().isoformat()
        }
        
        import json
        with open(f'{model_dir}/readiness_metadata.json', 'w') as f:
            json.dump(metadata, f)
    
    def load_models(self):
        """Load saved models"""
        model_dir = 'backend/models/saved_models'
        
        try:
            # Load metadata
            with open(f'{model_dir}/readiness_metadata.json', 'r') as f:
                metadata = json.load(f)
            
            self.feature_names = metadata['feature_names']
            
            # Load models
            for model_name in metadata['models']:
                model_path = f'{model_dir}/readiness_{model_name}.pkl'
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
            
            self.is_trained = True
            print(f"✅ Loaded {len(self.models)} readiness models")
            
        except Exception as e:
            print(f"⚠️  Could not load saved models: {str(e)}")
            self.is_trained = False
    
    def generate_sample_data(self):
        """Generate sample data for testing"""
        np.random.seed(42)
        
        sample_data = []
        for i in range(100):  # 100 sample records
            record = {
                'TrainID': f'TRAIN_{i:03d}',
                'BrakepadWear%': np.random.uniform(20, 95),
                'HVACWear%': np.random.uniform(15, 90),
                'BatteryHealth%': np.random.uniform(60, 100),
                'CompressorEfficiency%': np.random.uniform(70, 98),
                'OpenJobCards': np.random.poisson(1.5),
                'TotalMileageKM': np.random.randint(15000, 50000),
                'MileageSinceLastServiceKM': np.random.randint(500, 9000),
                'RollingStockFitnessStatus': np.random.choice([True, False], p=[0.85, 0.15]),
                'SignallingFitnessStatus': np.random.choice([True, False], p=[0.90, 0.10]),
                'TelecomFitnessStatus': np.random.choice([True, False], p=[0.88, 0.12]),
                'CleaningRequired': np.random.choice([True, False], p=[0.25, 0.75]),
                'JobCardStatus': np.random.choice(['close', 'open'], p=[0.7, 0.3])
            }
            
            sample_data.append(record)
        
        return pd.DataFrame(sample_data)

# Test the readiness model
if __name__ == "__main__":
    print("🚇 Testing KMRL Train Readiness Model")
    print("="*50)
    
    model = TrainReadinessModel()
    
    # Train with sample data
    training_results = model.train_model()
    print(f"Training Results: {training_results}")
    
    # Test prediction
    sample_train = {
        'BrakepadWear%': 65,
        'HVACWear%': 45,
        'BatteryHealth%': 85,
        'OpenJobCards': 1,
        'RollingStockFitnessStatus': True,
        'SignallingFitnessStatus': True,
        'TelecomFitnessStatus': True
    }
    
    prediction = model.predict_readiness(sample_train)
    print(f"\nSample Prediction: {prediction}")
    
    print("\n✅ Train Readiness Model Test Complete!")
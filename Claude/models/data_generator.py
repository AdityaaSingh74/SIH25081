import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from faker import Faker

fake = Faker()

class DataGenerator:
    def __init__(self):
        self.routes = ['Red Line', 'Blue Line', 'Green Line', 'Yellow Line', 'Purple Line']
        self.depots = ['Aluva Depot', 'Thripunithura Depot', 'Kakkanad Depot']
        self.weather_conditions = ['Clear', 'Rainy', 'Cloudy', 'Foggy', 'Stormy']
        self.maintenance_types = [
            'Routine Inspection', 'Brake System', 'Engine Service', 'Electrical Check',
            'AC Service', 'Door Mechanism', 'Safety Systems', 'Wheel Replacement'
        ]
        
    def generate_train_fleet(self, num_trains=30):
        """Generate realistic train fleet data"""
        trains = []
        
        for i in range(num_trains):
            train_id = f"KMRL-{i+1:03d}"
            
            # Assign to routes and depots
            route = random.choice(self.routes)
            depot = random.choice(self.depots)
            
            # Generate realistic operational parameters
            mechanical_score = np.random.beta(8, 2)  # Skewed towards higher scores
            energy_consumption = np.random.normal(75, 15)  # Mean 75 kWh with std 15
            energy_consumption = max(30, min(120, energy_consumption))  # Clamp to realistic range
            
            # Passenger load based on time and route popularity
            base_load = {'Red Line': 180, 'Blue Line': 150, 'Green Line': 120, 
                        'Yellow Line': 100, 'Purple Line': 90}.get(route, 120)
            passenger_load = int(np.random.normal(base_load, 30))
            passenger_load = max(0, min(300, passenger_load))
            
            # Maintenance dates
            last_maintenance = fake.date_between(start_date='-90d', end_date='today')
            days_until_next = np.random.exponential(30) + 10  # Exponential distribution, min 10 days
            next_maintenance = datetime.now().date() + timedelta(days=int(days_until_next))
            
            # Brand hours (advertisement display hours remaining)
            brand_hours_remaining = np.random.uniform(0, 12)
            
            # Crew assignment (80% have crew)
            crew_id = f"CREW-{random.randint(1000, 9999)}" if random.random() < 0.8 else None
            
            # Current location (for running trains)
            stations = [
                'Aluva', 'Pulivasal', 'Thripunithura', 'Ernakulam South', 
                'Mg Road', 'Town Hall', 'Kaloor', 'JLN Stadium', 'Kakkanad'
            ]
            current_location = random.choice(stations)
            
            # Determine status based on conditions
            if mechanical_score < 0.5 or days_until_next < 7:
                status = 'Maintenance'
            elif mechanical_score < 0.7 or energy_consumption > 100:
                status = 'Held'
            elif random.random() < 0.1:
                status = 'Ready'
            else:
                status = 'Running'
            
            # Calculate readiness score
            readiness_components = [
                mechanical_score * 0.4,
                min(1.0, (90 - (datetime.now().date() - last_maintenance).days) / 90) * 0.25,
                min(1.0, (120 - energy_consumption) / 120) * 0.2,
                min(1.0, brand_hours_remaining / 8) * 0.1,
                (1.0 if crew_id else 0.5) * 0.05
            ]
            readiness_score = sum(readiness_components)
            
            train = {
                'train_id': train_id,
                'route': route,
                'depot': depot,
                'status': status,
                'current_location': current_location,
                'passenger_load': passenger_load,
                'energy_consumption': round(energy_consumption, 2),
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance,
                'crew_id': crew_id,
                'brand_hours_remaining': round(brand_hours_remaining, 2),
                'mechanical_score': round(mechanical_score, 3),
                'readiness_score': round(readiness_score, 3)
            }
            
            trains.append(train)
        
        return trains
    
    def generate_historical_schedules(self, num_records=100000):
        """Generate comprehensive historical schedule data"""
        schedules = []
        
        # Generate data for the past year
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_records):
            schedule_id = f"SCH-{i+1:06d}"
            
            # Random date in the past year
            random_days = random.randint(0, 365)
            schedule_date = start_date + timedelta(days=random_days)
            
            # Random time of day (5 AM to 11 PM)
            hour = random.randint(5, 23)
            minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
            
            scheduled_departure = schedule_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Trip duration based on route
            route = random.choice(self.routes)
            base_duration = {'Red Line': 45, 'Blue Line': 38, 'Green Line': 42, 
                           'Yellow Line': 35, 'Purple Line': 40}.get(route, 40)
            
            # Add variation
            duration_minutes = int(np.random.normal(base_duration, 5))
            duration_minutes = max(20, min(60, duration_minutes))
            
            scheduled_arrival = scheduled_departure + timedelta(minutes=duration_minutes)
            
            # Generate delays based on realistic factors
            delay_probability = self._calculate_delay_probability(schedule_date, hour, route)
            
            if random.random() < delay_probability:
                # Generate delay based on multiple factors
                base_delay = np.random.exponential(3) + 1  # Exponential distribution
                
                # Weather impact
                weather = random.choice(self.weather_conditions)
                weather_multiplier = {
                    'Clear': 1.0, 'Cloudy': 1.1, 'Rainy': 1.5, 
                    'Foggy': 1.8, 'Stormy': 2.5
                }.get(weather, 1.0)
                
                # Peak hour impact
                peak_multiplier = 1.5 if hour in [7, 8, 9, 17, 18, 19] else 1.0
                
                # Weekend impact (less delay)
                weekend_multiplier = 0.7 if schedule_date.weekday() in [5, 6] else 1.0
                
                delay_minutes = int(base_delay * weather_multiplier * peak_multiplier * weekend_multiplier)
                delay_minutes = min(delay_minutes, 30)  # Cap at 30 minutes
            else:
                delay_minutes = 0
                weather = 'Clear'  # Assume clear weather for on-time trains
            
            actual_departure = scheduled_departure + timedelta(minutes=delay_minutes)
            actual_arrival = scheduled_arrival + timedelta(minutes=delay_minutes)
            
            # Passenger load based on time, day, route, and weather
            base_load = {'Red Line': 180, 'Blue Line': 150, 'Green Line': 120, 
                        'Yellow Line': 100, 'Purple Line': 90}.get(route, 120)
            
            # Time of day factor
            if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
                load_multiplier = 1.8
            elif hour in [10, 11, 14, 15, 16]:  # Off-peak but busy
                load_multiplier = 1.2
            elif hour in [6, 20, 21, 22]:  # Early morning / evening
                load_multiplier = 0.8
            else:  # Late night / very early
                load_multiplier = 0.4
            
            # Day of week factor
            if schedule_date.weekday() < 5:  # Weekday
                dow_multiplier = 1.0
            elif schedule_date.weekday() == 5:  # Saturday
                dow_multiplier = 0.8
            else:  # Sunday
                dow_multiplier = 0.6
            
            # Weather factor
            weather_load_factor = {
                'Clear': 1.0, 'Cloudy': 1.0, 'Rainy': 1.3, 
                'Foggy': 0.9, 'Stormy': 0.7
            }.get(weather, 1.0)
            
            passenger_load = int(base_load * load_multiplier * dow_multiplier * weather_load_factor)
            passenger_load += int(np.random.normal(0, 20))  # Add noise
            passenger_load = max(0, min(300, passenger_load))
            
            # Generate train_id (one of our fleet)
            train_id = f"KMRL-{random.randint(1, 30):03d}"
            
            # Status
            if delay_minutes > 15:
                status = 'Delayed'
            elif delay_minutes > 0:
                status = 'Minor Delay'
            else:
                status = 'On Time'
            
            schedule = {
                'schedule_id': schedule_id,
                'train_id': train_id,
                'route': route,
                'scheduled_departure': scheduled_departure,
                'scheduled_arrival': scheduled_arrival,
                'actual_departure': actual_departure,
                'actual_arrival': actual_arrival,
                'delay_minutes': delay_minutes,
                'passenger_load': passenger_load,
                'weather_condition': weather,
                'status': status
            }
            
            schedules.append(schedule)
        
        return schedules
    
    def _calculate_delay_probability(self, date, hour, route):
        """Calculate probability of delay based on various factors"""
        base_probability = 0.15  # Base 15% delay rate
        
        # Peak hour increase
        if hour in [7, 8, 9, 17, 18, 19]:
            base_probability *= 1.8
        
        # Day of week factor
        if date.weekday() < 5:  # Weekday
            base_probability *= 1.2
        
        # Route factor (some routes more prone to delays)
        route_factor = {
            'Red Line': 1.1,  # Busiest route
            'Blue Line': 1.0,
            'Green Line': 0.9,
            'Yellow Line': 0.8,
            'Purple Line': 0.7
        }.get(route, 1.0)
        
        base_probability *= route_factor
        
        # Seasonal factor
        if date.month in [6, 7, 8, 9]:  # Monsoon season
            base_probability *= 1.4
        
        return min(base_probability, 0.4)  # Cap at 40%
    
    def generate_maintenance_records(self, num_records=5000):
        """Generate maintenance history records"""
        maintenance_records = []
        
        for i in range(num_records):
            maintenance_id = f"MAINT-{i+1:05d}"
            train_id = f"KMRL-{random.randint(1, 30):03d}"
            
            # Maintenance type
            maintenance_type = random.choice(self.maintenance_types)
            
            # Scheduled date (past year)
            scheduled_date = fake.date_between(start_date='-365d', end_date='today')
            
            # Completion status (85% completed)
            if random.random() < 0.85:
                status = 'Completed'
                completion_date = scheduled_date + timedelta(days=random.randint(0, 3))
                
                # Duration based on maintenance type
                duration_hours = {
                    'Routine Inspection': np.random.normal(4, 1),
                    'Brake System': np.random.normal(8, 2),
                    'Engine Service': np.random.normal(12, 3),
                    'Electrical Check': np.random.normal(6, 1.5),
                    'AC Service': np.random.normal(5, 1),
                    'Door Mechanism': np.random.normal(3, 0.5),
                    'Safety Systems': np.random.normal(10, 2),
                    'Wheel Replacement': np.random.normal(16, 4)
                }.get(maintenance_type, 6)
                
                duration_hours = max(1, duration_hours)
                
                # Cost based on type and duration
                base_cost = {
                    'Routine Inspection': 5000,
                    'Brake System': 25000,
                    'Engine Service': 50000,
                    'Electrical Check': 15000,
                    'AC Service': 12000,
                    'Door Mechanism': 8000,
                    'Safety Systems': 30000,
                    'Wheel Replacement': 75000
                }.get(maintenance_type, 10000)
                
                cost = base_cost * (0.8 + 0.4 * random.random())  # ±20% variation
                
            else:
                status = random.choice(['Scheduled', 'In Progress', 'Delayed'])
                completion_date = None
                duration_hours = None
                cost = None
            
            # Priority
            priority = random.choice(['Low', 'Medium', 'High', 'Critical'])
            if maintenance_type in ['Safety Systems', 'Brake System']:
                priority = random.choice(['High', 'Critical'])
            
            # Description
            descriptions = {
                'Routine Inspection': 'Regular scheduled inspection of all systems',
                'Brake System': 'Brake pad replacement and system calibration',
                'Engine Service': 'Complete engine overhaul and performance optimization',
                'Electrical Check': 'Electrical system diagnostics and repairs',
                'AC Service': 'Air conditioning system maintenance and filter replacement',
                'Door Mechanism': 'Door alignment and safety sensor calibration',
                'Safety Systems': 'Emergency brake and safety protocol verification',
                'Wheel Replacement': 'Wheel set replacement due to wear'
            }
            
            description = descriptions.get(maintenance_type, 'General maintenance work')
            
            maintenance = {
                'maintenance_id': maintenance_id,
                'train_id': train_id,
                'maintenance_type': maintenance_type,
                'scheduled_date': scheduled_date,
                'completion_date': completion_date,
                'duration_hours': round(duration_hours, 2) if duration_hours else None,
                'cost': round(cost, 2) if cost else None,
                'priority': priority,
                'description': description,
                'status': status
            }
            
            maintenance_records.append(maintenance)
        
        return maintenance_records
    
    def validate_and_clean_data(self, df, data_type):
        """Validate and clean uploaded data"""
        validated_df = df.copy()
        
        if data_type == 'schedules':
            # Required columns
            required_cols = ['train_id', 'route', 'scheduled_departure']
            
            # Ensure required columns exist
            for col in required_cols:
                if col not in validated_df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Clean and validate data
            validated_df['scheduled_departure'] = pd.to_datetime(validated_df['scheduled_departure'])
            validated_df['delay_minutes'] = validated_df.get('delay_minutes', 0).fillna(0)
            validated_df['passenger_load'] = validated_df.get('passenger_load', 0).fillna(0)
            
            # Remove invalid records
            validated_df = validated_df[validated_df['delay_minutes'] >= 0]
            validated_df = validated_df[validated_df['passenger_load'] >= 0]
            
        elif data_type == 'trains':
            required_cols = ['train_id', 'route', 'status']
            
            for col in required_cols:
                if col not in validated_df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Validate status values
            valid_statuses = ['Running', 'Ready', 'Held', 'Maintenance']
            validated_df = validated_df[validated_df['status'].isin(valid_statuses)]
            
        elif data_type == 'maintenance':
            required_cols = ['train_id', 'maintenance_type', 'scheduled_date']
            
            for col in required_cols:
                if col not in validated_df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            validated_df['scheduled_date'] = pd.to_datetime(validated_df['scheduled_date'])
        
        return validated_df
    
    def calculate_quality_score(self, df):
        """Calculate data quality score"""
        score = 100.0
        
        # Penalize missing values
        missing_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        score -= missing_percentage * 2
        
        # Penalize duplicate records
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        score -= duplicate_percentage * 3
        
        # Bonus for recent data
        if 'scheduled_departure' in df.columns:
            df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'])
            recent_data_percentage = (
                df[df['scheduled_departure'] >= datetime.now() - timedelta(days=30)].shape[0] / len(df)
            ) * 100
            score += recent_data_percentage * 0.5
        
        return max(0, min(100, score))
"""
🚇 KMRL Multi-Objective Optimizer (MOO)
Advanced scoring system inspired by user's SIH25081 MOO implementation

Features:
- 15+ factor comprehensive scoring
- Real-time constraint handling
- Weighted multi-objective optimization
- Ranking system with tie-breakers
"""

import pandas as pd
import numpy as np
from pulp import *
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MOOOptimizer:
    def __init__(self):
        self.MILEAGE_LIMIT_BEFORE_SERVICE = 45000  # Enhanced threshold
        self.SERVICE_QUOTA = 13
        self.MAX_MAINTENANCE_SLOTS = 8
        self.MAX_CLEANING_SLOTS = 5
        
        # Scoring weights (tunable)
        self.weights = {
            'fitness_status': 0.25,      # Safety first
            'job_card_status': 0.20,     # Operational readiness
            'branding_priority': 0.15,   # Revenue generation
            'mileage_factors': 0.15,     # Fleet balancing
            'wear_tear': 0.10,           # Preventive maintenance
            'operational_status': 0.10,  # Current state
            'efficiency_factors': 0.05   # Optimization bonuses
        }
    
    def calculate_comprehensive_score(self, row):
        """Enhanced scoring system with 15+ factors"""
        score = 0.0
        
        # === SAFETY & FITNESS (Critical - 25%) ===
        fitness_score = 0
        
        # Rolling stock fitness (most critical)
        if row.get("RollingStockFitnessStatus", True):
            fitness_score += 15
        else:
            return 0  # Cannot operate without fitness
        
        # Signalling fitness
        if row.get("SignallingFitnessStatus", True):
            fitness_score += 10
        else:
            return 0  # Safety critical
        
        # Telecom fitness
        if row.get("TelecomFitnessStatus", True):
            fitness_score += 10
        else:
            return 0  # Communication critical
        
        score += fitness_score * self.weights['fitness_status']
        
        # === JOB CARD MANAGEMENT (20%) ===
        job_score = 0
        
        # Job card status
        job_status = str(row.get("JobCardStatus", "close")).strip().lower()
        if job_status == "close":
            job_score += 8
        else:
            job_score -= 5  # Penalty for open jobs
        
        # Open job cards (fewer is better)
        open_jobs = max(0, row.get("OpenJobCards", 0))
        job_score += max(0, 7 - (open_jobs * 2))
        
        # Job priority handling
        if hasattr(row, 'JobCardPriority'):
            priority = row.get("JobCardPriority", 0)
            job_score -= priority * 1.5  # Higher priority = more urgent
        
        score += job_score * self.weights['job_card_status']
        
        # === BRANDING & REVENUE (15%) ===
        branding_score = 0
        
        if row.get("BrandingActive", False):
            branding_score += 5
            
            # Exposure hours calculation
            target_hours = row.get("ExposureHoursTarget", 300)
            accrued_hours = row.get("ExposureHoursAccrued", 0)
            
            if target_hours > 0:
                completion_ratio = accrued_hours / target_hours
                # Reward incomplete campaigns (need more exposure)
                branding_score += max(0, 10 * (1 - completion_ratio))
        
        score += branding_score * self.weights['branding_priority']
        
        # === MILEAGE MANAGEMENT (15%) ===
        mileage_score = 0
        
        # Total mileage bands
        total_mileage = row.get("TotalMileageKM", 25000)
        if total_mileage < 30000:  # Newer trains preferred
            mileage_score += 8
        elif total_mileage < 40000:  # Medium age
            mileage_score += 5
        else:  # Older trains
            mileage_score += 2
        
        # Mileage since last service
        service_mileage = row.get("MileageSinceLastServiceKM", 5000)
        if service_mileage < 5000:
            mileage_score += 5  # Recently serviced
        elif service_mileage < 8000:
            mileage_score += 3  # Moderate
        else:
            mileage_score -= 2  # Needs service soon
        
        # Mileage balance variance (fleet optimization)
        mileage_variance = abs(row.get("MileageBalanceVariance", 0))
        mileage_balance_bonus = max(0, 5 - (mileage_variance / 1000))
        mileage_score += mileage_balance_bonus
        
        score += mileage_score * self.weights['mileage_factors']
        
        # === WEAR & TEAR (10%) ===
        wear_score = 0
        
        # Brake pad wear (0-100%)
        brake_wear = row.get("BrakepadWear%", 50)
        wear_score += max(0, 8 - (brake_wear / 12.5))  # Linear decrease
        
        # HVAC wear (0-100%)
        hvac_wear = row.get("HVACWear%", 40)
        wear_score += max(0, 6 - (hvac_wear / 16.7))  # Linear decrease
        
        # Additional wear factors
        if hasattr(row, 'DoorSystemWear%'):
            door_wear = row.get("DoorSystemWear%", 30)
            wear_score += max(0, 4 - (door_wear / 25))
        
        score += wear_score * self.weights['wear_tear']
        
        # === OPERATIONAL STATUS (10%) ===
        ops_score = 0
        
        current_status = str(row.get("OperationalStatus", "standby")).strip().lower()
        if current_status == "in_service":
            ops_score += 5  # Prefer trains already operational
        elif current_status == "standby":
            ops_score += 3  # Ready to deploy
        else:  # under_maintenance
            ops_score += 1  # Needs evaluation
        
        # Cleaning status
        if not row.get("CleaningRequired", True):
            ops_score += 3  # Clean trains preferred
        
        # Shunting efficiency
        shunting_moves = row.get("ShuntingMovesRequired", 2)
        ops_score += max(0, 4 - shunting_moves)  # Fewer moves = better
        
        score += ops_score * self.weights['operational_status']
        
        # === EFFICIENCY FACTORS (5%) ===
        efficiency_score = 0
        
        # Bay position optimization
        bay_position = row.get("BayPositionID", 10)
        if bay_position <= 5:  # Closer bays preferred
            efficiency_score += 2
        
        # Depot efficiency
        depot = row.get("Depot", "Main")
        if depot == "Main":
            efficiency_score += 1
        
        # Historical performance
        if hasattr(row, 'ReliabilityScore'):
            reliability = row.get("ReliabilityScore", 0.85)
            efficiency_score += reliability * 3
        
        score += efficiency_score * self.weights['efficiency_factors']
        
        # === BONUS/PENALTY ADJUSTMENTS ===
        
        # Emergency readiness bonus
        if (score > 70 and 
            row.get("RollingStockFitnessStatus", True) and 
            row.get("JobCardStatus", "close").lower() == "close"):
            score += 5
        
        # Critical maintenance penalty
        if (brake_wear > 85 or hvac_wear > 90 or open_jobs >= 3):
            score -= 10  # Should go to maintenance
        
        # Peak readiness bonus (high-scoring, ready trains)
        if score > 80 and current_status != "under_maintenance":
            score += 3
        
        return round(max(0, score), 2)  # Ensure non-negative
    
    def optimize(self, data_path=None, constraints=None):
        """Run Multi-Objective Optimization"""
        try:
            print("📊 Starting Multi-Objective Optimization...")
            
            # Load or generate data
            if data_path and pd.io.common.file_exists(data_path):
                df = pd.read_csv(data_path)
                print(f"   Loaded data: {len(df)} trains")
            else:
                df = self.generate_sample_data()
                print("   Using generated sample data")
            
            # Update constraints
            if constraints:
                self.SERVICE_QUOTA = constraints.get('service_quota', self.SERVICE_QUOTA)
                self.MAX_MAINTENANCE_SLOTS = constraints.get('max_maintenance', self.MAX_MAINTENANCE_SLOTS)
            
            # Calculate comprehensive scores
            print("   Calculating comprehensive scores...")
            df["Score"] = df.apply(self.calculate_comprehensive_score, axis=1)
            
            # Create tie-breaker columns
            df = self.add_tie_breakers(df)
            
            # Optimization using PuLP
            print("   Running linear programming optimization...")
            optimized_df = self.solve_with_pulp(df)
            
            # Fallback to ranking if LP fails
            if optimized_df is None:
                print("   LP failed, using ranking approach...")
                optimized_df = self.rank_based_optimization(df)
            
            # Add metadata
            optimized_df['OptimizationMethod'] = 'Multi-Objective Optimization'
            optimized_df['OptimizationTimestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print("✅ Multi-Objective Optimization complete!")
            self.print_optimization_summary(optimized_df)
            
            return optimized_df
            
        except Exception as e:
            print(f"❌ MOO optimization failed: {str(e)}")
            return self.create_fallback_solution()
    
    def solve_with_pulp(self, df):
        """Solve using PuLP linear programming"""
        try:
            # Decision variables: x[i] = 1 if train i is selected for service
            train_indices = df.index.tolist()
            x = pulp.LpVariable.dicts("train", train_indices, cat='Binary')
            
            # Problem setup
            prob = LpProblem("KMRL_Train_Selection", LpMaximize)
            
            # Objective: Maximize total score
            prob += lpSum([df.loc[i, 'Score'] * x[i] for i in train_indices])
            
            # Constraints
            
            # 1. Service quota constraint
            prob += lpSum([x[i] for i in train_indices]) == self.SERVICE_QUOTA
            
            # 2. Fitness constraints (hard constraints)
            for i in train_indices:
                if not df.loc[i, 'RollingStockFitnessStatus']:
                    prob += x[i] == 0  # Cannot operate without fitness
            
            # 3. Job card constraints
            for i in train_indices:
                if df.loc[i, 'JobCardStatus'].lower() == 'open' and df.loc[i, 'OpenJobCards'] >= 3:
                    prob += x[i] == 0  # Too many open jobs
            
            # 4. Maintenance priority (high wear items should not be in service)
            for i in train_indices:
                brake_wear = df.loc[i, 'BrakepadWear%']
                hvac_wear = df.loc[i, 'HVACWear%']
                if brake_wear > 85 or hvac_wear > 90:
                    prob += x[i] == 0  # Force maintenance
            
            # Solve
            prob.solve(PULP_CBC_CMD(msg=0))
            
            if prob.status == 1:  # Optimal
                # Create solution
                df['OperationalStatus'] = 'standby'  # Default
                service_trains = [i for i in train_indices if x[i].varValue == 1]
                
                df.loc[service_trains, 'OperationalStatus'] = 'service'
                
                # Assign maintenance based on needs
                maintenance_candidates = df[
                    (df['OperationalStatus'] == 'standby') & 
                    ((df['BrakepadWear%'] > 80) | 
                     (df['HVACWear%'] > 85) | 
                     (df['OpenJobCards'] >= 2))
                ].head(self.MAX_MAINTENANCE_SLOTS)
                
                df.loc[maintenance_candidates.index, 'OperationalStatus'] = 'maintenance'
                
                return df
            else:
                return None
                
        except Exception as e:
            print(f"   PuLP optimization error: {str(e)}")
            return None
    
    def rank_based_optimization(self, df):
        """Ranking-based optimization as fallback"""
        # Sort by comprehensive score and tie-breakers
        df_sorted = df.sort_values([
            "Score",
            "JobCardPriority",
            "BrandingCompletionRatio", 
            "MileageBalanceAbs",
            "CleaningPriority",
            "ShuntingPriority"
        ], ascending=[False, True, True, True, True, True])
        
        # Assign ranks
        df_sorted["Rank"] = range(1, len(df_sorted) + 1)
        
        # Initialize all as standby
        df_sorted['OperationalStatus'] = 'standby'
        
        # Select top trains for service (with constraints)
        service_count = 0
        for idx, row in df_sorted.iterrows():
            if service_count >= self.SERVICE_QUOTA:
                break
                
            # Check constraints
            if (row['RollingStockFitnessStatus'] and 
                row['SignallingFitnessStatus'] and
                row['TelecomFitnessStatus'] and
                row.get('JobCardStatus', 'close').lower() == 'close'):
                
                df_sorted.loc[idx, 'OperationalStatus'] = 'service'
                service_count += 1
        
        # Assign maintenance to high-priority cases
        maintenance_candidates = df_sorted[
            (df_sorted['OperationalStatus'] == 'standby') &
            ((df_sorted['BrakepadWear%'] > 80) | 
             (df_sorted['HVACWear%'] > 85) |
             (df_sorted['OpenJobCards'] >= 2))
        ].head(self.MAX_MAINTENANCE_SLOTS)
        
        df_sorted.loc[maintenance_candidates.index, 'OperationalStatus'] = 'maintenance'
        
        return df_sorted.reset_index(drop=True)
    
    def add_tie_breakers(self, df):
        """Add tie-breaker columns for ranking"""
        # Job card priority
        df["JobCardPriority"] = df.apply(
            lambda r: r.get("OpenJobCards", 0) if str(r.get("JobCardStatus", "close")).strip().lower() == "open" else 0,
            axis=1
        )
        
        # Branding completion ratio
        df["BrandingCompletionRatio"] = df.apply(
            lambda r: (r.get("ExposureHoursAccrued", 0) / r.get("ExposureHoursTarget", 1)) 
            if r.get("BrandingActive", False) and r.get("ExposureHoursTarget", 0) > 0 else 1,
            axis=1
        )
        
        # Mileage balance (absolute variance)
        df["MileageBalanceAbs"] = abs(df.get("MileageBalanceVariance", pd.Series([0])))
        
        # Cleaning priority
        df["CleaningPriority"] = df.get("CleaningRequired", pd.Series([False])).astype(int)
        
        # Shunting priority
        df["ShuntingPriority"] = df.get("ShuntingMovesRequired", pd.Series([0]))
        
        return df
    
    def generate_sample_data(self, num_trains=25):
        """Generate realistic sample data for testing"""
        np.random.seed(42)
        
        train_names = [
            "KRISHNA", "TAPTI", "NILA", "SARAYU", "ARUTH",
            "VAIGAI", "JHANAVI", "DHWANIL", "BHAVANI", "PADMA",
            "MANDAKINI", "YAMUNA", "PERIYAR", "KABANI", "VAAYU",
            "KAVERI", "SHIRIYA", "PAMPA", "NARMADA", "MAHE",
            "MAARUT", "SABARMATHI", "GODHAVARI", "GANGA", "PAVAN"
        ]
        
        data = []
        for i in range(num_trains):
            train_data = {
                'TrainID': train_names[i] if i < len(train_names) else f'TRAIN_{i+1:03d}',
                'RollingStockFitnessStatus': np.random.choice([True, False], p=[0.85, 0.15]),
                'SignallingFitnessStatus': np.random.choice([True, False], p=[0.90, 0.10]),
                'TelecomFitnessStatus': np.random.choice([True, False], p=[0.88, 0.12]),
                'JobCardStatus': np.random.choice(['close', 'open'], p=[0.7, 0.3]),
                'OpenJobCards': max(0, np.random.poisson(1.5)),
                'BrandingActive': np.random.choice([True, False], p=[0.3, 0.7]),
                'ExposureHoursTarget': np.random.choice([280, 300, 320, 340]),
                'ExposureHoursAccrued': np.random.randint(0, 250),
                'TotalMileageKM': np.random.randint(15000, 50000),
                'MileageSinceLastServiceKM': np.random.randint(1000, 9000),
                'MileageBalanceVariance': np.random.normal(0, 1500),
                'BrakepadWear%': np.random.uniform(20, 95),
                'HVACWear%': np.random.uniform(15, 90),
                'OperationalStatus': np.random.choice(['in_service', 'standby', 'under_maintenance']),
                'CleaningRequired': np.random.choice([True, False], p=[0.25, 0.75]),
                'ShuntingMovesRequired': max(0, np.random.poisson(1.8)),
                'BayPositionID': np.random.randint(1, 20),
                'Depot': np.random.choice(['Main', 'Secondary'], p=[0.7, 0.3])
            }
            
            data.append(train_data)
        
        return pd.DataFrame(data)
    
    def create_fallback_solution(self):
        """Create basic fallback solution"""
        print("⚠️  Creating MOO fallback solution...")
        
        df = self.generate_sample_data()
        df['Score'] = 50.0  # Default score
        df['OperationalStatus'] = 'standby'
        
        # Simple assignment
        df.iloc[:self.SERVICE_QUOTA, df.columns.get_loc('OperationalStatus')] = 'service'
        df.iloc[self.SERVICE_QUOTA:self.SERVICE_QUOTA+5, df.columns.get_loc('OperationalStatus')] = 'maintenance'
        
        return df
    
    def print_optimization_summary(self, df):
        """Print optimization results summary"""
        summary = {
            'Total Trains': len(df),
            'Service': len(df[df['OperationalStatus'] == 'service']),
            'Standby': len(df[df['OperationalStatus'] == 'standby']),
            'Maintenance': len(df[df['OperationalStatus'] == 'maintenance']),
            'Avg Score': df['Score'].mean(),
            'Min Score (Service)': df[df['OperationalStatus'] == 'service']['Score'].min() if len(df[df['OperationalStatus'] == 'service']) > 0 else 0,
            'Fitness Compliance': len(df[df['RollingStockFitnessStatus'] == True]) / len(df) * 100
        }
        
        print("📋 MOO Optimization Summary:")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")

# Test the MOO optimizer
if __name__ == "__main__":
    print("📊 Testing KMRL Multi-Objective Optimizer")
    print("="*50)
    
    optimizer = MOOOptimizer()
    
    # Test optimization
    result = optimizer.optimize()
    print(f"\\nOptimization Result Shape: {result.shape}")
    print("\\nTop 5 trains by score:")
    print(result.nlargest(5, 'Score')[['TrainID', 'Score', 'OperationalStatus']].to_string())
    
    print("\\n✅ MOO Test Complete!")
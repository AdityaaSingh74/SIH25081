"""
🚇 KMRL Genetic Algorithm Optimizer
Inspired by Ysh0910/KMRL implementation with enhancements

Features:
- Multi-constraint optimization
- Real KMRL train names
- Dynamic scheduling with rotations
- Fitness-based selection with realistic constraints
"""

import random
import numpy as np
from deap import base, creator, tools
from datetime import datetime, date, timedelta
import pandas as pd
import copy

class GeneticOptimizer:
    def __init__(self):
        self.NUM_TRAINS = 25
        self.ACTIONS = ["SERVICE", "STANDBY", "MAINTENANCE"]
        self.TRAIN_NAMES = [
            "KRISHNA", "TAPTI", "NILA", "SARAYU", "ARUTH",
            "VAIGAI", "JHANAVI", "DHWANIL", "BHAVANI", "PADMA",
            "MANDAKINI", "YAMUNA", "PERIYAR", "KABANI", "VAAYU",
            "KAVERI", "SHIRIYA", "PAMPA", "NARMADA", "MAHE",
            "MAARUT", "SABARMATHI", "GODHAVARI", "GANGA", "PAVAN"
        ]
        
        # Enhanced configuration
        self.config = {
            'service_quota': 13,  # Minimum trains in service
            'max_cleaning_slots': 5,
            'max_maintenance_slots': 8,
            'mileage_service_threshold': 45000,
            'daily_mileage_per_train': 450,
            'brake_threshold': 85.0,
            'hvac_threshold': 90.0,
            'fitness_validity_days': 30,
            'optimization_weights': {
                'service_compliance': 0.35,
                'maintenance_urgency': 0.25,
                'mileage_balance': 0.20,
                'operational_efficiency': 0.20
            }
        }
        
        self.toolbox = None
        self.setup_genetic_algorithm()
        
    def setup_genetic_algorithm(self):
        """Setup DEAP genetic algorithm framework"""
        # Create fitness and individual classes
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_action", lambda: random.choice(self.ACTIONS))
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, 
                             self.toolbox.attr_action, n=self.NUM_TRAINS)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self.custom_mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self.evaluate_individual)
        
    def custom_mutate(self, individual):
        """Custom mutation with constraint awareness"""
        mutation_rate = 0.15  # Higher mutation rate for exploration
        
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                # Smart mutation based on current state
                current_action = individual[i]
                
                # Prefer beneficial mutations
                if current_action == "MAINTENANCE":
                    # Maintenance trains can go to service or standby
                    individual[i] = random.choice(["SERVICE", "STANDBY"])
                elif current_action == "STANDBY":
                    # Standby trains preferably go to service
                    individual[i] = random.choice(["SERVICE", "SERVICE", "MAINTENANCE"])
                else:  # SERVICE
                    # Service trains can go to standby or maintenance
                    individual[i] = random.choice(["STANDBY", "MAINTENANCE"])
        
        return individual,
    
    def evaluate_individual(self, individual):
        """Enhanced fitness evaluation with multiple objectives"""
        try:
            if not hasattr(self, 'train_data'):
                # Use default data if none provided
                self.train_data = self.generate_default_train_data()
            
            score = 0.0
            penalty = 0.0
            
            # Count actions
            service_count = individual.count("SERVICE")
            standby_count = individual.count("STANDBY")
            maintenance_count = individual.count("MAINTENANCE")
            
            # 1. Service Quota Compliance (Critical)
            service_target = self.config['service_quota']
            if service_count < service_target:
                penalty += (service_target - service_count) * 200  # High penalty
            elif service_count == service_target:
                score += 150  # Reward exact compliance
            else:
                penalty += (service_count - service_target) * 50  # Penalty for excess
            
            # 2. Constraint Violations (Hard constraints)
            for i, action in enumerate(individual):
                train_data = self.train_data.iloc[i] if i < len(self.train_data) else {}
                
                # Fitness certificate violations
                fitness_ok = train_data.get('RollingStockFitnessStatus', True)
                if action == "SERVICE" and not fitness_ok:
                    penalty += 300  # Critical safety violation
                
                # Job card status violations
                job_status = train_data.get('JobCardStatus', 'close')
                if action == "SERVICE" and job_status.lower() == 'open':
                    penalty += 150  # Operational risk
                
                # Maintenance capacity
                if maintenance_count > self.config['max_maintenance_slots']:
                    penalty += (maintenance_count - self.config['max_maintenance_slots']) * 100
            
            # 3. Operational Efficiency Rewards
            for i, action in enumerate(individual):
                train_data = self.train_data.iloc[i] if i < len(self.train_data) else {}
                
                # Reward good decisions
                if action == "SERVICE":
                    # High-scoring trains in service
                    train_score = train_data.get('Score', 50)
                    score += train_score * 0.5
                    
                    # Brand priority
                    if train_data.get('BrandingActive', False):
                        score += 30
                
                elif action == "MAINTENANCE":
                    # Maintenance when needed
                    brake_wear = train_data.get('BrakepadWear%', 0)
                    hvac_wear = train_data.get('HVACWear%', 0)
                    open_jobs = train_data.get('OpenJobCards', 0)
                    
                    if (brake_wear > self.config['brake_threshold'] or 
                        hvac_wear > self.config['hvac_threshold'] or 
                        open_jobs >= 3):
                        score += 80  # Preventive maintenance reward
                    else:
                        penalty += 20  # Unnecessary maintenance
                
                elif action == "STANDBY":
                    # Standby should be for lower priority trains
                    train_score = train_data.get('Score', 50)
                    if train_score < 40:
                        score += 10  # Good to keep low-score trains on standby
                    else:
                        penalty += 5   # High-score trains shouldn't be standby
            
            # 4. Mileage Balancing
            mileage_variance = self.calculate_mileage_variance(individual)
            score += max(0, 100 - mileage_variance * 0.01)  # Reward low variance
            
            # 5. Operational Continuity
            if standby_count >= 2:  # Ensure backup availability
                score += 25
            
            # 6. Cleaning Resource Management
            cleaning_needed = sum(1 for i in range(len(individual)) 
                                if individual[i] == "MAINTENANCE" and 
                                self.train_data.iloc[i].get('CleaningRequired', False))
            
            if cleaning_needed <= self.config['max_cleaning_slots']:
                score += 20
            else:
                penalty += (cleaning_needed - self.config['max_cleaning_slots']) * 30
            
            # Final fitness calculation
            fitness = max(0, score - penalty)
            return (fitness,)
            
        except Exception as e:
            print(f"Error in fitness evaluation: {str(e)}")
            return (0,)  # Return minimum fitness on error
    
    def calculate_mileage_variance(self, individual):
        """Calculate mileage variance for load balancing"""
        try:
            current_mileages = []
            for i, action in enumerate(individual):
                base_mileage = self.train_data.iloc[i].get('TotalMileageKM', 20000) if i < len(self.train_data) else 20000
                
                # Add daily mileage for service trains
                if action == "SERVICE":
                    projected_mileage = base_mileage + self.config['daily_mileage_per_train']
                else:
                    projected_mileage = base_mileage
                
                current_mileages.append(projected_mileage)
            
            return np.var(current_mileages)
            
        except:
            return 1000000  # High variance penalty on error
    
    def optimize(self, data_path=None, constraints=None):
        """Run genetic algorithm optimization"""
        try:
            print("🧬 Starting Genetic Algorithm Optimization...")
            
            # Load training data
            if data_path and pd.io.common.file_exists(data_path):
                self.train_data = pd.read_csv(data_path)
                print(f"   Loaded data: {len(self.train_data)} trains")
            else:
                self.train_data = self.generate_default_train_data()
                print("   Using generated default data")
            
            # Update configuration with constraints
            if constraints:
                self.config.update(constraints)
            
            # Ensure we have enough trains
            if len(self.train_data) < self.NUM_TRAINS:
                additional_trains = self.generate_default_train_data(self.NUM_TRAINS - len(self.train_data))
                self.train_data = pd.concat([self.train_data, additional_trains], ignore_index=True)
            
            # Initialize population
            population = self.toolbox.population(n=100)  # Smaller population for speed
            
            # Evolution parameters
            NGEN = 50  # Generations
            CXPB = 0.7  # Crossover probability
            MUTPB = 0.3  # Mutation probability
            
            print(f"   Population: {len(population)}, Generations: {NGEN}")
            
            # Evaluate initial population
            fitnesses = list(map(self.toolbox.evaluate, population))
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit
            
            # Evolution loop
            for generation in range(NGEN):
                # Selection
                offspring = self.toolbox.select(population, len(population))
                offspring = list(map(self.toolbox.clone, offspring))
                
                # Crossover
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < CXPB:
                        self.toolbox.mate(child1, child2)
                        del child1.fitness.values, child2.fitness.values
                
                # Mutation
                for mutant in offspring:
                    if random.random() < MUTPB:
                        self.toolbox.mutate(mutant)
                        del mutant.fitness.values
                
                # Evaluate invalid individuals
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(self.toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit
                
                population[:] = offspring
                
                # Progress reporting
                if generation % 10 == 0:
                    best_fitness = max(ind.fitness.values[0] for ind in population)
                    print(f"   Generation {generation}: Best fitness = {best_fitness:.2f}")
            
            # Get best solution
            best_individual = tools.selBest(population, 1)[0]
            best_fitness = best_individual.fitness.values[0]
            
            print(f"✅ Optimization complete! Best fitness: {best_fitness:.2f}")
            
            # Create result schedule
            result_schedule = self.create_schedule_dataframe(best_individual)
            
            return result_schedule
            
        except Exception as e:
            print(f"❌ Optimization failed: {str(e)}")
            return self.create_fallback_schedule()
    
    def create_schedule_dataframe(self, solution):
        """Create detailed schedule from GA solution"""
        try:
            schedule_data = []
            
            for i, action in enumerate(solution):
                train_name = self.TRAIN_NAMES[i] if i < len(self.TRAIN_NAMES) else f"TRAIN_{i+1:03d}"
                train_data = self.train_data.iloc[i] if i < len(self.train_data) else {}
                
                schedule_entry = {
                    'TrainID': train_name,
                    'OperationalStatus': action.lower(),
                    'Score': train_data.get('Score', np.random.uniform(30, 90)),
                    'Rank': i + 1,
                    'RollingStockFitnessStatus': train_data.get('RollingStockFitnessStatus', True),
                    'SignallingFitnessStatus': train_data.get('SignallingFitnessStatus', True),
                    'TelecomFitnessStatus': train_data.get('TelecomFitnessStatus', True),
                    'JobCardStatus': train_data.get('JobCardStatus', 'close'),
                    'OpenJobCards': train_data.get('OpenJobCards', np.random.randint(0, 3)),
                    'BrandingActive': train_data.get('BrandingActive', np.random.choice([True, False])),
                    'TotalMileageKM': train_data.get('TotalMileageKM', np.random.randint(15000, 45000)),
                    'MileageSinceLastServiceKM': train_data.get('MileageSinceLastServiceKM', np.random.randint(1000, 8000)),
                    'BrakepadWear%': train_data.get('BrakepadWear%', np.random.uniform(20, 95)),
                    'HVACWear%': train_data.get('HVACWear%', np.random.uniform(15, 85)),
                    'CleaningRequired': train_data.get('CleaningRequired', np.random.choice([True, False])),
                    'ShuntingMovesRequired': train_data.get('ShuntingMovesRequired', np.random.randint(0, 4)),
                    'AssignedDateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'OptimizationAlgorithm': 'Genetic Algorithm'
                }
                
                # Add delay predictions if available
                if hasattr(self, 'delay_predictor'):
                    delay_pred = self.delay_predictor.predict_schedule(60, 8.5, 0.7)
                    schedule_entry['PredictedDelayMinutes'] = delay_pred.get('Predicted Delay Minutes', 0)
                    schedule_entry['DelayCategory'] = delay_pred.get('Predicted Delay Category', 'Low')
                
                schedule_data.append(schedule_entry)
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Add summary statistics
            summary_stats = {
                'total_trains': len(schedule_df),
                'service_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'service']),
                'standby_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'standby']),
                'maintenance_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'maintenance']),
                'avg_score': schedule_df['Score'].mean(),
                'fitness_compliance': len(schedule_df[schedule_df['RollingStockFitnessStatus'] == True]) / len(schedule_df) * 100
            }
            
            print("📊 Schedule Summary:")
            for key, value in summary_stats.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value}")
            
            return schedule_df
            
        except Exception as e:
            print(f"Error creating schedule: {str(e)}")
            return self.create_fallback_schedule()
    
    def generate_default_train_data(self, num_trains=None):
        """Generate realistic train data for optimization"""
        if num_trains is None:
            num_trains = self.NUM_TRAINS
            
        np.random.seed(42)
        
        train_data = []
        for i in range(num_trains):
            train_name = self.TRAIN_NAMES[i] if i < len(self.TRAIN_NAMES) else f"TRAIN_{i+1:03d}"
            
            # Generate realistic operational data
            train_entry = {
                'TrainID': train_name,
                'Score': np.random.uniform(30, 95),
                'RollingStockFitnessStatus': np.random.choice([True, False], p=[0.85, 0.15]),
                'SignallingFitnessStatus': np.random.choice([True, False], p=[0.90, 0.10]),
                'TelecomFitnessStatus': np.random.choice([True, False], p=[0.88, 0.12]),
                'JobCardStatus': np.random.choice(['close', 'open'], p=[0.75, 0.25]),
                'OpenJobCards': np.random.poisson(1.2),  # Average 1.2 open jobs
                'BrandingActive': np.random.choice([True, False], p=[0.3, 0.7]),
                'TotalMileageKM': np.random.randint(15000, 50000),
                'MileageSinceLastServiceKM': np.random.randint(500, 9000),
                'BrakepadWear%': np.random.uniform(20, 95),
                'HVACWear%': np.random.uniform(15, 90),
                'CleaningRequired': np.random.choice([True, False], p=[0.25, 0.75]),
                'ShuntingMovesRequired': np.random.poisson(1.5),
                'ExposureHoursAccrued': np.random.randint(0, 200),
                'ExposureHoursTarget': np.random.choice([280, 300, 320, 340]),
                'BayPositionID': np.random.randint(1, 20)
            }
            
            train_data.append(train_entry)
        
        return pd.DataFrame(train_data)
    
    def create_fallback_schedule(self):
        """Create a basic fallback schedule"""
        print("⚠️  Creating fallback schedule...")
        
        fallback_data = []
        for i in range(self.NUM_TRAINS):
            train_name = self.TRAIN_NAMES[i] if i < len(self.TRAIN_NAMES) else f"TRAIN_{i+1:03d}"
            
            # Simple rule-based assignment
            if i < 13:  # First 13 trains in service
                status = 'service'
            elif i < 20:  # Next 7 on standby
                status = 'standby'
            else:  # Rest in maintenance
                status = 'maintenance'
            
            fallback_data.append({
                'TrainID': train_name,
                'OperationalStatus': status,
                'Score': 50.0,
                'Rank': i + 1,
                'OptimizationAlgorithm': 'Fallback Rule-based'
            })
        
        return pd.DataFrame(fallback_data)
    
    def combine_schedules(self, schedule1, schedule2):
        """Combine two schedules using ensemble approach"""
        try:
            combined_schedule = schedule1.copy()
            
            # Add ensemble information
            combined_schedule['EnsembleMethod'] = 'GA + MOO Hybrid'
            combined_schedule['AlternativeStatus'] = schedule2['OperationalStatus'].values
            
            # Use voting for conflicting decisions
            conflicts = (schedule1['OperationalStatus'] != schedule2['OperationalStatus'])
            print(f"   Resolving {conflicts.sum()} scheduling conflicts...")
            
            # Keep higher-scoring option for conflicts
            for idx in combined_schedule[conflicts].index:
                score1 = schedule1.loc[idx, 'Score']
                score2 = schedule2.loc[idx, 'Score']
                
                if score2 > score1:
                    combined_schedule.loc[idx, 'OperationalStatus'] = schedule2.loc[idx, 'OperationalStatus']
            
            return combined_schedule
            
        except Exception as e:
            print(f"Error combining schedules: {str(e)}")
            return schedule1  # Return first schedule on error

# Test the genetic optimizer
if __name__ == "__main__":
    print("🧬 Testing KMRL Genetic Algorithm Optimizer")
    print("="*50)
    
    optimizer = GeneticOptimizer()
    
    # Test optimization
    schedule = optimizer.optimize()
    print(f"\\nOptimized Schedule Shape: {schedule.shape}")
    print("\\nFirst 5 trains:")
    print(schedule.head().to_string())
    
    print("\\n✅ Genetic Algorithm Test Complete!")
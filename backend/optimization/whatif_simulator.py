"""
🚇 KMRL What-If Simulator - FIXED VERSION
Advanced scenario analysis for train scheduling decisions

Features:
- Emergency scenario simulation
- Weather impact analysis
- Peak demand modeling
- Maintenance window optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import copy

class WhatIfSimulator:
    def __init__(self):
        self.scenario_types = {
            'train_failure': self.simulate_train_failure,
            'weather_delay': self.simulate_weather_impact,
            'peak_demand': self.simulate_peak_demand,
            'maintenance_window': self.simulate_maintenance_window,
            'emergency': self.simulate_emergency,
            'station_closure': self.simulate_station_closure
        }
        
        self.impact_factors = {
            'delay_multiplier': 1.0,
            'capacity_reduction': 0.0,
            'service_disruption': 0.0,
            'maintenance_urgency': 0.0,
            'passenger_impact': 0.0
        }
    
    def run_scenario(self, base_data_path, scenario_config):
        """Run what-if scenario analysis"""
        try:
            print(f"🔍 Running what-if scenario: {scenario_config.get('type', 'unknown')}")
            
            # Load base data
            if isinstance(base_data_path, str):
                base_df = pd.read_csv(base_data_path)
            else:
                base_df = base_data_path  # Assume it's already a DataFrame
            
            scenario_type = scenario_config.get('type', 'train_failure')
            
            # Run specific scenario simulation
            if scenario_type in self.scenario_types:
                results = self.scenario_types[scenario_type](base_df, scenario_config)
            else:
                results = self.simulate_generic_scenario(base_df, scenario_config)
            
            # Add analysis summary
            results['analysis_summary'] = self.generate_analysis_summary(results)
            
            print("✅ What-if scenario analysis complete")
            return results
            
        except Exception as e:
            print(f"❌ Scenario simulation failed: {str(e)}")
            return {'error': str(e)}
    
    def simulate_train_failure(self, df, config):
        """Simulate single or multiple train failures"""
        affected_trains = config.get('affected_trains', [])
        failure_type = config.get('failure_type', 'mechanical')
        duration_hours = config.get('duration_hours', 4)
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Apply failure impacts
        for train_id in affected_trains:
            train_idx = scenario_df[scenario_df['TrainID'] == train_id].index
            
            if len(train_idx) > 0:
                idx = train_idx[0]
                scenario_df.loc[idx, 'OperationalStatus'] = 'under_maintenance'
                scenario_df.loc[idx, 'FailureType'] = failure_type
                scenario_df.loc[idx, 'EstimatedRepairTime'] = duration_hours
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        service_gap = len(affected_trains)
        
        return {
            'scenario_type': 'train_failure',
            'affected_trains': affected_trains,
            'failure_details': {
                'type': failure_type,
                'duration_hours': duration_hours,
                'trains_affected': len(affected_trains)
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'impact_analysis': {
                'service_reduction': service_gap,
                'passenger_impact_score': self.calculate_passenger_impact(service_gap),
                'revenue_loss_estimate': service_gap * duration_hours * 2500,
                'recovery_time_estimate': duration_hours + (service_gap * 0.5)
            },
            'recommendations': self.generate_failure_recommendations(affected_trains, failure_type, service_gap),
            'scenario_data': scenario_df
        }
    
    def simulate_weather_impact(self, df, config):
        """Simulate weather-related delays and disruptions"""
        weather_type = config.get('weather_type', 'heavy_rain')
        intensity = config.get('intensity', 'moderate')
        duration_hours = config.get('duration_hours', 6)
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Weather impact factors
        weather_impacts = {
            'heavy_rain': {'delay_factor': 1.5, 'speed_reduction': 0.2},
            'fog': {'delay_factor': 2.0, 'speed_reduction': 0.4},
            'storm': {'delay_factor': 3.0, 'speed_reduction': 0.6}
        }
        
        impact = weather_impacts.get(weather_type, weather_impacts['heavy_rain'])
        
        # Apply weather effects
        service_trains = scenario_df[scenario_df['OperationalStatus'] == 'service']
        for idx in service_trains.index:
            if 'predicted_delay_minutes' in scenario_df.columns:
                base_delay = scenario_df.loc[idx, 'predicted_delay_minutes']
                weather_delay = base_delay * impact['delay_factor']
                scenario_df.loc[idx, 'predicted_delay_minutes'] = weather_delay
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        
        return {
            'scenario_type': 'weather_impact',
            'weather_details': {
                'type': weather_type,
                'intensity': intensity,
                'duration_hours': duration_hours
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'recommendations': self.generate_weather_recommendations(weather_type, intensity),
            'scenario_data': scenario_df
        }
    
    def simulate_peak_demand(self, df, config):
        """Simulate peak demand scenarios"""
        demand_multiplier = config.get('demand_multiplier', 1.8)
        event_type = config.get('event_type', 'festival')
        duration_hours = config.get('duration_hours', 12)
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Increase load factors for service trains
        service_trains = scenario_df[scenario_df['OperationalStatus'] == 'service']
        current_service_trains = len(service_trains)
        required_service_trains = int(current_service_trains * demand_multiplier * 0.8)
        service_gap = max(0, required_service_trains - current_service_trains)
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        
        return {
            'scenario_type': 'peak_demand',
            'demand_details': {
                'multiplier': demand_multiplier,
                'event_type': event_type,
                'duration_hours': duration_hours
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'capacity_analysis': {
                'current_service_trains': current_service_trains,
                'required_service_trains': required_service_trains,
                'service_gap': service_gap
            },
            'recommendations': self.generate_peak_demand_recommendations(service_gap, 0, demand_multiplier),
            'scenario_data': scenario_df
        }
    
    def simulate_maintenance_window(self, df, config):
        """Simulate planned maintenance window impacts"""
        maintenance_trains = config.get('maintenance_trains', [])
        window_hours = config.get('window_hours', 8)
        window_type = config.get('window_type', 'preventive')
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Move specified trains to maintenance
        for train_id in maintenance_trains:
            train_idx = scenario_df[scenario_df['TrainID'] == train_id].index
            if len(train_idx) > 0:
                idx = train_idx[0]
                scenario_df.loc[idx, 'OperationalStatus'] = 'under_maintenance'
                scenario_df.loc[idx, 'MaintenanceType'] = window_type
                scenario_df.loc[idx, 'MaintenanceWindowHours'] = window_hours
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        trains_in_maintenance = len(maintenance_trains)
        
        return {
            'scenario_type': 'maintenance_window',
            'maintenance_details': {
                'trains_count': trains_in_maintenance,
                'window_hours': window_hours,
                'maintenance_type': window_type,
                'affected_trains': maintenance_trains
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'recommendations': self.generate_maintenance_recommendations(trains_in_maintenance, window_hours, 0),
            'scenario_data': scenario_df
        }
    
    def simulate_emergency(self, df, config):
        """Simulate emergency scenarios"""
        emergency_type = config.get('emergency_type', 'system_wide')
        severity = config.get('severity', 'high')
        affected_percentage = config.get('affected_percentage', 0.3)
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Determine affected trains based on percentage
        total_trains = len(scenario_df)
        affected_count = int(total_trains * affected_percentage)
        
        # Randomly select affected trains
        np.random.seed(42)
        affected_indices = np.random.choice(scenario_df.index, affected_count, replace=False)
        
        for idx in affected_indices:
            scenario_df.loc[idx, 'OperationalStatus'] = 'under_maintenance'
            scenario_df.loc[idx, 'EmergencyType'] = emergency_type
            scenario_df.loc[idx, 'EmergencySeverity'] = severity
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        
        return {
            'scenario_type': 'emergency',
            'emergency_details': {
                'type': emergency_type,
                'severity': severity,
                'affected_percentage': affected_percentage,
                'affected_trains': affected_count
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'recommendations': self.generate_emergency_recommendations(emergency_type, severity, affected_count),
            'scenario_data': scenario_df
        }
    
    def simulate_station_closure(self, df, config):
        """Simulate station closure scenarios"""
        closed_stations = config.get('closed_stations', ['MG Road'])
        closure_duration = config.get('closure_duration', 4)
        closure_reason = config.get('closure_reason', 'maintenance')
        
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        
        # Impact on service trains (reduced capacity/longer routes)
        service_trains = scenario_df[scenario_df['OperationalStatus'] == 'service']
        capacity_reduction = len(closed_stations) * 0.15  # 15% reduction per station
        
        for idx in service_trains.index:
            if 'predicted_delay_minutes' in scenario_df.columns:
                base_delay = scenario_df.loc[idx, 'predicted_delay_minutes']
                closure_delay = base_delay * (1 + capacity_reduction)
                scenario_df.loc[idx, 'predicted_delay_minutes'] = closure_delay
        
        scenario_metrics = self.calculate_metrics(scenario_df)
        
        return {
            'scenario_type': 'station_closure',
            'closure_details': {
                'closed_stations': closed_stations,
                'duration_hours': closure_duration,
                'reason': closure_reason,
                'capacity_reduction': capacity_reduction
            },
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'recommendations': self.generate_closure_recommendations(closed_stations, closure_duration),
            'scenario_data': scenario_df
        }
    
    def simulate_generic_scenario(self, df, config):
        """Generic scenario simulation for unknown types"""
        scenario_df = df.copy()
        original_metrics = self.calculate_metrics(df)
        scenario_metrics = self.calculate_metrics(scenario_df)
        
        return {
            'scenario_type': 'generic',
            'original_metrics': original_metrics,
            'scenario_metrics': scenario_metrics,
            'recommendations': ['Review scenario configuration', 'Check scenario type validity'],
            'scenario_data': scenario_df
        }
    
    def calculate_metrics(self, df):
        """Calculate key operational metrics"""
        service_trains = df[df['OperationalStatus'] == 'service'] if 'OperationalStatus' in df.columns else df
        standby_trains = df[df['OperationalStatus'] == 'standby'] if 'OperationalStatus' in df.columns else pd.DataFrame()
        maintenance_trains = df[df['OperationalStatus'] == 'under_maintenance'] if 'OperationalStatus' in df.columns else pd.DataFrame()
        
        return {
            'total_trains': len(df),
            'service_count': len(service_trains),
            'standby_count': len(standby_trains),
            'maintenance_count': len(maintenance_trains),
            'avg_score': df['Score'].mean() if 'Score' in df.columns else 50.0,
            'avg_delay': df['predicted_delay_minutes'].mean() if 'predicted_delay_minutes' in df.columns else 2.0,
            'fitness_compliance': len(df[df.get('RollingStockFitnessStatus', True) == True]) / len(df) * 100 if len(df) > 0 else 100
        }
    
    def calculate_passenger_impact(self, service_shortage):
        """Calculate passenger impact score (0-100)"""
        if service_shortage <= 0:
            return 0
        elif service_shortage <= 2:
            return 25  # Minor impact
        elif service_shortage <= 5:
            return 60  # Moderate impact
        else:
            return 95  # Severe impact
    
    def generate_failure_recommendations(self, affected_trains, failure_type, service_shortage):
        """Generate recommendations for train failure scenarios"""
        recommendations = [
            f"Immediately activate {min(service_shortage, 3)} standby trains",
            "Notify passengers of service disruptions via all channels"
        ]
        
        if failure_type == 'mechanical':
            recommendations.extend([
                "Deploy emergency repair crew to affected trains",
                "Inspect similar components in other trains"
            ])
        elif failure_type == 'electrical':
            recommendations.extend([
                "Check electrical systems in similar trains",
                "Monitor battery health across fleet"
            ])
        
        return recommendations
    
    def generate_weather_recommendations(self, weather_type, intensity):
        """Generate weather-specific recommendations"""
        recommendations = [
            "Increase headway between trains for safety",
            "Deploy additional staff at stations"
        ]
        
        if weather_type == 'heavy_rain':
            recommendations.append("Monitor track drainage systems")
        elif weather_type == 'fog':
            recommendations.append("Activate enhanced signaling systems")
        
        return recommendations
    
    def generate_peak_demand_recommendations(self, service_gap, can_activate, demand_multiplier):
        """Generate peak demand handling recommendations"""
        recommendations = [
            "Implement crowd control measures at stations",
            "Deploy additional security personnel"
        ]
        
        if service_gap > 0:
            recommendations.append(f"Consider activating {service_gap} additional trains")
        
        return recommendations
    
    def generate_maintenance_recommendations(self, trains_count, window_hours, net_reduction):
        """Generate maintenance window recommendations"""
        recommendations = [
            f"Schedule {trains_count}-train maintenance during low-demand hours",
            "Verify all safety systems after maintenance"
        ]
        
        if window_hours > 6:
            recommendations.append("Ensure maintenance crews work in shifts")
        
        return recommendations
    
    def generate_emergency_recommendations(self, emergency_type, severity, affected_count):
        """Generate emergency scenario recommendations"""
        recommendations = [
            "Activate emergency management protocols",
            "Coordinate with local emergency services",
            f"Prepare backup services for {affected_count} affected trains"
        ]
        
        if severity == 'high':
            recommendations.append("Consider temporary service suspension if needed")
        
        return recommendations
    
    def generate_closure_recommendations(self, closed_stations, duration):
        """Generate station closure recommendations"""
        recommendations = [
            f"Announce closure of {', '.join(closed_stations)} stations",
            "Provide alternative transport information",
            f"Prepare for {duration}-hour service adjustments"
        ]
        
        return recommendations
    
    def generate_analysis_summary(self, results):
        """Generate executive summary of scenario analysis"""
        scenario_type = results.get('scenario_type', 'unknown')
        
        if scenario_type == 'train_failure':
            impact = results.get('impact_analysis', {})
            summary = f"""
            TRAIN FAILURE SCENARIO ANALYSIS
            
            Affected Trains: {len(results.get('affected_trains', []))}
            Service Reduction: {impact.get('service_reduction', 0)} trains
            Revenue Impact: ₹{impact.get('revenue_loss_estimate', 0):,}
            
            Critical Actions:
            - Activate available standby trains
            - Deploy emergency repair crews
            """
        else:
            summary = f"""
            {scenario_type.upper()} SCENARIO ANALYSIS
            
            Scenario Impact: Moderate to High
            Service Adjustments: Required
            
            Critical Actions:
            - Monitor situation closely
            - Implement contingency plans
            """
        
        return summary.strip()

# Test the what-if simulator
if __name__ == "__main__":
    print("🔍 Testing KMRL What-If Simulator")
    print("="*50)
    
    simulator = WhatIfSimulator()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'TrainID': ['KRISHNA', 'TAPTI', 'NILA', 'SARAYU', 'ARUTH'],
        'OperationalStatus': ['service', 'service', 'standby', 'service', 'maintenance'],
        'Score': [85, 78, 92, 81, 45],
        'RollingStockFitnessStatus': [True, True, True, True, False],
        'predicted_delay_minutes': [2.1, 3.5, 0.0, 4.2, 0.0]
    })
    
    # Test train failure scenario
    failure_scenario = {
        'type': 'train_failure',
        'affected_trains': ['KRISHNA', 'TAPTI'],
        'failure_type': 'mechanical',
        'duration_hours': 6
    }
    
    results = simulator.run_scenario(sample_data, failure_scenario)
    
    if 'error' not in results:
        print(f"\n✅ Scenario: {results['scenario_type']}")
        print(f"Affected trains: {len(results['affected_trains'])}")
        print("\nRecommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"{i}. {rec}")
    else:
        print(f"❌ Simulation failed: {results['error']}")
    
    print("\n✅ What-If Simulator Test Complete!")
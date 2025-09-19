import pandas as pd
import numpy as np
import os

def run_disruption_simulation(schedule_path='backend/optimization/schedules/optimized_schedule.csv', disruption_rate=0.1, disruption_severity=(5, 15)):
    """
    Applies random delays to an optimized schedule to simulate real-world
    disruptions and test the schedule's resilience.
    """
    print("Running disruption simulation...")
    if not os.path.exists(schedule_path):
        raise FileNotFoundError("Optimized schedule not found. Please generate a schedule first.")

    schedule_df = pd.read_csv(schedule_path)
    
    # --- Simulate Disruptions ---
    num_disruptions = max(1, int(len(schedule_df) * disruption_rate))
    disruption_indices = np.random.choice(schedule_df.index, num_disruptions, replace=False)
    
    min_delay, max_delay = disruption_severity
    extra_delay = np.random.uniform(min_delay, max_delay, size=num_disruptions)
    
    schedule_df['simulated_delay_minutes'] = schedule_df['predicted_delay_minutes']
    schedule_df.loc[disruption_indices, 'simulated_delay_minutes'] += extra_delay
    schedule_df['was_disrupted'] = False
    schedule_df.loc[disruption_indices, 'was_disrupted'] = True

    # --- Calculate Results ---
    original_total_delay = schedule_df['predicted_delay_minutes'].sum()
    simulated_total_delay = schedule_df['simulated_delay_minutes'].sum()
    
    print(f"Simulation complete. Original total predicted delay: {original_total_delay:.2f} mins. Simulated total delay: {simulated_total_delay:.2f} mins.")

    return {
        "original_total_delay": round(original_total_delay, 2),
        "simulated_total_delay": round(simulated_total_delay, 2),
        "num_disruptions_applied": num_disruptions,
        "disrupted_trips_details": schedule_df[schedule_df['was_disrupted']].to_dict('records')
    }

if __name__ == '__main__':
    run_disruption_simulation()


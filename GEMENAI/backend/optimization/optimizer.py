import pandas as pd
import pulp
import joblib
import os

def run_schedule_optimization(data_path='data/processed_schedule_data.csv'):
    """
    Uses trained ML models to predict readiness and delays, then runs PuLP
    optimization to generate the most efficient and reliable schedule.
    """
    print("Starting schedule optimization...")

    # --- 1. Load Data and Models ---
    model_dir = 'backend/ml/saved_models'
    if not os.path.exists(data_path):
        raise FileNotFoundError("Processed data not found. Run preprocessing.")
    if not (os.path.exists(os.path.join(model_dir, 'readiness_model.pkl')) and os.path.exists(os.path.join(model_dir, 'delay_model.pkl'))):
        raise FileNotFoundError("ML models not found. Please run training first.")

    df = pd.read_csv(data_path)
    df = df.drop_duplicates(subset='trip_id').head(100) # Use a subset for faster optimization

    readiness_model = joblib.load(os.path.join(model_dir, 'readiness_model.pkl'))
    readiness_features = joblib.load(os.path.join(model_dir, 'readiness_features.pkl'))
    delay_model = joblib.load(os.path.join(model_dir, 'delay_model.pkl'))
    delay_features = joblib.load(os.path.join(model_dir, 'delay_features.pkl'))

    trips = df['trip_id'].unique()
    trains = df['train_id'].unique()

    # --- 2. Predict for All Possible Pairings ---
    possible_assignments = pd.DataFrame([(trip, train) for trip in trips for train in trains], columns=['trip_id', 'train_id'])
    prediction_df = pd.merge(possible_assignments, df.drop(columns=['train_id']), on='trip_id')
    
    prediction_df['predicted_readiness'] = readiness_model.predict(prediction_df[readiness_features])
    prediction_df['predicted_delay'] = delay_model.predict(prediction_df[delay_features])

    # --- 3. PuLP Optimization ---
    prob = pulp.LpProblem("Train_Scheduling_Optimization", pulp.LpMinimize)
    assign_vars = pulp.LpVariable.dicts("Assign", (trains, trips), 0, 1, pulp.LpBinary)

    # Objective: Minimize delay + heavy penalty for using a non-ready train
    penalty = 100 
    objective_df = prediction_df.set_index(['train_id', 'trip_id'])
    objective = pulp.lpSum(
        (objective_df.loc[(i, j), 'predicted_delay'] + penalty * (1 - objective_df.loc[(i, j), 'predicted_readiness'])) * assign_vars[i][j]
        for i in trains for j in trips
    )
    prob += objective

    # --- Constraints ---
    for j in trips:
        prob += pulp.lpSum([assign_vars[i][j] for i in trains]) == 1 # Each trip gets one train

    for i in trains:
        prob += pulp.lpSum([assign_vars[i][j] for j in trips]) <= 15 # Max trips per train

    prob.solve()
    print(f"Optimization Status: {pulp.LpStatus[prob.status]}")

    # --- 4. Extract and Save Results ---
    result = []
    for var in prob.variables():
        if var.varValue == 1:
            _, train_id, trip_id_str = var.name.split('_')
            trip_id = int(trip_id_str)
            match = objective_df.loc[(train_id, trip_id)]
            result.append({
                'trip_id': trip_id,
                'assigned_train': train_id,
                'hour_of_day': int(match['hour_of_day']),
                'predicted_delay_minutes': round(match['predicted_delay'], 2),
                'was_predicted_ready': int(match['predicted_readiness'])
            })

    result_df = pd.DataFrame(result).sort_values('hour_of_day')
    
    output_dir = 'backend/optimization/schedules'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'optimized_schedule.csv')
    result_df.to_csv(output_path, index=False)
    
    print(f"Optimized schedule saved to {output_path}")
    return {
        "status": pulp.LpStatus[prob.status],
        "total_objective_value": pulp.value(prob.objective),
        "num_trips_optimized": len(result_df),
        "schedule_path": output_path
    }

if __name__ == '__main__':
    run_schedule_optimization()


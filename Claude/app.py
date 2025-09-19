
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import json
import sqlite3
import pandas as pd
import numpy as np
import threading
import time
from models.ai_model import *
from models.optimization import *
from models.data_generator import *

app = Flask(__name__)
app.secret_key = 'smart_metro_ai_os_2025'

# Global variables for real-time data
current_system_state = {
    'trains': {},
    'schedules': {},
    'alerts': [],
    'performance_metrics': {},
    'last_update': datetime.now()
}

# Initialize AI models
ai_engine = SmartMetroAI()
optimizer = MetroOptimizer()
data_gen = DataGenerator()

class SystemOrchestrator:
    def __init__(self):
        self.initialize_database()
        self.load_initial_data()
        self.start_real_time_updates()
    
    def initialize_database(self):
        """Initialize SQLite database with comprehensive schema"""
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Trains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trains (
                train_id TEXT PRIMARY KEY,
                route TEXT,
                depot TEXT,
                status TEXT,
                current_location TEXT,
                passenger_load INTEGER,
                energy_consumption REAL,
                last_maintenance DATE,
                next_maintenance DATE,
                crew_id TEXT,
                brand_hours_remaining REAL,
                mechanical_score REAL,
                readiness_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                schedule_id TEXT PRIMARY KEY,
                train_id TEXT,
                route TEXT,
                scheduled_departure TIMESTAMP,
                scheduled_arrival TIMESTAMP,
                actual_departure TIMESTAMP,
                actual_arrival TIMESTAMP,
                delay_minutes INTEGER,
                passenger_load INTEGER,
                weather_condition TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (train_id) REFERENCES trains (train_id)
            )
        ''')
        
        # Maintenance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                maintenance_id TEXT PRIMARY KEY,
                train_id TEXT,
                maintenance_type TEXT,
                scheduled_date DATE,
                completion_date DATE,
                duration_hours REAL,
                cost REAL,
                priority TEXT,
                description TEXT,
                status TEXT,
                FOREIGN KEY (train_id) REFERENCES trains (train_id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE,
                scheduling_accuracy REAL,
                average_delay REAL,
                passenger_wait_time REAL,
                train_availability REAL,
                energy_efficiency REAL,
                operational_cost REAL,
                customer_satisfaction REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_initial_data(self):
        """Load comprehensive initial dataset"""
        print("Generating comprehensive dataset...")
        
        # Generate 25+ trains with realistic data
        trains_data = data_gen.generate_train_fleet(30)
        schedules_data = data_gen.generate_historical_schedules(100000)  # 100K records
        maintenance_data = data_gen.generate_maintenance_records(5000)
        
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        
        # Load trains
        trains_df = pd.DataFrame(trains_data)
        trains_df.to_sql('trains', conn, if_exists='replace', index=False)
        
        # Load schedules
        schedules_df = pd.DataFrame(schedules_data)
        schedules_df.to_sql('schedules', conn, if_exists='replace', index=False)
        
        # Load maintenance
        maintenance_df = pd.DataFrame(maintenance_data)
        maintenance_df.to_sql('maintenance', conn, if_exists='replace', index=False)
        
        conn.close()
        
        # Train AI models
        print("Training AI models...")
        ai_engine.train_models(schedules_df, trains_df, maintenance_df)
        
        print("System initialization completed!")
    
    def start_real_time_updates(self):
        """Start background thread for real-time updates"""
        def update_system():
            while True:
                try:
                    self.update_train_statuses()
                    self.update_performance_metrics()
                    current_system_state['last_update'] = datetime.now()
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    print(f"Real-time update error: {e}")
                    time.sleep(60)
        
        update_thread = threading.Thread(target=update_system, daemon=True)
        update_thread.start()
    
    def update_train_statuses(self):
        """Update train statuses using AI predictions"""
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        
        # Get current trains
        trains_df = pd.read_sql_query("SELECT * FROM trains", conn)
        
        # Update readiness scores using AI
        for idx, train in trains_df.iterrows():
            # AI-driven readiness assessment
            readiness_score = ai_engine.calculate_train_readiness(train)
            
            # Determine status based on AI assessment
            if readiness_score >= 0.9:
                status = 'Running'
            elif readiness_score >= 0.7:
                status = 'Ready'
            elif readiness_score >= 0.5:
                status = 'Held'
            else:
                status = 'Maintenance'
            
            # Update database
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trains 
                SET status = ?, readiness_score = ? 
                WHERE train_id = ?
            ''', (status, readiness_score, train['train_id']))
        
        conn.commit()
        conn.close()
    
    def update_performance_metrics(self):
        """Calculate and update system performance metrics"""
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        
        # Calculate current performance
        today = datetime.now().date()
        
        # Scheduling accuracy
        accuracy_query = '''
            SELECT 
                AVG(CASE WHEN delay_minutes <= 2 THEN 1.0 ELSE 0.0 END) as accuracy
            FROM schedules 
            WHERE DATE(scheduled_departure) = ?
        '''
        accuracy = pd.read_sql_query(accuracy_query, conn, params=[today])['accuracy'].iloc[0] or 0.95
        
        # Average delay
        delay_query = '''
            SELECT AVG(delay_minutes) as avg_delay
            FROM schedules 
            WHERE DATE(scheduled_departure) = ?
        '''
        avg_delay = pd.read_sql_query(delay_query, conn, params=[today])['avg_delay'].iloc[0] or 2.5
        
        # Train availability
        availability_query = '''
            SELECT 
                AVG(CASE WHEN status IN ('Running', 'Ready') THEN 1.0 ELSE 0.0 END) as availability
            FROM trains
        '''
        availability = pd.read_sql_query(availability_query, conn)['availability'].iloc[0] or 0.85
        
        # Update performance metrics
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO performance_metrics 
            (metric_date, scheduling_accuracy, average_delay, train_availability, passenger_wait_time, energy_efficiency, operational_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (today, accuracy, avg_delay, availability, 4.2, 0.92, 850000))
        
        conn.commit()
        conn.close()
        
        # Update global state
        current_system_state['performance_metrics'] = {
            'scheduling_accuracy': accuracy * 100,
            'average_delay': avg_delay,
            'train_availability': availability * 100,
            'passenger_wait_time': 4.2,
            'energy_efficiency': 92.0,
            'operational_cost': 850000
        }

# Initialize system
orchestrator = SystemOrchestrator()


# ============================================================================
# Routes - Page 1: Main Dashboard
# ============================================================================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Main Dashboard - Real-time overview of 25+ trains"""
    return render_template('dashboard.html')

@app.route('/api/dashboard_data')
def dashboard_data():
    """API endpoint for dashboard real-time data"""
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    
    # Get train status distribution
    train_status = pd.read_sql_query('''
        SELECT status, COUNT(*) as count
        FROM trains
        GROUP BY status
    ''', conn)
    
    # Get recent performance metrics
    performance = pd.read_sql_query('''
        SELECT * FROM performance_metrics
        ORDER BY metric_date DESC
        LIMIT 1
    ''', conn)
    
    # Get recent schedules for delay analysis
    recent_schedules = pd.read_sql_query('''
        SELECT route, AVG(delay_minutes) as avg_delay, COUNT(*) as trips
        FROM schedules
        WHERE DATE(scheduled_departure) >= DATE('now', '-7 days')
        GROUP BY route
        ORDER BY avg_delay DESC
        LIMIT 10
    ''', conn)
    
    conn.close()
    
    return jsonify({
        'train_status': train_status.to_dict('records'),
        'performance': performance.to_dict('records')[0] if not performance.empty else current_system_state['performance_metrics'],
        'route_performance': recent_schedules.to_dict('records'),
        'last_update': current_system_state['last_update'].strftime('%Y-%m-%d %H:%M:%S'),
        'alerts': current_system_state.get('alerts', [])
    })

@app.route('/api/search_trains')
def search_trains():
    """Search functionality for trains/routes"""
    query = request.args.get('query', '')
    
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    
    search_results = pd.read_sql_query('''
        SELECT train_id, route, status, depot, readiness_score, passenger_load
        FROM trains
        WHERE train_id LIKE ? OR route LIKE ? OR depot LIKE ?
        ORDER BY readiness_score DESC
        LIMIT 20
    ''', conn, params=[f'%{query}%', f'%{query}%', f'%{query}%'])
    
    conn.close()
    
    return jsonify(search_results.to_dict('records'))

# ============================================================================
# Routes - Page 2: Train Status & Management
# ============================================================================

@app.route('/trains')
def train_management():
    """Train Status & Management page"""
    return render_template('train_management.html')

@app.route('/api/trains')
def get_trains():
    """Get all trains with filtering"""
    status_filter = request.args.get('status', 'all')
    route_filter = request.args.get('route', 'all')
    
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    
    query = "SELECT * FROM trains WHERE 1=1"
    params = []
    
    if status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
    
    if route_filter != 'all':
        query += " AND route = ?"
        params.append(route_filter)
    
    query += " ORDER BY readiness_score DESC"
    
    trains = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return jsonify(trains.to_dict('records'))

@app.route('/api/train/<train_id>')
def get_train_details(train_id):
    """Get detailed train information"""
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    
    # Get train details
    train = pd.read_sql_query('''
        SELECT * FROM trains WHERE train_id = ?
    ''', conn, params=[train_id])
    
    # Get recent schedules
    recent_schedules = pd.read_sql_query('''
        SELECT * FROM schedules 
        WHERE train_id = ?
        ORDER BY scheduled_departure DESC
        LIMIT 10
    ''', conn, params=[train_id])
    
    # Get maintenance history
    maintenance = pd.read_sql_query('''
        SELECT * FROM maintenance
        WHERE train_id = ?
        ORDER BY scheduled_date DESC
        LIMIT 5
    ''', conn, params=[train_id])
    
    conn.close()
    
    # AI reasoning for status
    if not train.empty:
        train_data = train.iloc[0]
        ai_reasoning = ai_engine.explain_train_status(train_data)
        
        return jsonify({
            'train': train.to_dict('records')[0],
            'recent_schedules': recent_schedules.to_dict('records'),
            'maintenance_history': maintenance.to_dict('records'),
            'ai_reasoning': ai_reasoning
        })
    
    return jsonify({'error': 'Train not found'}), 404

# ============================================================================
# Routes - Page 3: Schedule Optimization
# ============================================================================

@app.route('/scheduling')
def schedule_optimization():
    """Schedule Optimization page"""
    return render_template('scheduling.html')

@app.route('/api/optimize_schedule', methods=['POST'])
def optimize_schedule():
    """Generate optimal schedule using OR-Tools"""
    data = request.json
    
    # Get current constraints
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    trains = pd.read_sql_query("SELECT * FROM trains WHERE status IN ('Running', 'Ready')", conn)
    conn.close()
    
    # Run optimization
    try:
        optimal_schedule = optimizer.optimize_schedule(
            trains=trains,
            routes=data.get('routes', ['Red Line', 'Blue Line', 'Green Line']),
            time_horizon=data.get('time_horizon', 24),
            constraints=data.get('constraints', {})
        )
        
        return jsonify({
            'success': True,
            'optimal_schedule': optimal_schedule,
            'performance_improvement': optimizer.calculate_improvement(optimal_schedule),
            'conflicts_resolved': optimizer.get_conflicts_resolved()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/current_schedule')
def get_current_schedule():
    """Get current schedule with performance analysis"""
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    
    current_schedule = pd.read_sql_query('''
        SELECT s.*, t.status as train_status, t.readiness_score
        FROM schedules s
        JOIN trains t ON s.train_id = t.train_id
        WHERE DATE(s.scheduled_departure) = DATE('now')
        ORDER BY s.scheduled_departure
    ''', conn)
    
    # Route efficiency analysis
    route_efficiency = pd.read_sql_query('''
        SELECT 
            route,
            AVG(delay_minutes) as avg_delay,
            COUNT(*) as total_trips,
            AVG(passenger_load) as avg_load
        FROM schedules
        WHERE DATE(scheduled_departure) >= DATE('now', '-7 days')
        GROUP BY route
    ''', conn)
    
    conn.close()
    
    return jsonify({
        'current_schedule': current_schedule.to_dict('records'),
        'route_efficiency': route_efficiency.to_dict('records')
    })

# ============================================================================
# Routes - Page 4: Predictive Analytics
# ============================================================================

@app.route('/analytics')
def predictive_analytics():
    """Predictive Analytics page"""
    return render_template('analytics.html')

@app.route('/api/demand_forecast')
def demand_forecast():
    """Generate demand forecast with confidence intervals"""
    days_ahead = int(request.args.get('days', 7))
    route = request.args.get('route', 'all')
    
    try:
        forecast = ai_engine.predict_demand(days_ahead=days_ahead, route=route)
        return jsonify({
            'success': True,
            'forecast': forecast,
            'confidence_intervals': ai_engine.get_confidence_intervals(forecast),
            'factors': ai_engine.get_demand_factors()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/maintenance_prediction')
def maintenance_prediction():
    """Predict maintenance needs"""
    conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
    trains = pd.read_sql_query("SELECT * FROM trains", conn)
    conn.close()
    
    predictions = []
    for _, train in trains.iterrows():
        prediction = ai_engine.predict_maintenance(train)
        predictions.append({
            'train_id': train['train_id'],
            'prediction': prediction,
            'confidence': prediction.get('confidence', 0.8),
            'recommended_action': prediction.get('action', 'Monitor'),
            'days_until_maintenance': prediction.get('days_until', 30)
        })
    
    return jsonify(predictions)

@app.route('/api/delay_prediction')
def delay_prediction():
    """Predict delays with contributing factors"""
    route = request.args.get('route', 'Red Line')
    time_of_day = request.args.get('time', '08:00')
    
    try:
        prediction = ai_engine.predict_delays(route=route, time_of_day=time_of_day)
        return jsonify({
            'success': True,
            'predicted_delay': prediction['delay'],
            'confidence': prediction['confidence'],
            'contributing_factors': prediction['factors'],
            'mitigation_suggestions': prediction['suggestions']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# Routes - Page 5: Emergency Management & Testing
# ============================================================================

@app.route('/emergency')
def emergency_management():
    """Emergency Management & Testing page"""
    return render_template('emergency.html')

@app.route('/api/emergency_simulation', methods=['POST'])
def emergency_simulation():
    """Simulate emergency scenarios"""
    scenario = request.json
    
    try:
        # Get current system state
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        available_trains = pd.read_sql_query('''
            SELECT * FROM trains 
            WHERE status IN ('Ready', 'Held') AND readiness_score > 0.7
        ''', conn)
        conn.close()
        
        # Run AI emergency response
        response = ai_engine.emergency_response(
            scenario_type=scenario.get('type'),
            affected_trains=scenario.get('affected_trains', []),
            affected_routes=scenario.get('affected_routes', []),
            available_trains=available_trains
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'alternative_routes': response.get('alternative_routes', []),
            'backup_trains': response.get('backup_trains', []),
            'estimated_impact': response.get('impact', {}),
            'recovery_time': response.get('recovery_time', '15-30 minutes')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/what_if_analysis', methods=['POST'])
def what_if_analysis():
    """Perform what-if analysis"""
    analysis_params = request.json
    
    try:
        results = ai_engine.what_if_analysis(
            scenario=analysis_params.get('scenario'),
            parameters=analysis_params.get('parameters', {}),
            time_horizon=analysis_params.get('time_horizon', 24)
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'performance_impact': results.get('performance_delta', {}),
            'recommendations': results.get('recommendations', [])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# Routes - Page 6: Data Input & System Configuration
# ============================================================================

@app.route('/config')
def data_configuration():
    """Data Input & System Configuration page"""
    return render_template('data_config.html')

@app.route('/api/upload_data', methods=['POST'])
def upload_data():
    """Handle custom data upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    data_type = request.form.get('data_type', 'schedules')
    
    try:
        # Process uploaded file
        df = pd.read_csv(file)
        
        # Validate and clean data
        validated_df = data_gen.validate_and_clean_data(df, data_type)
        
        # Save to database
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        validated_df.to_sql(data_type, conn, if_exists='append', index=False)
        conn.close()
        
        # Retrain models if needed
        if data_type in ['schedules', 'trains']:
            ai_engine.incremental_training(validated_df, data_type)
        
        return jsonify({
            'success': True,
            'records_processed': len(validated_df),
            'data_quality_score': data_gen.calculate_quality_score(validated_df)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/retrain_models', methods=['POST'])
def retrain_models():
    """Retrain AI models with latest data"""
    try:
        conn = sqlite3.connect('metro_ai_system.db', check_same_thread=False)
        
        schedules_df = pd.read_sql_query("SELECT * FROM schedules", conn)
        trains_df = pd.read_sql_query("SELECT * FROM trains", conn)
        maintenance_df = pd.read_sql_query("SELECT * FROM maintenance", conn)
        
        conn.close()
        
        # Retrain models
        training_results = ai_engine.retrain_models(schedules_df, trains_df, maintenance_df)
        
        return jsonify({
            'success': True,
            'training_results': training_results,
            'model_performance': ai_engine.get_model_performance()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

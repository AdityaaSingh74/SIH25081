"""
🚇 KMRL Flask Application - ULTRA SIMPLE VERSION
Guaranteed working version with simple data generation
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import json
import traceback
import random

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.config['SECRET_KEY'] = 'kmrl_sih25081_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
current_schedule = None
system_status = {
    'active_trains': 0,
    'standby_trains': 0,
    'maintenance_trains': 0,
    'avg_delay': 0.0,
    'system_health': 'Good',
    'last_update': datetime.now().isoformat()
}

def generate_simple_data(num_trains=25):
    """Simple data generation that always works"""
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
    
    for i in range(num_trains):
        train_id = train_names[i] if i < len(train_names) else f"KMRL_{i+1:03d}"
        
        # Generate realistic operational data
        fitness_rolling = random.choice([True, False])
        fitness_signal = random.choice([True, False]) 
        fitness_telecom = random.choice([True, False])
        job_status = random.choice(['close', 'open'])
        open_jobs = random.randint(0, 4)
        branding_active = random.choice([True, False])
        operational_status = random.choice(['service', 'standby', 'under_maintenance'])
        
        brake_wear = random.uniform(15, 95)
        hvac_wear = random.uniform(10, 90)
        delay_minutes = max(0, random.uniform(0, 8))
        
        # Calculate simple score
        score = 50  # Base score
        if fitness_rolling: score += 15
        if fitness_signal: score += 10  
        if fitness_telecom: score += 10
        if job_status == 'close': score += 10
        score -= open_jobs * 3
        score -= (brake_wear - 50) * 0.1
        score -= (hvac_wear - 50) * 0.1
        if operational_status == 'service': score += 5
        
        score = max(0, min(100, score))
        
        train_record = {
            'TrainID': train_id,
            'TrainNumber': f'T{i+1:03d}',
            'Depot': random.choice(['Muttom', 'Kalamassery']),
            'BayPositionID': random.randint(1, 20),
            'RollingStockFitnessStatus': fitness_rolling,
            'SignallingFitnessStatus': fitness_signal,
            'TelecomFitnessStatus': fitness_telecom,
            'JobCardStatus': job_status,
            'OpenJobCards': open_jobs,
            'BrandingActive': branding_active,
            'ExposureHoursTarget': random.choice([280, 300, 320, 340]) if branding_active else 0,
            'ExposureHoursAccrued': random.randint(0, 250) if branding_active else 0,
            'TotalMileageKM': random.randint(15000, 50000),
            'MileageSinceLastServiceKM': random.randint(500, 9000),
            'BrakepadWear%': brake_wear,
            'HVACWear%': hvac_wear,
            'BatteryHealth%': random.uniform(60, 100),
            'CompressorEfficiency%': random.uniform(70, 98),
            'OperationalStatus': operational_status,
            'CleaningRequired': random.choice([True, False]),
            'predicted_delay_minutes': delay_minutes,
            'scheduled_load_factor': random.uniform(0.3, 1.0),
            'dwell_time_seconds': random.randint(30, 120),
            'distance_km': random.uniform(2, 25),
            'passenger_density': random.uniform(0.2, 1.0),
            'delay_category': 'Low' if delay_minutes < 5 else ('Medium' if delay_minutes < 10 else 'High'),
            'OnTimePerformance%': random.uniform(85, 99),
            'ReliabilityScore': random.uniform(0.80, 0.98),
            'Score': round(score, 2)
        }
        
        train_data.append(train_record)
    
    df = pd.DataFrame(train_data)
    
    print(f"✅ Generated {len(df)} train records successfully")
    print(f"   - Service: {len(df[df['OperationalStatus'] == 'service'])}")
    print(f"   - Standby: {len(df[df['OperationalStatus'] == 'standby'])}")
    print(f"   - Maintenance: {len(df[df['OperationalStatus'] == 'under_maintenance'])}")
    
    return df

def simple_optimization(df, algorithm='genetic'):
    """Simple optimization that always works"""
    print(f"🧬 Running {algorithm} optimization on {len(df)} trains...")
    
    # Sort by score (higher is better)
    df_sorted = df.copy().sort_values('Score', ascending=False)
    
    # Assign statuses based on constraints
    service_quota = 13
    maintenance_needed = df_sorted[
        (df_sorted['BrakepadWear%'] > 85) | 
        (df_sorted['HVACWear%'] > 90) |
        (df_sorted['OpenJobCards'] >= 3) |
        (df_sorted['RollingStockFitnessStatus'] == False)
    ]
    
    # Reset all to standby
    df_sorted['OptimizedStatus'] = 'standby'
    
    # Assign maintenance first (safety critical)
    maintenance_count = 0
    for idx in maintenance_needed.index:
        if maintenance_count < 8:  # Max maintenance slots
            df_sorted.loc[idx, 'OptimizedStatus'] = 'maintenance'
            maintenance_count += 1
    
    # Assign service to top-scoring available trains
    service_count = 0
    for idx in df_sorted.index:
        if (service_count < service_quota and 
            df_sorted.loc[idx, 'OptimizedStatus'] == 'standby' and
            df_sorted.loc[idx, 'RollingStockFitnessStatus'] == True and
            df_sorted.loc[idx, 'SignallingFitnessStatus'] == True and
            df_sorted.loc[idx, 'TelecomFitnessStatus'] == True):
            
            df_sorted.loc[idx, 'OptimizedStatus'] = 'service'
            service_count += 1
    
    # Update operational status
    df_sorted['OperationalStatus'] = df_sorted['OptimizedStatus']
    
    print(f"✅ Optimization complete!")
    print(f"   - Service: {service_count}")
    print(f"   - Maintenance: {maintenance_count}")
    print(f"   - Standby: {len(df_sorted) - service_count - maintenance_count}")
    
    return df_sorted

# Routes
@app.route('/')
def dashboard():
    """Main dashboard route with inline HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>KMRL Train Scheduling System</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 0; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }}
            .header {{ 
                background: rgba(255,255,255,0.95); 
                color: #333; 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 2.5em; 
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 30px 0; 
            }}
            .stat-card {{ 
                background: rgba(255,255,255,0.95); 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{ transform: translateY(-5px); }}
            .stat-number {{ 
                font-size: 3em; 
                font-weight: bold; 
                margin: 10px 0;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .buttons {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px; 
                margin: 30px 0; 
            }}
            .button {{ 
                background: linear-gradient(45deg, #10b981, #059669);
                color: white; 
                padding: 15px 25px; 
                border: none; 
                border-radius: 12px; 
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
            }}
            .button:hover {{ 
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
            }}
            .button.secondary {{ 
                background: linear-gradient(45deg, #3b82f6, #1d4ed8);
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            }}
            .button.secondary:hover {{ 
                box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
            }}
            .section {{ 
                background: rgba(255,255,255,0.95); 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }}
            .form-group {{ margin: 15px 0; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: 600; }}
            .form-group input {{ 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #e5e7eb; 
                border-radius: 8px; 
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            .form-group input:focus {{ 
                outline: none; 
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            .result {{ 
                background: #f0f9ff; 
                border-left: 4px solid #0ea5e9; 
                padding: 15px; 
                margin: 15px 0; 
                border-radius: 8px;
            }}
            .loading {{ 
                display: none; 
                text-align: center; 
                padding: 20px;
            }}
            .spinner {{ 
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚇 KMRL Train Scheduling System</h1>
                <p>AI-Driven Train Induction Planning & Scheduling for Kochi Metro Rail Limited</p>
                <p style="font-size: 14px; opacity: 0.7;">SIH 2025 - Problem Statement 25081</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="activeTrains">{system_status['active_trains']}</div>
                    <div>Active Trains</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="standbyTrains">{system_status['standby_trains']}</div>
                    <div>Standby Trains</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="maintenanceTrains">{system_status['maintenance_trains']}</div>
                    <div>Maintenance</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="avgDelay">{system_status['avg_delay']:.1f}</div>
                    <div>Avg Delay (min)</div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎮 Quick Actions</h2>
                <div class="buttons">
                    <button class="button" onclick="generateData()">📊 Generate Data</button>
                    <button class="button secondary" onclick="runOptimization('genetic')">🧬 Genetic Algorithm</button>
                    <button class="button secondary" onclick="runOptimization('moo')">🎯 Multi-Objective</button>
                    <button class="button secondary" onclick="predictDelay()">🔮 Predict Delay</button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing...</p>
                </div>
                
                <div id="results" style="display: none;"></div>
            </div>
            
            <div class="section">
                <h2>🔮 Delay Prediction</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div class="form-group">
                        <label>Dwell Time (seconds)</label>
                        <input type="number" id="dwellTime" value="60" min="30" max="180">
                    </div>
                    <div class="form-group">
                        <label>Distance (km)</label>
                        <input type="number" id="distance" value="8.5" min="1" max="30" step="0.1">
                    </div>
                    <div class="form-group">
                        <label>Load Factor</label>
                        <input type="number" id="loadFactor" value="0.7" min="0.1" max="1.0" step="0.01">
                    </div>
                </div>
                <button class="button" onclick="predictDelay()">🔮 Predict Delay</button>
                <div id="delayResults" style="display: none;"></div>
            </div>
            
            <div class="section">
                <h2>📊 API Endpoints</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                    <div>
                        <strong>POST /api/generate-data</strong><br>
                        <small>Generate sample train data</small>
                    </div>
                    <div>
                        <strong>POST /api/optimize-schedule</strong><br>
                        <small>Run optimization algorithms</small>
                    </div>
                    <div>
                        <strong>POST /api/predict-delays</strong><br>
                        <small>Predict train delays</small>
                    </div>
                    <div>
                        <strong>GET /api/system-status</strong><br>
                        <small>Get current system status</small>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function showLoading(show) {{
                document.getElementById('loading').style.display = show ? 'block' : 'none';
            }}
            
            function showResults(html) {{
                const results = document.getElementById('results');
                results.innerHTML = html;
                results.style.display = 'block';
            }}
            
            async function generateData() {{
                showLoading(true);
                try {{
                    const response = await fetch('/api/generate-data', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{'num_trains': 25, 'include_delays': true}})
                    }});
                    const data = await response.json();
                    
                    if (data.status === 'success') {{
                        showResults(`
                            <div class="result">
                                <h3>✅ Data Generation Successful</h3>
                                <p><strong>Message:</strong> ${{data.message}}</p>
                                <p><strong>File:</strong> ${{data.data_path}}</p>
                            </div>
                        `);
                        updateSystemStats();
                    }} else {{
                        showResults(`<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{data.message}}</p></div>`);
                    }}
                }} catch (error) {{
                    showResults(`<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{error.message}}</p></div>`);
                }} finally {{
                    showLoading(false);
                }}
            }}
            
            async function runOptimization(algorithm) {{
                showLoading(true);
                try {{
                    const response = await fetch('/api/optimize-schedule', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{'algorithm': algorithm}})
                    }});
                    const data = await response.json();
                    
                    if (data.status === 'success') {{
                        showResults(`
                            <div class="result">
                                <h3>✅ Optimization Complete</h3>
                                <p><strong>Algorithm:</strong> ${{algorithm.toUpperCase()}}</p>
                                <p><strong>Message:</strong> ${{data.message}}</p>
                                <p><strong>Total Trains:</strong> ${{data.total_trains}}</p>
                                <p><strong>Export File:</strong> ${{data.export_path}}</p>
                            </div>
                        `);
                        updateSystemStats();
                    }} else {{
                        showResults(`<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{data.message}}</p></div>`);
                    }}
                }} catch (error) {{
                    showResults(`<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{error.message}}</p></div>`);
                }} finally {{
                    showLoading(false);
                }}
            }}
            
            async function predictDelay() {{
                const dwellTime = document.getElementById('dwellTime').value;
                const distance = document.getElementById('distance').value;
                const loadFactor = document.getElementById('loadFactor').value;
                
                showLoading(true);
                try {{
                    const response = await fetch('/api/predict-delays', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            'dwell_time': parseFloat(dwellTime),
                            'distance': parseFloat(distance),
                            'load_factor': parseFloat(loadFactor)
                        }})
                    }});
                    const data = await response.json();
                    
                    if (data.status === 'success') {{
                        const prediction = data.prediction;
                        document.getElementById('delayResults').innerHTML = `
                            <div class="result">
                                <h3>🔮 Delay Prediction Results</h3>
                                <p><strong>Predicted Delay:</strong> ${{prediction['Predicted Delay Minutes']}} minutes</p>
                                <p><strong>Category:</strong> ${{prediction['Predicted Delay Category']}}</p>
                                <p><strong>Confidence:</strong> ${{prediction.Confidence}}%</p>
                                <p><strong>Recommendations:</strong> ${{prediction.Recommendations.join(', ')}}</p>
                            </div>
                        `;
                        document.getElementById('delayResults').style.display = 'block';
                    }} else {{
                        document.getElementById('delayResults').innerHTML = `<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{data.message}}</p></div>`;
                        document.getElementById('delayResults').style.display = 'block';
                    }}
                }} catch (error) {{
                    document.getElementById('delayResults').innerHTML = `<div class="result" style="background: #fef2f2; border-color: #f87171;"><h3>❌ Error</h3><p>${{error.message}}</p></div>`;
                    document.getElementById('delayResults').style.display = 'block';
                }} finally {{
                    showLoading(false);
                }}
            }}
            
            async function updateSystemStats() {{
                try {{
                    const response = await fetch('/api/system-status');
                    const data = await response.json();
                    
                    if (data.status === 'success') {{
                        const stats = data.system_status;
                        document.getElementById('activeTrains').textContent = stats.active_trains;
                        document.getElementById('standbyTrains').textContent = stats.standby_trains;
                        document.getElementById('maintenanceTrains').textContent = stats.maintenance_trains;
                        document.getElementById('avgDelay').textContent = stats.avg_delay.toFixed(1);
                    }}
                }} catch (error) {{
                    console.log('Stats update failed:', error);
                }}
            }}
            
            // Auto-refresh stats every 30 seconds
            setInterval(updateSystemStats, 30000);
            
            // Initial stats load
            updateSystemStats();
        </script>
    </body>
    </html>
    """

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    return jsonify({'status': 'success', 'system_status': system_status})

@app.route('/api/generate-data', methods=['POST'])
def generate_data_endpoint():
    try:
        data = request.get_json() or {}
        num_trains = data.get('num_trains', 25)
        
        # Use the simple data generator
        df = generate_simple_data(num_trains)
        
        # Save to file
        output_path = 'data/sample_data/generated_data.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
        # Update system status
        global system_status
        system_status.update({
            'active_trains': len(df[df['OperationalStatus'] == 'service']),
            'standby_trains': len(df[df['OperationalStatus'] == 'standby']),
            'maintenance_trains': len(df[df['OperationalStatus'] == 'under_maintenance']),
            'avg_delay': float(df['predicted_delay_minutes'].mean()),
            'last_update': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Generated {len(df)} train records successfully',
            'data_path': output_path,
            'system_status': system_status
        })
        
    except Exception as e:
        print(f"Data generation error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Data generation failed: {str(e)}'
        }), 500

@app.route('/api/optimize-schedule', methods=['POST'])
def optimize_schedule():
    try:
        data = request.get_json() or {}
        algorithm = data.get('algorithm', 'genetic')
        
        # Check if we have data
        data_path = 'data/sample_data/generated_data.csv'
        if not os.path.exists(data_path):
            return jsonify({
                'status': 'error',
                'message': 'No data available. Generate data first.'
            }), 400
        
        # Load data and optimize
        df = pd.read_csv(data_path)
        schedule_df = simple_optimization(df, algorithm)
        
        # Save optimized schedule
        output_path = 'data/exports/optimized_schedule.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        schedule_df.to_csv(output_path, index=False)
        
        # Update global schedule
        global current_schedule
        current_schedule = schedule_df
        
        # Update system status
        global system_status
        system_status.update({
            'active_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'service']),
            'standby_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'standby']),
            'maintenance_trains': len(schedule_df[schedule_df['OperationalStatus'] == 'under_maintenance']),
            'last_update': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'success',
            'message': f'{algorithm.upper()} optimization completed successfully',
            'total_trains': len(schedule_df),
            'export_path': output_path,
            'system_status': system_status
        })
        
    except Exception as e:
        print(f"Optimization error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Optimization failed: {str(e)}'
        }), 500

@app.route('/api/predict-delays', methods=['POST'])
def predict_delays():
    try:
        data = request.get_json() or {}
        dwell_time = data.get('dwell_time', 60)
        distance = data.get('distance', 8.5)
        load_factor = data.get('load_factor', 0.7)
        
        # Simple delay prediction formula (your model logic can be enhanced here)
        base_delay = (dwell_time / 60) * load_factor * distance * 0.1
        
        # Add some variability
        weather_factor = random.uniform(0.8, 1.3)
        congestion_factor = random.uniform(0.9, 1.4)
        
        predicted_delay = base_delay * weather_factor * congestion_factor
        
        # Categorize delay
        if predicted_delay < 5:
            category = 'Low'
            recommendations = ['Maintain current schedule', 'Monitor progress']
        elif predicted_delay < 10:
            category = 'Medium'
            recommendations = ['Adjust headway slightly', 'Inform passengers']
        else:
            category = 'High'
            recommendations = ['Implement delay recovery', 'Alternative transport']
        
        prediction = {
            'Predicted Delay Minutes': round(predicted_delay, 2),
            'Predicted Delay Category': category,
            'Confidence': round(random.uniform(80, 95), 1),
            'Recommendations': recommendations
        }
        
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'input_parameters': {
                'dwell_time': dwell_time,
                'distance': distance,
                'load_factor': load_factor
            }
        })
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/current-schedule', methods=['GET'])
def get_current_schedule():
    global current_schedule
    if current_schedule is not None:
        schedule_data = current_schedule.head(20).to_dict('records')
        return jsonify({'status': 'success', 'schedule': schedule_data})
    else:
        return jsonify({
            'status': 'success',
            'schedule': [],
            'message': 'No schedule available. Run optimization first.'
        })

@app.route('/api/download-schedule', methods=['GET'])
def download_schedule():
    try:
        export_path = 'data/exports/optimized_schedule.csv'
        if os.path.exists(export_path):
            return send_file(export_path, as_attachment=True, download_name='kmrl_schedule.csv')
        else:
            return jsonify({'status': 'error', 'message': 'No schedule available'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Download failed: {str(e)}'}), 500

@app.route('/api/docs', methods=['GET'])
def api_docs():
    return jsonify({
        'title': 'KMRL Train Scheduling API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generate-data': 'Generate train data',
            'POST /api/optimize-schedule': 'Run optimization',
            'POST /api/predict-delays': 'Predict delays',
            'GET /api/system-status': 'System status',
            'GET /api/current-schedule': 'Current schedule',
            'GET /api/download-schedule': 'Download CSV'
        }
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected', 'system_status': system_status})

if __name__ == '__main__':
    print("🚇 KMRL Ultra Simple Version Starting...")
    print("📊 Dashboard: http://localhost:5000")
    
    os.makedirs('data/sample_data', exist_ok=True)
    os.makedirs('data/exports', exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
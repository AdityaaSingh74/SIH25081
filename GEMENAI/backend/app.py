import os
import sys
import traceback

# This is a fix for the ModuleNotFoundError. It adds the project's root directory
# to Python's path, allowing it to find the 'backend' module.
# This makes the script runnable both as `python backend/app.py` and `python -m backend.app`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify, send_file

# Import your custom modules
from backend.ml.feature_engineering import preprocess_data
from backend.ml.train_model import train_all_models
from backend.optimization.optimizer import run_schedule_optimization
from backend.optimization.simulation import run_disruption_simulation

# --- Flask App Initialization ---
app = Flask(__name__, template_folder='../templates')

# --- Helper Function for Error Handling ---
def create_error_response(e, status_code=500):
    traceback.print_exc()
    return jsonify({"status": "error", "message": str(e)}), status_code

# --- API Endpoints ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/preprocess', methods=['POST'])
def preprocess():
    """Endpoint to trigger data preprocessing."""
    try:
        _, preview_json = preprocess_data()
        return jsonify({
            "status": "success",
            "message": "Data preprocessing completed successfully!",
            "data_preview": preview_json
        })
    except Exception as e:
        return create_error_response(e)

@app.route('/train', methods=['POST'])
def train():
    """Endpoint to trigger model training."""
    try:
        metrics = train_all_models()
        return jsonify({
            "status": "success",
            "message": "ML models trained successfully!",
            "metrics": metrics
        })
    except Exception as e:
        return create_error_response(e)

@app.route('/optimize', methods=['POST'])
def optimize():
    """Endpoint to run the schedule optimization."""
    try:
        results = run_schedule_optimization()
        return jsonify({
            "status": "success",
            "message": f"Optimization finished with status: {results['status']}",
            "results": results
        })
    except Exception as e:
        return create_error_response(e)

@app.route('/simulate', methods=['POST'])
def simulate():
    """Endpoint to run the disruption simulation."""
    try:
        results = run_disruption_simulation()
        return jsonify({
            "status": "success",
            "message": "Simulation completed!",
            "results": results
        })
    except Exception as e:
        return create_error_response(e)

@app.route('/download_schedule')
def download_schedule():
    """Endpoint to download the optimized schedule CSV."""
    try:
        path = os.path.join(os.path.dirname(__file__), 'optimization', 'schedules', 'optimized_schedule.csv')
        if not os.path.exists(path):
            return "File not found. Please generate a schedule first.", 404
        return send_file(path, as_attachment=True)
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)



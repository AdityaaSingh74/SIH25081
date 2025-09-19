"""
backend/app.py

Minimal Flask app exposing /optimize endpoint with SocketIO support for real-time features.
"""
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from backend.optimization.optimization_run import run_optimization
import os

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/optimize", methods=["POST"])
def optimize():
    payload = request.json or {}
    trainsets = payload.get("trainsets_csv", "data/trainsets.csv")
    jobcards = payload.get("jobcards_csv")
    model = payload.get("model_path")
    min_peak = int(payload.get("min_peak", 18))
    res = run_optimization(trainset_csv=trainsets, jobcards_csv=jobcards, model_path=model, min_peak_trainsets=min_peak)
    details = res.get("details")
    if hasattr(details, "to_dict"):
        details = details.to_dict(orient="records")
    return jsonify({
        "status": res.get("pulp_status"),
        "objective": res.get("objective_value"),
        "selected_trainsets": res.get("selected_trainsets"),
        "details": details
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)

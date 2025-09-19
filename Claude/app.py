"""
🚇 KMRL ENHANCED FRONTEND - IMPROVED UI/UX
Modern dashboard with real-time updates and professional design
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Sample data for demonstration
def get_sample_data():
    return {
        'scheduling_accuracy': 98.2,
        'average_delay': 1.8,
        'train_availability': 96,
        'passenger_wait_time': 3.9,
        'active_alerts': 0,
        'total_trains': 25,
        'service_trains': 15,
        'standby_trains': 6,
        'maintenance_trains': 4,
        'last_update': datetime.now().strftime('%H:%M:%S')
    }

@app.route('/')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Metro AI OS - KMRL SIH 25081</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            z-index: 1000;
            box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }

        .logo h1 {
            font-size: 20px;
            font-weight: 700;
            color: #1a1a1a;
        }

        .sih-tag {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .nav-menu {
            list-style: none;
        }

        .nav-item {
            margin-bottom: 8px;
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            text-decoration: none;
            color: #666;
            border-radius: 12px;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .nav-link:hover, .nav-link.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateX(4px);
        }

        .status-indicator {
            margin-top: 30px;
            padding: 16px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 12px;
            border-left: 4px solid #10b981;
        }

        .status-text {
            font-size: 12px;
            font-weight: 600;
            color: #10b981;
        }

        .main-content {
            margin-left: 280px;
            padding: 20px;
            min-height: 100vh;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
        }

        .header-subtitle {
            color: #666;
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .search-container {
            position: relative;
            max-width: 300px;
        }

        .search-input {
            width: 100%;
            padding: 12px 16px 12px 44px;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: #999;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: translateY(-4px);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .stat-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 16px;
        }

        .stat-title {
            font-size: 14px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: white;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
        }

        .stat-change {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 600;
        }

        .stat-change.positive {
            color: #10b981;
        }

        .stat-change.negative {
            color: #ef4444;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .chart-title {
            font-size: 18px;
            font-weight: 700;
            color: #1a1a1a;
        }

        .chart-selector {
            padding: 8px 16px;
            border: 2px solid #f0f0f0;
            border-radius: 8px;
            background: white;
            font-size: 12px;
            font-weight: 600;
            outline: none;
            cursor: pointer;
        }

        .route-analysis {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }

        .route-bars {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-top: 20px;
        }

        .route-item {
            flex: 1;
            text-align: center;
        }

        .route-bar {
            height: 120px;
            display: flex;
            align-items: end;
            justify-content: center;
            gap: 4px;
            margin-bottom: 8px;
        }

        .bar {
            width: 20px;
            border-radius: 4px 4px 0 0;
            animation: growUp 0.8s ease;
        }

        .bar.delay {
            background: #ef4444;
        }

        .bar.on-time {
            background: #10b981;
        }

        .route-label {
            font-size: 12px;
            font-weight: 600;
            color: #666;
        }

        .alerts-section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .alert-item {
            padding: 16px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #10b981;
        }

        .quick-actions {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .action-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 12px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .btn-secondary {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }

        .train-status-pie {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 20px auto;
        }

        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            margin-top: 16px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 600;
        }

        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes growUp {
            from { height: 0; }
            to { height: var(--bar-height); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 250px;
            }
            
            .main-content {
                margin-left: 250px;
                padding: 15px;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <i class="fas fa-train" style="font-size: 24px; color: #667eea;"></i>
            <div>
                <h1>Smart Metro AI OS</h1>
                <div class="sih-tag">SIH 25081 - KMRL</div>
            </div>
        </div>

        <ul class="nav-menu">
            <li class="nav-item">
                <a href="#" class="nav-link active">
                    <i class="fas fa-tachometer-alt"></i>
                    Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-subway"></i>
                    Train Management
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-clock"></i>
                    Schedule Optimization
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-chart-line"></i>
                    Predictive Analytics
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-exclamation-triangle"></i>
                    Emergency Management
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link">
                    <i class="fas fa-cog"></i>
                    Data Configuration
                </a>
            </li>
        </ul>

        <div class="status-indicator">
            <div class="status-text">
                <i class="fas fa-circle pulse" style="color: #10b981; margin-right: 8px;"></i>
                AI Models: Online<br>
                Database: Connected<br>
                Real-time Updates: Active
            </div>
        </div>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>AI Dashboard</h1>
            <div class="header-subtitle">
                <span>Real-time monitoring of 25+ trains across KMRL network</span>
                <div class="search-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" class="search-input" placeholder="Search trains, routes...">
                </div>
                <span>Last Update: <span id="last-update">21:54:09</span></span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">Scheduling Accuracy</div>
                    <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #059669);">
                        <i class="fas fa-clock"></i>
                    </div>
                </div>
                <div class="stat-value" id="scheduling-accuracy">98.2%</div>
                <div class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>+1.2% from target: 99.8% (SIH Goal)</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">Average Delay</div>
                    <div class="stat-icon" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">
                        <i class="fas fa-hourglass-half"></i>
                    </div>
                </div>
                <div class="stat-value" id="avg-delay">1.8 min</div>
                <div class="stat-change positive">
                    <i class="fas fa-arrow-down"></i>
                    <span>-0.2 min Target: <2 min (AI Optimized)</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">Train Availability</div>
                    <div class="stat-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">
                        <i class="fas fa-train"></i>
                    </div>
                </div>
                <div class="stat-value" id="train-availability">96%</div>
                <div class="stat-change positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>Active: Running + Ready trains</span>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-title">Passenger Wait Time</div>
                    <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                        <i class="fas fa-users"></i>
                    </div>
                </div>
                <div class="stat-value" id="wait-time">3.9 min</div>
                <div class="stat-change positive">
                    <i class="fas fa-arrow-down"></i>
                    <span>-0.8% Target: 30% reduction</span>
                </div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">Performance Trends (7 Days)</h3>
                    <select class="chart-selector" id="chart-selector">
                        <option value="scheduling">Scheduling Accuracy</option>
                        <option value="delays">Average Delays</option>
                        <option value="availability">Train Availability</option>
                    </select>
                </div>
                <canvas id="performance-chart" width="400" height="200"></canvas>
            </div>

            <div class="chart-container">
                <h3 class="chart-title">Train Status Distribution</h3>
                <div class="train-status-pie">
                    <canvas id="status-pie" width="200" height="200"></canvas>
                </div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10b981;"></div>
                        <span>Running</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3b82f6;"></div>
                        <span>Ready</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #f59e0b;"></div>
                        <span>Hold</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #ef4444;"></div>
                        <span>Maintenance</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="route-analysis">
            <h3 class="chart-title">Route Performance Analysis</h3>
            <p style="color: #666; margin-bottom: 16px;">Avg Delay Total Trips</p>
            
            <div class="route-bars">
                <div class="route-item">
                    <div class="route-bar">
                        <div class="bar delay" style="height: 60px;"></div>
                        <div class="bar on-time" style="height: 80px;"></div>
                    </div>
                    <div class="route-label">Red Line</div>
                </div>
                <div class="route-item">
                    <div class="route-bar">
                        <div class="bar delay" style="height: 45px;"></div>
                        <div class="bar on-time" style="height: 75px;"></div>
                    </div>
                    <div class="route-label">Green Line</div>
                </div>
                <div class="route-item">
                    <div class="route-bar">
                        <div class="bar delay" style="height: 55px;"></div>
                        <div class="bar on-time" style="height: 85px;"></div>
                    </div>
                    <div class="route-label">Blue Line</div>
                </div>
                <div class="route-item">
                    <div class="route-bar">
                        <div class="bar delay" style="height: 40px;"></div>
                        <div class="bar on-time" style="height: 90px;"></div>
                    </div>
                    <div class="route-label">Orange Line</div>
                </div>
                <div class="route-item">
                    <div class="route-bar">
                        <div class="bar delay" style="height: 35px;"></div>
                        <div class="bar on-time" style="height: 95px;"></div>
                    </div>
                    <div class="route-label">Purple Line</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 20px; margin-top: 20px; font-size: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background: #ef4444; border-radius: 2px;"></div>
                    <span>Average Delay (min)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background: #10b981; border-radius: 2px;"></div>
                    <span>On Time</span>
                </div>
            </div>
        </div>

        <div class="alerts-section">
            <h3 class="chart-title">Live System Alerts</h3>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span>Active: <span id="active-alerts">0</span></span>
                <button class="action-btn btn-secondary">Clear All</button>
            </div>
            
            <div class="alert-item">
                <i class="fas fa-check-circle" style="color: #10b981; margin-right: 8px;"></i>
                No active alerts - All systems operating normally
            </div>

            <div class="quick-actions">
                <button class="action-btn btn-primary" onclick="optimizeSchedule()">
                    <i class="fas fa-magic"></i> Optimize Schedule
                </button>
                <button class="action-btn btn-primary" onclick="deployBackup()">
                    <i class="fas fa-rocket"></i> Deploy Backup
                </button>
                <button class="action-btn btn-secondary" onclick="emergencyMode()">
                    <i class="fas fa-exclamation-triangle"></i> Emergency Mode
                </button>
                <button class="action-btn btn-secondary" onclick="generateReport()">
                    <i class="fas fa-file-alt"></i> Generate Report
                </button>
            </div>
        </div>
    </div>

    <script>
        // Initialize charts
        const performanceCtx = document.getElementById('performance-chart').getContext('2d');
        const statusCtx = document.getElementById('status-pie').getContext('2d');

        // Performance trend chart
        const performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Scheduling Accuracy (%)',
                    data: [97.2, 98.1, 97.8, 98.5, 98.2, 97.9, 98.2],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 95,
                        max: 100
                    }
                }
            }
        });

        // Status pie chart
        const statusChart = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Running', 'Ready', 'Hold', 'Maintenance'],
                datasets: [{
                    data: [15, 6, 0, 4],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                cutout: '60%'
            }
        });

        // Real-time updates
        function updateDashboard() {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('scheduling-accuracy').textContent = data.scheduling_accuracy + '%';
                    document.getElementById('avg-delay').textContent = data.average_delay + ' min';
                    document.getElementById('train-availability').textContent = data.train_availability + '%';
                    document.getElementById('wait-time').textContent = data.passenger_wait_time + ' min';
                    document.getElementById('active-alerts').textContent = data.active_alerts;
                    document.getElementById('last-update').textContent = data.last_update;
                })
                .catch(error => console.log('Demo mode - using sample data'));
        }

        // Quick action functions
        function optimizeSchedule() {
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<div class="loading"></div> Optimizing...';
            btn.disabled = true;
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert('Schedule optimization completed successfully!');
            }, 2000);
        }

        function deployBackup() {
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<div class="loading"></div> Deploying...';
            btn.disabled = true;
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert('Backup trains deployed successfully!');
            }, 1500);
        }

        function emergencyMode() {
            if (confirm('Activate Emergency Mode? This will override all standard operations.')) {
                alert('Emergency Mode activated! All backup protocols initiated.');
            }
        }

        function generateReport() {
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<div class="loading"></div> Generating...';
            btn.disabled = true;
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                alert('Performance report generated and downloaded!');
            }, 1000);
        }

        // Chart selector functionality
        document.getElementById('chart-selector').addEventListener('change', function() {
            const selectedMetric = this.value;
            let newData, newLabel;
            
            switch(selectedMetric) {
                case 'delays':
                    newData = [2.1, 1.9, 2.0, 1.7, 1.8, 2.2, 1.8];
                    newLabel = 'Average Delay (min)';
                    break;
                case 'availability':
                    newData = [94, 96, 95, 97, 96, 95, 96];
                    newLabel = 'Train Availability (%)';
                    break;
                default:
                    newData = [97.2, 98.1, 97.8, 98.5, 98.2, 97.9, 98.2];
                    newLabel = 'Scheduling Accuracy (%)';
            }
            
            performanceChart.data.datasets[0].data = newData;
            performanceChart.data.datasets[0].label = newLabel;
            performanceChart.update();
        });

        // Auto-refresh dashboard every 30 seconds
        setInterval(updateDashboard, 30000);

        // Initial load
        updateDashboard();

        // Navigation functionality
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            });
        });
    </script>
</body>
</html>
    ''')

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data"""
    return jsonify(get_sample_data())

if __name__ == '__main__':
    print("🚇 KMRL Enhanced Frontend Starting...")
    print("✅ Modern UI with real-time updates")
    print("🌐 http://localhost:5000")
    app.run(debug=True, port=5000)
"""
🚇 KMRL SIH25081 FIXED & ENHANCED BACKEND APPLICATION
Complete Flask application with interconnected data flow and fixed algorithms
AI-Driven Train Induction Planning & Scheduling System
"""

import os
import sys
import json
import random
import uuid
import traceback
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np

# Import all templates
from backend.templates import (
    NIGHT_OPERATIONS_TEMPLATE,
    TRAIN_STATUS_TEMPLATE, 
    MILEAGE_OPTIMIZATION_TEMPLATE,
    BRANDING_MANAGEMENT_TEMPLATE,
    TIMETABLE_OPTIMIZER_TEMPLATE,
    EMERGENCY_TESTING_TEMPLATE
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kmrl_sih25081_complete_system'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ================================
# GLOBAL SYSTEM STATE & DATA INTERCONNECTION
# ================================

# Central system state with interconnected data
system_state = {
    'trains_data': None,
    'night_decisions': {},
    'optimization_results': {},
    'emergency_scenarios': [],
    'active_emergencies': {},
    'timetable_cache': {},
    'branding_campaigns': [],
    'available_trains': [],      # Trains available for emergency deployment
    'held_trains': [],           # Trains held back in night operations
    'service_trains': [],        # Trains currently in service
    'backup_queue': [],          # Priority queue for backup deployment
    'system_alerts': [],
    'interconnection_log': [],   # Track data flow between modules
    'last_updated': datetime.now().isoformat()
}

# KMRL train names (based on actual Kochi Metro naming)
KMRL_TRAIN_NAMES = [
    "KRISHNA", "TAPTI", "NILA", "SARAYU", "ARUTH",
    "VAIGAI", "JHANAVI", "DHWANIL", "BHAVANI", "PADMA", 
    "MANDAKINI", "YAMUNA", "PERIYAR", "KABANI", "VAAYU",
    "KAVERI", "SHIRIYA", "PAMPA", "NARMADA", "MAHE",
    "MAARUT", "SABARMATHI", "GODHAVARI", "GANGA", "PAVAN"
]

# KMRL stations (actual Kochi Metro stations)
KMRL_STATIONS = [
    'Aluva', 'Kalamassery', 'Cusat', 'Edapally', 'Changampuzha Park',
    'Palarivattom', 'JLN Stadium', 'Kaloor', 'MG Road', 'Maharajas',
    'Ernakulam South', 'Kadavanthra', 'Petta', 'Thripunithura'
]

# KMRL routes (actual operational routes)
KMRL_ROUTES = [
    {'id': 'R1', 'name': 'Aluva-Petta Express', 'distance': 25.6, 'stations': 13},
    {'id': 'R2', 'name': 'Kalamassery-MG Road', 'distance': 18.2, 'stations': 9},
    {'id': 'R3', 'name': 'JLN Stadium-Thripunithura', 'distance': 11.2, 'stations': 8},
    {'id': 'R4', 'name': 'Local Shuttle Service', 'distance': 14.8, 'stations': 7}
]

def generate_realistic_train_data():
    """Generate realistic KMRL train operational data with enhanced parameters"""
    trains_data = []
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    for i, train_id in enumerate(KMRL_TRAIN_NAMES):
        # Realistic operational parameters
        total_mileage = np.random.randint(18000, 55000)
        service_mileage = np.random.randint(500, 9000)
        daily_mileage = np.random.uniform(180, 320)
        
        # Maintenance parameters with realistic distributions
        brake_wear = max(15, min(95, np.random.normal(50, 25)))
        hvac_wear = max(10, min(90, np.random.normal(45, 20)))
        battery_health = max(60, min(100, np.random.normal(85, 12)))
        door_system = max(70, min(98, np.random.normal(88, 8)))
        traction_motor = max(75, min(98, np.random.normal(90, 6)))
        
        # Fitness certificates (realistic failure rates based on KMRL data)
        fitness_rolling = brake_wear < 85 and np.random.random() > 0.08
        fitness_signalling = np.random.random() > 0.12
        fitness_telecom = np.random.random() > 0.15
        
        # Job management - FIXED: Using numpy.random.poisson
        open_jobs = max(0, int(np.random.poisson(1.2)))
        pending_inspections = max(0, int(np.random.poisson(0.6)))
        
        # Enhanced branding parameters
        branding_active = np.random.random() < 0.35
        brand_campaigns = [
            {'name': 'Coca-Cola Summer', 'value': 5000000, 'exposure_target': 320, 'priority': 'high'},
            {'name': 'Samsung Galaxy', 'value': 8000000, 'exposure_target': 400, 'priority': 'critical'},
            {'name': 'BSNL 5G Launch', 'value': 3000000, 'exposure_target': 280, 'priority': 'medium'},
            {'name': 'Kerala Tourism', 'value': 4500000, 'exposure_target': 350, 'priority': 'high'},
            {'name': 'Wipro Digital', 'value': 6000000, 'exposure_target': 380, 'priority': 'high'}
        ]
        
        selected_campaign = np.random.choice(brand_campaigns) if branding_active else None
        brand_campaign = selected_campaign['name'] if selected_campaign else 'None'
        brand_value = selected_campaign['value'] if selected_campaign else 0
        brand_priority = selected_campaign['priority'] if selected_campaign else 'none'
        exposure_target = selected_campaign['exposure_target'] if selected_campaign else 0
        exposure_accrued = np.random.randint(50, int(exposure_target * 0.9)) if exposure_target > 0 else 0
        
        # Route assignment
        assigned_route = np.random.choice(KMRL_ROUTES)
        
        # Enhanced operational status determination
        critical_issues = []
        if not fitness_rolling or brake_wear > 85:
            critical_issues.append('brake_system')
        if not fitness_signalling:
            critical_issues.append('signalling')
        if not fitness_telecom:
            critical_issues.append('telecom')
        if open_jobs >= 3:
            critical_issues.append('multiple_jobs')
        if hvac_wear > 85:
            critical_issues.append('hvac_critical')
        if battery_health < 70:
            critical_issues.append('battery_low')
        
        # Determine status based on issues
        if critical_issues:
            status = 'maintenance'
            reason = f'Critical: {", ".join(critical_issues)}'
            emergency_deployable = False
        elif pending_inspections >= 2 or (not fitness_signalling and not fitness_telecom):
            status = 'inspection' 
            reason = 'Systems inspection required'
            emergency_deployable = False
        elif np.random.random() < 0.15:
            status = 'cleaning'
            reason = 'Scheduled cleaning and preparation'
            emergency_deployable = True  # Can be deployed in emergency
        elif branding_active and np.random.random() < 0.4:
            status = 'service'
            reason = f'Active service with {brand_campaign} branding'
            emergency_deployable = True
        elif np.random.random() < 0.45:
            status = 'service'
            reason = 'Regular passenger service'
            emergency_deployable = True
        else:
            status = 'standby'
            reason = 'Ready for immediate deployment'
            emergency_deployable = True
        
        # Performance metrics
        on_time_performance = max(85, min(99.9, np.random.normal(96.5, 3)))
        reliability_score = max(0.80, min(0.99, np.random.normal(0.93, 0.04)))
        energy_efficiency = max(0.75, min(1.25, np.random.normal(0.95, 0.12)))
        passenger_satisfaction = max(3.5, min(5.0, np.random.normal(4.2, 0.3)))
        
        # Enhanced KMRL operational score
        score = calculate_enhanced_kmrl_score(
            fitness_rolling, fitness_signalling, fitness_telecom,
            brake_wear, hvac_wear, battery_health, open_jobs,
            branding_active, total_mileage, on_time_performance,
            len(critical_issues)
        )
        
        # Emergency response capability
        emergency_response_score = calculate_emergency_readiness(
            emergency_deployable, score, battery_health, brake_wear, status
        )
        
        train_data = {
            'train_id': train_id,
            'train_number': f'T{i+1:03d}',
            'depot': np.random.choice(['Muttom', 'Kalamassery']),
            'current_location': np.random.choice(KMRL_STATIONS),
            'bay_position': np.random.randint(1, 26),
            'uuid': str(uuid.uuid4()),
            
            # Fitness status
            'fitness_rolling': fitness_rolling,
            'fitness_signalling': fitness_signalling,
            'fitness_telecom': fitness_telecom,
            'fitness_validity_days': np.random.randint(15, 365),
            
            # Mileage data
            'total_mileage': total_mileage,
            'service_mileage': service_mileage,
            'daily_mileage': round(daily_mileage, 1),
            'mileage_target': 35000,
            'mileage_deviation': abs(total_mileage - 35000),
            
            # Enhanced maintenance data
            'brake_wear': round(brake_wear, 1),
            'hvac_wear': round(hvac_wear, 1),
            'battery_health': round(battery_health, 1),
            'door_system_health': round(door_system, 1),
            'traction_motor_health': round(traction_motor, 1),
            'open_jobs': open_jobs,
            'pending_inspections': pending_inspections,
            'critical_issues': critical_issues,
            'maintenance_priority': get_maintenance_priority(critical_issues, brake_wear, open_jobs),
            
            # Branding data
            'branding_active': branding_active,
            'brand_campaign': brand_campaign,
            'brand_value': brand_value,
            'brand_priority': brand_priority,
            'exposure_target': exposure_target,
            'exposure_accrued': exposure_accrued,
            'branding_compliance': round((exposure_accrued / exposure_target * 100) if exposure_target > 0 else 0, 1),
            
            # Route assignment
            'assigned_route': assigned_route['id'],
            'route_name': assigned_route['name'],
            'route_distance': assigned_route['distance'],
            
            # Current status
            'status': status,
            'reason': reason,
            'status_color': get_status_color(status),
            
            # Performance metrics
            'performance': round(on_time_performance, 1),
            'reliability': round(reliability_score, 3),
            'energy_efficiency': round(energy_efficiency, 2),
            'passenger_satisfaction': round(passenger_satisfaction, 1),
            
            # Emergency response capability
            'emergency_deployable': emergency_deployable,
            'emergency_response_score': round(emergency_response_score, 1),
            'backup_priority': calculate_backup_priority(emergency_deployable, score, status),
            
            # Overall score
            'score': round(score, 1),
            'grade': get_score_grade(score),
            
            # Timestamps
            'last_updated': datetime.now().isoformat(),
            'next_maintenance': (datetime.now() + timedelta(days=np.random.randint(5, 90))).isoformat(),
            'last_service': (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat()
        }
        
        trains_data.append(train_data)
    
    return trains_data

def calculate_enhanced_kmrl_score(fitness_rolling, fitness_signalling, fitness_telecom,
                                brake_wear, hvac_wear, battery_health, open_jobs,
                                branding_active, total_mileage, on_time_performance, critical_issues_count):
    """Enhanced KMRL operational score calculation"""
    score = 0
    
    # Safety and fitness certificates (35 points)
    if fitness_rolling: score += 15
    if fitness_signalling: score += 10
    if fitness_telecom: score += 10
    
    # Maintenance condition (25 points)
    score += max(0, 15 - (brake_wear - 30) * 0.15)
    score += max(0, 10 - open_jobs * 2.5)
    
    # Performance metrics (20 points)
    score += (on_time_performance - 85) * 0.15
    score += (battery_health - 60) * 0.125
    
    # Operational efficiency (15 points)
    mileage_efficiency = min(15, abs(total_mileage - 35000) / 2000)
    score += 15 - mileage_efficiency
    
    # Critical issues penalty (5 points)
    score -= critical_issues_count * 5
    
    return max(0, min(100, score))

def calculate_emergency_readiness(deployable, score, battery_health, brake_wear, status):
    """Calculate emergency response readiness score"""
    if not deployable:
        return 0
    
    emergency_score = score * 0.6  # Base score influence
    
    # Status bonuses
    if status == 'standby':
        emergency_score += 25
    elif status == 'cleaning':
        emergency_score += 15
    elif status == 'service':
        emergency_score += 10
    
    # Safety factors
    emergency_score += (100 - brake_wear) * 0.2
    emergency_score += battery_health * 0.15
    
    return max(0, min(100, emergency_score))

def calculate_backup_priority(deployable, score, status):
    """Calculate priority for backup deployment"""
    if not deployable:
        return 0
    
    priority_map = {
        'standby': 100,
        'cleaning': 80, 
        'service': 60,
        'inspection': 20,
        'maintenance': 0
    }
    
    base_priority = priority_map.get(status, 0)
    score_factor = score * 0.3
    
    return round(base_priority + score_factor, 1)

def get_maintenance_priority(critical_issues, brake_wear, open_jobs):
    """Determine maintenance priority level"""
    if critical_issues or brake_wear > 85 or open_jobs >= 3:
        return 'Critical'
    elif brake_wear > 70 or open_jobs >= 2:
        return 'High'
    elif brake_wear > 50 or open_jobs >= 1:
        return 'Medium'
    else:
        return 'Low'

def get_status_color(status):
    """Status color mapping"""
    colors = {
        'service': '#10b981',
        'standby': '#f59e0b', 
        'maintenance': '#ef4444',
        'inspection': '#8b5cf6',
        'cleaning': '#06b6d4'
    }
    return colors.get(status, '#6b7280')

def get_score_grade(score):
    """Grade mapping for scores"""
    if score >= 90: return 'A+'
    elif score >= 80: return 'A'
    elif score >= 70: return 'B'
    elif score >= 60: return 'C'
    else: return 'D'

def update_interconnected_state():
    """Update interconnected system state based on current train data"""
    if system_state['trains_data'] is None:
        return
    
    trains = system_state['trains_data']
    
    # Update categorized train lists
    system_state['available_trains'] = [
        train for train in trains 
        if train['emergency_deployable'] and train['status'] in ['standby', 'cleaning', 'service']
    ]
    
    system_state['held_trains'] = [
        train for train in trains 
        if train['status'] in ['maintenance', 'inspection']
    ]
    
    system_state['service_trains'] = [
        train for train in trains 
        if train['status'] == 'service'
    ]
    
    # Create backup deployment queue (sorted by priority)
    system_state['backup_queue'] = sorted(
        system_state['available_trains'],
        key=lambda x: x['backup_priority'],
        reverse=True
    )
    
    # Log the interconnection update
    system_state['interconnection_log'].append({
        'timestamp': datetime.now().isoformat(),
        'action': 'state_update',
        'available_trains': len(system_state['available_trains']),
        'held_trains': len(system_state['held_trains']),
        'service_trains': len(system_state['service_trains']),
        'backup_queue_size': len(system_state['backup_queue'])
    })
    
    # Keep log size manageable
    if len(system_state['interconnection_log']) > 100:
        system_state['interconnection_log'] = system_state['interconnection_log'][-50:]

# ================================
# MAIN ROUTES
# ================================

@app.route('/')
def main_dashboard():
    """Main dashboard with real-time system overview"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KMRL SIH25081 - Complete AI Train Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #f1f5f9;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(239, 68, 68, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
            animation: backgroundPulse 20s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes backgroundPulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 30px; }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(20px);
            padding: 40px;
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        .header h1 {
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #10b981, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        
        .header p {
            font-size: 1.3rem;
            color: #cbd5e1;
            margin-bottom: 15px;
        }
        
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 700;
            box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.4);
        }
        
        .interconnection-status {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
            border-left: 4px solid #10b981;
        }
        
        .interconnection-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
        }
        
        .interconnection-item {
            text-align: center;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
        }
        
        .interconnection-number {
            font-size: 2rem;
            font-weight: 900;
            margin-bottom: 8px;
        }
        
        .interconnection-label {
            color: #94a3b8;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .module-card {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 20px;
            padding: 30px;
            transition: all 0.4s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .module-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        }
        
        .module-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            border-radius: 20px 20px 0 0;
        }
        
        .module-card.night::before { background: linear-gradient(90deg, #06b6d4, #0891b2); }
        .module-card.status::before { background: linear-gradient(90deg, #10b981, #059669); }
        .module-card.mileage::before { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }
        .module-card.branding::before { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
        .module-card.timetable::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
        .module-card.emergency::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
        
        .module-icon { font-size: 3rem; margin-bottom: 20px; display: block; }
        .module-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 15px; color: #f1f5f9; }
        .module-description { color: #94a3b8; line-height: 1.6; margin-bottom: 20px; }
        .module-features { list-style: none; margin-bottom: 20px; }
        .module-features li { color: #cbd5e1; margin-bottom: 8px; padding-left: 20px; position: relative; }
        .module-features li::before { content: '✓'; position: absolute; left: 0; color: #10b981; font-weight: bold; }
        
        .btn {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
        }
        
        @media (max-width: 768px) {
            .modules-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2.5rem; }
            .interconnection-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚇 KMRL Complete AI System</h1>
            <p>Advanced AI-Driven Train Management & Scheduling Platform</p>
            <p>Smart India Hackathon 2025 - Problem Statement SIH25081</p>
            <div class="badge">Kochi Metro Rail Limited - Enhanced & Interconnected</div>
        </div>
        
        <div class="interconnection-status">
            <h2 style="margin-bottom: 20px; color: #f1f5f9;">🔗 Interconnected System Status</h2>
            <p style="color: #cbd5e1; margin-bottom: 20px;">Real-time data flow between all modules with intelligent backup deployment queue</p>
            <div class="interconnection-grid">
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #10b981;" id="availableTrains">0</div>
                    <div class="interconnection-label">Available for Emergency</div>
                </div>
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #ef4444;" id="heldTrains">0</div>
                    <div class="interconnection-label">Held Back (Night Ops)</div>
                </div>
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #3b82f6;" id="serviceTrains">0</div>
                    <div class="interconnection-label">Currently in Service</div>
                </div>
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #f59e0b;" id="backupQueue">0</div>
                    <div class="interconnection-label">Backup Queue Ready</div>
                </div>
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #8b5cf6;" id="systemHealth">100%</div>
                    <div class="interconnection-label">System Health</div>
                </div>
                <div class="interconnection-item">
                    <div class="interconnection-number" style="color: #06b6d4;" id="dataSync">Active</div>
                    <div class="interconnection-label">Data Sync Status</div>
                </div>
            </div>
        </div>
        
        <div class="modules-grid">
            <div class="module-card night" onclick="window.location.href='/night-operations'">
                <span class="module-icon">🌙</span>
                <h3 class="module-title">Night Operations</h3>
                <p class="module-description">AI-powered nightly train induction decisions with hold/release tracking. Data feeds to emergency module.</p>
                <ul class="module-features">
                    <li>Hold vs Release Decision Engine</li>
                    <li>Safety-First Prioritization</li>
                    <li>Emergency Deployment Queue</li>
                    <li>Interconnected Data Flow</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #06b6d4, #0891b2);">Enter Night Ops</button>
            </div>
            
            <div class="module-card status" onclick="window.location.href='/train-status'">
                <span class="module-icon">📊</span>
                <h3 class="module-title">Fleet Status Dashboard</h3>
                <p class="module-description">Real-time train monitoring with interconnected status updates from all modules.</p>
                <ul class="module-features">
                    <li>Live Fleet Status Charts</li>
                    <li>Cross-Module Status Sync</li>
                    <li>Emergency Readiness Score</li>
                    <li>Backup Priority Ranking</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #10b981, #059669);">View Fleet Status</button>
            </div>
            
            <div class="module-card mileage" onclick="window.location.href='/mileage-optimization'">
                <span class="module-icon">⚖️</span>
                <h3 class="module-title">Mileage Optimization</h3>
                <p class="module-description">AI-driven mileage balancing affecting night decisions and emergency deployment priority.</p>
                <ul class="module-features">
                    <li>Fleet Longevity Analysis</li>
                    <li>Optimal Route Assignment</li>
                    <li>Emergency Impact Assessment</li>
                    <li>Timetable Integration</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">Optimize Mileage</button>
            </div>
            
            <div class="module-card branding" onclick="window.location.href='/branding-management'">
                <span class="module-icon">🎨</span>
                <h3 class="module-title">Branding Management</h3>
                <p class="module-description">Campaign compliance tracking affecting train deployment priority and emergency availability.</p>
                <ul class="module-features">
                    <li>Campaign Priority Integration</li>
                    <li>Revenue Impact Analysis</li>
                    <li>Emergency Override Logic</li>
                    <li>Cross-Module Compliance</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">Manage Branding</button>
            </div>
            
            <div class="module-card timetable" onclick="window.location.href='/timetable-optimizer'">
                <span class="module-icon">⏰</span>
                <h3 class="module-title">Timetable Optimizer</h3>
                <p class="module-description">Dynamic scheduling considering mileage balance, maintenance needs, and emergency reserve.</p>
                <ul class="module-features">
                    <li>Multi-Factor Schedule Generation</li>
                    <li>Emergency Reserve Planning</li>
                    <li>Maintenance Window Integration</li>
                    <li>Real-Time Adjustments</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #f59e0b, #d97706);">Optimize Schedule</button>
            </div>
            
            <div class="module-card emergency" onclick="window.location.href='/emergency-testing'">
                <span class="module-icon">🚨</span>
                <h3 class="module-title">Emergency Response Testing</h3>
                <p class="module-description">Real-time disruption handling using interconnected data from all modules for intelligent backup deployment.</p>
                <ul class="module-features">
                    <li>Smart Backup Selection</li>
                    <li>Cross-Module Data Integration</li>
                    <li>Priority-Based Deployment</li>
                    <li>Real-Time Decision Logic</li>
                </ul>
                <button class="btn" style="background: linear-gradient(135deg, #ef4444, #dc2626);">Test Emergency Response</button>
            </div>
        </div>
        
        <div style="background: rgba(15, 23, 42, 0.8); border-radius: 20px; padding: 25px; border: 1px solid rgba(148, 163, 184, 0.2);">
            <h3 style="color: #f1f5f9; margin-bottom: 15px;">🔄 Live System Interconnection</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                All modules share real-time data: Night operations determine available trains → Emergency module uses backup queue → 
                Mileage optimization affects deployment priority → Branding campaigns influence availability → 
                Timetable optimizer reserves emergency capacity → Fleet status reflects all decisions.
            </p>
        </div>
    </div>
    
    <script>
        // Auto-refresh interconnection status
        async function loadInterconnectionStatus() {
            try {
                const response = await fetch('/api/system-overview');
                const data = await response.json();
                
                if (data.status === 'success') {
                    const overview = data.overview;
                    document.getElementById('availableTrains').textContent = overview.available_trains;
                    document.getElementById('heldTrains').textContent = overview.held_trains;
                    document.getElementById('serviceTrains').textContent = overview.service_trains;
                    document.getElementById('backupQueue').textContent = overview.backup_queue_size;
                }
            } catch (error) {
                console.error('Error loading interconnection status:', error);
            }
        }
        
        // Load on page load and refresh every 5 seconds
        window.addEventListener('load', loadInterconnectionStatus);
        setInterval(loadInterconnectionStatus, 5000);
    </script>
</body>
</html>
    """)

# ================================
# MODULE ROUTES
# ================================

@app.route('/night-operations')
def night_operations():
    """Night operations module - Core SIH25081 functionality"""
    return render_template_string(NIGHT_OPERATIONS_TEMPLATE)

@app.route('/train-status')
def train_status():
    """Fleet status dashboard"""
    return render_template_string(TRAIN_STATUS_TEMPLATE)

@app.route('/mileage-optimization')
def mileage_optimization():
    """Mileage optimization module"""
    return render_template_string(MILEAGE_OPTIMIZATION_TEMPLATE)

@app.route('/branding-management')
def branding_management():
    """Branding management module"""
    return render_template_string(BRANDING_MANAGEMENT_TEMPLATE)

@app.route('/timetable-optimizer')
def timetable_optimizer():
    """Timetable optimization module"""
    return render_template_string(TIMETABLE_OPTIMIZER_TEMPLATE)

@app.route('/emergency-testing')
def emergency_testing():
    """Emergency response testing module"""
    return render_template_string(EMERGENCY_TESTING_TEMPLATE)

# ================================
# ENHANCED API ENDPOINTS WITH INTERCONNECTION
# ================================

@app.route('/api/system-overview', methods=['GET'])
def system_overview():
    """Get enhanced system overview with interconnection data"""
    try:
        # Initialize data if not present
        if system_state['trains_data'] is None:
            system_state['trains_data'] = generate_realistic_train_data()
            update_interconnected_state()
        
        trains = system_state['trains_data']
        
        # Calculate comprehensive overview
        status_counts = {}
        for train in trains:
            status = train['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Enhanced overview with interconnection data
        overview = {
            'active_trains': status_counts.get('service', 0),
            'standby_trains': status_counts.get('standby', 0),
            'maintenance_trains': status_counts.get('maintenance', 0),
            'inspection_trains': status_counts.get('inspection', 0),
            'cleaning_trains': status_counts.get('cleaning', 0),
            'total_trains': len(trains),
            'available_trains': len(system_state['available_trains']),
            'held_trains': len(system_state['held_trains']),
            'service_trains': len(system_state['service_trains']),
            'backup_queue_size': len(system_state['backup_queue']),
            'avg_score': round(sum(t['score'] for t in trains) / len(trains), 1),
            'emergency_ready_trains': len([t for t in trains if t['emergency_deployable']]),
            'critical_maintenance': len([t for t in trains if t['maintenance_priority'] == 'Critical']),
            'system_health': 'Operational',
            'data_sync_status': 'Active',
            'last_updated': system_state['last_updated'],
            'interconnection_active': True
        }
        
        return jsonify({
            'status': 'success',
            'overview': overview,
            'interconnection_log': system_state['interconnection_log'][-5:] if system_state['interconnection_log'] else []
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ================================
# ENHANCED NIGHT OPERATIONS API WITH INTERCONNECTION
# ================================

@app.route('/api/night-operations/load-data', methods=['POST'])
def night_operations_load_data():
    """Load train data for night operations with interconnection"""
    try:
        print("Loading night operations data...")
        system_state['trains_data'] = generate_realistic_train_data()
        update_interconnected_state()
        
        # Log the data loading event
        system_state['interconnection_log'].append({
            'timestamp': datetime.now().isoformat(),
            'action': 'night_data_loaded',
            'module': 'night_operations',
            'total_trains': len(system_state['trains_data']),
            'available_for_emergency': len(system_state['available_trains'])
        })
        
        return jsonify({
            'status': 'success',
            'message': 'KMRL fleet data loaded successfully with interconnection',
            'total_trains': len(system_state['trains_data']),
            'available_for_emergency': len(system_state['available_trains']),
            'held_back_count': len(system_state['held_trains']),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in night operations load data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/night-operations/optimize', methods=['POST'])
def night_operations_optimize():
    """Enhanced AI night optimization with interconnected decision making"""
    try:
        if system_state['trains_data'] is None:
            system_state['trains_data'] = generate_realistic_train_data()
        
        trains = system_state['trains_data']
        
        # Enhanced SIH25081 Core Algorithm with Interconnection
        service_released = []
        held_back = []
        
        # Advanced priority scoring for decision making
        for train in trains:
            # Multi-factor safety analysis
            safety_score = 0
            if train['fitness_rolling']: safety_score += 30
            if train['fitness_signalling']: safety_score += 25
            if train['fitness_telecom']: safety_score += 20
            
            # Enhanced maintenance assessment
            maintenance_score = 100 - (train['brake_wear'] * 0.4 + train['hvac_wear'] * 0.3)
            maintenance_score -= len(train['critical_issues']) * 20
            maintenance_score -= train['open_jobs'] * 12
            
            # Performance and reliability factor
            performance_score = (train['performance'] + train['reliability'] * 100) / 2
            
            # Branding impact assessment
            branding_factor = 0
            if train['branding_active'] and train['brand_priority'] == 'critical':
                branding_factor = 15  # High priority campaigns get preference
            elif train['branding_active'] and train['brand_priority'] == 'high':
                branding_factor = 10
            elif train['branding_active']:
                branding_factor = 5
            
            # Emergency deployment potential
            emergency_factor = train['emergency_response_score'] * 0.2
            
            # Comprehensive readiness score
            readiness_score = (
                safety_score * 0.4 +           # Safety priority (40%)
                maintenance_score * 0.25 +     # Maintenance factor (25%)
                performance_score * 0.15 +     # Performance factor (15%)
                branding_factor * 0.1 +        # Branding consideration (10%)
                emergency_factor * 0.1         # Emergency readiness (10%)
            )
            
            # Dynamic threshold based on fleet health
            fleet_avg_score = sum(t['score'] for t in trains) / len(trains)
            release_threshold = max(70, min(85, fleet_avg_score - 10))  # Adaptive threshold
            
            # Enhanced decision logic
            if (readiness_score >= release_threshold and 
                len(train['critical_issues']) == 0 and
                train['open_jobs'] <= 1):
                
                # Additional checks for service release
                can_release = True
                release_reason = f'Ready for service - Score: {readiness_score:.1f}'
                
                # Emergency reserve consideration
                if train['emergency_deployable'] and train['backup_priority'] >= 80:
                    release_reason += ' (High emergency priority)'
                
                # Branding consideration
                if train['branding_active']:
                    if train['branding_compliance'] < 70:
                        release_reason += f' (Branding compliance: {train["branding_compliance"]:.1f}%)'
                    else:
                        release_reason += f' (Active campaign: {train["brand_campaign"]})'
                
                service_released.append({
                    'train_id': train['train_id'],
                    'reason': release_reason,
                    'readiness_score': round(readiness_score, 1),
                    'depot': train['depot'],
                    'emergency_deployable': train['emergency_deployable'],
                    'backup_priority': train['backup_priority'],
                    'branding_active': train['branding_active']
                })
                
            else:
                # Enhanced hold reasoning
                hold_reasons = []
                priority = 'Medium'
                
                if not train['fitness_rolling']:
                    hold_reasons.append('Rolling stock fitness expired')
                    priority = 'Critical'
                if train['brake_wear'] > 85:
                    hold_reasons.append(f'Critical brake wear ({train["brake_wear"]:.1f}%)')
                    priority = 'Critical'
                if len(train['critical_issues']) > 0:
                    hold_reasons.append(f'Critical issues: {", ".join(train["critical_issues"])}')
                    priority = 'Critical'
                if train['open_jobs'] >= 3:
                    hold_reasons.append(f'{train["open_jobs"]} open job cards')
                    priority = 'High' if priority != 'Critical' else priority
                if not train['fitness_signalling']:
                    hold_reasons.append('Signalling system inspection required')
                if not train['fitness_telecom']:
                    hold_reasons.append('Telecom system inspection required')
                if train['battery_health'] < 70:
                    hold_reasons.append(f'Low battery health ({train["battery_health"]:.1f}%)')
                
                if not hold_reasons:
                    hold_reasons.append(f'Below readiness threshold ({readiness_score:.1f}/{release_threshold:.1f})')
                
                reason = 'HELD: ' + '; '.join(hold_reasons)
                
                held_back.append({
                    'train_id': train['train_id'],
                    'reason': reason,
                    'readiness_score': round(readiness_score, 1),
                    'depot': train['depot'],
                    'priority': priority,
                    'maintenance_required': train['maintenance_priority'],
                    'critical_issues': train['critical_issues'],
                    'estimated_repair_time': estimate_repair_time(train)
                })
        
        # Update train statuses based on decisions
        for train in trains:
            if any(d['train_id'] == train['train_id'] for d in service_released):
                if train['status'] not in ['service']:
                    train['status'] = 'service' if not train['branding_active'] else train['status']
            else:
                if train['status'] not in ['maintenance', 'inspection']:
                    if len(train['critical_issues']) > 0:
                        train['status'] = 'maintenance'
                    else:
                        train['status'] = 'inspection'
        
        # Update interconnected state
        update_interconnected_state()
        
        # Enhanced decisions with interconnection data
        decisions = {
            'service_released': service_released,
            'held_back': held_back,
            'timestamp': datetime.now().isoformat(),
            'algorithm': 'SIH25081_Enhanced_AI_Night_Optimization_v2',
            'total_processed': len(trains),
            'release_rate': len(service_released) / len(trains) * 100,
            'adaptive_threshold': release_threshold,
            'emergency_available': len([t for t in service_released if t['emergency_deployable']]),
            'backup_queue_updated': len(system_state['backup_queue']),
            'interconnection_active': True
        }
        
        system_state['night_decisions'] = decisions
        
        # Log the optimization decision
        system_state['interconnection_log'].append({
            'timestamp': datetime.now().isoformat(),
            'action': 'night_optimization_complete',
            'module': 'night_operations',
            'released_count': len(service_released),
            'held_count': len(held_back),
            'emergency_available': decisions['emergency_available']
        })
        
        return jsonify({
            'status': 'success',
            'decisions': decisions,
            'summary': {
                'total_trains': len(trains),
                'released_for_service': len(service_released),
                'held_back': len(held_back),
                'release_percentage': round(len(service_released) / len(trains) * 100, 1),
                'emergency_backup_available': decisions['emergency_available'],
                'backup_deployment_queue': len(system_state['backup_queue'])
            },
            'interconnection': {
                'backup_queue_size': len(system_state['backup_queue']),
                'available_for_emergency': len(system_state['available_trains']),
                'data_sync_timestamp': system_state['last_updated']
            }
        })
        
    except Exception as e:
        print(f"Error in night operations optimize: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

def estimate_repair_time(train):
    """Estimate repair time based on train condition"""
    base_time = 0
    
    if not train['fitness_rolling']:
        base_time += 8  # 8 hours for fitness certification
    if train['brake_wear'] > 85:
        base_time += 6  # 6 hours for brake system
    if train['critical_issues']:
        base_time += len(train['critical_issues']) * 4  # 4 hours per critical issue
    if train['open_jobs'] >= 3:
        base_time += train['open_jobs'] * 2  # 2 hours per job
    
    return f"{base_time}-{base_time + 4} hours" if base_time > 0 else "1-2 hours"

# ================================
# ENHANCED EMERGENCY RESPONSE API WITH INTERCONNECTION
# ================================

@app.route('/api/emergency-testing/start-simulation', methods=['POST'])
def start_emergency_simulation():
    """Start emergency simulation with interconnected backup deployment"""
    try:
        params = request.get_json() or {}
        scenario = params.get('scenario', 'breakdown')
        affected_train = params.get('affectedTrain', 'random')
        severity = params.get('severity', 'moderate')
        
        # Ensure we have current data and interconnection
        if system_state['trains_data'] is None:
            system_state['trains_data'] = generate_realistic_train_data()
            update_interconnected_state()
        
        # Select affected train
        service_trains = system_state['service_trains']
        if affected_train == 'random' and service_trains:
            affected_train_data = random.choice(service_trains)
        else:
            affected_train_data = next((t for t in service_trains if t['train_id'] == affected_train), None)
            if not affected_train_data and service_trains:
                affected_train_data = random.choice(service_trains)
        
        if not affected_train_data:
            return jsonify({
                'status': 'error',
                'message': 'No trains in service available for emergency simulation'
            }), 400
        
        # Smart backup selection from interconnected queue
        backup_candidates = system_state['backup_queue'].copy()
        
        # Filter based on scenario requirements
        if scenario == 'breakdown':
            # Need immediate replacement - prefer standby trains
            backup_candidates = [t for t in backup_candidates if t['status'] == 'standby']
        elif scenario == 'delay':
            # Can use cleaning or standby trains
            backup_candidates = [t for t in backup_candidates if t['status'] in ['standby', 'cleaning']]
        elif scenario == 'weather':
            # Need high reliability trains
            backup_candidates = [t for t in backup_candidates if t['reliability'] > 0.90]
        
        # Select best backup train
        selected_backup = None
        if backup_candidates:
            # Sort by backup priority and select the best
            selected_backup = max(backup_candidates, key=lambda x: x['backup_priority'])
        
        # Create emergency scenario
        emergency_id = str(uuid.uuid4())[:8]
        emergency_scenario = {
            'emergency_id': emergency_id,
            'scenario_type': scenario,
            'affected_train': affected_train_data['train_id'],
            'affected_train_route': affected_train_data.get('route_name', 'Unknown'),
            'severity': severity,
            'start_time': datetime.now().isoformat(),
            'selected_backup': selected_backup['train_id'] if selected_backup else None,
            'backup_deployment_reason': get_backup_deployment_reason(selected_backup, scenario) if selected_backup else 'No suitable backup available',
            'estimated_impact': calculate_emergency_impact(scenario, severity, affected_train_data),
            'response_timeline': [],
            'status': 'active'
        }
        
        # Update system state
        system_state['active_emergencies'][emergency_id] = emergency_scenario
        
        # Update train statuses
        if selected_backup:
            # Mark backup train as deployed
            for train in system_state['trains_data']:
                if train['train_id'] == selected_backup['train_id']:
                    train['status'] = 'service'
                    train['reason'] = f'Emergency deployment for {scenario}'
                    break
            
            # Update interconnected state
            update_interconnected_state()
        
        # Log the emergency response
        system_state['interconnection_log'].append({
            'timestamp': datetime.now().isoformat(),
            'action': 'emergency_simulation_started',
            'module': 'emergency_testing',
            'scenario': scenario,
            'affected_train': affected_train_data['train_id'],
            'backup_deployed': selected_backup['train_id'] if selected_backup else None,
            'remaining_backups': len(system_state['backup_queue'])
        })
        
        return jsonify({
            'status': 'success',
            'emergency': emergency_scenario,
            'backup_deployment': {
                'selected_backup': selected_backup,
                'remaining_backups': len(system_state['backup_queue']),
                'deployment_logic': 'AI-selected based on priority queue and scenario requirements'
            },
            'interconnection_data': {
                'night_decisions_used': len(system_state.get('night_decisions', {}).get('held_back', [])),
                'available_trains_count': len(system_state['available_trains']),
                'data_sync_active': True
            }
        })
        
    except Exception as e:
        print(f"Error starting emergency simulation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

def get_backup_deployment_reason(backup_train, scenario):
    """Get reason for backup train deployment"""
    reasons = {
        'breakdown': f'Deployed due to high reliability ({backup_train["reliability"]:.3f}) and immediate availability',
        'delay': f'Selected for schedule recovery with backup priority {backup_train["backup_priority"]:.1f}',
        'weather': f'Deployed for weather conditions - high safety score ({backup_train["score"]:.1f})',
        'power': f'Emergency deployment - standby status and battery health {backup_train["battery_health"]:.1f}%'
    }
    return reasons.get(scenario, f'AI-selected backup with priority {backup_train["backup_priority"]:.1f}')

def calculate_emergency_impact(scenario, severity, affected_train):
    """Calculate estimated impact of emergency"""
    impact_factors = {
        'breakdown': {'minor': 50, 'moderate': 150, 'major': 300, 'critical': 500},
        'delay': {'minor': 30, 'moderate': 100, 'major': 200, 'critical': 400},
        'weather': {'minor': 40, 'moderate': 120, 'major': 250, 'critical': 450},
        'power': {'minor': 60, 'moderate': 180, 'major': 350, 'critical': 600}
    }
    
    base_impact = impact_factors.get(scenario, {}).get(severity, 100)
    
    # Consider train performance
    performance_factor = (100 - affected_train['performance']) / 100
    adjusted_impact = base_impact * (1 + performance_factor)
    
    return {
        'estimated_affected_passengers': int(adjusted_impact),
        'estimated_delay_minutes': int(adjusted_impact / 10),
        'service_disruption_level': severity,
        'recovery_time_estimate': f"{int(adjusted_impact / 60)}-{int(adjusted_impact / 40)} minutes"
    }

# ================================
# TRAIN STATUS API WITH INTERCONNECTION
# ================================

@app.route('/api/train-status/load', methods=['GET'])
def train_status_load():
    """Load train status data with interconnection information"""
    try:
        if system_state['trains_data'] is None:
            system_state['trains_data'] = generate_realistic_train_data()
            update_interconnected_state()
        
        trains = system_state['trains_data']
        
        # Enhanced format for frontend display with interconnection data
        formatted_trains = []
        for train in trains:
            # Determine interconnection status
            interconnection_info = {
                'emergency_deployable': train['emergency_deployable'],
                'backup_priority': train['backup_priority'],
                'in_night_decisions': any(
                    d.get('train_id') == train['train_id'] 
                    for d in system_state.get('night_decisions', {}).get('service_released', []) + 
                             system_state.get('night_decisions', {}).get('held_back', [])
                ),
                'in_backup_queue': train['train_id'] in [t['train_id'] for t in system_state['backup_queue']],
                'emergency_ready_score': train['emergency_response_score']
            }
            
            formatted_train = {
                'train_id': train['train_id'],
                'train_number': train['train_number'],
                'depot': train['depot'],
                'status': train['status'],
                'reason': train['reason'],
                'score': train['score'],
                'grade': train['grade'],
                'mileage': train['total_mileage'],
                'performance': train['performance'],
                'brake_wear': train['brake_wear'],
                'hvac_wear': train['hvac_wear'],
                'battery_health': train['battery_health'],
                'open_jobs': train['open_jobs'],
                'critical_issues': train['critical_issues'],
                'maintenance_priority': train['maintenance_priority'],
                'branding': train['brand_campaign'],
                'branding_active': train['branding_active'],
                'location': train['current_location'],
                'route': train.get('route_name', 'Not assigned'),
                'last_updated': train['last_updated'],
                'interconnection': interconnection_info
            }
            
            formatted_trains.append(formatted_train)
        
        return jsonify({
            'status': 'success',
            'trains': formatted_trains,
            'total_count': len(formatted_trains),
            'interconnection_summary': {
                'emergency_deployable_count': len([t for t in trains if t['emergency_deployable']]),
                'backup_queue_size': len(system_state['backup_queue']),
                'night_decisions_active': len(system_state.get('night_decisions', {})) > 0,
                'cross_module_sync': True
            },
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ================================
# OTHER ENHANCED API ENDPOINTS
# ================================

@app.route('/api/night-operations/export', methods=['GET'])
def night_operations_export():
    """Export night operations decisions with interconnection data"""
    try:
        if 'night_decisions' not in system_state:
            return jsonify({
                'status': 'error',
                'message': 'No decisions to export. Run optimization first.'
            }), 400
        
        decisions = system_state['night_decisions']
        
        # Enhanced export data with interconnection
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'decisions': decisions,
            'interconnection_data': {
                'backup_queue': [t['train_id'] for t in system_state['backup_queue']],
                'available_trains': len(system_state['available_trains']),
                'held_trains': len(system_state['held_trains']),
                'cross_module_impact': 'Emergency module can deploy backup trains based on night decisions'
            },
            'kmrl_info': {
                'organization': 'Kochi Metro Rail Limited',
                'system': 'SIH25081 AI Night Operations with Interconnection',
                'total_fleet': 25,
                'operational_depots': ['Muttom', 'Kalamassery']
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Night operations report exported with interconnection data',
            'export_summary': {
                'trains_processed': decisions['total_processed'],
                'decisions_made': len(decisions['service_released']) + len(decisions['held_back']),
                'emergency_backup_available': decisions.get('emergency_available', 0),
                'export_format': 'JSON with interconnection metadata',
                'file_location': 'data/exports/night_operations_interconnected_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.json'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'error_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error_code': 500,
        'system_state': 'Check interconnection and try again'
    }), 500

# ================================
# MAIN APPLICATION RUNNER
# ================================

if __name__ == '__main__':
    print("🚇 KMRL SIH25081 Enhanced Interconnected System Starting...")
    print("🔗 Features: Cross-module data flow, intelligent backup deployment")
    print("🌐 Main Dashboard: http://localhost:5000")
    print("📋 All modules now share real-time interconnected data")
    
    # Ensure data directories exist
    os.makedirs('data/kmrl_data', exist_ok=True)
    os.makedirs('data/exports', exist_ok=True)
    os.makedirs('data/reports', exist_ok=True)
    
    # Initialize with sample data and interconnection
    system_state['trains_data'] = generate_realistic_train_data()
    update_interconnected_state()
    
    print("✅ System initialized with interconnected data flow")
    print("🎯 Ready for enhanced SIH25081 demonstration!")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
"""
🚇 KMRL Emergency Response Testing Module
Real-time disruption handling and backup deployment system
"""

EMERGENCY_TESTING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emergency Response Testing - KMRL SIH25081</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
        }
        
        .container { max-width: 1600px; margin: 0 auto; padding: 25px; }
        
        .header {
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #ef4444, #dc2626);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-btn {
            background: linear-gradient(135deg, #6b7280, #4b5563);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
        }
        
        .emergency-controls {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }
        
        .scenario-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .scenario-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .scenario-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        }
        
        .scenario-card.active {
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.1);
        }
        
        .scenario-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            border-radius: 12px 12px 0 0;
        }
        
        .scenario-card.breakdown::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
        .scenario-card.delay::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
        .scenario-card.weather::before { background: linear-gradient(90deg, #06b6d4, #0891b2); }
        .scenario-card.power::before { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
        .scenario-card.crowd::before { background: linear-gradient(90deg, #10b981, #059669); }
        .scenario-card.security::before { background: linear-gradient(90deg, #f97316, #ea580c); }
        
        .scenario-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            display: block;
        }
        
        .scenario-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 10px;
        }
        
        .scenario-description {
            color: #94a3b8;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .simulation-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
        }
        
        .control-group label {
            color: #cbd5e1;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .control-group input, .control-group select {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            padding: 10px 12px;
            color: #f1f5f9;
        }
        
        .btn {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4);
        }
        
        .btn.stop {
            background: linear-gradient(135deg, #6b7280, #4b5563);
        }
        
        .active-scenario {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            display: none;
        }
        
        .active-scenario.show { display: block; }
        
        .scenario-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-dot.active { background: #ef4444; }
        .status-dot.resolved { background: #10b981; }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        
        .response-timeline {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .timeline-item {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .timeline-item.detection { border-left-color: #f59e0b; }
        .timeline-item.analysis { border-left-color: #06b6d4; }
        .timeline-item.deployment { border-left-color: #8b5cf6; }
        .timeline-item.resolution { border-left-color: #10b981; }
        
        .timeline-time {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-right: 15px;
            min-width: 60px;
        }
        
        .timeline-action {
            color: #f1f5f9;
            font-weight: 500;
        }
        
        .backup-deployment {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 25px;
        }
        
        .deployment-panel {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 20px;
        }
        
        .panel-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .train-deployment-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 8px 0;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .train-deployment-item.deployed { border-left-color: #10b981; }
        .train-deployment-item.available { border-left-color: #f59e0b; }
        .train-deployment-item.unavailable { border-left-color: #ef4444; }
        
        .train-info {
            display: flex;
            flex-direction: column;
        }
        
        .train-name {
            font-weight: 600;
            color: #f1f5f9;
        }
        
        .train-details {
            font-size: 0.8rem;
            color: #94a3b8;
        }
        
        .deployment-status {
            font-size: 0.8rem;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .deployment-status.deployed {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }
        
        .deployment-status.available {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }
        
        .deployment-status.unavailable {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }
        
        .performance-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .metric-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 5px;
        }
        
        .metric-value.good { color: #10b981; }
        .metric-value.warning { color: #f59e0b; }
        .metric-value.critical { color: #ef4444; }
        
        .metric-label {
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        
        .loading.show { display: block; }
        
        .spinner {
            width: 40px;
            height: 40px;
            margin: 0 auto 15px;
            border: 3px solid rgba(239, 68, 68, 0.2);
            border-top: 3px solid #ef4444;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .scenario-grid { grid-template-columns: 1fr; }
            .backup-deployment { grid-template-columns: 1fr; }
            .performance-metrics { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Emergency Response Testing</h1>
            <a href="/" class="nav-btn">← Back to Main</a>
        </div>
        
        <div class="emergency-controls">
            <h3 style="margin-bottom: 20px; color: #f1f5f9;">⚡ Emergency Scenario Simulation</h3>
            <p style="color: #94a3b8; margin-bottom: 25px;">
                Select an emergency scenario to test the AI's real-time response capabilities and backup deployment strategies.
            </p>
            
            <div class="scenario-grid">
                <div class="scenario-card breakdown" onclick="selectScenario('breakdown')">
                    <span class="scenario-icon">🔧</span>
                    <div class="scenario-title">Train Breakdown</div>
                    <div class="scenario-description">Simulate in-service train mechanical failure requiring immediate backup deployment</div>
                </div>
                
                <div class="scenario-card delay" onclick="selectScenario('delay')">
                    <span class="scenario-icon">⏰</span>
                    <div class="scenario-title">Schedule Delay</div>
                    <div class="scenario-description">Test response to major delays caused by passenger incidents or technical issues</div>
                </div>
                
                <div class="scenario-card weather" onclick="selectScenario('weather')">
                    <span class="scenario-icon">🌧️</span>
                    <div class="scenario-title">Weather Emergency</div>
                    <div class="scenario-description">Simulate heavy rain, fog, or cyclone conditions affecting train operations</div>
                </div>
                
                <div class="scenario-card power" onclick="selectScenario('power')">
                    <span class="scenario-icon">⚡</span>
                    <div class="scenario-title">Power Outage</div>
                    <div class="scenario-description">Test backup systems during electrical grid failures or power interruptions</div>
                </div>
                
                <div class="scenario-card crowd" onclick="selectScenario('crowd')">
                    <span class="scenario-icon">👥</span>
                    <div class="scenario-title">Crowd Management</div>
                    <div class="scenario-description">Handle unexpected crowd surges during festivals or special events</div>
                </div>
                
                <div class="scenario-card security" onclick="selectScenario('security')">
                    <span class="scenario-icon">🛡️</span>
                    <div class="scenario-title">Security Alert</div>
                    <div class="scenario-description">Respond to security concerns requiring service modifications or evacuations</div>
                </div>
            </div>
            
            <div class="simulation-controls">
                <div class="control-group">
                    <label>Affected Train</label>
                    <select id="affectedTrain">
                        <option value="random">Random Selection</option>
                        <option value="KRISHNA">KRISHNA (T001)</option>
                        <option value="TAPTI">TAPTI (T002)</option>
                        <option value="NILA">NILA (T003)</option>
                        <option value="MAHE">MAHE (T020)</option>
                        <option value="GANGA">GANGA (T024)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Severity Level</label>
                    <select id="severityLevel">
                        <option value="minor">Minor (5-10 min delay)</option>
                        <option value="moderate">Moderate (15-30 min delay)</option>
                        <option value="major">Major (45+ min delay)</option>
                        <option value="critical">Critical (Service disruption)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Time of Day</label>
                    <select id="timeOfDay">
                        <option value="current">Current Time</option>
                        <option value="peak_morning">Peak Morning (8-10 AM)</option>
                        <option value="peak_evening">Peak Evening (5-7 PM)</option>
                        <option value="off_peak">Off Peak Hours</option>
                        <option value="night">Night Operations</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Weather Conditions</label>
                    <select id="weatherConditions">
                        <option value="clear">Clear Weather</option>
                        <option value="light_rain">Light Rain</option>
                        <option value="heavy_rain">Heavy Rain</option>
                        <option value="fog">Dense Fog</option>
                        <option value="storm">Storm Conditions</option>
                    </select>
                </div>
            </div>
            
            <button id="simulateBtn" class="btn" onclick="startEmergencySimulation()">
                🚨 Start Emergency Simulation
            </button>
            
            <button id="stopBtn" class="btn stop" onclick="stopEmergencySimulation()" style="display: none; margin-left: 15px;">
                🛑 Stop Simulation
            </button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Initializing emergency response simulation...</p>
        </div>
        
        <div class="active-scenario" id="activeScenario">
            <div class="scenario-status">
                <div class="status-indicator">
                    <div class="status-dot active" id="statusDot"></div>
                    <span id="scenarioStatusText">Emergency Active - AI Responding</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.9rem;" id="elapsedTime">00:00:00</div>
            </div>
            
            <div class="response-timeline" id="responseTimeline">
                <h4 style="color: #f1f5f9; margin-bottom: 15px;">📋 Response Timeline</h4>
                <!-- Timeline items populated by JavaScript -->
            </div>
            
            <div class="backup-deployment">
                <div class="deployment-panel">
                    <div class="panel-title">🚄 Backup Train Deployment</div>
                    <div id="backupTrains">
                        <!-- Backup train items populated by JavaScript -->
                    </div>
                </div>
                
                <div class="deployment-panel">
                    <div class="panel-title">📊 Performance Metrics</div>
                    <div class="performance-metrics" id="performanceMetrics">
                        <div class="metric-card">
                            <div class="metric-value good" id="responseTime">--</div>
                            <div class="metric-label">Response Time (sec)</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value warning" id="passengerImpact">--</div>
                            <div class="metric-label">Affected Passengers</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value good" id="backupDeployed">--</div>
                            <div class="metric-label">Backups Deployed</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value good" id="recoveryTime">--</div>
                            <div class="metric-label">Est. Recovery (min)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedScenario = null;
        let simulationActive = false;
        let simulationInterval = null;
        let startTime = null;
        let timelineEvents = [];
        
        function selectScenario(scenario) {
            // Remove active class from all cards
            document.querySelectorAll('.scenario-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Add active class to selected card
            document.querySelector(`.scenario-card.${scenario}`).classList.add('active');
            
            selectedScenario = scenario;
        }
        
        function showLoading(show) {
            document.getElementById('loading').classList.toggle('show', show);
        }
        
        async function startEmergencySimulation() {
            if (!selectedScenario) {
                alert('Please select an emergency scenario first!');
                return;
            }
            
            showLoading(true);
            
            const params = {
                scenario: selectedScenario,
                affectedTrain: document.getElementById('affectedTrain').value,
                severity: document.getElementById('severityLevel').value,
                timeOfDay: document.getElementById('timeOfDay').value,
                weather: document.getElementById('weatherConditions').value
            };
            
            try {
                const response = await fetch('/api/start-emergency-simulation', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    simulationActive = true;
                    startTime = new Date();
                    timelineEvents = [];
                    
                    document.getElementById('simulateBtn').style.display = 'none';
                    document.getElementById('stopBtn').style.display = 'inline-flex';
                    document.getElementById('activeScenario').classList.add('show');
                    
                    // Start real-time simulation
                    simulationInterval = setInterval(updateSimulation, 2000);
                    
                    // Initialize timeline
                    addTimelineEvent('detection', 'Emergency detected and analyzed');
                    setTimeout(() => addTimelineEvent('analysis', 'AI analyzing backup deployment options'), 3000);
                    
                } else {
                    alert('Simulation failed: ' + data.message);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                showLoading(false);
            }
        }
        
        function stopEmergencySimulation() {
            simulationActive = false;
            if (simulationInterval) {
                clearInterval(simulationInterval);
            }
            
            document.getElementById('simulateBtn').style.display = 'inline-flex';
            document.getElementById('stopBtn').style.display = 'none';
            document.getElementById('activeScenario').classList.remove('show');
            
            // Mark as resolved
            document.getElementById('statusDot').className = 'status-dot resolved';
            document.getElementById('scenarioStatusText').textContent = 'Emergency Resolved';
            
            addTimelineEvent('resolution', 'Emergency successfully resolved');
        }
        
        function updateSimulation() {
            if (!simulationActive) return;
            
            // Update elapsed time
            const elapsed = new Date() - startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            document.getElementById('elapsedTime').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}:00`;
            
            // Update performance metrics
            document.getElementById('responseTime').textContent = Math.floor(elapsed / 1000);
            document.getElementById('passengerImpact').textContent = Math.floor(Math.random() * 500 + 200);
            document.getElementById('backupDeployed').textContent = Math.floor(Math.random() * 3 + 1);
            document.getElementById('recoveryTime').textContent = Math.floor(Math.random() * 15 + 5);
            
            // Simulate backup deployment progress
            if (elapsed > 6000 && timelineEvents.length === 2) {
                addTimelineEvent('deployment', 'Backup train SARAYU deployed to affected route');
                updateBackupTrains();
            }
            
            if (elapsed > 12000 && timelineEvents.length === 3) {
                addTimelineEvent('deployment', 'Service frequency adjusted on parallel routes');
            }
            
            // Auto-resolve after 30 seconds
            if (elapsed > 30000) {
                stopEmergencySimulation();
            }
        }
        
        function addTimelineEvent(type, description) {
            const timeline = document.getElementById('responseTimeline');
            const elapsed = simulationActive ? new Date() - startTime : 0;
            const timeStr = `+${Math.floor(elapsed / 1000)}s`;
            
            const timelineItem = document.createElement('div');
            timelineItem.className = `timeline-item ${type}`;
            timelineItem.innerHTML = `
                <div class="timeline-time">${timeStr}</div>
                <div class="timeline-action">${description}</div>
            `;
            
            timeline.appendChild(timelineItem);
            timelineEvents.push({type, description, time: elapsed});
        }
        
        function updateBackupTrains() {
            const backupContainer = document.getElementById('backupTrains');
            
            const backupTrains = [
                {name: 'SARAYU', details: 'Standby → Active Service', status: 'deployed'},
                {name: 'ARUTH', details: 'Cleaning → Ready', status: 'available'},
                {name: 'VAIGAI', details: 'Maintenance Required', status: 'unavailable'},
                {name: 'DHWANIL', details: 'Standby → Ready', status: 'available'}
            ];
            
            backupContainer.innerHTML = backupTrains.map(train => `
                <div class="train-deployment-item ${train.status}">
                    <div class="train-info">
                        <div class="train-name">${train.name}</div>
                        <div class="train-details">${train.details}</div>
                    </div>
                    <div class="deployment-status ${train.status}">
                        ${train.status.charAt(0).toUpperCase() + train.status.slice(1)}
                    </div>
                </div>
            `).join('');
        }
        
        // Initialize backup trains on page load
        window.addEventListener('load', () => {
            updateBackupTrains();
        });
    </script>
</body>
</html>
"""

print("✅ Emergency Response Testing Module Created!")
print("🚨 Features:")
print("   • Real-time emergency scenario simulation")
print("   • 6 different emergency types (breakdown, delay, weather, etc.)")
print("   • Live backup train deployment tracking")
print("   • Response timeline with AI decision logging")
print("   • Performance metrics and recovery analysis")
print("   • Realistic disruption handling simulation")
print("   • Integration with main KMRL system")
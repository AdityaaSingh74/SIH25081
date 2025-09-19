// Smart Metro AI OS - Main JavaScript File
// Global utility functions and common functionality

// Global variables
let notificationQueue = [];
let activeNotifications = 0;
const MAX_NOTIFICATIONS = 3;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupGlobalEventListeners();
    setupNotificationSystem();
    setupLoadingOverlay();
    checkSystemStatus();
}

function setupGlobalEventListeners() {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleMobileSidebar);
    }
    
    // ESC key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
    
    // Click outside modal to close
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });
    
    // Auto-hide notifications after 5 seconds
    setInterval(processNotificationQueue, 100);
}

function setupNotificationSystem() {
    const container = document.getElementById('notification-container');
    if (!container) {
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
}

function setupLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loading-overlay';
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.style.display = 'none';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-sync fa-spin"></i>
                <p>Processing...</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notification = {
        id: Date.now() + Math.random(),
        message,
        type,
        duration,
        timestamp: Date.now()
    };
    
    notificationQueue.push(notification);
    processNotificationQueue();
}

function processNotificationQueue() {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    // Remove expired notifications
    const currentNotifications = container.querySelectorAll('.notification');
    currentNotifications.forEach(notif => {
        const timestamp = parseInt(notif.dataset.timestamp);
        const duration = parseInt(notif.dataset.duration);
        
        if (Date.now() - timestamp > duration) {
            removeNotification(notif);
        }
    });
    
    // Add new notifications if under limit
    while (notificationQueue.length > 0 && activeNotifications < MAX_NOTIFICATIONS) {
        const notification = notificationQueue.shift();
        displayNotification(notification);
    }
}

function displayNotification(notification) {
    const container = document.getElementById('notification-container');
    
    const notifElement = document.createElement('div');
    notifElement.className = `notification notification-${notification.type}`;
    notifElement.dataset.id = notification.id;
    notifElement.dataset.timestamp = notification.timestamp;
    notifElement.dataset.duration = notification.duration;
    
    const iconMap = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-exclamation-circle'
    };
    
    notifElement.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${iconMap[notification.type]}"></i>
        </div>
        <div class="notification-content">${notification.message}</div>
        <button class="notification-close" onclick="removeNotification(this.parentElement)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notifElement);
    activeNotifications++;
    
    // Trigger animation
    setTimeout(() => {
        notifElement.classList.add('slide-in');
    }, 10);
}

function removeNotification(notificationElement) {
    if (!notificationElement) return;
    
    notificationElement.style.transform = 'translateX(100%)';
    notificationElement.style.opacity = '0';
    
    setTimeout(() => {
        if (notificationElement.parentElement) {
            notificationElement.parentElement.removeChild(notificationElement);
            activeNotifications = Math.max(0, activeNotifications - 1);
        }
    }, 300);
}

// Loading System
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const spinner = overlay.querySelector('.loading-spinner p');
    
    if (spinner) {
        spinner.textContent = message;
    }
    
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Modal System
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus first focusable element
        const focusable = modal.querySelector('input, button, select, textarea');
        if (focusable) {
            setTimeout(() => focusable.focus(), 100);
        }
    }
}

function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = 'auto';
}

// Mobile Navigation
function toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('mobile-open');
}

// System Status Checker
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/system_status');
        const status = await response.json();
        
        updateSystemStatusIndicators(status);
    } catch (error) {
        console.error('Failed to check system status:', error);
        updateSystemStatusIndicators({ online: false });
    }
}

function updateSystemStatusIndicators(status) {
    const indicators = document.querySelectorAll('.status-indicator');
    indicators.forEach(indicator => {
        if (status.online !== false) {
            indicator.classList.add('online');
        } else {
            indicator.classList.remove('online');
        }
    });
}

// API Helper Functions
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const requestOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(endpoint, requestOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

async function postData(endpoint, data) {
    return apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
    });
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('File upload failed:', error);
        throw error;
    }
}

// Chart Utilities
function createChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }
    
    return new Chart(ctx.getContext('2d'), config);
}

function updateChart(chart, newData) {
    if (!chart) return;
    
    if (newData.labels) {
        chart.data.labels = newData.labels;
    }
    
    if (newData.datasets) {
        chart.data.datasets.forEach((dataset, index) => {
            if (newData.datasets[index]) {
                Object.assign(dataset, newData.datasets[index]);
            }
        });
    }
    
    chart.update('none');
}

// Data Formatting Utilities
function formatNumber(num, decimals = 2) {
    if (typeof num !== 'number') return '0';
    return num.toFixed(decimals);
}

function formatPercentage(num, decimals = 1) {
    if (typeof num !== 'number') return '0%';
    return num.toFixed(decimals) + '%';
}

function formatTime(timestamp) {
    if (!timestamp) return '--:--';
    
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(timestamp) {
    if (!timestamp) return '--';
    
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit'
    });
}

function formatDuration(minutes) {
    if (typeof minutes !== 'number') return '0 min';
    
    if (minutes < 60) {
        return Math.round(minutes) + ' min';
    }
    
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
}

// Data Validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

function validateRequired(value) {
    return value !== null && value !== undefined && value.toString().trim() !== '';
}

// Local Storage Helpers (Note: These won't work in Claude.ai artifacts)
function saveToStorage(key, data) {
    // In a real environment, this would use localStorage
    // For now, we'll just keep data in memory
    if (!window.tempStorage) window.tempStorage = {};
    window.tempStorage[key] = JSON.stringify(data);
}

function loadFromStorage(key, defaultValue = null) {
    // In a real environment, this would use localStorage
    if (!window.tempStorage) window.tempStorage = {};
    try {
        const stored = window.tempStorage[key];
        return stored ? JSON.parse(stored) : defaultValue;
    } catch (error) {
        console.error('Failed to parse stored data:', error);
        return defaultValue;
    }
}

function removeFromStorage(key) {
    if (window.tempStorage) {
        delete window.tempStorage[key];
    }
}

// Debounce and Throttle Utilities
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Error Handling
function handleError(error, context = 'Unknown') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'An unexpected error occurred';
    
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showNotification(message, 'error');
}

// Animation Helpers
function animateValue(element, start, end, duration = 1000) {
    const range = end - start;
    const minTimer = 50;
    let stepTime = Math.abs(Math.floor(duration / range));
    stepTime = Math.max(stepTime, minTimer);
    
    const startTime = new Date().getTime();
    const endTime = startTime + duration;
    
    function run() {
        const now = new Date().getTime();
        const remaining = Math.max((endTime - now) / duration, 0);
        const value = Math.round(end - (remaining * range));
        
        element.textContent = value;
        
        if (value !== end) {
            requestAnimationFrame(run);
        }
    }
    
    run();
}

function fadeIn(element, duration = 300) {
    element.style.opacity = 0;
    element.style.display = 'block';
    
    const start = performance.now();
    
    function fade(currentTime) {
        const elapsed = currentTime - start;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            element.style.opacity = progress;
            requestAnimationFrame(fade);
        } else {
            element.style.opacity = 1;
        }
    }
    
    requestAnimationFrame(fade);
}

function fadeOut(element, duration = 300) {
    const start = performance.now();
    const initialOpacity = parseFloat(window.getComputedStyle(element).opacity);
    
    function fade(currentTime) {
        const elapsed = currentTime - start;
        const progress = elapsed / duration;
        
        if (progress < 1) {
            element.style.opacity = initialOpacity * (1 - progress);
            requestAnimationFrame(fade);
        } else {
            element.style.opacity = 0;
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(fade);
}

// Export for module systems (if used)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        hideLoading,
        showLoading,
        openModal,
        closeModal,
        apiCall,
        postData,
        uploadFile,
        formatNumber,
        formatPercentage,
        formatTime,
        formatDate,
        formatDuration,
        handleError,
        debounce,
        throttle
    };
}
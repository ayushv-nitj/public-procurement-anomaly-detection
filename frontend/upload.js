// Global state
let currentSource = null;
let resultsData = null;

// API endpoint - Flask backend runs on port 5000
// Use environment-aware URL: localhost for development, or disable for production
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:5000/api' 
    : null; // No backend in production (GitHub Pages)

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupSourceButtons();
    setupFileUploads();
});

function setupSourceButtons() {
    const buttons = document.querySelectorAll('.source-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            buttons.forEach(b => b.classList.remove('active'));
            // Add active to clicked
            btn.classList.add('active');
            
            // Hide all input sections
            document.querySelectorAll('.input-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Show selected input section
            const source = btn.dataset.source;
            currentSource = source;
            document.getElementById(`input-${source}`).classList.add('active');
            
            // Hide error and results
            hideError();
            hideResults();
        });
    });
}

function setupFileUploads() {
    ['csv', 'json', 'xml'].forEach(type => {
        const uploadDiv = document.getElementById(`${type}-upload`);
        const fileInput = document.getElementById(`${type}-file`);
        const textarea = document.getElementById(`${type}-data`);
        
        // Click to browse
        uploadDiv.addEventListener('click', () => fileInput.click());
        
        // File selected
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    textarea.value = e.target.result;
                };
                reader.readAsText(file);
            }
        });
        
        // Drag and drop
        uploadDiv.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadDiv.classList.add('dragover');
        });
        
        uploadDiv.addEventListener('dragleave', () => {
            uploadDiv.classList.remove('dragover');
        });
        
        uploadDiv.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadDiv.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    textarea.value = e.target.result;
                };
                reader.readAsText(file);
            }
        });
    });
}

async function loadSample(type) {
    try {
        const response = await fetch(`${API_URL}/sample-data/${type}`);
        const data = await response.text();
        document.getElementById(`${type}-data`).value = data;
    } catch (error) {
        showError('Failed to load sample data: ' + error.message);
    }
}

async function processData() {
    if (!currentSource) {
        showError('Please select a data source');
        return;
    }
    
    // Check if backend is available
    if (!API_URL) {
        showError('This feature requires running the Flask backend locally. Please see the README for setup instructions.');
        return;
    }
    
    // Show loading
    showLoading();
    hideError();
    hideResults();
    
    try {
        let payload = { source: currentSource };
        
        if (currentSource === 'synthetic') {
            // No additional data needed
        } else if (currentSource === 'csv') {
            const data = document.getElementById('csv-data').value;
            if (!data.trim()) {
                throw new Error('Please provide CSV data');
            }
            payload.data = data;
        } else if (currentSource === 'json') {
            const data = document.getElementById('json-data').value;
            if (!data.trim()) {
                throw new Error('Please provide JSON data');
            }
            payload.data = data;
        } else if (currentSource === 'xml') {
            const data = document.getElementById('xml-data').value;
            if (!data.trim()) {
                throw new Error('Please provide XML data');
            }
            payload.data = data;
        } else if (currentSource === 'api') {
            const apiUrl = document.getElementById('api-url').value;
            if (!apiUrl.trim()) {
                throw new Error('Please provide API URL');
            }
            payload.api_url = apiUrl;
            payload.api_key = document.getElementById('api-key').value;
            payload.api_format = document.getElementById('api-format').value;
            payload.api_limit = parseInt(document.getElementById('api-limit').value);
        }
        
        // Make API call
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (!response.ok || !result.success) {
            throw new Error(result.error || 'Processing failed');
        }
        
        // Store results
        resultsData = result;
        
        // Save to localStorage for dashboard
        localStorage.setItem('anomalyResults', JSON.stringify(result));
        
        // Show results
        showResults(result);
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error').classList.add('active');
}

function hideError() {
    document.getElementById('error').classList.remove('active');
}

function showResults(data) {
    document.getElementById('stat-total').textContent = data.summary.total_contracts;
    document.getElementById('stat-anomalies').textContent = data.summary.total_anomalies;
    document.getElementById('stat-high-risk').textContent = data.summary.high_risk_count;
    document.getElementById('stat-avg-risk').textContent = data.summary.avg_risk_score;
    
    document.getElementById('results').classList.add('active');
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function hideResults() {
    document.getElementById('results').classList.remove('active');
}

function viewDashboard() {
    // Save results and redirect to main dashboard
    if (resultsData) {
        // Save to results.json format for the dashboard
        const dashboardData = {
            summary: resultsData.summary,
            contracts: resultsData.contracts,
            feature_importance: resultsData.feature_importance,
            department_stats: resultsData.department_stats,
            top_risky_vendors: resultsData.top_risky_vendors,
            similar_pairs: resultsData.similar_pairs,
            risk_distribution: resultsData.risk_distribution
        };
        
        // Save to localStorage
        localStorage.setItem('anomalyResults', JSON.stringify(dashboardData));
        
        // Also save to results.json via API
        fetch(`${API_URL}/save-results`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dashboardData)
        }).then(() => {
            // Redirect to dashboard at port 8080
            window.location.href = 'http://localhost:8080/dashboard.html';
        }).catch(err => {
            console.error('Failed to save results:', err);
            // Still redirect even if save fails
            window.location.href = 'http://localhost:8080/dashboard.html';
        });
    }
}

function reset() {
    // Clear selections
    document.querySelectorAll('.source-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.input-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Clear inputs
    document.querySelectorAll('textarea').forEach(ta => ta.value = '');
    document.querySelectorAll('input[type="text"]').forEach(input => input.value = '');
    document.querySelectorAll('input[type="password"]').forEach(input => input.value = '');
    
    // Hide results and error
    hideResults();
    hideError();
    
    currentSource = null;
    resultsData = null;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

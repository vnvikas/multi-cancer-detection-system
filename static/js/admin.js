// Admin Dashboard JavaScript

// Global variables
let currentPage = 1;
let itemsPerPage = 10;

// Document ready
$(document).ready(function() {
    initializeCharts();
    initializeDataTables();
    setupEventListeners();
    loadDashboardStats();
});

// Initialize Charts
function initializeCharts() {
    // Monthly Patients Chart
    const monthlyCtx = document.getElementById('monthlyPatientsChart');
    if (monthlyCtx) {
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'New Patients',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Number of Patients' } }
                }
            }
        });
    }
    
    // Predictions by Type Chart
    const typeCtx = document.getElementById('predictionsByTypeChart');
    if (typeCtx) {
        new Chart(typeCtx, {
            type: 'pie',
            data: {
                labels: ['Brain Tumor', 'Lung Cancer', 'Breast Cancer'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#3498db', '#2ecc71', '#e74c3c']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
    
    // Model Performance Chart
    const modelCtx = document.getElementById('modelPerformanceChart');
    if (modelCtx) {
        new Chart(modelCtx, {
            type: 'bar',
            data: {
                labels: ['Brain', 'Lung', 'Breast'],
                datasets: [
                    { label: 'Accuracy', data: [0, 0, 0], backgroundColor: '#3498db' },
                    { label: 'Precision', data: [0, 0, 0], backgroundColor: '#2ecc71 },
                    { label: 'Recall', data: [0, 0, 0], backgroundColor: '#e74c3c' }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: 'Percentage (%)' } } }
            }
        });
    }
}

// Initialize DataTables
function initializeDataTables() {
    $('.data-table').each(function() {
        const table = $(this);
        if (!table.hasClass('initialized')) {
            table.DataTable({
                pageLength: itemsPerPage,
                responsive: true,
                language: {
                    search: "Search:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries"
                }
            });
            table.addClass('initialized');
        }
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Refresh button
    $('#refreshStats').on('click', function() {
        loadDashboardStats();
        showNotification('Stats refreshed', 'success');
    });
    
    // Date range picker
    $('.date-range').on('change', function() {
        loadDashboardStats();
    });
    
    // Export buttons
    $('#exportCSV').on('click', function() {
        exportData('csv');
    });
    
    $('#exportPDF').on('click', function() {
        exportData('pdf');
    });
    
    // Retrain model button
    $('#retrainModel').on('click', function() {
        const cancerType = $('#cancerTypeSelect').val();
        if (cancerType) {
            retrainModel(cancerType);
        } else {
            showNotification('Please select a cancer type', 'warning');
        }
    });
    
    // Delete confirmation
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
}

// Load Dashboard Stats via AJAX
function loadDashboardStats() {
    $.ajax({
        url: '/api/admin/dashboard',
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            updateStats(response);
            updateCharts(response);
        },
        error: function(xhr) {
            console.error('Error loading stats:', xhr);
            showNotification('Failed to load dashboard stats', 'error');
        }
    });
}

// Update Statistics Cards
function updateStats(stats) {
    $('#totalDoctors').text(stats.total_doctors || 0);
    $('#totalPatients').text(stats.total_patients || 0);
    $('#totalScans').text(stats.total_scans || 0);
    $('#totalPredictions').text(stats.total_predictions || 0);
    $('#avgConfidence').text((stats.avg_confidence * 100 || 0).toFixed(1) + '%');
}

// Update Charts
function updateCharts(stats) {
    // Update monthly patients chart
    if (stats.monthly_data && stats.monthly_data.patients) {
        const monthlyChart = Chart.getChart('monthlyPatientsChart');
        if (monthlyChart) {
            monthlyChart.data.labels = stats.monthly_data.patients.map(p => p.month);
            monthlyChart.data.datasets[0].data = stats.monthly_data.patients.map(p => p.count);
            monthlyChart.update();
        }
    }
    
    // Update predictions by type chart
    if (stats.predictions_by_type) {
        const typeChart = Chart.getChart('predictionsByTypeChart');
        if (typeChart) {
            typeChart.data.labels = stats.predictions_by_type.map(p => p.type);
            typeChart.data.datasets[0].data = stats.predictions_by_type.map(p => p.count);
            typeChart.update();
        }
    }
}

// Retrain Model
function retrainModel(cancerType) {
    showLoading();
    
    $.ajax({
        url: '/api/admin/retrain',
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify({ cancer_type: cancerType }),
        contentType: 'application/json',
        success: function(response) {
            hideLoading();
            showNotification('Model retraining started successfully', 'success');
            startRetrainingProgress();
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Failed to start retraining', 'error');
        }
    });
}

// Start Retraining Progress
function startRetrainingProgress() {
    const progressBar = $('#retrainProgress');
    if (progressBar.length) {
        let progress = 0;
        const interval = setInterval(function() {
            progress += 10;
            progressBar.css('width', progress + '%');
            progressBar.text(progress + '%');
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    showNotification('Model retraining completed!', 'success');
                    loadDashboardStats();
                }, 1000);
            }
        }, 1000);
    }
}

// Export Data
function exportData(format) {
    const dataType = $('#exportType').val();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    
    window.location.href = `/api/admin/export?type=${dataType}&format=${format}&start=${startDate}&end=${endDate}`;
}

// Manage Doctors
function addDoctor() {
    const doctorData = {
        name: $('#doctorName').val(),
        email: $('#doctorEmail').val(),
        password: $('#doctorPassword').val(),
        specialization: $('#doctorSpecialization').val(),
        hospital_name: $('#doctorHospital').val(),
        contact_number: $('#doctorContact').val()
    };
    
    $.ajax({
        url: '/api/admin/doctors',
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify(doctorData),
        contentType: 'application/json',
        success: function(response) {
            showNotification('Doctor added successfully', 'success');
            location.reload();
        },
        error: function(xhr) {
            showNotification('Failed to add doctor', 'error');
        }
    });
}

function deleteDoctor(doctorId, doctorName) {
    if (confirm(`Delete Dr. ${doctorName}?`)) {
        $.ajax({
            url: `/api/admin/doctors/${doctorId}`,
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + getToken() },
            success: function(response) {
                showNotification('Doctor deleted successfully', 'success');
                location.reload();
            },
            error: function(xhr) {
                showNotification('Failed to delete doctor', 'error');
            }
        });
    }
}

// View System Logs
function loadSystemLogs(page = 1) {
    $.ajax({
        url: `/api/admin/logs?page=${page}`,
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            displayLogs(response);
        },
        error: function(xhr) {
            console.error('Error loading logs:', xhr);
        }
    });
}

function displayLogs(logs) {
    const tbody = $('#logsTable tbody');
    tbody.empty();
    
    logs.items.forEach(log => {
        tbody.append(`
            <tr>
                <td>${new Date(log.created_at).toLocaleString()}</td>
                <td>${log.user || 'System'}</td>
                <td><span class="badge bg-${getLogColor(log.action)}">${log.action}</span></td>
                <td>${log.entity_type || 'N/A'}</td>
                <td>${log.details || ''}</td>
            </tr>
        `);
    });
}

function getLogColor(action) {
    const colors = {
        'LOGIN': 'success',
        'LOGOUT': 'info',
        'CREATE': 'primary',
        'UPDATE': 'warning',
        'DELETE': 'danger'
    };
    return colors[action] || 'secondary';
}

// View Model Performance
function loadModelPerformance() {
    $.ajax({
        url: '/api/admin/model-stats',
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            updateModelCharts(response);
        }
    });
}

function updateModelCharts(models) {
    const brainModel = models.find(m => m.cancer_type === 'brain');
    const lungModel = models.find(m => m.cancer_type === 'lung');
    const breastModel = models.find(m => m.cancer_type === 'breast');
    
    const modelChart = Chart.getChart('modelPerformanceChart');
    if (modelChart) {
        modelChart.data.datasets[0].data = [
            (brainModel?.accuracy || 0) * 100,
            (lungModel?.accuracy || 0) * 100,
            (breastModel?.accuracy || 0) * 100
        ];
        modelChart.data.datasets[1].data = [
            (brainModel?.precision_val || 0) * 100,
            (lungModel?.precision_val || 0) * 100,
            (breastModel?.precision_val || 0) * 100
        ];
        modelChart.data.datasets[2].data = [
            (brainModel?.recall_val || 0) * 100,
            (lungModel?.recall_val || 0) * 100,
            (breastModel?.recall_val || 0) * 100
        ];
        modelChart.update();
    }
}

// Utility Functions
function getToken() {
    return localStorage.getItem('access_token');
}

function showLoading() {
    $('#loadingOverlay').fadeIn();
}

function hideLoading() {
    $('#loadingOverlay').fadeOut();
}

function showNotification(message, type = 'info') {
    const toast = `
        <div class="toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    $('body').append(toast);
    const toastElement = $('.toast').last();
    const bsToast = new bootstrap.Toast(toastElement[0], { autohide: true, delay: 3000 });
    bsToast.show();
    
    setTimeout(() => {
        toastElement.remove();
    }, 3000);
}

// Auto-refresh every 30 seconds
setInterval(() => {
    if (window.location.pathname.includes('/admin/dashboard')) {
        loadDashboardStats();
    }
}, 30000);
// Doctor Dashboard JavaScript

$(document).ready(function() {
    initializeDoctorDashboard();
    setupDoctorEventListeners();
    loadDoctorStats();
    loadRecentPatients();
});

// Initialize Doctor Dashboard
function initializeDoctorDashboard() {
    // Initialize date pickers
    $('.date-picker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true
    });
    
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();
}

// Setup Event Listeners
function setupDoctorEventListeners() {
    // Search patient
    $('#patientSearch').on('keyup', function() {
        filterPatients($(this).val());
    });
    
    // Filter by cancer type
    $('#cancerTypeFilter').on('change', function() {
        filterPredictions($(this).val());
    });
    
    // Quick actions
    $('.quick-action').on('click', function() {
        const action = $(this).data('action');
        performQuickAction(action);
    });
    
    // Refresh button
    $('#refreshData').on('click', function() {
        loadDoctorStats();
        loadRecentPatients();
        showNotification('Data refreshed', 'success');
    });
}

// Load Doctor Stats
function loadDoctorStats() {
    $.ajax({
        url: '/api/doctor/dashboard',
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            updateStatsCards(response);
            updateActivityCharts(response);
        },
        error: function(xhr) {
            console.error('Error loading stats:', xhr);
        }
    });
}

// Update Stats Cards
function updateStatsCards(stats) {
    $('#totalPatients').text(stats.total_patients || 0);
    $('#totalScans').text(stats.total_scans || 0);
    $('#totalPredictions').text(stats.total_predictions || 0);
    $('#pendingVerifications').text(stats.pending_verifications || 0);
    
    // Update verification rate
    const verifiedCount = stats.verified_predictions || 0;
    const totalCount = stats.total_predictions || 1;
    const rate = (verifiedCount / totalCount * 100).toFixed(1);
    $('#verificationRate').text(rate + '%');
    
    // Update verification progress bar
    $('#verificationProgress').css('width', rate + '%');
}

// Update Activity Charts
function updateActivityCharts(stats) {
    // Weekly activity chart
    const activityCtx = document.getElementById('weeklyActivityChart');
    if (activityCtx && stats.weekly_activity) {
        new Chart(activityCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Scans',
                    data: stats.weekly_activity.scans || [0,0,0,0,0,0,0],
                    backgroundColor: '#3498db'
                }, {
                    label: 'Predictions',
                    data: stats.weekly_activity.predictions || [0,0,0,0,0,0,0],
                    backgroundColor: '#2ecc71'
                }]
            },
            options: {
                responsive: true,
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

// Load Recent Patients
function loadRecentPatients() {
    $.ajax({
        url: '/api/doctor/patients?limit=10',
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            displayRecentPatients(response.patients);
        }
    });
}

// Display Recent Patients
function displayRecentPatients(patients) {
    const container = $('#recentPatients');
    container.empty();
    
    if (patients.length === 0) {
        container.html('<div class="text-center text-muted">No patients found</div>');
        return;
    }
    
    patients.forEach(patient => {
        container.append(`
            <div class="patient-card card mb-2" data-patient-id="${patient.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${patient.name}</h6>
                            <small class="text-muted">ID: ${patient.patient_uid} | Age: ${patient.age}</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-info" onclick="viewPatient('${patient.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-primary" onclick="uploadScan('${patient.id}')">
                                <i class="fas fa-upload"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    });
}

// Filter Patients
function filterPatients(searchTerm) {
    $('.patient-card').each(function() {
        const patientName = $(this).find('h6').text().toLowerCase();
        const patientId = $(this).find('small').text().toLowerCase();
        
        if (patientName.includes(searchTerm.toLowerCase()) || patientId.includes(searchTerm.toLowerCase())) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

// Filter Predictions
function filterPredictions(cancerType) {
    $('.prediction-card').each(function() {
        if (cancerType === 'all' || $(this).data('cancer-type') === cancerType) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

// Perform Quick Action
function performQuickAction(action) {
    switch(action) {
        case 'add_patient':
            window.location.href = '/doctor/add-patient';
            break;
        case 'upload_scan':
            window.location.href = '/doctor/upload-scan';
            break;
        case 'view_history':
            window.location.href = '/doctor/predictions-history';
            break;
        case 'generate_report':
            $('#reportModal').modal('show');
            break;
    }
}

// View Patient Details
function viewPatient(patientId) {
    window.location.href = `/doctor/patient/${patientId}`;
}

// Upload Scan for Patient
function uploadScan(patientId) {
    window.location.href = `/doctor/upload-scan?patient=${patientId}`;
}

// View Prediction Results
function viewPrediction(predictionId) {
    window.location.href = `/doctor/prediction/${predictionId}`;
}

// Verify Prediction
function verifyPrediction(predictionId) {
    $('#verifyModal').modal('show');
    $('#verifyPredictionId').val(predictionId);
}

// Submit Verification
function submitVerification() {
    const predictionId = $('#verifyPredictionId').val();
    const isCorrect = $('#isCorrect').val();
    const doctorNotes = $('#doctorNotes').val();
    
    const data = {
        is_correct: isCorrect === 'true',
        doctor_notes: doctorNotes
    };
    
    if (isCorrect === 'false') {
        data.correct_cancer_type = $('#correctCancerType').val();
        data.correct_subtype = $('#correctSubtype').val();
        data.correct_stage = $('#correctStage').val();
    }
    
    $.ajax({
        url: `/api/predict/verify/${predictionId}`,
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            $('#verifyModal').modal('hide');
            showNotification('Prediction verified successfully', 'success');
            location.reload();
        },
        error: function(xhr) {
            showNotification('Verification failed', 'error');
        }
    });
}

// Generate Report
function generateReport(predictionId) {
    showLoading();
    window.location.href = `/doctor/generate-report/${predictionId}`;
    setTimeout(() => hideLoading(), 2000);
}

// Load Prediction History
function loadPredictionHistory(page = 1) {
    $.ajax({
        url: `/api/predict/history?page=${page}`,
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            displayPredictionHistory(response);
        }
    });
}

// Display Prediction History
function displayPredictionHistory(data) {
    const tbody = $('#predictionHistory tbody');
    tbody.empty();
    
    data.predictions.forEach(pred => {
        tbody.append(`
            <tr>
                <td>${new Date(pred.created_at).toLocaleDateString()}</td>
                <td>${pred.patient_name}</td>
                <td>${pred.cancer_type}</td>
                <td>${pred.cancer_subtype}</td>
                <td>${(pred.confidence_score * 100).toFixed(1)}%</td>
                <td>
                    <span class="badge bg-${pred.risk_score > 70 ? 'danger' : pred.risk_score > 30 ? 'warning' : 'success'}">
                        ${pred.risk_score}%
                    </span>
                </td>
                <td>
                    ${pred.doctor_verified ? 
                        '<span class="badge bg-success">Verified</span>' : 
                        '<span class="badge bg-warning">Pending</span>'}
                </td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewPrediction('${pred.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="generateReport('${pred.id}')">
                        <i class="fas fa-file-pdf"></i>
                    </button>
                </td>
            </tr>
        `);
    });
}

// Schedule Follow-up
function scheduleFollowup(patientId) {
    const date = $('#followupDate').val();
    const notes = $('#followupNotes').val();
    
    $.ajax({
        url: '/api/doctor/schedule-followup',
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify({
            patient_id: patientId,
            scheduled_date: date,
            notes: notes
        }),
        contentType: 'application/json',
        success: function(response) {
            $('#followupModal').modal('hide');
            showNotification('Follow-up scheduled', 'success');
        }
    });
}

// Upload Scan with Preview
function previewScanImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#scanPreview').attr('src', e.target.result).show();
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Submit Scan Upload
function submitScanUpload() {
    const formData = new FormData();
    formData.append('patient_id', $('#patientSelect').val());
    formData.append('cancer_type', $('#cancerType').val());
    formData.append('scan_type', $('#scanType').val());
    formData.append('scan_image', $('#scanImage')[0].files[0]);
    formData.append('scan_notes', $('#scanNotes').val());
    
    showLoading();
    
    $.ajax({
        url: '/api/predict/upload',
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            hideLoading();
            showNotification('Scan uploaded successfully', 'success');
            setTimeout(() => {
                window.location.href = `/doctor/predict-scan/${response.scan_id}`;
            }, 1500);
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Upload failed', 'error');
        }
    });
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

function showNotification(message, type) {
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    const bsToast = new bootstrap.Toast(toast[0], { autohide: true, delay: 3000 });
    bsToast.show();
    
    setTimeout(() => toast.remove(), 3000);
}

// Auto-refresh every 30 seconds on dashboard
if (window.location.pathname.includes('/doctor/dashboard')) {
    setInterval(() => {
        loadDoctorStats();
        loadRecentPatients();
    }, 30000);
}
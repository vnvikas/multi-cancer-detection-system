// Prediction Module JavaScript

// Global prediction variables
let currentPrediction = null;
let confidenceChart = null;

$(document).ready(function() {
    initializePredictionPage();
});

// Initialize Prediction Page
function initializePredictionPage() {
    // Initialize confidence meter
    updateConfidenceMeter();
    
    // Initialize risk gauge
    initializeRiskGauge();
    
    // Initialize charts
    initializePredictionCharts();
    
    // Setup event listeners
    setupPredictionEventListeners();
}

// Update Confidence Meter
function updateConfidenceMeter() {
    const confidence = $('#confidenceScore').data('value');
    if (confidence) {
        const percentage = (confidence * 100).toFixed(1);
        $('#confidenceFill').css('width', percentage + '%');
        $('#confidenceText').text(percentage + '%');
        
        // Set color based on confidence
        if (confidence > 0.8) {
            $('#confidenceFill').addClass('bg-success');
        } else if (confidence > 0.6) {
            $('#confidenceFill').addClass('bg-warning');
        } else {
            $('#confidenceFill').addClass('bg-danger');
        }
    }
}

// Initialize Risk Gauge
function initializeRiskGauge() {
    const riskScore = $('#riskScore').data('value');
    if (riskScore) {
        const gauge = $('#riskGauge');
        const angle = (riskScore / 100) * 180;
        
        gauge.css('transform', `rotate(${angle}deg)`);
        
        // Set color based on risk
        if (riskScore > 70) {
            gauge.addClass('text-danger');
        } else if (riskScore > 30) {
            gauge.addClass('text-warning');
        } else {
            gauge.addClass('text-success');
        }
    }
}

// Initialize Prediction Charts
function initializePredictionCharts() {
    // Cancer Type Probability Chart
    const probCtx = document.getElementById('probabilityChart');
    if (probCtx) {
        const probabilities = $('#probabilityData').data('probabilities');
        confidenceChart = new Chart(probCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(probabilities || {}),
                datasets: [{
                    label: 'Probability',
                    data: Object.values(probabilities || {}).map(p => p * 100),
                    backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12'],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: 'Probability (%)' }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Feature Importance Chart
    const featureCtx = document.getElementById('featureImportanceChart');
    if (featureCtx) {
        new Chart(featureCtx, {
            type: 'horizontalBar',
            data: {
                labels: ['Texture', 'Shape', 'Intensity', 'Edge', 'Size'],
                datasets: [{
                    label: 'Importance',
                    data: [0.35, 0.25, 0.20, 0.12, 0.08],
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 0.5,
                        title: { display: true, text: 'Importance Score' }
                    }
                }
            }
        });
    }
}

// Setup Event Listeners
function setupPredictionEventListeners() {
    // Verify button
    $('#verifyPrediction').on('click', function() {
        showVerificationModal();
    });
    
    // Report button
    $('#generateReport').on('click', function() {
        generatePDFReport();
    });
    
    // Share button
    $('#shareReport').on('click', function() {
        shareReport();
    });
    
    // Compare button
    $('#compareWithPrevious').on('click', function() {
        showComparisonModal();
    });
    
    // Treatment plan button
    $('#createTreatmentPlan').on('click', function() {
        createTreatmentPlan();
    });
}

// Show Verification Modal
function showVerificationModal() {
    const predictionId = $('#predictionId').val();
    
    $('#verificationModal').modal('show');
    $('#verifyPredictionId').val(predictionId);
    
    // Populate current prediction for reference
    $('#currentCancerType').text($('#cancerType').text());
    $('#currentSubtype').text($('#cancerSubtype').text());
    $('#currentStage').text($('#cancerStage').text());
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
    
    showLoading();
    
    $.ajax({
        url: `/api/predict/verify/${predictionId}`,
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            hideLoading();
            $('#verificationModal').modal('hide');
            showNotification('Prediction verified successfully', 'success');
            
            // Update UI
            $('#verificationStatus').html('<span class="badge bg-success">Verified</span>');
            $('#doctorNotes').val(doctorNotes);
            
            setTimeout(() => location.reload(), 1500);
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Verification failed', 'error');
        }
    });
}

// Generate PDF Report
function generatePDFReport() {
    const predictionId = $('#predictionId').val();
    
    showLoading();
    
    $.ajax({
        url: `/api/predict/report/${predictionId}`,
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        xhrFields: {
            responseType: 'blob'
        },
        success: function(blob) {
            hideLoading();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `prediction_report_${predictionId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Report downloaded successfully', 'success');
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Failed to generate report', 'error');
        }
    });
}

// Share Report
function shareReport() {
    const predictionId = $('#predictionId').val();
    const shareUrl = `${window.location.origin}/doctor/prediction/${predictionId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Cancer Detection Report',
            text: 'Medical report for patient',
            url: shareUrl
        }).catch(console.error);
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(shareUrl);
        showNotification('Link copied to clipboard', 'success');
    }
}

// Show Comparison Modal
function showComparisonModal() {
    const patientId = $('#patientId').val();
    
    $.ajax({
        url: `/api/doctor/patients/${patientId}/predictions`,
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        success: function(response) {
            populateComparisonModal(response.predictions);
            $('#comparisonModal').modal('show');
        }
    });
}

// Populate Comparison Modal
function populateComparisonModal(predictions) {
    const container = $('#comparisonTable tbody');
    container.empty();
    
    predictions.forEach(pred => {
        container.append(`
            <tr>
                <td>${new Date(pred.created_at).toLocaleDateString()}</td>
                <td>${pred.cancer_type}</td>
                <td>${pred.cancer_subtype}</td>
                <td>${pred.cancer_stage}</td>
                <td>${(pred.confidence_score * 100).toFixed(1)}%</td>
                <td>${pred.risk_score}%</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewPrediction('${pred.id}')">
                        View
                    </button>
                </td>
            </tr>
        `);
    });
}

// Create Treatment Plan
function createTreatmentPlan() {
    const patientId = $('#patientId').val();
    const predictionId = $('#predictionId').val();
    
    window.location.href = `/doctor/treatment-plan/${patientId}?prediction=${predictionId}`;
}

// Save Treatment Plan
function saveTreatmentPlan() {
    const data = {
        patient_id: $('#patientId').val(),
        prediction_id: $('#predictionId').val(),
        treatment_type: $('#treatmentType').val(),
        start_date: $('#startDate').val(),
        end_date: $('#endDate').val(),
        medications: $('#medications').val(),
        dosage: $('#dosage').val(),
        follow_up_frequency: $('#followupFrequency').val(),
        special_instructions: $('#specialInstructions').val()
    };
    
    showLoading();
    
    $.ajax({
        url: '/api/doctor/treatment-plan',
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            hideLoading();
            $('#treatmentModal').modal('hide');
            showNotification('Treatment plan created', 'success');
            location.reload();
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Failed to create treatment plan', 'error');
        }
    });
}

// View Prediction Details
function viewPrediction(predictionId) {
    window.location.href = `/doctor/prediction/${predictionId}`;
}

// Export Prediction Data
function exportPredictionData(format) {
    const predictionId = $('#predictionId').val();
    
    window.location.href = `/api/predict/export/${predictionId}?format=${format}`;
}

// Add Clinical Note
function addClinicalNote() {
    const note = $('#clinicalNote').val();
    const predictionId = $('#predictionId').val();
    
    if (!note) {
        showNotification('Please enter a note', 'warning');
        return;
    }
    
    $.ajax({
        url: `/api/predict/note/${predictionId}`,
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        data: JSON.stringify({ note: note }),
        contentType: 'application/json',
        success: function(response) {
            $('#clinicalNote').val('');
            showNotification('Note added successfully', 'success');
            
            // Append note to list
            $('#clinicalNotesList').prepend(`
                <div class="note-item border-bottom mb-2 pb-2">
                    <small class="text-muted">${new Date().toLocaleString()}</small>
                    <p class="mb-0">${note}</p>
                </div>
            `);
        },
        error: function(xhr) {
            showNotification('Failed to add note', 'error');
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
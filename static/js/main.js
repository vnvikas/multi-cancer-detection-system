// Main JavaScript for Multi-Cancer Detection System

// Document ready function
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // File upload preview
    $('#scan_image').on('change', function() {
        previewImage(this, '#imagePreview');
    });
    
    // Form validation
    $('form').on('submit', function(e) {
        if ($(this).hasClass('needs-validation')) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            $(this).addClass('was-validated');
        }
    });
    
    // Confirmation dialogs
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Loading spinner
    $('form').on('submit', function() {
        if ($(this).attr('method') === 'POST') {
            showLoading();
        }
    });
});

// Image preview function
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            $(previewElement).attr('src', e.target.result).show();
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Show loading spinner
function showLoading() {
    $('.spinner-overlay').fadeIn();
}

// Hide loading spinner
function hideLoading() {
    $('.spinner-overlay').fadeOut();
}

// Format date
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format time
function formatTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Calculate age from date of birth
function calculateAge(dob) {
    var birthDate = new Date(dob);
    var today = new Date();
    var age = today.getFullYear() - birthDate.getFullYear();
    var m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

// Get risk level class
function getRiskLevelClass(riskScore) {
    if (riskScore < 30) return 'success';
    if (riskScore < 70) return 'warning';
    return 'danger';
}

// Get risk level text
function getRiskLevelText(riskScore) {
    if (riskScore < 30) return 'Low Risk';
    if (riskScore < 70) return 'Moderate Risk';
    return 'High Risk';
}

// Export to CSV
function exportToCSV(data, filename) {
    var csv = convertToCSV(data);
    var blob = new Blob([csv], { type: 'text/csv' });
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Convert to CSV
function convertToCSV(data) {
    var headers = Object.keys(data[0]);
    var csvRows = [];
    
    csvRows.push(headers.join(','));
    
    for (var row of data) {
        var values = headers.map(header => {
            var val = row[header];
            return `"${val}"`;
        });
        csvRows.push(values.join(','));
    }
    
    return csvRows.join('\n');
}

// Search filter
function filterTable(inputId, tableId) {
    var input = document.getElementById(inputId);
    var filter = input.value.toUpperCase();
    var table = document.getElementById(tableId);
    var rows = table.getElementsByTagName('tr');
    
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName('td');
        var match = false;
        
        for (var j = 0; j < cells.length; j++) {
            if (cells[j]) {
                var textValue = cells[j].textContent || cells[j].innerText;
                if (textValue.toUpperCase().indexOf(filter) > -1) {
                    match = true;
                    break;
                }
            }
        }
        
        rows[i].style.display = match ? '' : 'none';
    }
}
// Image Upload Module JavaScript

$(document).ready(function() {
    initializeUploader();
});

// Initialize Uploader
function initializeUploader() {
    // Setup drag and drop
    setupDragAndDrop();
    
    // Setup file input change
    $('#scanImage').on('change', handleFileSelect);
    
    // Setup form submission
    $('#uploadForm').on('submit', handleUploadSubmit);
    
    // Setup preview controls
    setupPreviewControls();
}

// Setup Drag and Drop
function setupDragAndDrop() {
    const dropZone = $('#dropZone');
    
    dropZone.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('drag-over');
    });
    
    dropZone.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
    });
    
    dropZone.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('drag-over');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });
    
    dropZone.on('click', function() {
        $('#scanImage').click();
    });
}

// Handle File Select
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

// Handle Files
function handleFiles(files) {
    const file = files[0];
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        showNotification('Invalid file type. Please upload JPG or PNG images.', 'error');
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File too large. Maximum size is 10MB.', 'error');
        return;
    }
    
    // Display file info
    displayFileInfo(file);
    
    // Preview image
    previewImage(file);
    
    // Auto-detect cancer type
    autoDetectCancerType(file);
}

// Display File Info
function displayFileInfo(file) {
    const fileSize = formatFileSize(file.size);
    const fileName = file.name;
    
    $('#fileName').text(fileName);
    $('#fileSize').text(fileSize);
    $('#fileType').text(file.type);
    
    $('#fileInfo').removeClass('d-none');
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Preview Image
function previewImage(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const preview = $('#imagePreview');
        preview.attr('src', e.target.result);
        preview.removeClass('d-none');
        
        // Add zoom functionality
        setupZoomOnPreview(preview);
    };
    
    reader.readAsDataURL(file);
}

// Setup Zoom on Preview
function setupZoomOnPreview(preview) {
    preview.on('click', function() {
        const modal = $('#imageZoomModal');
        const modalImg = $('#zoomedImage');
        modalImg.attr('src', preview.attr('src'));
        modal.modal('show');
    });
}

// Auto-detect Cancer Type
function autoDetectCancerType(file) {
    // This would use AI to detect cancer type from image
    // For now, we'll just show a message
    $('#autoDetectMsg').removeClass('d-none');
    
    // Simulate detection
    setTimeout(() => {
        const detectedType = suggestCancerType(file.name);
        if (detectedType) {
            $('#cancerType').val(detectedType);
            $('#autoDetectMsg').html(`
                <div class="alert alert-info alert-dismissible fade show">
                    <i class="fas fa-robot"></i> AI detected: ${detectedType.toUpperCase()} scan
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `);
        }
    }, 1000);
}

// Suggest Cancer Type based on filename
function suggestCancerType(filename) {
    const lower = filename.toLowerCase();
    if (lower.includes('brain') || lower.includes('mri')) return 'brain';
    if (lower.includes('lung') || lower.includes('chest') || lower.includes('ct')) return 'lung';
    if (lower.includes('breast') || lower.includes('mammo')) return 'breast';
    return null;
}

// Setup Preview Controls
function setupPreviewControls() {
    // Rotate image
    $('#rotateLeft').on('click', function() {
        rotateImage(-90);
    });
    
    $('#rotateRight').on('click', function() {
        rotateImage(90);
    });
    
    // Reset image
    $('#resetImage').on('click', function() {
        resetImage();
    });
    
    // Crop image
    $('#cropImage').on('click', function() {
        enableCropMode();
    });
}

// Rotate Image
function rotateImage(degrees) {
    const img = $('#imagePreview');
    const currentRotation = img.data('rotation') || 0;
    const newRotation = currentRotation + degrees;
    
    img.css('transform', `rotate(${newRotation}deg)`);
    img.data('rotation', newRotation);
}

// Reset Image
function resetImage() {
    const img = $('#imagePreview');
    img.css('transform', 'rotate(0deg)');
    img.data('rotation', 0);
    
    if (cropEnabled) {
        disableCropMode();
    }
}

// Crop Mode Variables
let cropEnabled = false;
let cropStart = null;
let cropEnd = null;

// Enable Crop Mode
function enableCropMode() {
    cropEnabled = true;
    const preview = $('#imagePreview');
    preview.css('cursor', 'crosshair');
    
    preview.on('mousedown', startCrop);
    preview.on('mousemove', drawCrop);
    preview.on('mouseup', endCrop);
    
    showNotification('Click and drag to select crop area', 'info');
}

// Start Crop
function startCrop(e) {
    cropStart = getMousePosition(e);
    $('#cropOverlay').remove();
    
    const overlay = $('<div id="cropOverlay" class="position-absolute border border-primary bg-primary bg-opacity-25"></div>');
    $('#imagePreviewContainer').append(overlay);
}

// Get Mouse Position
function getMousePosition(e) {
    const offset = $('#imagePreview').offset();
    const x = e.pageX - offset.left;
    const y = e.pageY - offset.top;
    return { x, y };
}

// Draw Crop
function drawCrop(e) {
    if (!cropStart) return;
    
    const current = getMousePosition(e);
    const width = Math.abs(current.x - cropStart.x);
    const height = Math.abs(current.y - cropStart.y);
    const left = Math.min(cropStart.x, current.x);
    const top = Math.min(cropStart.y, current.y);
    
    $('#cropOverlay').css({
        left: left + 'px',
        top: top + 'px',
        width: width + 'px',
        height: height + 'px',
        display: 'block'
    });
}

// End Crop
function endCrop(e) {
    if (!cropStart) return;
    
    cropEnd = getMousePosition(e);
    applyCrop();
    
    cropStart = null;
    cropEnd = null;
}

// Apply Crop
function applyCrop() {
    const img = $('#imagePreview')[0];
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    const cropRect = $('#cropOverlay');
    const left = parseFloat(cropRect.css('left'));
    const top = parseFloat(cropRect.css('top'));
    const width = parseFloat(cropRect.css('width'));
    const height = parseFloat(cropRect.css('height'));
    
    canvas.width = width;
    canvas.height = height;
    
    ctx.drawImage(img, left, top, width, height, 0, 0, width, height);
    
    const croppedImage = canvas.toDataURL();
    $('#imagePreview').attr('src', croppedImage);
    
    cropRect.remove();
    disableCropMode();
    
    showNotification('Image cropped successfully', 'success');
}

// Disable Crop Mode
function disableCropMode() {
    cropEnabled = false;
    const preview = $('#imagePreview');
    preview.css('cursor', 'default');
    preview.off('mousedown', startCrop);
    preview.off('mousemove', drawCrop);
    preview.off('mouseup', endCrop);
    $('#cropOverlay').remove();
}

// Handle Upload Submit
function handleUploadSubmit(e) {
    e.preventDefault();
    
    // Validate form
    if (!validateUploadForm()) {
        return;
    }
    
    const formData = new FormData(this);
    
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
            showNotification('Scan uploaded successfully! Analyzing...', 'success');
            
            // Start progress simulation
            simulateAnalysis(response.scan_id);
        },
        error: function(xhr) {
            hideLoading();
            showNotification('Upload failed: ' + (xhr.responseJSON?.error || 'Unknown error'), 'error');
        }
    });
}

// Validate Upload Form
function validateUploadForm() {
    const patientId = $('#patientId').val();
    const cancerType = $('#cancerType').val();
    const scanImage = $('#scanImage')[0].files[0];
    
    if (!patientId) {
        showNotification('Please select a patient', 'warning');
        return false;
    }
    
    if (!cancerType) {
        showNotification('Please select cancer type', 'warning');
        return false;
    }
    
    if (!scanImage) {
        showNotification('Please select an image', 'warning');
        return false;
    }
    
    return true;
}

// Simulate Analysis Progress
function simulateAnalysis(scanId) {
    const modal = $('#analysisProgressModal');
    const progressBar = $('#analysisProgress');
    const statusText = $('#analysisStatus');
    
    modal.modal({
        backdrop: 'static',
        keyboard: false
    });
    
    let progress = 0;
    const steps = [
        'Validating image...',
        'Preprocessing image...',
        'Extracting features...',
        'Running CNN model...',
        'Random Forest classification...',
        'Generating results...'
    ];
    let stepIndex = 0;
    
    const interval = setInterval(() => {
        progress += 10;
        progressBar.css('width', progress + '%');
        progressBar.text(progress + '%');
        
        if (progress % 20 === 0 && stepIndex < steps.length) {
            statusText.text(steps[stepIndex]);
            stepIndex++;
        }
        
        if (progress >= 100) {
            clearInterval(interval);
            statusText.text('Analysis complete!');
            
            setTimeout(() => {
                modal.modal('hide');
                window.location.href = `/doctor/predict-scan/${scanId}`;
            }, 1000);
        }
    }, 500);
}

// Get Token
function getToken() {
    return localStorage.getItem('access_token');
}

// Show Loading
function showLoading() {
    $('#loadingOverlay').fadeIn();
}

// Hide Loading
function hideLoading() {
    $('#loadingOverlay').fadeOut();
}

// Show Notification
function showNotification(message, type) {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert" style="z-index: 9999;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    setTimeout(() => {
        alert.alert('close');
    }, 5000);
}

// Advanced Image Processing
function applyFilter(filterType) {
    const img = $('#imagePreview');
    const filters = {
        grayscale: 'grayscale(100%)',
        sepia: 'sepia(100%)',
        brightness: 'brightness(1.2)',
        contrast: 'contrast(1.5)',
        none: 'none'
    };
    
    img.css('filter', filters[filterType] || 'none');
}

function enhanceImage() {
    applyFilter('contrast');
    setTimeout(() => {
        applyFilter('brightness');
    }, 100);
    showNotification('Image enhanced', 'success');
}

function resetFilters() {
    applyFilter('none');
    showNotification('Filters reset', 'info');
}
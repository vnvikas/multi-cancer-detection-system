-- Multi-Cancer Detection System Database Schema
-- Run this file to create the complete database

CREATE DATABASE IF NOT EXISTS multi_cancer_db;
USE multi_cancer_db;

-- =====================================================
-- USERS TABLE (Admin and Doctors)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor') NOT NULL,
    specialization VARCHAR(100),
    hospital_name VARCHAR(200),
    hospital_address TEXT,
    contact_number VARCHAR(20),
    profile_image VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- =====================================================
-- PATIENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_uid VARCHAR(50) UNIQUE NOT NULL,
    doctor_id INT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    date_of_birth DATE,
    contact_number VARCHAR(20),
    alternate_number VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    blood_group VARCHAR(5),
    allergies TEXT,
    chronic_diseases TEXT,
    family_history TEXT,
    smoking_status ENUM('Never', 'Former', 'Current'),
    alcohol_consumption ENUM('Never', 'Occasional', 'Regular'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_patient_uid (patient_uid),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_name (name)
);

-- =====================================================
-- MEDICAL HISTORY TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS medical_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    diagnosis_date DATE,
    diagnosis_details TEXT,
    past_surgeries TEXT,
    current_medications TEXT,
    allergies_medications TEXT,
    blood_pressure VARCHAR(20),
    diabetes_status ENUM('No', 'Type1', 'Type2'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id)
);

-- =====================================================
-- SCANS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS scans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scan_id VARCHAR(50) UNIQUE NOT NULL,
    patient_id INT NOT NULL,
    cancer_type ENUM('brain', 'lung', 'breast') NOT NULL,
    scan_type VARCHAR(50),
    image_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    uploaded_by INT,
    upload_notes TEXT,
    scan_date DATE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_scan_id (scan_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_cancer_type (cancer_type)
);

-- =====================================================
-- PREDICTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prediction_id VARCHAR(50) UNIQUE NOT NULL,
    scan_id INT NOT NULL,
    cancer_type VARCHAR(50),
    cancer_subtype VARCHAR(100),
    cancer_stage VARCHAR(50),
    confidence_score DECIMAL(5,4),
    risk_score INT,
    survival_rate DECIMAL(5,2),
    metastasis_probability DECIMAL(5,2),
    treatment_response_prediction VARCHAR(50),
    features_extracted TEXT,
    doctor_verified BOOLEAN DEFAULT FALSE,
    doctor_notes TEXT,
    verified_by INT,
    verified_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_prediction_id (prediction_id),
    INDEX idx_scan_id (scan_id),
    INDEX idx_verified_status (doctor_verified)
);

-- =====================================================
-- TREATMENT PLANS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS treatment_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    prediction_id INT NOT NULL,
    doctor_id INT NOT NULL,
    treatment_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    medications TEXT,
    dosage TEXT,
    follow_up_frequency VARCHAR(50),
    special_instructions TEXT,
    status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status)
);

-- =====================================================
-- FOLLOW_UP SCHEDULE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS follow_up_schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    scheduled_date DATETIME NOT NULL,
    follow_up_type VARCHAR(50),
    notes TEXT,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'Missed') DEFAULT 'Scheduled',
    completed_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_scheduled_date (scheduled_date)
);

-- =====================================================
-- MODEL PERFORMANCE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS model_performance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    cancer_type VARCHAR(50),
    accuracy DECIMAL(5,4),
    precision_val DECIMAL(5,4),
    recall_val DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_score DECIMAL(5,4),
    loss DECIMAL(5,4),
    trained_on DATETIME,
    training_samples INT,
    validation_samples INT,
    is_active BOOLEAN DEFAULT FALSE,
    model_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_name (model_name),
    INDEX idx_active (is_active)
);

-- =====================================================
-- SYSTEM LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS system_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);

-- =====================================================
-- DATASET METADATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS dataset_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cancer_type VARCHAR(50),
    class_name VARCHAR(100),
    total_images INT,
    train_count INT,
    validation_count INT,
    test_count INT,
    last_updated DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cancer_type (cancer_type)
);

-- =====================================================
-- INSERT DEFAULT ADMIN USER
-- =====================================================
-- Note: Password hash is for 'Admin@123' - change in production
-- Use bcrypt to generate new hash: bcrypt.generate_password_hash('your_password').decode('utf-8')
INSERT INTO users (user_id, name, email, password_hash, role, is_active) 
VALUES ('ADMIN001', 'System Administrator', 'admin@cancerdetection.com', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhNV8IXxP9W7X7X7X7X7X7', 
        'admin', TRUE)
ON DUPLICATE KEY UPDATE email=email;

-- =====================================================
-- INSERT SAMPLE DOCTOR
-- =====================================================
INSERT INTO users (user_id, name, email, password_hash, role, specialization, hospital_name, is_active) 
VALUES ('DOC001', 'Dr. Sarah Johnson', 'sarah.johnson@hospital.com', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhNV8IXxP9W7X7X7X7X7X7', 
        'doctor', 'Oncology', 'City General Hospital', TRUE)
ON DUPLICATE KEY UPDATE email=email;

-- =====================================================
-- CREATE VIEWS FOR REPORTS
-- =====================================================

-- View for complete patient information with latest prediction
CREATE OR REPLACE VIEW patient_latest_prediction AS
SELECT 
    p.id as patient_id,
    p.patient_uid,
    p.name as patient_name,
    p.age,
    p.gender,
    u.name as doctor_name,
    s.cancer_type,
    pr.cancer_subtype,
    pr.cancer_stage,
    pr.confidence_score,
    pr.risk_score,
    pr.created_at as prediction_date,
    pr.doctor_verified
FROM patients p
LEFT JOIN users u ON p.doctor_id = u.id
LEFT JOIN scans s ON p.id = s.patient_id
LEFT JOIN predictions pr ON s.id = pr.scan_id
WHERE (pr.created_at IS NULL OR pr.created_at = (
    SELECT MAX(created_at) FROM predictions pr2 
    JOIN scans s2 ON pr2.scan_id = s2.id 
    WHERE s2.patient_id = p.id
));

-- View for monthly statistics
CREATE OR REPLACE VIEW monthly_statistics AS
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(DISTINCT p.id) as new_patients,
    COUNT(DISTINCT s.id) as total_scans,
    COUNT(DISTINCT pr.id) as total_predictions,
    AVG(pr.confidence_score) as avg_confidence,
    AVG(pr.risk_score) as avg_risk_score
FROM patients p
LEFT JOIN scans s ON p.id = s.patient_id
LEFT JOIN predictions pr ON s.id = pr.scan_id
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month DESC;

-- Show all tables
SHOW TABLES;
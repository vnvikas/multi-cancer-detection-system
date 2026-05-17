from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.database.models import db, User, Patient, Scan, Prediction, ModelPerformance, SystemLog
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import text
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_doctors = User.query.filter_by(role='doctor', is_active=True).count()
    total_patients = Patient.query.count()
    total_scans = Scan.query.count()
    total_predictions = Prediction.query.count()
    
    # Recent activity
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    recent_scans = Scan.query.order_by(Scan.uploaded_at.desc()).limit(5).all()
    
    # Model performance
    active_models = ModelPerformance.query.filter_by(is_active=True).all()
    
    # Statistics for charts - FIXED QUERIES
    # Monthly patient registrations
    monthly_patients = db.session.query(
        db.func.date_format(Patient.created_at, '%Y-%m').label('month'),
        db.func.count(Patient.id).label('count')
    ).group_by('month').order_by(text('month desc')).limit(6).all()
    
    # Predictions by cancer type
    predictions_by_type = db.session.query(
        Prediction.cancer_type,
        db.func.count(Prediction.id).label('count')
    ).group_by(Prediction.cancer_type).all()
    
    # Average confidence score
    avg_confidence = db.session.query(db.func.avg(Prediction.confidence_score)).scalar() or 0
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_scans': total_scans,
        'total_predictions': total_predictions,
        'avg_confidence': float(avg_confidence) * 100,
        'recent_patients': recent_patients,
        'recent_scans': recent_scans,
        'active_models': active_models,
        'monthly_patients': json.dumps([{'month': m[0], 'count': m[1]} for m in monthly_patients]) if monthly_patients else '[]',
        'predictions_by_type': json.dumps([{'type': p[0] or 'Unknown', 'count': p[1]} for p in predictions_by_type]) if predictions_by_type else '[]'
    }
    
    return render_template('admin/dashboard.html', **context)

@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    doctors = User.query.filter_by(role='doctor').order_by(User.created_at.desc()).all()
    return render_template('admin/doctors.html', doctors=doctors)

@admin_bp.route('/add-doctor', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        specialization = request.form.get('specialization')
        hospital_name = request.form.get('hospital_name')
        contact_number = request.form.get('contact_number')
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('admin/add_doctor.html')
        
        # Create doctor
        doctor = User(
            user_id=f"DOC{User.query.count() + 1:04d}",
            name=name,
            email=email,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role='doctor',
            specialization=specialization,
            hospital_name=hospital_name,
            contact_number=contact_number,
            is_active=True
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        flash(f'Doctor {name} added successfully', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/add_doctor.html')

@admin_bp.route('/edit-doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    
    if doctor.role != 'doctor':
        flash('Invalid user type', 'danger')
        return redirect(url_for('admin.doctors'))
    
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.specialization = request.form.get('specialization')
        doctor.hospital_name = request.form.get('hospital_name')
        doctor.contact_number = request.form.get('contact_number')
        doctor.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Doctor information updated successfully', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/edit_doctor.html', doctor=doctor)

@admin_bp.route('/delete-doctor/<int:doctor_id>')
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    
    if doctor.role != 'doctor':
        flash('Invalid user type', 'danger')
        return redirect(url_for('admin.doctors'))
    
    # Check if doctor has patients
    if doctor.patients:
        flash(f'Cannot delete doctor {doctor.name} because they have assigned patients. Reassign patients first.', 'danger')
        return redirect(url_for('admin.doctors'))
    
    db.session.delete(doctor)
    db.session.commit()
    
    flash(f'Doctor {doctor.name} deleted successfully', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('admin/patients.html', patients=patients)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    return render_template('admin/reports.html', predictions=predictions)

@admin_bp.route('/model-stats')
@login_required
@admin_required
def model_stats():
    models = ModelPerformance.query.order_by(ModelPerformance.created_at.desc()).all()
    
    latest_brain = ModelPerformance.query.filter_by(cancer_type='brain', is_active=True).first()
    latest_lung = ModelPerformance.query.filter_by(cancer_type='lung', is_active=True).first()
    latest_breast = ModelPerformance.query.filter_by(cancer_type='breast', is_active=True).first()
    
    return render_template('admin/model_stats.html', 
                          models=models,
                          latest_brain=latest_brain,
                          latest_lung=latest_lung,
                          latest_breast=latest_breast)

@admin_bp.route('/model-retrain', methods=['GET', 'POST'])
@login_required
@admin_required
def model_retrain():
    if request.method == 'POST':
        cancer_type = request.form.get('cancer_type')
        
        flash(f'Model retraining for {cancer_type} cancer has been triggered. This may take some time.', 'info')
        
        # Log the retraining action
        log = SystemLog(
            user_id=current_user.id,
            action='MODEL_RETRAIN',
            entity_type='model',
            details=f'Retraining triggered for {cancer_type} cancer model',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return redirect(url_for('admin.model_stats'))
    
    return render_template('admin/model_retrain.html')

@admin_bp.route('/system-logs')
@login_required
@admin_required
def system_logs():
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/system_logs.html', logs=logs)

@admin_bp.route('/dataset-manager')
@login_required
@admin_required
def dataset_manager():
    from backend.database.models import DatasetMetadata
    datasets = DatasetMetadata.query.all()
    return render_template('admin/dataset_manager.html', datasets=datasets)
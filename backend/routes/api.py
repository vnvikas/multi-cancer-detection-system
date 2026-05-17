from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from backend.database.models import db, User, Patient, Scan, Prediction, ModelPerformance, SystemLog
from backend.services.prediction_service import PredictionService
from backend.services.patient_service import PatientService
from functools import wraps
from datetime import datetime, timedelta
import os

# Try to import jwt, handle if not installed
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("Warning: PyJWT not installed. Run: pip install PyJWT")

api_bp = Blueprint('api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not JWT_AVAILABLE:
            return jsonify({'error': 'JWT authentication not available. Please install PyJWT'}), 500
        
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except Exception as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# Authentication Endpoints
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API Login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not JWT_AVAILABLE:
                return jsonify({
                    'success': True,
                    'message': 'Login successful (JWT disabled)',
                    'role': user.role,
                    'user': user.to_dict() if hasattr(user, 'to_dict') else {'id': user.id, 'email': user.email}
                })
            
            token = jwt.encode({
                'user_id': user.id,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, current_app.config['JWT_SECRET_KEY'])
            
            return jsonify({
                'success': True,
                'token': token,
                'role': user.role,
                'user': user.to_dict() if hasattr(user, 'to_dict') else {'id': user.id, 'email': user.email}
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health Check Endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'jwt_available': JWT_AVAILABLE,
        'database': 'connected' if check_database() else 'disconnected'
    })

def check_database():
    """Check database connection"""
    try:
        db.session.execute('SELECT 1')
        return True
    except:
        return False

# Admin Endpoints
@api_bp.route('/admin/dashboard', methods=['GET'])
@token_required
def api_admin_dashboard(current_user_id):
    """Get admin dashboard statistics"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        stats = {
            'total_doctors': User.query.filter_by(role='doctor').count(),
            'total_patients': Patient.query.count(),
            'total_scans': Scan.query.count(),
            'total_predictions': Prediction.query.count(),
            'avg_confidence': float(db.session.query(db.func.avg(Prediction.confidence_score)).scalar() or 0)
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/doctors', methods=['GET'])
@token_required
def api_get_doctors(current_user_id):
    """Get all doctors"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        doctors = User.query.filter_by(role='doctor').all()
        return jsonify([{
            'id': d.id,
            'user_id': d.user_id,
            'name': d.name,
            'email': d.email,
            'specialization': d.specialization,
            'hospital_name': d.hospital_name,
            'contact_number': d.contact_number,
            'is_active': d.is_active
        } for d in doctors])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/admin/doctors', methods=['POST'])
@token_required
def api_add_doctor(current_user_id):
    """Add a new doctor"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        doctor = User(
            user_id=f"DOC{User.query.count() + 1:04d}",
            name=data['name'],
            email=data['email'],
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            role='doctor',
            specialization=data.get('specialization'),
            hospital_name=data.get('hospital_name'),
            contact_number=data.get('contact_number'),
            is_active=True
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'id': doctor.id,
            'user_id': doctor.user_id,
            'name': doctor.name,
            'email': doctor.email,
            'message': 'Doctor added successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Doctor Endpoints
@api_bp.route('/doctor/dashboard', methods=['GET'])
@token_required
def api_doctor_dashboard(current_user_id):
    """Get doctor dashboard statistics"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'doctor':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get doctor's patients
        patients = Patient.query.filter_by(doctor_id=user.id).all()
        patient_ids = [p.id for p in patients]
        
        # Count scans
        scans = Scan.query.filter(Scan.patient_id.in_(patient_ids)).count() if patient_ids else 0
        
        # Count predictions
        predictions = Prediction.query.join(Scan).filter(Scan.patient_id.in_(patient_ids)).count() if patient_ids else 0
        
        # Pending verifications
        pending = Prediction.query.join(Scan).filter(
            Scan.patient_id.in_(patient_ids),
            Prediction.doctor_verified == False
        ).count() if patient_ids else 0
        
        stats = {
            'total_patients': len(patients),
            'total_scans': scans,
            'total_predictions': predictions,
            'pending_verifications': pending,
            'verified_predictions': predictions - pending
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/doctor/patients', methods=['GET'])
@token_required
def api_get_patients(current_user_id):
    """Get doctor's patients"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'doctor':
            return jsonify({'error': 'Access denied'}), 403
        
        patients = Patient.query.filter_by(doctor_id=user.id).all()
        return jsonify([{
            'id': p.id,
            'patient_uid': p.patient_uid,
            'name': p.name,
            'age': p.age,
            'gender': p.gender,
            'contact_number': p.contact_number,
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in patients])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/doctor/patients', methods=['POST'])
@token_required
def api_add_patient(current_user_id):
    """Add a new patient"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'doctor':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        patient = Patient(
            patient_uid=f"PAT{Patient.query.count() + 1:06d}",
            doctor_id=user.id,
            name=data['name'],
            age=data.get('age'),
            gender=data.get('gender'),
            contact_number=data.get('contact_number'),
            email=data.get('email'),
            address=data.get('address')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'id': patient.id,
            'patient_uid': patient.patient_uid,
            'name': patient.name,
            'message': 'Patient added successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Prediction Endpoints
@api_bp.route('/predict/upload', methods=['POST'])
@token_required
def api_upload_scan(current_user_id):
    """Upload a scan for prediction"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'doctor':
            return jsonify({'error': 'Access denied'}), 403
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file'}), 400
        
        file = request.files['image']
        patient_id = request.form.get('patient_id')
        cancer_type = request.form.get('cancer_type')
        
        if not patient_id or not cancer_type:
            return jsonify({'error': 'Patient ID and cancer type required'}), 400
        
        patient = Patient.query.filter_by(id=patient_id, doctor_id=user.id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Save file
        from werkzeug.utils import secure_filename
        filename = secure_filename(f"{patient.patient_uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        
        cancer_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{cancer_type}_scans")
        os.makedirs(cancer_folder, exist_ok=True)
        
        filepath = os.path.join(cancer_folder, filename)
        file.save(filepath)
        
        # Create scan record
        scan = Scan(
            scan_id=f"SCN{Scan.query.count() + 1:08d}",
            patient_id=patient.id,
            cancer_type=cancer_type,
            image_path=filepath,
            uploaded_by=user.id
        )
        
        db.session.add(scan)
        db.session.commit()
        
        return jsonify({
            'scan_id': scan.id,
            'scan_uid': scan.scan_id,
            'message': 'Scan uploaded successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predict/detect', methods=['POST'])
@token_required
def api_detect_cancer(current_user_id):
    """Run cancer detection on a scan"""
    try:
        user = User.query.get(current_user_id)
        if user.role != 'doctor':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        scan_id = data.get('scan_id')
        
        if not scan_id:
            return jsonify({'error': 'Scan ID required'}), 400
        
        scan = Scan.query.get(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        patient = Patient.query.get(scan.patient_id)
        if patient.doctor_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Mock prediction (replace with actual model prediction)
        import random
        
        cancer_types = {
            'brain': ['Glioma', 'Meningioma', 'Pituitary'],
            'lung': ['Adenocarcinoma', 'Squamous Cell', 'Large Cell'],
            'breast': ['Ductal Carcinoma', 'Lobular Carcinoma', 'Medullary Carcinoma']
        }
        
        stages = ['Stage I', 'Stage II', 'Stage III', 'Stage IV']
        
        prediction = Prediction(
            prediction_id=f"PRD{Prediction.query.count() + 1:08d}",
            scan_id=scan.id,
            cancer_type=scan.cancer_type.title(),
            cancer_subtype=random.choice(cancer_types.get(scan.cancer_type, ['Unknown'])),
            cancer_stage=random.choice(stages),
            confidence_score=round(random.uniform(0.75, 0.98), 4),
            risk_score=random.randint(20, 90),
            survival_rate=round(random.uniform(40, 95), 2),
            metastasis_probability=round(random.uniform(5, 60), 2),
            doctor_verified=False
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'prediction_id': prediction.id,
            'prediction_uid': prediction.prediction_id,
            'cancer_type': prediction.cancer_type,
            'cancer_subtype': prediction.cancer_subtype,
            'cancer_stage': prediction.cancer_stage,
            'confidence_score': float(prediction.confidence_score),
            'risk_score': prediction.risk_score,
            'survival_rate': float(prediction.survival_rate),
            'metastasis_probability': float(prediction.metastasis_probability),
            'message': 'Prediction completed'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predict/result/<int:prediction_id>', methods=['GET'])
@token_required
def api_get_prediction(current_user_id, prediction_id):
    """Get prediction result"""
    try:
        user = User.query.get(current_user_id)
        
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        scan = Scan.query.get(prediction.scan_id)
        patient = Patient.query.get(scan.patient_id)
        
        if user.role == 'doctor' and patient.doctor_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'id': prediction.prediction_id,
            'cancer_type': prediction.cancer_type,
            'cancer_subtype': prediction.cancer_subtype,
            'cancer_stage': prediction.cancer_stage,
            'confidence_score': float(prediction.confidence_score) if prediction.confidence_score else 0,
            'risk_score': prediction.risk_score,
            'survival_rate': float(prediction.survival_rate) if prediction.survival_rate else 0,
            'metastasis_probability': float(prediction.metastasis_probability) if prediction.metastasis_probability else 0,
            'doctor_verified': prediction.doctor_verified,
            'created_at': prediction.created_at.isoformat() if prediction.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
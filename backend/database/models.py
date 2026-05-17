from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

# Create db instance without initializing with app yet
db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4()).replace('-', '')[:8].upper()

@property
def created_at_str(self):
    if self.created_at:
        return self.created_at.strftime('%Y-%m-%d')
    return 'N/A'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'doctor'), nullable=False)
    specialization = db.Column(db.String(100))
    hospital_name = db.Column(db.String(200))
    hospital_address = db.Column(db.Text)
    contact_number = db.Column(db.String(20))
    profile_image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patients = db.relationship('Patient', backref='doctor', lazy=True, foreign_keys='Patient.doctor_id')
    uploaded_scans = db.relationship('Scan', backref='uploader', lazy=True, foreign_keys='Scan.uploaded_by')
    verified_predictions = db.relationship('Prediction', backref='verifier', lazy=True, foreign_keys='Prediction.verified_by')
    
    def get_id(self):
        return str(self.id)
    
    def to_dict(self):
        return {
            'id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'specialization': self.specialization,
            'hospital_name': self.hospital_name,
            'contact_number': self.contact_number,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_uid = db.Column(db.String(50), unique=True, nullable=False, default=generate_uuid)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'))
    date_of_birth = db.Column(db.Date)
    contact_number = db.Column(db.String(20))
    alternate_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    family_history = db.Column(db.Text)
    smoking_status = db.Column(db.Enum('Never', 'Former', 'Current'))
    alcohol_consumption = db.Column(db.Enum('Never', 'Occasional', 'Regular'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scans = db.relationship('Scan', backref='patient', lazy=True, cascade='all, delete-orphan')
    medical_histories = db.relationship('MedicalHistory', backref='patient', lazy=True, cascade='all, delete-orphan')
    treatment_plans = db.relationship('TreatmentPlan', backref='patient', lazy=True, cascade='all, delete-orphan')
    follow_ups = db.relationship('FollowUpSchedule', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.patient_uid,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact_number': self.contact_number,
            'email': self.email,
            'smoking_status': self.smoking_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MedicalHistory(db.Model):
    __tablename__ = 'medical_history'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    diagnosis_date = db.Column(db.Date)
    diagnosis_details = db.Column(db.Text)
    past_surgeries = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    allergies_medications = db.Column(db.Text)
    blood_pressure = db.Column(db.String(20))
    diabetes_status = db.Column(db.Enum('No', 'Type1', 'Type2'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(50), unique=True, nullable=False, default=generate_uuid)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    cancer_type = db.Column(db.Enum('brain', 'lung', 'breast'), nullable=False)
    scan_type = db.Column(db.String(50))
    image_path = db.Column(db.String(500), nullable=False)
    thumbnail_path = db.Column(db.String(500))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    upload_notes = db.Column(db.Text)
    scan_date = db.Column(db.Date)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='scan', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.scan_id,
            'cancer_type': self.cancer_type,
            'image_path': self.image_path,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.String(50), unique=True, nullable=False, default=generate_uuid)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    cancer_type = db.Column(db.String(50))
    cancer_subtype = db.Column(db.String(100))
    cancer_stage = db.Column(db.String(50))
    confidence_score = db.Column(db.Numeric(5,4))
    risk_score = db.Column(db.Integer)
    survival_rate = db.Column(db.Numeric(5,2))
    metastasis_probability = db.Column(db.Numeric(5,2))
    treatment_response_prediction = db.Column(db.String(50))
    features_extracted = db.Column(db.Text)
    doctor_verified = db.Column(db.Boolean, default=False)
    doctor_notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.prediction_id,
            'cancer_type': self.cancer_type,
            'cancer_subtype': self.cancer_subtype,
            'cancer_stage': self.cancer_stage,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'risk_score': self.risk_score,
            'survival_rate': float(self.survival_rate) if self.survival_rate else None,
            'doctor_verified': self.doctor_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TreatmentPlan(db.Model):
    __tablename__ = 'treatment_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    treatment_type = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    medications = db.Column(db.Text)
    dosage = db.Column(db.Text)
    follow_up_frequency = db.Column(db.String(50))
    special_instructions = db.Column(db.Text)
    status = db.Column(db.Enum('Active', 'Completed', 'Cancelled'), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FollowUpSchedule(db.Model):
    __tablename__ = 'follow_up_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    follow_up_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    status = db.Column(db.Enum('Scheduled', 'Completed', 'Cancelled', 'Missed'), default='Scheduled')
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModelPerformance(db.Model):
    __tablename__ = 'model_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50), nullable=False)
    model_version = db.Column(db.String(50), nullable=False)
    cancer_type = db.Column(db.String(50))
    accuracy = db.Column(db.Numeric(5,4))
    precision_val = db.Column(db.Numeric(5,4))
    recall_val = db.Column(db.Numeric(5,4))
    f1_score = db.Column(db.Numeric(5,4))
    auc_score = db.Column(db.Numeric(5,4))
    loss = db.Column(db.Numeric(5,4))
    trained_on = db.Column(db.DateTime)
    training_samples = db.Column(db.Integer)
    validation_samples = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=False)
    model_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DatasetMetadata(db.Model):
    __tablename__ = 'dataset_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    cancer_type = db.Column(db.String(50))
    class_name = db.Column(db.String(100))
    total_images = db.Column(db.Integer)
    train_count = db.Column(db.Integer)
    validation_count = db.Column(db.Integer)
    test_count = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
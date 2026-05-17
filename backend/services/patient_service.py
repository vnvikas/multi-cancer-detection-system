from backend.database.models import db, Patient, MedicalHistory, SystemLog
from datetime import datetime
import uuid

class PatientService:
    
    def create_patient(self, patient_data, doctor_id):
        """Create a new patient"""
        try:
            patient = Patient(
                doctor_id=doctor_id,
                name=patient_data.get('name'),
                age=patient_data.get('age'),
                gender=patient_data.get('gender'),
                date_of_birth=patient_data.get('date_of_birth'),
                contact_number=patient_data.get('contact_number'),
                alternate_number=patient_data.get('alternate_number'),
                email=patient_data.get('email'),
                address=patient_data.get('address'),
                blood_group=patient_data.get('blood_group'),
                allergies=patient_data.get('allergies'),
                chronic_diseases=patient_data.get('chronic_diseases'),
                family_history=patient_data.get('family_history'),
                smoking_status=patient_data.get('smoking_status'),
                alcohol_consumption=patient_data.get('alcohol_consumption')
            )
            
            db.session.add(patient)
            db.session.flush()
            
            # Add medical history if provided
            if patient_data.get('diagnosis_details'):
                medical_history = MedicalHistory(
                    patient_id=patient.id,
                    diagnosis_details=patient_data.get('diagnosis_details'),
                    past_surgeries=patient_data.get('past_surgeries'),
                    current_medications=patient_data.get('current_medications'),
                    allergies_medications=patient_data.get('allergies_medications')
                )
                db.session.add(medical_history)
            
            db.session.commit()
            return patient
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating patient: {e}")
            return None
    
    def update_patient(self, patient_id, patient_data):
        """Update existing patient"""
        try:
            patient = Patient.query.get(patient_id)
            if not patient:
                return None
            
            for key, value in patient_data.items():
                if hasattr(patient, key) and value is not None:
                    setattr(patient, key, value)
            
            db.session.commit()
            return patient
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating patient: {e}")
            return None
    
    def get_patient_with_details(self, patient_id):
        """Get patient with all related data"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return None
        
        return {
            'patient': patient,
            'scans': patient.scans,
            'predictions': [p for scan in patient.scans for p in scan.predictions],
            'medical_history': patient.medical_histories,
            'treatment_plans': patient.treatment_plans
        }
    
    def search_patients(self, doctor_id, search_term):
        """Search patients by name or ID"""
        query = Patient.query.filter_by(doctor_id=doctor_id)
        
        if search_term:
            query = query.filter(
                db.or_(
                    Patient.name.contains(search_term),
                    Patient.patient_uid.contains(search_term),
                    Patient.contact_number.contains(search_term)
                )
            )
        
        return query.order_by(Patient.created_at.desc()).all()
    
    def get_patient_statistics(self, patient_id):
        """Get statistics for a patient"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return None
        
        predictions = [p for scan in patient.scans for p in scan.predictions]
        
        stats = {
            'total_scans': len(patient.scans),
            'total_predictions': len(predictions),
            'verified_predictions': sum(1 for p in predictions if p.doctor_verified),
            'avg_confidence': sum(float(p.confidence_score or 0) for p in predictions) / len(predictions) if predictions else 0,
            'latest_prediction': predictions[0].to_dict() if predictions else None
        }
        
        return stats
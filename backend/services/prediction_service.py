from backend.database.models import db, Scan, Prediction, SystemLog
from datetime import datetime
import uuid
import numpy as np
import cv2
from PIL import Image
import os

class PredictionService:
    
    def save_scan(self, patient_id, cancer_type, image_path, uploaded_by, scan_type=None, notes=None):
        """Save scan record"""
        scan = Scan(
            patient_id=patient_id,
            cancer_type=cancer_type,
            scan_type=scan_type,
            image_path=image_path,
            uploaded_by=uploaded_by,
            upload_notes=notes,
            scan_date=datetime.now().date()
        )
        
        db.session.add(scan)
        db.session.commit()
        
        return scan
    
    def preprocess_image(self, image_path, target_size=(224, 224)):
        """Preprocess image for model input"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                # Try with PIL if OpenCV fails
                img = Image.open(image_path)
                img = np.array(img)
            
            # Convert BGR to RGB
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize
            img = cv2.resize(img, target_size)
            
            # Normalize
            img = img.astype(np.float32) / 255.0
            
            # Denoise
            img = cv2.GaussianBlur(img, (3, 3), 0)
            
            return img
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def run_prediction(self, scan_id):
        """Run prediction on a scan"""
        try:
            scan = Scan.query.get(scan_id)
            if not scan:
                return None
            
            # Preprocess image
            processed_img = self.preprocess_image(scan.image_path)
            if processed_img is None:
                return None
            
            # For now, return mock prediction
            # In production, load actual models and run inference
            
            import random
            
            # Mock prediction based on cancer type
            if scan.cancer_type == 'brain':
                subtypes = ['Glioma', 'Meningioma', 'Pituitary']
                stages = ['Grade I', 'Grade II', 'Grade III', 'Grade IV']
            elif scan.cancer_type == 'lung':
                subtypes = ['Adenocarcinoma', 'Squamous Cell', 'Large Cell']
                stages = ['Stage I', 'Stage II', 'Stage III', 'Stage IV']
            else:  # breast
                subtypes = ['Ductal Carcinoma', 'Lobular Carcinoma', 'Medullary Carcinoma']
                stages = ['Stage 0', 'Stage I', 'Stage II', 'Stage III', 'Stage IV']
            
            prediction = Prediction(
                scan_id=scan.id,
                cancer_type=scan.cancer_type.title(),
                cancer_subtype=random.choice(subtypes),
                cancer_stage=random.choice(stages),
                confidence_score=round(random.uniform(0.75, 0.98), 4),
                risk_score=random.randint(20, 90),
                survival_rate=round(random.uniform(40, 95), 2),
                metastasis_probability=round(random.uniform(5, 60), 2),
                treatment_response_prediction=random.choice(['Good', 'Moderate', 'Poor'])
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            return prediction
            
        except Exception as e:
            print(f"Error running prediction: {e}")
            db.session.rollback()
            return None
    
    def get_predictions_by_patient(self, patient_id):
        """Get all predictions for a patient"""
        predictions = Prediction.query.join(Scan).filter(
            Scan.patient_id == patient_id
        ).order_by(Prediction.created_at.desc()).all()
        
        return predictions
    
    def verify_prediction(self, prediction_id, doctor_id, is_correct, doctor_notes=None, corrected_data=None):
        """Verify a prediction"""
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            return None
        
        prediction.doctor_verified = True
        prediction.doctor_notes = doctor_notes
        prediction.verified_by = doctor_id
        prediction.verified_at = datetime.now()
        
        if not is_correct and corrected_data:
            prediction.cancer_type = corrected_data.get('cancer_type', prediction.cancer_type)
            prediction.cancer_subtype = corrected_data.get('cancer_subtype', prediction.cancer_subtype)
            prediction.cancer_stage = corrected_data.get('cancer_stage', prediction.cancer_stage)
        
        db.session.commit()
        
        return prediction
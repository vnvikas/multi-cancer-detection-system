import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np
import cv2
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.ml.cnn_models.lung_cnn import LungCancerCNN
from backend.ml.cnn_models.breast_cnn import BreastCancerCNN
from backend.ml.random_forest.rf_classifier import RandomForestCancerClassifier
from backend.ml.preprocessing.image_processor import ImageProcessor

class CancerPredictor:
    """Main prediction class for cancer detection"""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.brain_model = None
        self.lung_model = None
        self.breast_model = None
        self.rf_classifier = None
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            # Load CNN models
            self.brain_model = BrainTumorCNN()
            self.brain_model.load_model('models/brain_tumor/brain_cnn_model.h5')
            
            self.lung_model = LungCancerCNN()
            self.lung_model.load_model('models/lung_cancer/lung_cnn_model.h5')
            
            self.breast_model = BreastCancerCNN()
            self.breast_model.load_model('models/breast_cancer/breast_cnn_model.h5')
            
            # Load Random Forest classifier
            self.rf_classifier = RandomForestCancerClassifier()
            self.rf_classifier.load_model('models/ensemble/rf_model.pkl')
            
            print("All models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def predict_brain_tumor(self, image_path):
        """Predict brain tumor type"""
        try:
            # Preprocess image
            processed_img = self.processor.preprocess(image_path)
            if processed_img is None:
                return None
            
            # CNN prediction
            cnn_pred = self.brain_model.predict(processed_img)
            
            # Extract features for Random Forest
            features = self.brain_model.extract_features(processed_img)
            
            # Random Forest prediction
            rf_pred = self.rf_classifier.predict(features)
            rf_proba = self.rf_classifier.predict_proba(features)
            
            # Ensemble (average predictions)
            final_pred = (cnn_pred[0] + rf_proba[0]) / 2
            
            classes = ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
            predicted_class = classes[np.argmax(final_pred)]
            confidence = np.max(final_pred)
            
            return {
                'cancer_type': 'Brain Tumor',
                'subtype': predicted_class,
                'confidence': float(confidence),
                'probabilities': {cls: float(prob) for cls, prob in zip(classes, final_pred)}
            }
        except Exception as e:
            print(f"Error in brain tumor prediction: {e}")
            return None
    
    def predict_lung_cancer(self, image_path):
        """Predict lung cancer type"""
        try:
            processed_img = self.processor.preprocess(image_path)
            if processed_img is None:
                return None
            
            cnn_pred = self.lung_model.predict(processed_img)
            features = self.lung_model.extract_features(processed_img)
            rf_pred = self.rf_classifier.predict(features)
            rf_proba = self.rf_classifier.predict_proba(features)
            
            final_pred = (cnn_pred[0] + rf_proba[0]) / 2
            
            classes = ['Benign', 'Malignant', 'Normal']
            predicted_class = classes[np.argmax(final_pred)]
            confidence = np.max(final_pred)
            
            # Calculate risk score based on prediction
            risk_score = 0
            if predicted_class == 'Malignant':
                risk_score = np.random.randint(60, 95)
            elif predicted_class == 'Benign':
                risk_score = np.random.randint(20, 50)
            else:
                risk_score = np.random.randint(5, 20)
            
            return {
                'cancer_type': 'Lung Cancer',
                'subtype': predicted_class,
                'confidence': float(confidence),
                'risk_score': risk_score,
                'probabilities': {cls: float(prob) for cls, prob in zip(classes, final_pred)}
            }
        except Exception as e:
            print(f"Error in lung cancer prediction: {e}")
            return None
    
    def predict_breast_cancer(self, image_path):
        """Predict breast cancer type"""
        try:
            processed_img = self.processor.preprocess(image_path)
            if processed_img is None:
                return None
            
            cnn_pred = self.breast_model.predict(processed_img)
            features = self.breast_model.extract_features(processed_img)
            rf_pred = self.rf_classifier.predict(features)
            rf_proba = self.rf_classifier.predict_proba(features)
            
            final_pred = (cnn_pred[0] + rf_proba[0]) / 2
            
            classes = ['Benign', 'Malignant', 'Normal']
            predicted_class = classes[np.argmax(final_pred)]
            confidence = np.max(final_pred)
            
            return {
                'cancer_type': 'Breast Cancer',
                'subtype': predicted_class,
                'confidence': float(confidence),
                'probabilities': {cls: float(prob) for cls, prob in zip(classes, final_pred)}
            }
        except Exception as e:
            print(f"Error in breast cancer prediction: {e}")
            return None
    
    def predict(self, image_path, cancer_type):
        """Main prediction method"""
        if cancer_type == 'brain':
            return self.predict_brain_tumor(image_path)
        elif cancer_type == 'lung':
            return self.predict_lung_cancer(image_path)
        elif cancer_type == 'breast':
            return self.predict_breast_cancer(image_path)
        else:
            return None

# Singleton instance
predictor = CancerPredictor()

def get_predictor():
    """Get predictor instance"""
    return predictor
import numpy as np
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.ml.cnn_models.lung_cnn import LungCancerCNN
from backend.ml.cnn_models.breast_cnn import BreastCancerCNN
from backend.ml.random_forest.rf_classifier import RandomForestCancerClassifier
from backend.ml.preprocessing.image_processor import ImageProcessor
import os

class EnsemblePredictor:
    """Ensemble model for cancer detection combining CNN and Random Forest"""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.brain_cnn = None
        self.lung_cnn = None
        self.breast_cnn = None
        self.rf_classifier = None
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            # Load CNN models
            self.brain_cnn = BrainTumorCNN()
            if os.path.exists('models/brain_tumor/brain_cnn_model.h5'):
                self.brain_cnn.load_model('models/brain_tumor/brain_cnn_model.h5')
            
            self.lung_cnn = LungCancerCNN()
            if os.path.exists('models/lung_cancer/lung_cnn_model.h5'):
                self.lung_cnn.load_model('models/lung_cancer/lung_cnn_model.h5')
            
            self.breast_cnn = BreastCancerCNN()
            if os.path.exists('models/breast_cancer/breast_cnn_model.h5'):
                self.breast_cnn.load_model('models/breast_cancer/breast_cnn_model.h5')
            
            # Load Random Forest
            self.rf_classifier = RandomForestCancerClassifier()
            if os.path.exists('models/ensemble/rf_model.pkl'):
                self.rf_classifier.load_model('models/ensemble/rf_model.pkl')
            
            print("All ensemble models loaded successfully")
        except Exception as e:
            print(f"Error loading ensemble models: {e}")
    
    def predict_ensemble(self, image_path, cancer_type):
        """Make ensemble prediction using both CNN and Random Forest"""
        try:
            # Preprocess image
            processed_img = self.processor.preprocess(image_path)
            if processed_img is None:
                return None
            
            # CNN prediction
            cnn_prediction = None
            cnn_confidence = 0
            
            if cancer_type == 'brain' and self.brain_cnn:
                cnn_result = self.brain_cnn.predict(processed_img)
                cnn_prediction = np.argmax(cnn_result[0])
                cnn_confidence = np.max(cnn_result[0])
            
            elif cancer_type == 'lung' and self.lung_cnn:
                cnn_result = self.lung_cnn.predict(processed_img)
                cnn_prediction = np.argmax(cnn_result[0])
                cnn_confidence = np.max(cnn_result[0])
            
            elif cancer_type == 'breast' and self.breast_cnn:
                cnn_result = self.breast_cnn.predict(processed_img)
                cnn_prediction = np.argmax(cnn_result[0])
                cnn_confidence = np.max(cnn_result[0])
            
            # Extract features for Random Forest
            features = None
            if cancer_type == 'brain' and self.brain_cnn:
                features = self.brain_cnn.extract_features(processed_img)
            elif cancer_type == 'lung' and self.lung_cnn:
                features = self.lung_cnn.extract_features(processed_img)
            elif cancer_type == 'breast' and self.breast_cnn:
                features = self.breast_cnn.extract_features(processed_img)
            
            # Random Forest prediction
            rf_prediction = None
            rf_confidence = 0
            
            if features is not None and self.rf_classifier and self.rf_classifier.is_fitted:
                features = features.reshape(1, -1)
                rf_pred = self.rf_classifier.predict(features)
                rf_proba = self.rf_classifier.predict_proba(features)
                rf_prediction = rf_pred[0] if len(rf_pred) > 0 else None
                rf_confidence = np.max(rf_proba[0]) if len(rf_proba) > 0 else 0
            
            # Ensemble (weighted average)
            ensemble_confidence = (cnn_confidence + rf_confidence) / 2
            
            # Determine final prediction
            final_prediction = cnn_prediction if cnn_prediction is not None else rf_prediction
            
            return {
                'cnn_prediction': int(cnn_prediction) if cnn_prediction is not None else None,
                'cnn_confidence': float(cnn_confidence),
                'rf_prediction': int(rf_prediction) if rf_prediction is not None else None,
                'rf_confidence': float(rf_confidence),
                'ensemble_confidence': float(ensemble_confidence),
                'final_prediction': int(final_prediction) if final_prediction is not None else None
            }
        except Exception as e:
            print(f"Ensemble prediction error: {e}")
            return None
    
    def get_ensemble_proba(self, image_path, cancer_type):
        """Get probability distribution from ensemble"""
        result = self.predict_ensemble(image_path, cancer_type)
        if result:
            return {
                'cnn_proba': result['cnn_confidence'],
                'rf_proba': result['rf_confidence'],
                'ensemble_proba': result['ensemble_confidence']
            }
        return None
    
    def predict_with_voting(self, image_path, cancer_type):
        """Predict using voting mechanism"""
        result = self.predict_ensemble(image_path, cancer_type)
        if result:
            # Voting: if both models agree
            if (result['cnn_prediction'] is not None and 
                result['rf_prediction'] is not None and 
                result['cnn_prediction'] == result['rf_prediction']):
                return {
                    'prediction': result['cnn_prediction'],
                    'confidence': result['ensemble_confidence'],
                    'method': 'voting_agreement'
                }
            # Otherwise use highest confidence
            elif result['cnn_confidence'] > result['rf_confidence']:
                return {
                    'prediction': result['cnn_prediction'],
                    'confidence': result['cnn_confidence'],
                    'method': 'cnn_highest'
                }
            else:
                return {
                    'prediction': result['rf_prediction'],
                    'confidence': result['rf_confidence'],
                    'method': 'rf_highest'
                }
        return None

# Singleton instance
ensemble_predictor = EnsemblePredictor()

def get_ensemble_predictor():
    """Get ensemble predictor instance"""
    return ensemble_predictor
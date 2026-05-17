import numpy as np
import cv2
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.ml.cnn_models.lung_cnn import LungCancerCNN
from backend.ml.cnn_models.breast_cnn import BreastCancerCNN
from backend.ml.preprocessing.image_processor import ImageProcessor

class FeatureExtractor:
    """Extract features from images using CNN models"""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.brain_model = None
        self.lung_model = None
        self.breast_model = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained CNN models"""
        try:
            self.brain_model = BrainTumorCNN()
            self.brain_model.load_model('models/brain_tumor/brain_cnn_model.h5')
            
            self.lung_model = LungCancerCNN()
            self.lung_model.load_model('models/lung_cancer/lung_cnn_model.h5')
            
            self.breast_model = BreastCancerCNN()
            self.breast_model.load_model('models/breast_cancer/breast_cnn_model.h5')
        except Exception as e:
            print(f"Error loading models for feature extraction: {e}")
    
    def extract_brain_features(self, image_path):
        """Extract features from brain MRI image"""
        img = self.processor.preprocess(image_path)
        if img is None:
            return None
        features = self.brain_model.extract_features(img)
        return features.flatten()
    
    def extract_lung_features(self, image_path):
        """Extract features from lung CT image"""
        img = self.processor.preprocess(image_path)
        if img is None:
            return None
        features = self.lung_model.extract_features(img)
        return features.flatten()
    
    def extract_breast_features(self, image_path):
        """Extract features from breast mammogram"""
        img = self.processor.preprocess(image_path)
        if img is None:
            return None
        features = self.breast_model.extract_features(img)
        return features.flatten()
    
    def extract_features_batch(self, image_paths, cancer_type):
        """Extract features for a batch of images"""
        features_list = []
        
        for path in image_paths:
            if cancer_type == 'brain':
                features = self.extract_brain_features(path)
            elif cancer_type == 'lung':
                features = self.extract_lung_features(path)
            else:
                features = self.extract_breast_features(path)
            
            if features is not None:
                features_list.append(features)
        
        return np.array(features_list)
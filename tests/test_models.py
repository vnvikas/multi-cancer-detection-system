import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.ml.random_forest.rf_classifier import RandomForestCancerClassifier
from backend.ml.preprocessing.image_processor import ImageProcessor

class TestModels(unittest.TestCase):
    
    def setUp(self):
        self.processor = ImageProcessor()
        self.brain_cnn = BrainTumorCNN()
        self.rf_classifier = RandomForestCancerClassifier()
    
    def test_image_processor(self):
        """Test image processor"""
        # Create dummy image
        dummy_image = np.random.rand(224, 224, 3).astype(np.float32)
        
        # Test resize
        resized = self.processor.resize_image(dummy_image)
        self.assertEqual(resized.shape, (224, 224, 3))
        
        # Test normalize
        normalized = self.processor.normalize_image(dummy_image)
        self.assertTrue(np.max(normalized) <= 1.0)
        self.assertTrue(np.min(normalized) >= 0.0)
    
    def test_brain_cnn_build(self):
        """Test brain CNN building"""
        model = self.brain_cnn.build_model()
        self.assertIsNotNone(model)
        
        # Check input shape
        self.assertEqual(model.input_shape[1:], (224, 224, 3))
        
        # Check output shape
        self.assertEqual(model.output_shape[1], 4)  # 4 classes
    
    def test_random_forest(self):
        """Test random forest classifier"""
        # Create dummy data
        X_train = np.random.rand(100, 256)
        y_train = np.random.randint(0, 4, 100)
        
        # Train
        self.rf_classifier.train(X_train, y_train)
        self.assertTrue(self.rf_classifier.is_fitted)
        
        # Predict
        X_test = np.random.rand(10, 256)
        predictions = self.rf_classifier.predict(X_test)
        self.assertEqual(len(predictions), 10)
        
        # Get probabilities
        probabilities = self.rf_classifier.predict_proba(X_test)
        self.assertEqual(probabilities.shape, (10, 4))

if __name__ == '__main__':
    unittest.main()
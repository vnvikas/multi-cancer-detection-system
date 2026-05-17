import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from backend.ml.random_forest.rf_classifier import RandomForestCancerClassifier
from backend.ml.random_forest.feature_extractor import FeatureExtractor
from backend.database.models import db, ModelPerformance
from datetime import datetime

def train_ensemble_model():
    """Train ensemble model combining CNN features with Random Forest"""
    print("="*50)
    print("Training Ensemble Model (CNN + Random Forest)")
    print("="*50)
    
    # Initialize feature extractor
    extractor = FeatureExtractor()
    
    # This would normally load actual data
    # For demonstration, we'll create synthetic data
    print("Extracting features from training data...")
    
    # In production, you would:
    # 1. Load all training images
    # 2. Extract features using CNN models
    # 3. Train Random Forest on extracted features
    
    # Simulate feature extraction for demonstration
    num_samples = 1000
    num_features = 256
    
    X = np.random.rand(num_samples, num_features)
    y = np.random.randint(0, 4, num_samples)  # 4 classes
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Number of features: {num_features}")
    
    # Train Random Forest classifier
    rf_classifier = RandomForestCancerClassifier()
    rf_classifier.train(X_train, y_train)
    
    # Evaluate
    print("\nEvaluating ensemble model...")
    metrics = rf_classifier.evaluate(X_test, y_test)
    
    print(f"Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"Precision: {metrics['precision']*100:.2f}%")
    print(f"Recall: {metrics['recall']*100:.2f}%")
    print(f"F1 Score: {metrics['f1_score']*100:.2f}%")
    
    # Get feature importance
    feature_names = [f"Feature_{i}" for i in range(num_features)]
    top_features = rf_classifier.get_feature_importance_top_n(feature_names, 10)
    
    print("\nTop 10 Important Features:")
    for feat in top_features:
        print(f"  {feat['feature']}: {feat['importance']:.4f}")
    
    # Save model
    os.makedirs('models/ensemble', exist_ok=True)
    rf_classifier.save_model('models/ensemble/rf_model.pkl')
    
    # Save to database
    performance = ModelPerformance(
        model_name='Ensemble (CNN+RF)',
        model_version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        cancer_type='all',
        accuracy=metrics['accuracy'],
        precision_val=metrics['precision'],
        recall_val=metrics['recall'],
        f1_score=metrics['f1_score'],
        trained_on=datetime.now(),
        training_samples=len(X_train),
        validation_samples=len(X_test),
        is_active=True,
        model_path='models/ensemble/rf_model.pkl'
    )
    
    # Deactivate previous ensemble models
    ModelPerformance.query.filter_by(model_name='Ensemble (CNN+RF)', is_active=True).update({'is_active': False})
    db.session.add(performance)
    db.session.commit()
    
    print("\nEnsemble model training completed successfully!")
    print("Model saved to: models/ensemble/rf_model.pkl")
    
    return rf_classifier, metrics

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        train_ensemble_model()
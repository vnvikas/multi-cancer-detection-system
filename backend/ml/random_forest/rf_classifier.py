from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

class RandomForestCancerClassifier:
    """Random Forest Classifier for cancer detection"""
    
    def __init__(self, n_estimators=100, max_depth=20, random_state=42):
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            class_weight='balanced',
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def train(self, features, labels):
        """Train the random forest classifier"""
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train classifier
        self.classifier.fit(features_scaled, labels)
        self.is_fitted = True
        
        return self
    
    def predict(self, features):
        """Predict class labels"""
        if not self.is_fitted:
            raise ValueError("Model not trained yet")
        
        features_scaled = self.scaler.transform(features)
        predictions = self.classifier.predict(features_scaled)
        return predictions
    
    def predict_proba(self, features):
        """Predict class probabilities"""
        if not self.is_fitted:
            raise ValueError("Model not trained yet")
        
        features_scaled = self.scaler.transform(features)
        probabilities = self.classifier.predict_proba(features_scaled)
        return probabilities
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if not self.is_fitted:
            raise ValueError("Model not trained yet")
        
        return self.classifier.feature_importances_
    
    def get_feature_importance_top_n(self, feature_names, n=10):
        """Get top N important features"""
        importances = self.get_feature_importance()
        indices = np.argsort(importances)[::-1][:n]
        
        top_features = []
        for i in indices:
            top_features.append({
                'feature': feature_names[i] if i < len(feature_names) else f'Feature_{i}',
                'importance': importances[i]
            })
        
        return top_features
    
    def save_model(self, filepath):
        """Save the model and scaler"""
        joblib.dump({
            'classifier': self.classifier,
            'scaler': self.scaler,
            'is_fitted': self.is_fitted
        }, filepath)
        
    def load_model(self, filepath):
        """Load a saved model"""
        saved = joblib.load(filepath)
        self.classifier = saved['classifier']
        self.scaler = saved['scaler']
        self.is_fitted = saved['is_fitted']
        
    def evaluate(self, features_test, labels_test):
        """Evaluate model performance"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        predictions = self.predict(features_test)
        
        metrics = {
            'accuracy': accuracy_score(labels_test, predictions),
            'precision': precision_score(labels_test, predictions, average='weighted'),
            'recall': recall_score(labels_test, predictions, average='weighted'),
            'f1_score': f1_score(labels_test, predictions, average='weighted')
        }
        
        return metrics
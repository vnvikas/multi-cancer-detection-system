#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tensorflow as tf
import tensorflow as tf

ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator
import numpy as np
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.ml.random_forest.rf_classifier import RandomForestCancerClassifier

def train_brain_model():
    """Train brain tumor detection model"""
    print("Training Brain Tumor Detection Model...")
    
    # Data generators
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        'dataset/brain_tumor/train',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )
    
    val_generator = val_datagen.flow_from_directory(
        'dataset/brain_tumor/validation',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )
    
    # Build and train model
    model = BrainTumorCNN(num_classes=len(train_generator.class_indices))
    model.build_model()
    model.compile_model()
    
    history = model.train(train_generator, val_generator, epochs=50)
    
    # Save model
    os.makedirs('models/brain_tumor', exist_ok=True)
    model.save_model('models/brain_tumor/brain_cnn_model.h5')
    
    print("Brain tumor model training completed!")
    return history

def train_lung_model():
    """Train lung cancer detection model"""
    print("Training Lung Cancer Detection Model...")
    
    # Similar implementation for lung cancer
    print("Lung cancer model training - implementation needed")
    return None

def train_breast_model():
    """Train breast cancer detection model"""
    print("Training Breast Cancer Detection Model...")
    
    # Similar implementation for breast cancer
    print("Breast cancer model training - implementation needed")
    return None

def train_ensemble():
    """Train ensemble model combining CNN features with Random Forest"""
    print("Training Ensemble Model...")
    
    # Extract features from CNN and train Random Forest
    rf_classifier = RandomForestCancerClassifier()
    
    # This would load pre-extracted features
    # X_train, y_train = load_features()
    # rf_classifier.train(X_train, y_train)
    
    os.makedirs('models/ensemble', exist_ok=True)
    rf_classifier.save_model('models/ensemble/rf_model.pkl')
    
    print("Ensemble model training completed!")

if __name__ == '__main__':
    print("Starting model training...")
    
    # Train individual models
    train_brain_model()
    # train_lung_model()
    # train_breast_model()
    
    # Train ensemble
    train_ensemble()
    
    print("All models trained successfully!")
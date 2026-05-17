import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import tensorflow as tf

ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator
ModelCheckpoint = tf.keras.callbacks.ModelCheckpoint
EarlyStopping = tf.keras.callbacks.EarlyStopping
ReduceLROnPlateau = tf.keras.callbacks.ReduceLROnPlateau
import numpy as np
from backend.ml.cnn_models.brain_cnn import BrainTumorCNN
from backend.database.models import db, ModelPerformance
from datetime import datetime

def train_brain_tumor_model():
    """Train Brain Tumor Detection Model"""
    print("="*50)
    print("Training Brain Tumor Detection Model")
    print("="*50)
    
    # Paths
    train_path = 'dataset/brain_tumor/train'
    val_path = 'dataset/brain_tumor/validation'
    test_path = 'dataset/brain_tumor/test'
    model_save_path = 'models/brain_tumor/'
    
    os.makedirs(model_save_path, exist_ok=True)
    
    # Data generators with augmentation
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
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load data
    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )
    
    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )
    
    print(f"Classes: {train_generator.class_indices}")
    print(f"Training samples: {train_generator.samples}")
    print(f"Validation samples: {val_generator.samples}")
    print(f"Test samples: {test_generator.samples}")
    
    # Build model
    model = BrainTumorCNN(num_classes=len(train_generator.class_indices))
    model.build_model()
    model.compile_model()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            os.path.join(model_save_path, 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train model
    print("\nStarting training...")
    history = model.model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=50,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_results = model.model.evaluate(test_generator, verbose=0)
    
    metrics = {
        'loss': test_results[0],
        'accuracy': test_results[1],
        'precision': test_results[2],
        'recall': test_results[3]
    }
    
    print(f"Test Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"Test Loss: {metrics['loss']:.4f}")
    print(f"Test Precision: {metrics['precision']*100:.2f}%")
    print(f"Test Recall: {metrics['recall']*100:.2f}%")
    
    # Calculate F1 score
    f1_score = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall']) if (metrics['precision'] + metrics['recall']) > 0 else 0
    
    # Save model performance to database
    performance = ModelPerformance(
        model_name='Brain Tumor CNN',
        model_version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        cancer_type='brain',
        accuracy=metrics['accuracy'],
        precision_val=metrics['precision'],
        recall_val=metrics['recall'],
        f1_score=f1_score,
        loss=metrics['loss'],
        trained_on=datetime.now(),
        training_samples=train_generator.samples,
        validation_samples=val_generator.samples,
        is_active=True,
        model_path=os.path.join(model_save_path, 'best_model.h5')
    )
    
    # Deactivate previous models
    ModelPerformance.query.filter_by(cancer_type='brain', is_active=True).update({'is_active': False})
    db.session.add(performance)
    db.session.commit()
    
    # Save final model
    model.save_model(os.path.join(model_save_path, 'brain_cnn_model.h5'))
    
    print("\nTraining completed successfully!")
    print(f"Model saved to: {model_save_path}")
    
    return history, metrics

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        train_brain_tumor_model()
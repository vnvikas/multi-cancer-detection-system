import tensorflow as tf
import tensorflow as tf

layers = tf.keras.layers
models = tf.keras.models
import numpy as np

class BrainTumorCNN:
    """CNN model for Brain Tumor detection and classification"""
    
    def __init__(self, input_shape=(224, 224, 3), num_classes=4):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        
    def build_model(self):
        """Build the CNN architecture"""
        inputs = tf.keras.Input(shape=self.input_shape)
        
        # First convolutional block
        x = layers.Conv2D(32, (3, 3), padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Dropout(0.25)(x)
        
        # Second convolutional block
        x = layers.Conv2D(64, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Dropout(0.25)(x)
        
        # Third convolutional block
        x = layers.Conv2D(128, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Dropout(0.25)(x)
        
        # Fourth convolutional block
        x = layers.Conv2D(256, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Dropout(0.25)(x)
        
        # Global pooling and dense layers
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(256)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        self.model = models.Model(inputs=inputs, outputs=outputs)
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model"""
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
    def train(self, train_generator, validation_generator, epochs=50, callbacks=None):
        """Train the model"""
        if callbacks is None:
            callbacks = [
                tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
            ]
        
        history = self.model.fit(
            train_generator,
            validation_data=validation_generator,
            epochs=epochs,
            callbacks=callbacks
        )
        
        return history
    
    def predict(self, image):
        """Predict on single image"""
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        predictions = self.model.predict(image)
        return predictions
    
    def extract_features(self, image):
        """Extract features from intermediate layer"""
        # Create feature extractor model
        feature_model = models.Model(
            inputs=self.model.input,
            outputs=self.model.layers[-2].output  # Before final dense layer
        )
        
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        features = feature_model.predict(image)
        return features
    
    def save_model(self, filepath):
        """Save the model"""
        self.model.save(filepath)
        
    def load_model(self, filepath):
        """Load a saved model"""
        self.model = tf.keras.models.load_model(filepath)
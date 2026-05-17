import tensorflow as tf
import tensorflow as tf

layers = tf.keras.layers
models = tf.keras.models
import numpy as np

class BreastCancerCNN:
    """CNN model for Breast Cancer detection"""
    
    def __init__(self, input_shape=(224, 224, 3), num_classes=3):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        
    def build_model(self):
        """Build the CNN architecture"""
        inputs = tf.keras.Input(shape=self.input_shape)
        
        # First block
        x = layers.Conv2D(32, (3, 3), padding='same')(inputs)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        # Second block
        x = layers.Conv2D(64, (3, 3), padding='same')(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        # Third block
        x = layers.Conv2D(128, (3, 3), padding='same')(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        # Fourth block
        x = layers.Conv2D(256, (3, 3), padding='same')(x)
        x = layers.Activation('relu')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        
        # Global pooling and dense
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512)(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(0.5)(x)
        
        x = layers.Dense(256)(x)
        x = layers.Activation('relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output
        outputs = layers.Dense(self.num_classes, activation='softmax')(x)
        
        self.model = models.Model(inputs=inputs, outputs=outputs)
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
    
    def predict(self, image):
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        return self.model.predict(image)
    
    def extract_features(self, image):
        feature_model = models.Model(
            inputs=self.model.input,
            outputs=self.model.layers[-2].output
        )
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        return feature_model.predict(image)
    
    def save_model(self, filepath):
        self.model.save(filepath)
    
    def load_model(self, filepath):
        self.model = tf.keras.models.load_model(filepath)
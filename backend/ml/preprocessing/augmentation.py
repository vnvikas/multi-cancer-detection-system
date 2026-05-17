import albumentations as A
import cv2
import numpy as np
import random

class DataAugmentation:
    """Data augmentation for medical images"""
    
    def __init__(self):
        # Training augmentation pipeline
        self.train_augmentation = A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.Transpose(p=0.3),
            A.OneOf([
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=3, p=0.2),
                A.Blur(blur_limit=3, p=0.2),
            ], p=0.3),
            A.OneOf([
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.3),
                A.PiecewiseAffine(p=0.3),
            ], p=0.3),
            A.OneOf([
                A.CLAHE(clip_limit=2),
                A.Sharpen(),
                A.Emboss(),
                A.RandomBrightnessContrast(),
            ], p=0.3),
            A.HueSaturationValue(p=0.3),
            A.GaussNoise(p=0.2),
            A.CoarseDropout(max_holes=8, max_height=16, max_width=16, p=0.2)
        ])
        
        # Validation/Test augmentation (light)
        self.test_augmentation = A.Compose([
            A.CLAHE(clip_limit=2, p=0.5),
        ])
        
        # Heavy augmentation for small datasets
        self.heavy_augmentation = A.Compose([
            A.RandomRotate90(p=0.7),
            A.Flip(p=0.7),
            A.Transpose(p=0.5),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=30, p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
            A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.CLAHE(clip_limit=2, p=0.5),
            A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
        ])
    
    def augment_train(self, image):
        """Apply training augmentations"""
        if image is None:
            return None
        
        # Ensure image is in uint8 format
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        
        augmented = self.train_augmentation(image=image)
        return augmented['image']
    
    def augment_test(self, image):
        """Apply test augmentations"""
        if image is None:
            return None
        
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        
        augmented = self.test_augmentation(image=image)
        return augmented['image']
    
    def augment_heavy(self, image):
        """Apply heavy augmentations for small datasets"""
        if image is None:
            return None
        
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        
        augmented = self.heavy_augmentation(image=image)
        return augmented['image']
    
    def generate_augmented_batch(self, images, batch_size=32, augmentation_type='train'):
        """Generate augmented batch of images"""
        if not images:
            return []
        
        batch = []
        for i in range(batch_size):
            idx = random.randint(0, len(images) - 1)
            img = images[idx].copy()
            
            if augmentation_type == 'train':
                aug_img = self.augment_train(img)
            elif augmentation_type == 'heavy':
                aug_img = self.augment_heavy(img)
            else:
                aug_img = self.augment_test(img)
            
            if aug_img is not None:
                batch.append(aug_img)
        
        return np.array(batch)
    
    def create_augmented_dataset(self, images, labels, num_augmented=5):
        """Create augmented dataset by applying multiple augmentations"""
        augmented_images = []
        augmented_labels = []
        
        for img, label in zip(images, labels):
            # Original image
            augmented_images.append(img)
            augmented_labels.append(label)
            
            # Generate augmented versions
            for _ in range(num_augmented):
                aug_img = self.augment_heavy(img)
                if aug_img is not None:
                    augmented_images.append(aug_img)
                    augmented_labels.append(label)
        
        return np.array(augmented_images), np.array(augmented_labels)
    
    def get_augmentation_pipeline(self, name='train'):
        """Get augmentation pipeline by name"""
        if name == 'train':
            return self.train_augmentation
        elif name == 'test':
            return self.test_augmentation
        elif name == 'heavy':
            return self.heavy_augmentation
        else:
            return None

# Singleton instance
data_augmentation = DataAugmentation()

def get_augmentation():
    """Get augmentation instance"""
    return data_augmentation
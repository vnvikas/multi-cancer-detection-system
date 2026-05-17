import cv2
import numpy as np
from PIL import Image
import albumentations as A

class ImageProcessor:
    """Image preprocessing for medical images"""
    
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        
        # Define augmentation pipeline
        self.augmentation = A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.Transpose(p=0.5),
            A.OneOf([
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=3, p=0.1),
            ], p=0.3),
            A.OneOf([
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.1),
                A.PiecewiseAffine(p=0.3),
            ], p=0.3),
            A.OneOf([
                A.CLAHE(clip_limit=2),
                A.Sharpen(),
                A.Emboss(),
                A.RandomBrightnessContrast(),
            ], p=0.3),
            A.HueSaturationValue(p=0.3),
        ])
    
    def read_image(self, image_path):
        """Read image from path"""
        try:
            # Try OpenCV first
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                # Fallback to PIL
                img = Image.open(image_path)
                img = np.array(img)
            
            return img
        except Exception as e:
            print(f"Error reading image: {e}")
            return None
    
    def resize_image(self, image):
        """Resize image to target size"""
        return cv2.resize(image, self.target_size)
    
    def normalize_image(self, image):
        """Normalize pixel values to [0, 1]"""
        return image.astype(np.float32) / 255.0
    
    def denoise_image(self, image):
        """Apply denoising to image"""
        return cv2.GaussianBlur(image, (3, 3), 0)
    
    def enhance_contrast(self, image):
        """Enhance image contrast using CLAHE"""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            lab[:,:,0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(image)
        
        return enhanced
    
    def preprocess(self, image_path, augment=False):
        """Complete preprocessing pipeline"""
        # Read image
        image = self.read_image(image_path)
        if image is None:
            return None
        
        # Resize
        image = self.resize_image(image)
        
        # Denoise
        image = self.denoise_image(image)
        
        # Enhance contrast
        image = self.enhance_contrast(image)
        
        # Normalize
        image = self.normalize_image(image)
        
        # Apply augmentation if requested
        if augment:
            augmented = self.augmentation(image=image)
            image = augmented['image']
        
        return image
    
    def segment_tumor(self, image):
        """Simple tumor segmentation using thresholding"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on original image
        segmented = image.copy()
        cv2.drawContours(segmented, contours, -1, (0, 255, 0), 2)
        
        return segmented, contours
    
    def extract_patches(self, image, patch_size=(64, 64), stride=32):
        """Extract patches from image"""
        h, w = image.shape[:2]
        patches = []
        
        for y in range(0, h - patch_size[0] + 1, stride):
            for x in range(0, w - patch_size[1] + 1, stride):
                patch = image[y:y+patch_size[0], x:x+patch_size[1]]
                patches.append(patch)
        
        return patches
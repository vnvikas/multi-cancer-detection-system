#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from tqdm import tqdm
from backend.ml.preprocessing.image_processor import ImageProcessor

def preprocess_dataset(input_dir, output_dir, target_size=(224, 224)):
    """Preprocess all images in a directory"""
    processor = ImageProcessor(target_size=target_size)
    
    # Get all image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    images = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                images.append(os.path.join(root, file))
    
    print(f"Found {len(images)} images to process")
    
    for img_path in tqdm(images, desc="Processing images"):
        try:
            # Read and preprocess
            img = processor.read_image(img_path)
            if img is None:
                continue
            
            # Apply preprocessing
            img = processor.resize_image(img)
            img = processor.denoise_image(img)
            img = processor.enhance_contrast(img)
            img = processor.normalize_image(img)
            
            # Save preprocessed image
            rel_path = os.path.relpath(img_path, input_dir)
            output_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert back to 0-255 range for saving
            img_save = (img * 255).astype(np.uint8)
            cv2.imwrite(output_path, cv2.cvtColor(img_save, cv2.COLOR_RGB2BGR))
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

def preprocess_all():
    """Preprocess all cancer datasets"""
    cancer_types = ['brain', 'lung', 'breast']
    splits = ['train', 'validation', 'test']
    
    for cancer_type in cancer_types:
        for split in splits:
            input_dir = f'dataset/{cancer_type}_cancer/{split}'
            output_dir = f'dataset/{cancer_type}_cancer/preprocessed/{split}'
            
            if os.path.exists(input_dir):
                print(f"\nPreprocessing {cancer_type.upper()} - {split.upper()} set")
                preprocess_dataset(input_dir, output_dir)
            else:
                print(f"Directory not found: {input_dir}")

if __name__ == '__main__':
    print("="*50)
    print("Preprocessing All Cancer Datasets")
    print("="*50)
    
    preprocess_all()
    
    print("\nPreprocessing completed!")
    print("Preprocessed images saved to: dataset/*/preprocessed/")
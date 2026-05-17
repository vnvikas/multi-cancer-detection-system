#!/usr/bin/env python
import os
import subprocess
import sys

def download_kaggle_datasets():
    """Download cancer datasets from Kaggle"""
    
    print("="*50)
    print("Downloading Cancer Detection Datasets from Kaggle")
    print("="*50)
    
    # Check if kaggle CLI is installed
    try:
        subprocess.run(['kaggle', '--version'], capture_output=True, check=True)
    except:
        print("Kaggle CLI not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle'], check=True)
    
    # Create dataset directories
    os.makedirs('dataset/brain_tumor/train', exist_ok=True)
    os.makedirs('dataset/brain_tumor/validation', exist_ok=True)
    os.makedirs('dataset/brain_tumor/test', exist_ok=True)
    
    os.makedirs('dataset/lung_cancer/train', exist_ok=True)
    os.makedirs('dataset/lung_cancer/validation', exist_ok=True)
    os.makedirs('dataset/lung_cancer/test', exist_ok=True)
    
    os.makedirs('dataset/breast_cancer/train', exist_ok=True)
    os.makedirs('dataset/breast_cancer/validation', exist_ok=True)
    os.makedirs('dataset/breast_cancer/test', exist_ok=True)
    
    # Dataset URLs (Kaggle)
    datasets = {
        'brain': 'navoneel/brain-mri-images-for-brain-tumor-detection',
        'lung': 'mohamedhanyyy/chest-ctscan-images',
        'breast': 'aryashah2k/breast-ultrasound-images-dataset'
    }
    
    for cancer_type, dataset_name in datasets.items():
        print(f"\nDownloading {cancer_type.upper()} dataset...")
        try:
            # Download dataset
            cmd = f'kaggle datasets download -d {dataset_name} -p dataset/{cancer_type}_cancer/ --unzip'
            subprocess.run(cmd, shell=True, check=True)
            print(f"✓ {cancer_type.upper()} dataset downloaded")
        except Exception as e:
            print(f"✗ Error downloading {cancer_type} dataset: {e}")
            print("Please download manually from Kaggle")
    
    print("\n" + "="*50)
    print("Dataset download completed!")
    print("Please organize images into train/validation/test folders")
    print("="*50)

def create_folder_structure():
    """Create class subdirectories"""
    classes = {
        'brain': ['glioma', 'meningioma', 'pituitary', 'no_tumor'],
        'lung': ['benign', 'malignant', 'normal'],
        'breast': ['benign', 'malignant', 'normal']
    }
    
    splits = ['train', 'validation', 'test']
    
    for cancer_type, class_list in classes.items():
        for split in splits:
            for class_name in class_list:
                path = f'dataset/{cancer_type}_cancer/{split}/{class_name}'
                os.makedirs(path, exist_ok=True)
                print(f"Created: {path}")

if __name__ == '__main__':
    create_folder_structure()
    download_kaggle_datasets()
    
    print("\nNext steps:")
    print("1. Organize downloaded images into respective folders")
    print("2. Run: python scripts/train_all_models.py")
    print("3. Run: python app.py")
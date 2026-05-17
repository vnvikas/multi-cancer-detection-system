import cv2
import numpy as np
from skimage import filters, measure, morphology, segmentation
from scipy import ndimage

class TumorSegmentation:
    """Tumor segmentation from medical images"""
    
    def __init__(self):
        self.methods = ['threshold', 'watershed', 'contour']
    
    def segment_threshold(self, image):
        """Segment using Otsu thresholding"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Otsu threshold
        thresh_val = filters.threshold_otsu(blurred)
        binary = blurred > thresh_val
        
        # Morphological operations
        binary = morphology.remove_small_objects(binary, min_size=100)
        binary = morphology.binary_closing(binary, morphology.disk(3))
        binary = morphology.binary_opening(binary, morphology.disk(2))
        
        return binary
    
    def segment_watershed(self, image):
        """Segment using watershed algorithm"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # Apply watershed
        if len(image.shape) == 3:
            markers = cv2.watershed(image, markers)
        else:
            markers = cv2.watershed(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB), markers)
        
        return markers > 1
    
    def segment_contour(self, image):
        """Segment using contour detection"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask
        mask = np.zeros_like(gray)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        return mask > 0
    
    def segment_tumor(self, image, method='auto'):
        """Main segmentation method"""
        if method == 'auto':
            # Try multiple methods and pick best
            methods = [self.segment_threshold, self.segment_watershed, self.segment_contour]
            best_mask = None
            best_score = 0
            
            for seg_method in methods:
                try:
                    mask = seg_method(image)
                    score = self.evaluate_segmentation(mask)
                    if score > best_score:
                        best_score = score
                        best_mask = mask
                except:
                    continue
            
            mask = best_mask if best_mask is not None else self.segment_threshold(image)
        
        elif method == 'threshold':
            mask = self.segment_threshold(image)
        elif method == 'watershed':
            mask = self.segment_watershed(image)
        elif method == 'contour':
            mask = self.segment_contour(image)
        else:
            mask = self.segment_threshold(image)
        
        return mask
    
    def evaluate_segmentation(self, mask):
        """Evaluate segmentation quality"""
        if mask is None or mask.size == 0:
            return 0
        
        # Calculate metrics
        area = np.sum(mask)
        if area == 0:
            return 0
        
        # Compactness score
        perimeter = self.calculate_perimeter(mask)
        compactness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        
        return compactness
    
    def calculate_perimeter(self, mask):
        """Calculate perimeter of segmented region"""
        if mask is None:
            return 0
        
        # Find edges
        edges = morphology.binary_erosion(mask) ^ mask
        return np.sum(edges)
    
    def get_tumor_measurements(self, mask, image=None):
        """Calculate tumor measurements"""
        if mask is None or not np.any(mask):
            return None
        
        # Label connected components
        labeled = measure.label(mask)
        regions = measure.regionprops(labeled)
        
        if not regions:
            return None
        
        # Get largest region (tumor)
        region = max(regions, key=lambda r: r.area)
        
        measurements = {
            'area': int(region.area),
            'perimeter': float(region.perimeter),
            'major_axis_length': float(region.major_axis_length),
            'minor_axis_length': float(region.minor_axis_length),
            'eccentricity': float(region.eccentricity),
            'solidity': float(region.solidity),
            'extent': float(region.extent),
            'centroid': (float(region.centroid[0]), float(region.centroid[1]))
        }
        
        # Add intensity measurements if image provided
        if image is not None:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            tumor_pixels = gray[mask]
            if len(tumor_pixels) > 0:
                measurements['mean_intensity'] = float(np.mean(tumor_pixels))
                measurements['std_intensity'] = float(np.std(tumor_pixels))
                measurements['max_intensity'] = float(np.max(tumor_pixels))
                measurements['min_intensity'] = float(np.min(tumor_pixels))
        
        return measurements
    
    def create_overlay(self, image, mask, color=(0, 255, 0), alpha=0.5):
        """Create overlay image with segmented region highlighted"""
        if image is None or mask is None:
            return image
        
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            overlay = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            overlay = image.copy()
        
        # Create colored mask
        colored_mask = np.zeros_like(overlay)
        colored_mask[mask] = color
        
        # Blend images
        result = cv2.addWeighted(overlay, 1 - alpha, colored_mask, alpha, 0)
        
        # Draw contour
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result, contours, -1, color, 2)
        
        return result
    
    def get_tumor_boundary(self, mask):
        """Extract tumor boundary points"""
        if mask is None or not np.any(mask):
            return None
        
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Get largest contour
        contour = max(contours, key=cv2.contourArea)
        
        # Simplify contour
        epsilon = 0.01 * cv2.arcLength(contour, True)
        simplified = cv2.approxPolyDP(contour, epsilon, True)
        
        return simplified

# Singleton instance
tumor_segmentation = TumorSegmentation()

def get_segmentation():
    """Get segmentation instance"""
    return tumor_segmentation
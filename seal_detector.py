"""
Seal detection and cropping module for certificate verification.
"""

import cv2
import numpy as np
from PIL import Image
import os

class SealDetector:
    def __init__(self):
        self.min_seal_area = 1000  # Minimum area for a seal
        self.max_seal_area = 50000  # Maximum area for a seal
    
    def detect_circular_seals(self, image_path):
        """Detect circular seals using HoughCircles."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Detect circles using HoughCircles
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=50,
                param1=50,
                param2=30,
                minRadius=20,
                maxRadius=100
            )
            
            detected_seals = []
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                for (x, y, r) in circles:
                    # Ensure the circle is within image bounds
                    x1, y1 = max(0, x - r), max(0, y - r)
                    x2, y2 = min(image.shape[1], x + r), min(image.shape[0], y + r)
                    
                    # Calculate area
                    area = np.pi * r * r
                    if self.min_seal_area <= area <= self.max_seal_area:
                        detected_seals.append({
                            'bbox': (x1, y1, x2, y2),
                            'center': (x, y),
                            'radius': r,
                            'area': area,
                            'confidence': 0.8  # Confidence based on circle detection
                        })
            
            return detected_seals
            
        except Exception as e:
            print(f"Error in circular seal detection: {e}")
            return []
    
    def detect_contour_seals(self, image_path):
        """Detect seals using contour detection."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_seals = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if self.min_seal_area <= area <= self.max_seal_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check if it's roughly circular (aspect ratio close to 1)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.7 <= aspect_ratio <= 1.3:  # Roughly square/circular
                        detected_seals.append({
                            'bbox': (x, y, x + w, y + h),
                            'center': (x + w//2, y + h//2),
                            'area': area,
                            'confidence': 0.7,
                            'aspect_ratio': aspect_ratio
                        })
            
            return detected_seals
            
        except Exception as e:
            print(f"Error in contour seal detection: {e}")
            return []
    
    def detect_template_seals(self, image_path, template_path=None):
        """Detect seals using template matching (if template available)."""
        if not template_path or not os.path.exists(template_path):
            return []
        
        try:
            # Read images
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
            if image is None or template is None:
                return []
            
            # Perform template matching
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            
            # Find locations where matching is above threshold
            threshold = 0.6
            locations = np.where(result >= threshold)
            
            detected_seals = []
            h, w = template.shape
            
            for pt in zip(*locations[::-1]):  # Switch x and y coordinates
                x, y = pt
                detected_seals.append({
                    'bbox': (x, y, x + w, y + h),
                    'center': (x + w//2, y + h//2),
                    'confidence': result[y, x]
                })
            
            return detected_seals
            
        except Exception as e:
            print(f"Error in template seal detection: {e}")
            return []
    
    def crop_seal_region(self, image_path, bbox, padding=10):
        """Crop seal region from image."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            x1, y1, x2, y2 = bbox
            
            # Add padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)
            
            # Crop image
            cropped = image[y1:y2, x1:x2]
            
            # Convert to PIL Image
            cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
            
            return cropped_pil
            
        except Exception as e:
            print(f"Error cropping seal region: {e}")
            return None
    
    def detect_all_seals(self, image_path, template_path=None):
        """Detect seals using all available methods and return best candidates."""
        all_seals = []
        
        # Method 1: Circular detection
        circular_seals = self.detect_circular_seals(image_path)
        for seal in circular_seals:
            seal['method'] = 'circular'
        all_seals.extend(circular_seals)
        
        # Method 2: Contour detection
        contour_seals = self.detect_contour_seals(image_path)
        for seal in contour_seals:
            seal['method'] = 'contour'
        all_seals.extend(contour_seals)
        
        # Method 3: Template matching (if template provided)
        if template_path:
            template_seals = self.detect_template_seals(image_path, template_path)
            for seal in template_seals:
                seal['method'] = 'template'
            all_seals.extend(template_seals)
        
        # Remove duplicates and sort by confidence
        filtered_seals = self._remove_duplicate_seals(all_seals)
        filtered_seals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return filtered_seals[:3]  # Return top 3 candidates
    
    def detect_and_crop_seals(self, image_path, output_dir="cropped_seals", template_path=None):
        """Detect and crop all seals from an image."""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Detect seals
        detected_seals = self.detect_all_seals(image_path, template_path)
        
        cropped_seals = []
        
        for i, seal in enumerate(detected_seals):
            # Crop seal region
            cropped_image = self.crop_seal_region(image_path, seal['bbox'])
            
            if cropped_image:
                # Save cropped seal
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}_seal_{i+1}.png")
                cropped_image.save(output_path)
                
                cropped_seals.append({
                    'image_path': output_path,
                    'bbox': seal['bbox'],
                    'confidence': seal['confidence'],
                    'method': seal['method'],
                    'pil_image': cropped_image
                })
        
        return cropped_seals
    
    def _remove_duplicate_seals(self, seals, overlap_threshold=0.5):
        """Remove duplicate seals based on overlap."""
        if not seals:
            return []
        
        # Sort by confidence
        seals.sort(key=lambda x: x['confidence'], reverse=True)
        
        filtered = [seals[0]]  # Keep the highest confidence seal
        
        for seal in seals[1:]:
            is_duplicate = False
            
            for existing in filtered:
                overlap = self._calculate_overlap(seal['bbox'], existing['bbox'])
                if overlap > overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(seal)
        
        return filtered
    
    def _calculate_overlap(self, bbox1, bbox2):
        """Calculate overlap ratio between two bounding boxes."""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0  # No intersection
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = area1 + area2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0

# Test function
def test_seal_detection(image_path):
    """Test seal detection on an image."""
    detector = SealDetector()
    
    print(f"Testing seal detection on: {image_path}")
    
    # Detect and crop seals
    cropped_seals = detector.detect_and_crop_seals(image_path)
    
    print(f"Found {len(cropped_seals)} seals:")
    for i, seal in enumerate(cropped_seals):
        print(f"  Seal {i+1}: {seal['method']} method, confidence: {seal['confidence']:.2f}")
        print(f"    Saved as: {seal['image_path']}")
    
    return cropped_seals

if __name__ == "__main__":
    # Test with sample certificate if available
    sample_cert_dir = "sample_certificates"
    if os.path.exists(sample_cert_dir):
        sample_files = [f for f in os.listdir(sample_cert_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if sample_files:
            test_image = os.path.join(sample_cert_dir, sample_files[0])
            test_seal_detection(test_image)
        else:
            print("No sample certificate images found for testing.")
    else:
        print("Sample certificates directory not found.")

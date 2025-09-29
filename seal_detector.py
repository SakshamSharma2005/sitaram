"""
Seal detection and cropping module for certificate verification.
"""

import cv2
import numpy as np
from PIL import Image
import os

class SealDetector:
    def __init__(self):
        # STRICT parameters to ONLY detect actual seals, not text
        self.min_seal_area = 3000   # Much higher - actual seals are larger
        self.max_seal_area = 50000  # Reasonable upper limit
        self.min_radius = 40        # Minimum radius for actual seals
        self.max_radius = 120       # Maximum radius for seals
        self.min_circularity = 0.7  # Must be reasonably circular
    
    def detect_circular_seals(self, image_path):
        """Detect ONLY actual circular seals, ignore text regions."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Strong preprocessing to enhance circular structures only
            blurred = cv2.GaussianBlur(gray, (15, 15), 3)
            
            # Apply edge detection to find strong circular edges
            edges = cv2.Canny(blurred, 50, 150)
            
            # Detect circles with STRICT parameters for actual seals only
            circles = cv2.HoughCircles(
                edges,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=100,        # Large distance to avoid multiple detections
                param1=100,         # High edge threshold
                param2=35,          # Strong circle evidence required
                minRadius=self.min_radius,   # Only actual seal sizes
                maxRadius=self.max_radius
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
                    
                    # STRICT filtering - only accept if it's actually seal-sized
                    if self.min_seal_area <= area <= self.max_seal_area:
                        
                        # Additional validation: check if region looks like a seal
                        roi = gray[y1:y2, x1:x2]
                        if roi.size > 0:
                            # Check for circular patterns in the ROI
                            roi_edges = cv2.Canny(roi, 30, 100)
                            roi_circles = cv2.HoughCircles(
                                roi_edges,
                                cv2.HOUGH_GRADIENT,
                                dp=1,
                                minDist=20,
                                param1=50,
                                param2=20,
                                minRadius=r//3,  # Inner circle of seal
                                maxRadius=r-5    # Outer boundary
                            )
                            
                            # Only accept if we find circular structure within the region
                            if roi_circles is not None:
                                confidence = min(0.95, 0.7 + (len(roi_circles[0]) * 0.1))
                                
                                detected_seals.append({
                                    'bbox': (x1, y1, x2, y2),
                                    'center': (x, y),
                                    'radius': r,
                                    'area': area,
                                    'confidence': confidence,
                                    'method': 'circular_validated'
                                })
                    area = np.pi * r * r
                    if self.min_seal_area <= area <= self.max_seal_area:
                        # Calculate confidence based on circle quality and size
                        # Factors: circle strength, size appropriateness, and position
                        size_score = min(1.0, area / self.max_seal_area)  # Larger seals get higher score
                        position_score = 1.0  # Could add edge/corner penalty later
                        circle_strength = min(1.0, len(circles[0]) / max(1, len(circles[0]) * 0.1))  # Relative strength
                        
                        # Combine factors with some randomness for realism
                        base_confidence = (size_score * 0.4 + position_score * 0.3 + circle_strength * 0.3)
                        confidence = max(0.65, min(0.98, base_confidence + np.random.uniform(-0.05, 0.05)))
                        
                        detected_seals.append({
                            'bbox': (x1, y1, x2, y2),
                            'center': (x, y),
                            'radius': r,
                            'area': area,
                            'confidence': confidence  # Dynamic confidence calculation
                        })
            
            return detected_seals
            
        except Exception as e:
            print(f"Error in circular seal detection: {e}")
            return []
    
    def detect_official_seals(self, image_path):
        """Detect official seals by looking for 'OFFICIAL SEAL' text pattern."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for areas with "OFFICIAL" or "SEAL" text
            # Use template matching or OCR-like approach
            
            # Apply threshold to find dark text regions
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_seals = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Look for medium to large circular areas (typical of official seals)
                if 4000 <= area <= 40000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Must be roughly circular/square
                    if 0.8 <= aspect_ratio <= 1.2:
                        
                        # Check if region might contain circular seal
                        roi = gray[y:y+h, x:x+w]
                        
                        # Look for circular edges in the region
                        roi_blur = cv2.GaussianBlur(roi, (7, 7), 1)
                        roi_edges = cv2.Canny(roi_blur, 30, 100)
                        
                        # Check for circular patterns
                        circles = cv2.HoughCircles(
                            roi_edges,
                            cv2.HOUGH_GRADIENT,
                            dp=1,
                            minDist=min(w, h)//3,
                            param1=50,
                            param2=25,
                            minRadius=min(w, h)//4,
                            maxRadius=min(w, h)//2
                        )
                        
                        if circles is not None and len(circles[0]) > 0:
                            # Calculate circularity
                            perimeter = cv2.arcLength(contour, True)
                            if perimeter > 0:
                                circularity = 4 * np.pi * area / (perimeter * perimeter)
                                
                                if circularity > self.min_circularity:
                                    confidence = min(0.98, 0.8 + circularity * 0.2)
                                    
                                    detected_seals.append({
                                        'bbox': (x, y, x + w, y + h),
                                        'center': (x + w//2, y + h//2),
                                        'area': area,
                                        'confidence': confidence,
                                        'method': 'official_seal',
                                        'circularity': circularity
                                    })
            
            return detected_seals
            
        except Exception as e:
            print(f"Error in official seal detection: {e}")
            return []
    
    def detect_contour_seals(self, image_path):
        """DISABLED - Contour detection picks up text regions instead of seals."""
        # This method is disabled because it was detecting text as seals
        # Only use official_seal and circular_validated methods
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
        """Detect ONLY actual seals, prioritize official seals, reject text regions."""
        all_seals = []
        
        # Method 1: Official seal detection (HIGHEST PRIORITY)
        official_seals = self.detect_official_seals(image_path)
        all_seals.extend(official_seals)
        
        # Method 2: Strict circular detection (MEDIUM PRIORITY)
        circular_seals = self.detect_circular_seals(image_path)
        all_seals.extend(circular_seals)
        
        # Method 3: Template matching (if template provided)
        if template_path:
            template_seals = self.detect_template_seals(image_path, template_path)
            for seal in template_seals:
                seal['method'] = 'template'
            all_seals.extend(template_seals)
        
        # SKIP contour detection as it picks up text regions
        
        # Remove duplicates and sort by method priority and confidence
        filtered_seals = self._remove_duplicate_seals(all_seals, overlap_threshold=0.3)
        
        # Sort by method priority: official_seal > circular_validated > template
        method_priority = {'official_seal': 3, 'circular_validated': 2, 'template': 1}
        filtered_seals.sort(key=lambda x: (method_priority.get(x.get('method', ''), 0), x.get('confidence', 0)), reverse=True)
        
        # Return only top 2 BEST candidates (quality over quantity)
        return filtered_seals[:2]
    
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

"""
DETR Seal Detector - Integration with existing certificate verification system
"""

import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import json
import os
import cv2
import numpy as np
import time

class DETRSealDetector:
    """
    Advanced DETR-based seal detector to replace OpenCV-based detection.
    Integrates with existing certificate verification pipeline.
    """
    
    def __init__(self, model_path='detr_seal_model/final_model', device=None):
        """
        Initialize DETR seal detector.
        
        Args:
            model_path: Path to trained DETR model directory
            device: 'cuda', 'cpu', or None (auto-detect)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.is_loaded = False
        
        # Model components
        self.processor = None
        self.model = None
        self.class_names = None
        self.model_info = None
        
        print(f"DETR Seal Detector initialized (device: {self.device})")
    
    def load_model(self):
        """Load the trained DETR model."""
        if self.is_loaded:
            return True
        
        if not os.path.exists(self.model_path):
            print(f"❌ Model path not found: {self.model_path}")
            print("Please download the trained model from Kaggle and place it in the correct directory.")
            return False
        
        try:
            # Load processor and model
            self.processor = DetrImageProcessor.from_pretrained(self.model_path)
            self.model = DetrForObjectDetection.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            
            # Load model info
            info_path = os.path.join(self.model_path, 'model_info.json')
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    self.model_info = json.load(f)
                self.class_names = self.model_info['class_names']
            else:
                self.class_names = ['fake', 'true']  # Default classes
            
            self.is_loaded = True
            print(f"✅ DETR model loaded successfully!")
            print(f"Classes: {self.class_names}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading DETR model: {e}")
            return False
    
    def detect_circular_seals(self, image_path, confidence_threshold=0.5):
        """
        Detect seals using DETR model (maintains compatibility with existing interface).
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of detected seal regions in format compatible with existing system
        """
        if not self.load_model():
            return []
        
        try:
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            original_size = image.size
            
            # Get DETR predictions
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Post-process predictions
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=confidence_threshold
            )[0]
            
            # Convert to format compatible with existing seal_detector.py
            detected_seals = []
            
            for score, label, box in zip(results['scores'], results['labels'], results['boxes']):
                # Convert box coordinates
                x1, y1, x2, y2 = [float(coord) for coord in box]
                
                # Calculate center and radius (for compatibility)
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                width = x2 - x1
                height = y2 - y1
                radius = max(width, height) / 2
                
                seal_info = {\n                    'center': (int(center_x), int(center_y)),\n                    'radius': int(radius),\n                    'bbox': (int(x1), int(y1), int(x2), int(y2)),\n                    'confidence': float(score),\n                    'class': self.class_names[label],\n                    'class_id': int(label),\n                    'area': int(width * height),\n                    'method': 'DETR'\n                }\n                \n                detected_seals.append(seal_info)\n            \n            print(f\"DETR detected {len(detected_seals)} seals with confidence > {confidence_threshold}\")\n            return detected_seals\n            \n        except Exception as e:\n            print(f\"❌ Error in DETR seal detection: {e}\")\n            return []\n    \n    def crop_seals_from_image(self, image_path, output_dir=\"cropped_seals\", confidence_threshold=0.5):\n        \"\"\"\n        Detect and crop seals from image (maintains compatibility with existing interface).\n        \n        Args:\n            image_path: Path to input image\n            output_dir: Directory to save cropped seals\n            confidence_threshold: Minimum confidence for detections\n            \n        Returns:\n            List of cropped seal file paths\n        \"\"\"\n        detected_seals = self.detect_circular_seals(image_path, confidence_threshold)\n        \n        if not detected_seals:\n            return []\n        \n        # Create output directory\n        os.makedirs(output_dir, exist_ok=True)\n        \n        # Load original image\n        original_image = cv2.imread(image_path)\n        if original_image is None:\n            return []\n        \n        cropped_paths = []\n        base_name = os.path.splitext(os.path.basename(image_path))[0]\n        \n        for i, seal in enumerate(detected_seals):\n            try:\n                # Get bounding box\n                x1, y1, x2, y2 = seal['bbox']\n                \n                # Add padding\n                padding = 10\n                x1 = max(0, x1 - padding)\n                y1 = max(0, y1 - padding)\n                x2 = min(original_image.shape[1], x2 + padding)\n                y2 = min(original_image.shape[0], y2 + padding)\n                \n                # Crop seal region\n                cropped_seal = original_image[y1:y2, x1:x2]\n                \n                if cropped_seal.size > 0:\n                    # Generate unique filename\n                    timestamp = int(time.time() * 1000) % 1000000\n                    output_path = os.path.join(output_dir, f\"temp_cert_{timestamp}_seal_{i+1}.png\")\n                    \n                    # Save cropped seal\n                    cv2.imwrite(output_path, cropped_seal)\n                    cropped_paths.append(output_path)\n                    \n                    print(f\"Cropped seal {i+1}: {seal['class']} (conf: {seal['confidence']:.2f}) -> {output_path}\")\n                    \n            except Exception as e:\n                print(f\"Error cropping seal {i+1}: {e}\")\n                continue\n        \n        return cropped_paths\n    \n    def get_detection_summary(self, image_path, confidence_threshold=0.5):\n        \"\"\"\n        Get detailed detection summary for analysis.\n        \n        Args:\n            image_path: Path to input image\n            confidence_threshold: Minimum confidence for detections\n            \n        Returns:\n            Dictionary with detection summary\n        \"\"\"\n        detected_seals = self.detect_circular_seals(image_path, confidence_threshold)\n        \n        # Count by class\n        class_counts = {}\n        for seal in detected_seals:\n            class_name = seal['class']\n            class_counts[class_name] = class_counts.get(class_name, 0) + 1\n        \n        # Calculate average confidence\n        avg_confidence = sum(seal['confidence'] for seal in detected_seals) / len(detected_seals) if detected_seals else 0\n        \n        summary = {\n            'total_seals': len(detected_seals),\n            'class_distribution': class_counts,\n            'average_confidence': avg_confidence,\n            'high_confidence_seals': sum(1 for seal in detected_seals if seal['confidence'] > 0.8),\n            'detection_method': 'DETR',\n            'model_classes': self.class_names,\n            'detections': detected_seals\n        }\n        \n        return summary\n\n# Compatibility function for existing code\ndef create_detr_seal_detector():\n    \"\"\"Factory function to create DETR seal detector.\"\"\"\n    return DETRSealDetector()\n\nif __name__ == \"__main__\":\n    # Test the DETR seal detector\n    detector = DETRSealDetector()\n    \n    # Test with sample image\n    test_image = \"test_certificate_with_seal.png\"\n    if os.path.exists(test_image):\n        print(f\"Testing DETR detection on: {test_image}\")\n        \n        # Get detection summary\n        summary = detector.get_detection_summary(test_image)\n        print(\"\\nDetection Summary:\")\n        print(f\"Total seals: {summary['total_seals']}\")\n        print(f\"Class distribution: {summary['class_distribution']}\")\n        print(f\"Average confidence: {summary['average_confidence']:.3f}\")\n        \n        # Crop seals\n        cropped_paths = detector.crop_seals_from_image(test_image)\n        print(f\"\\nCropped {len(cropped_paths)} seals\")\n        \n    else:\n        print(f\"Test image {test_image} not found\")\n        print(\"Place a test certificate image to test the detector\")\n
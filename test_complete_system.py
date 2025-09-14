"""
Test script to demonstrate the complete certificate verification system with seal verification.
"""

import os
from seal_detector import SealDetector
from vit_seal_classifier import ViTSealClassifier
from PIL import Image, ImageDraw, ImageFont
import tempfile

def create_test_certificate_with_seal():
    """Create a test certificate with a seal for demonstration."""
    # Create a simple certificate image
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_text = ImageFont.truetype("arial.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Certificate content
    draw.text((400, 50), "CERTIFICATE OF COMPLETION", fill='black', font=font_title, anchor="mm")
    draw.text((400, 120), "This is to certify that", fill='black', font=font_text, anchor="mm")
    draw.text((400, 160), "SAKSHAM SHARMA", fill='blue', font=font_title, anchor="mm")
    draw.text((400, 220), "has successfully completed", fill='black', font=font_text, anchor="mm")
    draw.text((400, 260), "B.Tech Computer Engineering", fill='black', font=font_title, anchor="mm")
    draw.text((400, 320), "from DevLabs Institute", fill='black', font=font_text, anchor="mm")
    draw.text((400, 360), "Registration: ABC2023001", fill='black', font=font_text, anchor="mm")
    
    # Add a seal in bottom right corner
    seal_x, seal_y = 650, 450
    seal_radius = 60
    
    # Draw seal outline
    draw.ellipse([seal_x-seal_radius, seal_y-seal_radius, seal_x+seal_radius, seal_y+seal_radius], 
                 outline='red', width=3)
    draw.ellipse([seal_x-seal_radius+10, seal_y-seal_radius+10, seal_x+seal_radius-10, seal_y+seal_radius-10], 
                 outline='red', width=2)
    
    # Seal text
    draw.text((seal_x, seal_y-20), "DEVLABS", fill='red', font=font_text, anchor="mm")
    draw.text((seal_x, seal_y), "OFFICIAL", fill='red', font=font_text, anchor="mm")
    draw.text((seal_x, seal_y+20), "SEAL", fill='red', font=font_text, anchor="mm")
    
    # Save test certificate
    test_cert_path = "test_certificate_with_seal.png"
    img.save(test_cert_path)
    print(f"✅ Test certificate created: {test_cert_path}")
    
    return test_cert_path

def test_seal_detection(image_path):
    """Test seal detection functionality."""
    print(f"\n🔍 Testing Seal Detection on: {image_path}")
    print("-" * 50)
    
    detector = SealDetector()
    
    # Detect and crop seals
    cropped_seals = detector.detect_and_crop_seals(image_path)
    
    print(f"Found {len(cropped_seals)} seal(s):")
    for i, seal in enumerate(cropped_seals):
        print(f"  Seal {i+1}:")
        print(f"    Method: {seal['method']}")
        print(f"    Confidence: {seal['confidence']:.2%}")
        print(f"    Saved as: {seal['image_path']}")
    
    return cropped_seals

def test_vit_classification(cropped_seals):
    """Test ViT seal classification."""
    print(f"\n🤖 Testing ViT Seal Classification")
    print("-" * 50)
    
    classifier = ViTSealClassifier()
    
    if not cropped_seals:
        print("No seals to classify")
        return
    
    # Test individual seals
    for i, seal in enumerate(cropped_seals):
        result = classifier.predict_image(seal['pil_image'])
        print(f"Seal {i+1} Classification:")
        print(f"  Status: {result.get('seal_status', 'Unknown')}")
        print(f"  Confidence: {result.get('confidence', 0):.2%}")
        print(f"  Reason: {result.get('reason', 'No reason')}")
    
    # Test multiple seals together
    if len(cropped_seals) > 1:
        seal_images = [seal['pil_image'] for seal in cropped_seals]
        combined_result = classifier.predict_multiple_seals(seal_images)
        print(f"\nCombined Result:")
        print(f"  Overall Status: {combined_result.get('seal_status', 'Unknown')}")
        print(f"  Overall Confidence: {combined_result.get('confidence', 0):.2%}")
        print(f"  Real Seals: {combined_result.get('real_count', 0)}")
        print(f"  Fake Seals: {combined_result.get('fake_count', 0)}")

def test_complete_system():
    """Test the complete certificate verification system."""
    print("🚀 Testing Complete Certificate Verification System")
    print("=" * 60)
    
    # Step 1: Create test certificate
    test_cert_path = create_test_certificate_with_seal()
    
    # Step 2: Test seal detection
    cropped_seals = test_seal_detection(test_cert_path)
    
    # Step 3: Test ViT classification
    test_vit_classification(cropped_seals)
    
    # Step 4: Show final verdict
    print(f"\n🎯 Final Verification Verdict")
    print("-" * 50)
    
    # Simulate OCR result (would normally come from OCR + database verification)
    ocr_status = "Pass"  # Assume OCR verification passed
    
    # Get seal status
    if cropped_seals:
        classifier = ViTSealClassifier()
        seal_images = [seal['pil_image'] for seal in cropped_seals]
        seal_result = classifier.predict_multiple_seals(seal_images)
        seal_status = seal_result.get('status', 'Fail')
    else:
        seal_status = "Fail"
    
    # Final decision
    final_decision = "AUTHENTIC" if (ocr_status == "Pass" and seal_status == "Pass") else "FAKE"
    
    print(f"📝 OCR Verification: {ocr_status}")
    print(f"🔎 Seal Verification: {seal_status}")
    print(f"🎉 Final Decision: {final_decision}")
    
    if final_decision == "AUTHENTIC":
        print("✅ Certificate is VERIFIED as AUTHENTIC!")
    else:
        print("❌ Certificate verification FAILED!")
    
    print(f"\n💡 Instructions:")
    print(f"1. Run 'streamlit run main.py' to start the web interface")
    print(f"2. Upload the test certificate: {test_cert_path}")
    print(f"3. Enable 'Seal Verification' in the sidebar")
    print(f"4. Click 'Verify Certificate' to see the complete verification")

if __name__ == "__main__":
    # Check if model exists
    if not os.path.exists('vit_seal_checker.pth'):
        print("❌ ViT model not found!")
        print("Please run 'python train_vit_seal_model.py' first to train the model.")
    else:
        test_complete_system()

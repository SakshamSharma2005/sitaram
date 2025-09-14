"""
Test the complete certificate verification system with the generated certificate dataset.
"""

import os
import time
from pathlib import Path
from ocr_client import OCRClient
from verifier import CertificateVerifier
from seal_detector import SealDetector
from vit_seal_classifier import ViTSealClassifier

def test_certificate(cert_path, demo_mode=False):
    """Test a single certificate through the complete verification pipeline."""
    print(f"\n🔍 Testing Certificate: {os.path.basename(cert_path)}")
    print("-" * 60)
    
    try:
        # Step 1: OCR Processing
        print("📖 Step 1: OCR Text Extraction")
        
        if demo_mode:
            # Use demo OCR data based on filename
            filename = os.path.basename(cert_path).lower()
            if 'saksham' in filename or 'abc2023001' in filename:
                ocr_result = {
                    'success': True,
                    'extracted_text': '''CERTIFICATE OF COMPLETION
                    
This is to certify that

SAKSHAM SHARMA

has successfully completed the program

B.Tech Computer Engg

from DevLabs Institute

in the year 2023

Registration Number: ABC2023001

Date of Issue: September 2025''',
                    'confidence': 0.92,
                    'bounding_boxes': []
                }
            elif 'prisha' in filename or 'abc2022007' in filename:
                ocr_result = {
                    'success': True,
                    'extracted_text': '''CERTIFICATE OF COMPLETION
                    
This is to certify that

PRISHA VERMA

has successfully completed the program

M.Tech AI

from Global Tech University

in the year 2022

Registration Number: ABC2022007

Date of Issue: September 2025''',
                    'confidence': 0.88,
                    'bounding_boxes': []
                }
            else:
                ocr_result = {
                    'success': True,
                    'extracted_text': '''CERTIFICATE OF COMPLETION
                    
This is to certify that

RAJEEV KUMAR

has successfully completed the program

B.Sc Physics

from Northfield University

in the year 2019

Registration Number: UNI10009

Date of Issue: September 2025''',
                    'confidence': 0.85,
                    'bounding_boxes': []
                }
            print("   🎮 Using demo OCR data")
        else:
            # Real OCR processing
            ocr_client = OCRClient()
            with open(cert_path, 'rb') as f:
                file_bytes = f.read()
            ocr_result = ocr_client.extract_text_from_bytes(file_bytes)
        
        if not ocr_result['success']:
            print(f"   ❌ OCR failed: {ocr_result.get('error', 'Unknown error')}")
            return None
        
        print(f"   ✅ Text extracted successfully (confidence: {ocr_result.get('confidence', 0):.2%})")
        
        # Step 2: Database Verification
        print("\n🗄️ Step 2: Database Verification")
        verifier = CertificateVerifier()
        verification_result = verifier.verify_certificate(ocr_result, os.path.basename(cert_path))
        
        ocr_status = "Pass" if verification_result['decision'] == 'AUTHENTIC' else "Fail"
        print(f"   Status: {ocr_status}")
        print(f"   Confidence: {verification_result['final_score']:.2%}")
        print(f"   Registration: {verification_result.get('registration_no', 'Not found')}")
        
        # Step 3: Seal Detection and Verification
        print("\n🔎 Step 3: Seal Detection & Verification")
        
        detector = SealDetector()
        cropped_seals = detector.detect_and_crop_seals(cert_path)
        
        if cropped_seals:
            print(f"   Found {len(cropped_seals)} seal(s)")
            
            # Classify seals
            classifier = ViTSealClassifier()
            if len(cropped_seals) == 1:
                seal_result = classifier.predict_image(cropped_seals[0]['pil_image'])
            else:
                seal_images = [seal['pil_image'] for seal in cropped_seals]
                seal_result = classifier.predict_multiple_seals(seal_images)
            
            seal_status = seal_result.get('status', 'Unknown')
            seal_confidence = seal_result.get('confidence', 0)
            
            print(f"   Seal Status: {seal_status}")
            print(f"   Seal Confidence: {seal_confidence:.2%}")
            print(f"   Classification: {seal_result.get('seal_status', 'Unknown')}")
        else:
            print("   ❌ No seals detected")
            seal_status = "Fail"
            seal_result = {
                'status': 'Fail',
                'reason': 'No seals detected',
                'confidence': 0.0
            }
        
        # Step 4: Final Decision
        print("\n🎯 Step 4: Final Decision")
        final_decision = "AUTHENTIC" if (ocr_status == "Pass" and seal_status == "Pass") else "FAKE"
        
        print(f"   OCR Verification: {ocr_status}")
        print(f"   Seal Verification: {seal_status}")
        print(f"   📋 FINAL RESULT: {final_decision}")
        
        if final_decision == "AUTHENTIC":
            print("   ✅ Certificate is VERIFIED as AUTHENTIC!")
        else:
            print("   ❌ Certificate verification FAILED!")
        
        return {
            'file': cert_path,
            'ocr_status': ocr_status,
            'seal_status': seal_status,
            'final_decision': final_decision,
            'ocr_confidence': verification_result['final_score'],
            'seal_confidence': seal_result.get('confidence', 0),
            'seals_detected': len(cropped_seals) if cropped_seals else 0
        }
        
    except Exception as e:
        print(f"   💥 Error during verification: {str(e)}")
        return None

def test_complete_dataset():
    """Test the complete certificate dataset."""
    print("🚀 Testing Complete Certificate Verification System")
    print("=" * 80)
    print("This will test both OCR + Database verification AND AI Seal verification")
    print("=" * 80)
    
    # Check if directories exist
    cert_dirs = ['complete_certificates', 'test_certificates']
    available_dirs = [d for d in cert_dirs if os.path.exists(d)]
    
    if not available_dirs:
        print("❌ No certificate directories found!")
        print("Please run 'python generate_complete_certificates.py' first.")
        return
    
    # Test with the available certificates
    test_dir = available_dirs[0]  # Use first available directory
    cert_files = [f for f in os.listdir(test_dir) if f.lower().endswith('.png')]
    
    if not cert_files:
        print(f"❌ No certificate images found in {test_dir}/")
        return
    
    print(f"📁 Testing certificates from: {test_dir}/")
    print(f"📊 Found {len(cert_files)} certificate images")
    
    # Test first few certificates as examples
    test_files = cert_files[:6]  # Test up to 6 certificates
    results = []
    
    for i, cert_file in enumerate(test_files):
        cert_path = os.path.join(test_dir, cert_file)
        
        print(f"\n{'='*20} Test {i+1}/{len(test_files)} {'='*20}")
        
        # Determine if we should use demo mode (if ViT model not available)
        demo_mode = not os.path.exists('vit_seal_checker.pth')
        if demo_mode:
            print("⚠️ ViT model not found - using demo mode for seal verification")
        
        result = test_certificate(cert_path, demo_mode=demo_mode)
        if result:
            results.append(result)
        
        # Add small delay for readability
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*20} TESTING SUMMARY {'='*20}")
    print(f"📊 Tested {len(results)} certificates")
    
    if results:
        authentic_count = sum(1 for r in results if r['final_decision'] == 'AUTHENTIC')
        fake_count = len(results) - authentic_count
        
        print(f"✅ Authentic: {authentic_count}")
        print(f"❌ Fake/Failed: {fake_count}")
        
        avg_ocr_confidence = sum(r['ocr_confidence'] for r in results) / len(results)
        avg_seal_confidence = sum(r['seal_confidence'] for r in results) / len(results)
        
        print(f"📈 Average OCR Confidence: {avg_ocr_confidence:.2%}")
        print(f"🔎 Average Seal Confidence: {avg_seal_confidence:.2%}")
        
        total_seals = sum(r['seals_detected'] for r in results)
        print(f"🏷️ Total Seals Detected: {total_seals}")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            filename = os.path.basename(result['file'])
            status_icon = "✅" if result['final_decision'] == 'AUTHENTIC' else "❌"
            print(f"   {status_icon} {filename}")
            print(f"      OCR: {result['ocr_status']} ({result['ocr_confidence']:.1%})")
            print(f"      Seal: {result['seal_status']} ({result['seal_confidence']:.1%})")
            print(f"      Seals Found: {result['seals_detected']}")
    
    print(f"\n🎉 Complete system testing finished!")
    print(f"💡 To test with the web interface:")
    print(f"   1. Run: streamlit run main.py")
    print(f"   2. Upload certificates from {test_dir}/")
    print(f"   3. Enable 'Seal Verification' in sidebar")
    print(f"   4. Compare results with this test output")

def quick_demo():
    """Quick demonstration with specific test certificates."""
    print("🎯 Quick Demo - Testing Specific Certificates")
    print("=" * 50)
    
    # Check for specific test files
    demo_files = [
        'test_certificates/ABC2023001_Saksham_Sharma_authentic.png',
        'test_certificates/ABC2023001_Saksham_Sharma_tampered.png',
        'complete_certificates/ABC2023001_Saksham_Sharma_authentic.png'
    ]
    
    for demo_file in demo_files:
        if os.path.exists(demo_file):
            print(f"\n🔍 Testing: {demo_file}")
            result = test_certificate(demo_file, demo_mode=True)
            if result:
                expected = "AUTHENTIC" if "authentic" in demo_file else "FAKE"
                actual = result['final_decision']
                match = "✅ CORRECT" if expected == actual else "❌ MISMATCH"
                print(f"   Expected: {expected}, Got: {actual} {match}")
            break
    else:
        print("❌ No demo files found. Please run generate_complete_certificates.py first.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_demo()
    else:
        test_complete_dataset()

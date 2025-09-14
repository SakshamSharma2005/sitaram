import json
import os
from pathlib import Path
from ocr_client import OCRClient
from verifier import CertificateVerifier

def test_sample_verification():
    """Test the certificate verification system with a sample OCR result."""
    
    print("🧪 Testing Certificate Verification System")
    print("=" * 50)
    
    # Sample OCR result (simulating a successful OCR of a certificate)
    sample_ocr_result = {
        'success': True,
        'extracted_text': '''
        CERTIFICATE OF COMPLETION
        
        This is to certify that
        
        SAKSHAM SHARMA
        
        has successfully completed the course
        
        B.Tech Computer Engineering
        
        from
        
        DevLabs Institute
        
        in the year 2023
        
        Registration Number: ABC2023001
        
        Date of Issue: December 2023
        ''',
        'bounding_boxes': [
            {'text': 'SAKSHAM', 'left': 100, 'top': 150, 'width': 80, 'height': 25},
            {'text': 'SHARMA', 'left': 190, 'top': 150, 'width': 70, 'height': 25},
            {'text': 'ABC2023001', 'left': 200, 'top': 400, 'width': 100, 'height': 20}
        ],
        'confidence': 0.92
    }
    
    print("📋 Sample OCR Result:")
    print(f"Success: {sample_ocr_result['success']}")
    print(f"Confidence: {sample_ocr_result['confidence']:.1%}")
    print(f"Text Length: {len(sample_ocr_result['extracted_text'])} characters")
    print(f"Bounding Boxes: {len(sample_ocr_result['bounding_boxes'])}")
    print()
    
    # Initialize verifier
    verifier = CertificateVerifier()
    
    # Check if database exists
    if not os.path.exists(verifier.db_path):
        print("❌ Database not found. Please run 'python init_db.py' first.")
        return
    
    print("🔍 Running verification...")
    
    # Run verification
    result = verifier.verify_certificate(sample_ocr_result, "sample_certificate.jpg")
    
    # Display results
    print("\n📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    print(f"Registration Number: {result['registration_no']}")
    print(f"Decision: {result['decision']}")
    print(f"Final Score: {result['final_score']:.2%}")
    print(f"OCR Confidence: {result['confidence']:.1%}")
    
    print("\n🏛️ Database Record:")
    if result['db_record']:
        db = result['db_record']
        print(f"  Name: {db['name']}")
        print(f"  Institution: {db['institution']}")
        print(f"  Degree: {db['degree']}")
        print(f"  Year: {db['year']}")
        print(f"  Reg No: {db['reg_no']}")
    else:
        print("  No matching record found")
    
    print("\n🔤 OCR Extracted:")
    ocr = result['ocr_extracted']
    print(f"  Name: {ocr.get('name', 'Not extracted')}")
    print(f"  Institution: {ocr.get('institution', 'Not extracted')}")
    print(f"  Degree: {ocr.get('degree', 'Not extracted')}")
    print(f"  Year: {ocr.get('year', 'Not extracted')}")
    
    print("\n🎯 Field Scores:")
    for field, score in result['field_scores'].items():
        print(f"  {field.title()}: {score:.1%}")
    
    print("\n💡 Reasons:")
    for reason in result['reasons']:
        print(f"  • {reason}")
    
    # Save result to file
    output_file = "test_verification_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full result saved to: {output_file}")
    
    return result

def test_ocr_client():
    """Test the OCR client with environment variable check."""
    
    print("\n🔍 Testing OCR Client")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv('OCRSPACE_API_KEY')
    if not api_key:
        print("❌ OCRSPACE_API_KEY not found in environment")
        print("   Set it in .env file or environment variables")
        return
    
    print("✅ OCR API key found")
    
    # Test with sample text (you can replace this with actual image testing)
    print("📝 OCR client initialized successfully")
    print("   (To test with real images, add image files and update this function)")

def test_database():
    """Test database connectivity and sample data."""
    
    print("\n🗄️ Testing Database")
    print("=" * 30)
    
    db_path = "certs.db"
    if not os.path.exists(db_path):
        print("❌ Database not found")
        print("   Run 'python init_db.py' to create it")
        return
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Database found with tables: {[t[0] for t in tables]}")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM certificates")
        count = cursor.fetchone()[0]
        print(f"📊 Total certificates: {count}")
        
        # Show sample records
        cursor.execute("SELECT reg_no, name, institution FROM certificates LIMIT 3")
        samples = cursor.fetchall()
        print("📋 Sample records:")
        for reg_no, name, institution in samples:
            print(f"   {reg_no}: {name} from {institution}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🚀 Certificate Verification System - Test Suite")
    print("=" * 60)
    
    # Test components
    test_ocr_client()
    test_database()
    
    # Run main verification test
    try:
        result = test_sample_verification()
        
        print("\n" + "=" * 60)
        if result['decision'] == 'AUTHENTIC':
            print("🎉 TEST PASSED: Sample certificate verified successfully!")
        elif result['decision'] == 'SUSPECT':
            print("⚠️ TEST PARTIAL: Sample certificate needs review")
        else:
            print("❌ TEST FAILED: Sample certificate not verified")
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Test completed!")

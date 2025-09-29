from verifier import CertificateVerifier

# Test the updated verifier
verifier = CertificateVerifier()

# Test text extraction
test_text = """VISVESVARAYA TECHNOLOGICAL UNIVERSITY, BELAGA VI
KARNATAKA, INDIA
GRADE CARD
B.E. Computer Science & Engineering August 2020
TEUG 1B 19C100
Name of the Student: VIKRAM VERMA
Father o / Mothers Name : ASHOK VERMA
Name of the College: B.N.M. INSTITUTE OF TECHNOLOGY, BANGALORE
USN: 1BG19CS100"""

print("=== Testing Registration Number Extraction ===")
reg_numbers = verifier._extract_registration_numbers(test_text)
print(f"Extracted registration numbers: {reg_numbers}")

print("\n=== Testing Database Lookup ===")
for reg_no in reg_numbers:
    print(f"\nLooking up: {reg_no}")
    result = verifier._lookup_registration(reg_no)
    if result:
        print(f"✅ Found: {result['name']} (USN: {result.get('usn', 'N/A')})")
        print(f"   Father: {result.get('father_name', 'N/A')}")
        print(f"   Institution: {result.get('institution', 'N/A')}")
    else:
        print(f"❌ Not found in database")

print("\n=== Testing Full Verification ===")
mock_ocr = {
    'extracted_text': test_text,
    'confidence': 0.95,
    'success': True
}
verification_result = verifier.verify_certificate(mock_ocr)
print(f"Decision: {verification_result['decision']}")
print(f"Final Score: {verification_result['final_score']:.2f}")
print(f"Registration No: {verification_result['registration_no']}")
if verification_result['db_record']:
    print(f"Matched: {verification_result['db_record']['name']}")
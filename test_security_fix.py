"""
Test script to verify the security fix for fake seal detection
"""

# Mock test scenarios
def test_security_logic():
    """Test the new security-first verification logic"""
    
    print("=== Testing Security-First Verification Logic ===\n")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Scenario 1: Good OCR + Fake Seals (HIGH CONFIDENCE)",
            "ocr_status": "Pass",
            "ocr_confidence": 0.95,
            "seal_status": "Fail", 
            "seal_confidence": 0.85,
            "fake_seals": 3,
            "total_seals": 3,
            "expected": "Fake"
        },
        {
            "name": "Scenario 2: Good OCR + Good Seals",
            "ocr_status": "Pass", 
            "ocr_confidence": 0.95,
            "seal_status": "Pass",
            "seal_confidence": 0.90,
            "fake_seals": 0,
            "total_seals": 2,
            "expected": "Real"
        },
        {
            "name": "Scenario 3: Good OCR + Fake Seals (LOW CONFIDENCE)",
            "ocr_status": "Pass",
            "ocr_confidence": 0.95, 
            "seal_status": "Fail",
            "seal_confidence": 0.60,  # Below 0.7 threshold
            "fake_seals": 2,
            "total_seals": 2,
            "expected": "Fake"  # Still fail because seal status is fail
        },
        {
            "name": "Scenario 4: Poor OCR + Good Seals", 
            "ocr_status": "Fail",
            "ocr_confidence": 0.60,
            "seal_status": "Pass",
            "seal_confidence": 0.90,
            "fake_seals": 0,
            "total_seals": 1,
            "expected": "Fake"  # Fail because OCR failed
        },
        {
            "name": "Scenario 5: No Seal Verification + Good OCR",
            "ocr_status": "Pass",
            "ocr_confidence": 0.90,
            "seal_status": None,
            "seal_confidence": 0,
            "fake_seals": None,
            "total_seals": None,
            "expected": "Real"
        }
    ]
    
    for scenario in scenarios:
        print(f"🧪 {scenario['name']}")
        print(f"   OCR: {scenario['ocr_status']} ({scenario['ocr_confidence']:.1%})")
        if scenario['seal_status']:
            print(f"   Seals: {scenario['seal_status']} ({scenario['seal_confidence']:.1%}) - {scenario['fake_seals']}/{scenario['total_seals']} fake")
        else:
            print(f"   Seals: No verification performed")
        
        # Apply our security logic
        result = apply_security_logic(scenario)
        status = "✅ PASS" if result == scenario['expected'] else "❌ FAIL"
        
        print(f"   Expected: {scenario['expected']}")
        print(f"   Actual: {result}")
        print(f"   Test: {status}")
        print()

def apply_security_logic(scenario):
    """Apply the new security-first logic"""
    
    ocr_status = scenario['ocr_status']
    ocr_confidence = scenario['ocr_confidence']
    seal_status = scenario['seal_status'] 
    seal_confidence = scenario['seal_confidence']
    fake_seals = scenario['fake_seals']
    
    # Security-first decision criteria:
    both_pass = (ocr_status == "Pass" and seal_status == "Pass")
    
    # CRITICAL SECURITY CHECK: If fake seals detected with high confidence, REJECT
    fake_seals_detected = False
    if fake_seals is not None and fake_seals > 0 and seal_confidence > 0.7:
        fake_seals_detected = True
    
    # REJECT if fake seals detected with high confidence
    if fake_seals_detected:
        return "Fake"
    else:
        # Only pass if both OCR and seals pass, or if no seal verification was performed
        if seal_status is None:  # No seal verification
            return "Real" if (ocr_status == "Pass" and ocr_confidence > 0.8) else "Fake"
        else:  # Seal verification was performed
            return "Real" if both_pass else "Fake"

if __name__ == "__main__":
    test_security_logic()
    print("🔒 Security test completed!")
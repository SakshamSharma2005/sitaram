import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from PIL import Image
import time

from ocr_client import OCRClient
from verifier import CertificateVerifier
from seal_detector import SealDetector
from vit_seal_classifier import ViTSealClassifier

# Page configuration
st.set_page_config(
    page_title="Certificate Verification System",
    page_icon="🎓",
    layout="wide"
)

def init_session_state():
    """Initialize session state variables."""
    if 'verification_result' not in st.session_state:
        st.session_state.verification_result = None
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    if 'seal_result' not in st.session_state:
        st.session_state.seal_result = None
    if 'cropped_seals' not in st.session_state:
        st.session_state.cropped_seals = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

def display_verification_result(result, seal_result=None):
    """Display the verification result in a structured format."""
    
    # Final Decision Card
    st.subheader("🎯 Final Verification Decision")
    
    # Determine final decision based on OCR and Seal results
    ocr_status = "Pass" if result['decision'] == 'AUTHENTIC' else "Fail"
    seal_status = seal_result.get('status', 'Unknown') if seal_result else 'Unknown'
    
    # Final decision logic: Both OCR and Seal must pass
    final_decision = "Real" if (ocr_status == "Pass" and seal_status == "Pass") else "Fake"
    
    # Display final decision with color coding
    if final_decision == "Real":
        st.success("🎉 **CERTIFICATE VERIFIED AS AUTHENTIC** ✅")
    else:
        st.error("❌ **CERTIFICATE VERIFICATION FAILED** ❌")
    
    # Create columns for results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Final Decision", final_decision)
    
    with col2:
        combined_confidence = (result['final_score'] + seal_result.get('confidence', 0.5)) / 2 if seal_result else result['final_score']
        st.metric("Overall Confidence", f"{combined_confidence:.2%}")
    
    with col3:
        reg_no = result['registration_no'] or 'Not Found'
        st.info(f"**Registration:** {reg_no}")
    
    # Step-by-step results
    st.markdown("---")
    st.subheader("📋 Verification Steps")
    
    # Step 1: OCR Verification
    with st.container():
        st.markdown("### Step 1: OCR Text Verification")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if ocr_status == "Pass":
                st.success("✅ PASS")
            else:
                st.error("❌ FAIL")
        
        with col2:
            decision = result['decision']
            if decision == 'AUTHENTIC':
                st.write("✅ Certificate text matches database records")
            elif decision == 'SUSPECT':
                st.write("⚠️ Certificate text has discrepancies - requires review")
            else:
                st.write("❌ Certificate text does not match database records")
            
            st.metric("OCR Confidence", f"{result['final_score']:.2%}")
    
    # Step 2: Seal Verification
    with st.container():
        st.markdown("### Step 2: Seal/Stamp Verification")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if seal_result:
                if seal_result.get('status') == 'Pass':
                    st.success("✅ PASS")
                else:
                    st.error("❌ FAIL")
            else:
                st.warning("⚠️ NOT CHECKED")
        
        with col2:
            if seal_result:
                reason = seal_result.get('reason', 'No reason provided')
                st.write(reason)
                if 'confidence' in seal_result:
                    st.metric("Seal Confidence", f"{seal_result['confidence']:.2%}")
                
                # Show individual seal results if available
                if 'individual_predictions' in seal_result:
                    with st.expander(f"📸 Individual Seal Results ({len(seal_result['individual_predictions'])} seals found)"):
                        for i, pred in enumerate(seal_result['individual_predictions']):
                            st.write(f"**Seal {i+1}:** {pred.get('seal_status', 'Unknown')} ({pred.get('confidence', 0):.1%} confidence)")
            else:
                st.write("⚠️ Seal verification not performed")
                st.info("Enable seal verification in the sidebar to check seal authenticity")
    
    # Detailed results in expandable sections
    st.markdown("---")
    
    with st.expander("📋 Detailed OCR Verification Results", expanded=False):
        # Database record vs OCR extracted
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Database Record:**")
            if result['db_record']:
                db_record = result['db_record']
                st.json({
                    'Name': db_record['name'],
                    'Institution': db_record['institution'], 
                    'Degree': db_record['degree'],
                    'Year': db_record['year'],
                    'Reg No': db_record['reg_no']
                })
            else:
                st.write("No matching record found")
        
        with col2:
            st.write("**OCR Extracted:**")
            ocr_data = result['ocr_extracted']
            st.json({
                'Name': ocr_data.get('name', 'Not extracted'),
                'Institution': ocr_data.get('institution', 'Not extracted'),
                'Degree': ocr_data.get('degree', 'Not extracted'),
                'Year': ocr_data.get('year', 'Not extracted')
            })
        
        # Field scores
        if result['field_scores']:
            st.subheader("🎯 Field Comparison Scores")
            for field, score in result['field_scores'].items():
                st.progress(score, text=f"{field.title()}: {score:.1%}")
        
        # Reasons
        st.subheader("💡 Analysis Reasons")
        for reason in result['reasons']:
            st.write(f"• {reason}")
        
        # Raw OCR text
        with st.expander("📄 Raw OCR Text"):
            st.text(ocr_data.get('raw_text', 'No text extracted'))
    
    # Show cropped seals if available
    if st.session_state.cropped_seals:
        with st.expander("🔍 Detected Seals/Stamps", expanded=True):
            st.write(f"Found {len(st.session_state.cropped_seals)} seal(s) in the certificate:")
            
            cols = st.columns(min(3, len(st.session_state.cropped_seals)))
            for i, seal_info in enumerate(st.session_state.cropped_seals):
                with cols[i % 3]:
                    st.image(seal_info['pil_image'], caption=f"Seal {i+1} ({seal_info['method']} detection)")
                    st.write(f"Confidence: {seal_info['confidence']:.2%}")

def create_verification_report(result, seal_result=None):
    """Create a downloadable verification report."""
    
    # Determine final decision
    ocr_status = "Pass" if result['decision'] == 'AUTHENTIC' else "Fail"
    seal_status = seal_result.get('status', 'Not Checked') if seal_result else 'Not Checked'
    final_decision = "Real" if (ocr_status == "Pass" and seal_status == "Pass") else "Fake"
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'final_decision': final_decision,
        'ocr_verification': {
            'status': ocr_status,
            'decision': result['decision'],
            'confidence_score': result['final_score'],
            'registration_number': result['registration_no'],
            'database_match': result['db_record'] is not None,
            'details': result
        },
        'seal_verification': seal_result if seal_result else {
            'status': 'Not Checked',
            'reason': 'Seal verification was not performed'
        },
        'summary': {
            'final_decision': final_decision,
            'ocr_status': ocr_status,
            'seal_status': seal_status,
            'overall_confidence': (result['final_score'] + seal_result.get('confidence', 0.5)) / 2 if seal_result else result['final_score']
        }
    }
    
    return json.dumps(report, indent=2, ensure_ascii=False)

def main():
    """Main Streamlit application."""
    
    init_session_state()
    
    st.title("🎓 Certificate Verification System")
    st.markdown("Upload a certificate image to verify its authenticity against our database.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key status
        api_key = os.getenv('OCRSPACE_API_KEY')
        if api_key:
            st.success("✅ OCR API Key configured")
        else:
            st.error("❌ OCR API Key not found")
            st.write("Please set OCRSPACE_API_KEY in your .env file")
        
        # Database status
        db_path = "certs.db"
        if os.path.exists(db_path):
            st.success("✅ Database connected")
            
            # Show database stats
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM certificates")
                count = cursor.fetchone()[0]
                st.info(f"📊 {count} certificates in database")
                conn.close()
            except:
                st.warning("⚠️ Database error")
        else:
            st.error("❌ Database not found")
            st.write("Please run `python init_db.py` first")
        
        # OCR Settings
        st.subheader("🔧 OCR Settings")
        ocr_language = st.selectbox("Language", ["eng", "ara", "chs", "cht", "cze", "dan", "dut", "fin", "fre", "ger", "hun", "ita", "jpn", "kor", "nor", "pol", "por", "rus", "slv", "spa", "swe", "tur"])
        use_overlay = st.checkbox("Extract bounding boxes", value=True)
        
        # Demo Mode
        st.subheader("🎮 Demo Mode")
        demo_mode = st.checkbox("Use Demo Mode (Skip OCR)", help="Test verification with sample OCR data")
        
        # Seal Verification Settings
        st.subheader("🔎 Seal Verification")
        enable_seal_verification = st.checkbox("Enable Seal Verification", value=True, help="Detect and verify seals/stamps using AI")
        
        if enable_seal_verification:
            # Check if ViT model exists
            model_exists = os.path.exists('vit_seal_checker.pth')
            if model_exists:
                st.success("✅ ViT model ready")
            else:
                st.warning("⚠️ ViT model not found")
                st.info("Run train_vit_seal_model.py to train the model, or use demo mode")
            
            seal_demo_mode = st.checkbox("Seal Demo Mode", value=not model_exists, help="Use demo predictions for seal verification")
    
    # Main interface
    if not api_key:
        st.error("🚨 **Setup Required**: Please configure your OCR.space API key in the .env file before proceeding.")
        st.code("OCRSPACE_API_KEY=your_api_key_here")
        st.info("💡 **Alternative**: Enable 'Demo Mode' in the sidebar to test without OCR")
        return
    
    if not os.path.exists(db_path):
        st.error("🚨 **Setup Required**: Please initialize the database first.")
        st.code("python init_db.py")
        return
    
    # OCR Troubleshooting
    with st.expander("🔧 OCR Troubleshooting Guide"):
        st.markdown("""
        **If you're getting E301 errors:**
        
        1. **✅ Try Demo Mode**: Enable in sidebar to test verification without OCR
        2. **📸 Image Quality**: Use clear, well-lit, straight-aligned certificates
        3. **📁 File Format**: JPG/PNG work best (avoid PDF, TIFF)
        4. **📏 File Size**: Keep under 1MB (system auto-resizes but quality matters)
        5. **🎯 Text Clarity**: Ensure certificate text is readable and high-contrast
        
        **Demo Mode includes sample certificates:**
        - Saksham Sharma (ABC2023001) - DevLabs Institute
        - Prisha Verma (ABC2022007) - Global Tech University
        
        Upload any image and enable Demo Mode to see how verification works!
        """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a certificate image",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Upload a clear image of the certificate you want to verify"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
        # Display uploaded image
        if uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Certificate", use_container_width=True)
        
        # Verify button
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔍 Verify Certificate", type="primary"):
                verify_certificate(uploaded_file, ocr_language, use_overlay, demo_mode, 
                                 enable_seal_verification, seal_demo_mode if enable_seal_verification else False)
        
        with col2:
            if st.session_state.verification_result:
                report_json = create_verification_report(st.session_state.verification_result, st.session_state.seal_result)
                st.download_button(
                    "📥 Download Report",
                    data=report_json,
                    file_name=f"verification_report_{int(time.time())}.json",
                    mime="application/json"
                )
    
    # Display results
    if st.session_state.verification_result:
        st.markdown("---")
        display_verification_result(st.session_state.verification_result, st.session_state.seal_result)
        
        # Option to verify another certificate
        if st.button("🔄 Verify Another Certificate"):
            st.session_state.verification_result = None
            st.session_state.ocr_result = None
            st.session_state.seal_result = None
            st.session_state.cropped_seals = None
            st.session_state.uploaded_file = None
            st.rerun()

def verify_certificate(uploaded_file, language, use_overlay, demo_mode=False, enable_seal_verification=True, seal_demo_mode=False):
    """Process the certificate verification."""
    
    try:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📤 Processing file...")
        progress_bar.progress(5)
        
        # Read file data (reset file pointer first)
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        if len(file_bytes) == 0:
            st.error("❌ File appears to be empty or corrupted. Please try uploading again.")
            progress_bar.empty()
            status_text.empty()
            return
        
        # Save uploaded file temporarily for seal detection
        temp_image_path = None
        if enable_seal_verification and uploaded_file.type.startswith('image'):
            temp_dir = tempfile.mkdtemp()
            temp_image_path = os.path.join(temp_dir, f"temp_cert_{int(time.time())}.{uploaded_file.name.split('.')[-1]}")
            
            with open(temp_image_path, 'wb') as f:
                f.write(file_bytes)
        
        if demo_mode:
            # Use demo OCR data
            status_text.text("🎮 Using demo OCR data...")
            progress_bar.progress(30)
            
            # Sample OCR result based on filename or random selection
            demo_certificates = {
                "saksham": {
                    'success': True,
                    'extracted_text': '''CERTIFICATE OF COMPLETION
                    
This is to certify that

SAKSHAM SHARMA

has successfully completed the course

B.Tech Computer Engineering

from

DevLabs Institute

in the year 2023

Registration Number: ABC2023001

Date of Issue: December 2023''',
                    'confidence': 0.92,
                    'bounding_boxes': []
                },
                "prisha": {
                    'success': True,
                    'extracted_text': '''GRADUATION CERTIFICATE
                    
This certifies that

PRISHA VERMA

has completed

M.Tech AI

from

Global Tech University

Year: 2022

Registration: ABC2022007''',
                    'confidence': 0.88,
                    'bounding_boxes': []
                }
            }
            
            # Select demo data based on filename
            filename_lower = uploaded_file.name.lower()
            if 'saksham' in filename_lower or 'abc2023001' in filename_lower:
                ocr_result = demo_certificates["saksham"]
            elif 'prisha' in filename_lower or 'abc2022007' in filename_lower:
                ocr_result = demo_certificates["prisha"]
            else:
                # Default to Saksham's certificate
                ocr_result = demo_certificates["saksham"]
                
            st.info("🎮 Demo Mode: Using sample OCR data for testing")
            
        else:
            # Real OCR processing
            status_text.text("🔍 Running OCR analysis...")
            progress_bar.progress(20)
            
            # Run OCR
            ocr_client = OCRClient()
            ocr_result = ocr_client.extract_text_from_bytes(
                file_bytes,
                language=language,
                overlay=use_overlay
            )
        
        st.session_state.ocr_result = ocr_result
        
        if not ocr_result['success']:
            st.error(f"❌ OCR failed: {ocr_result.get('error', 'Unknown error')}")
            if not demo_mode:
                st.info("💡 **Tip**: Try enabling 'Demo Mode' in the sidebar to test the verification system without OCR")
            progress_bar.empty()
            status_text.empty()
            return
        
        status_text.text("🔍 Verifying against database...")
        progress_bar.progress(50)
        
        # Run OCR verification
        verifier = CertificateVerifier()
        verification_result = verifier.verify_certificate(ocr_result, uploaded_file.name)
        
        st.session_state.verification_result = verification_result
        
        # Step 2: Seal Verification
        seal_result = None
        if enable_seal_verification and temp_image_path:
            status_text.text("🔎 Detecting and verifying seals...")
            progress_bar.progress(70)
            
            try:
                # Import ViT classifier at the beginning to ensure it's available
                classifier = ViTSealClassifier()
                
                if seal_demo_mode:
                    # Use demo seal verification
                    seal_result = classifier.create_dummy_prediction(confidence=0.82)
                    st.session_state.cropped_seals = []  # No actual cropped seals in demo mode
                else:
                    # Real seal detection and verification
                    seal_detector = SealDetector()
                    cropped_seals = seal_detector.detect_and_crop_seals(temp_image_path)
                    st.session_state.cropped_seals = cropped_seals
                    
                    if cropped_seals:
                        # Classify detected seals
                        seal_images = [seal['pil_image'] for seal in cropped_seals]
                        seal_result = classifier.predict_multiple_seals(seal_images)
                    else:
                        seal_result = {
                            "step": "Seal Verification",
                            "status": "Fail",
                            "reason": "No seals detected in certificate",
                            "seal_status": "Fake",
                            "confidence": 0.0
                        }
                
            except Exception as e:
                st.warning(f"⚠️ Seal verification error: {str(e)}")
                seal_result = {
                    "step": "Seal Verification", 
                    "status": "Error",
                    "reason": f"Seal verification failed: {str(e)}",
                    "seal_status": "Error",
                    "confidence": 0.0
                }
            
            # Clean up temp file
            try:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                    os.rmdir(os.path.dirname(temp_image_path))
            except:
                pass
        
        st.session_state.seal_result = seal_result
        
        status_text.text("✅ Verification complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Show success message
        ocr_status = "Pass" if verification_result['decision'] == 'AUTHENTIC' else "Fail"
        seal_status = seal_result.get('status', 'Unknown') if seal_result else 'Not Checked'
        final_decision = "Real" if (ocr_status == "Pass" and seal_status == "Pass") else "Fake"
        
        if final_decision == "Real":
            st.success("🎉 Certificate verification completed - AUTHENTIC!")
        else:
            st.error("❌ Certificate verification failed - verification issues detected.")
        
        if seal_result and enable_seal_verification:
            st.info(f"🔎 Seal verification: {seal_result.get('seal_status', 'Unknown')}")
    
    except Exception as e:
        st.error(f"💥 Verification failed: {str(e)}")
        # Clear progress indicators
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()

if __name__ == "__main__":
    main()

import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from PIL import Image
import time

from ocr_client import OCRClient
from verifier import CertificateVerifier

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
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

def display_verification_result(result):
    """Display the verification result in a structured format."""
    
    # Main result
    col1, col2, col3 = st.columns(3)
    
    with col1:
        decision = result['decision']
        if decision == 'AUTHENTIC':
            st.success(f"✅ **{decision}**")
        elif decision == 'SUSPECT':
            st.warning(f"⚠️ **{decision}**")
        else:
            st.error(f"❌ **{decision}**")
    
    with col2:
        st.metric("Confidence Score", f"{result['final_score']:.2%}")
    
    with col3:
        reg_no = result['registration_no'] or 'Not Found'
        st.info(f"**Registration:** {reg_no}")
    
    # Detailed results
    st.subheader("📋 Verification Details")
    
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

def create_verification_report(result):
    """Create a downloadable verification report."""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'verification_result': result,
        'summary': {
            'decision': result['decision'],
            'confidence_score': result['final_score'],
            'registration_number': result['registration_no'],
            'database_match': result['db_record'] is not None
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
                verify_certificate(uploaded_file, ocr_language, use_overlay, demo_mode)
        
        with col2:
            if st.session_state.verification_result:
                report_json = create_verification_report(st.session_state.verification_result)
                st.download_button(
                    "📥 Download Report",
                    data=report_json,
                    file_name=f"verification_report_{int(time.time())}.json",
                    mime="application/json"
                )
    
    # Display results
    if st.session_state.verification_result:
        st.markdown("---")
        display_verification_result(st.session_state.verification_result)
        
        # Option to verify another certificate
        if st.button("🔄 Verify Another Certificate"):
            st.session_state.verification_result = None
            st.session_state.ocr_result = None
            st.session_state.uploaded_file = None
            st.rerun()

def verify_certificate(uploaded_file, language, use_overlay, demo_mode=False):
    """Process the certificate verification."""
    
    try:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📤 Processing file...")
        progress_bar.progress(10)
        
        # Read file data (reset file pointer first)
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        if len(file_bytes) == 0:
            st.error("❌ File appears to be empty or corrupted. Please try uploading again.")
            progress_bar.empty()
            status_text.empty()
            return
        
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
            progress_bar.progress(30)
            
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
        progress_bar.progress(70)
        
        # Run verification
        verifier = CertificateVerifier()
        verification_result = verifier.verify_certificate(ocr_result, uploaded_file.name)
        
        st.session_state.verification_result = verification_result
        
        status_text.text("✅ Verification complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Show success message
        decision = verification_result['decision']
        if decision == 'AUTHENTIC':
            st.success("🎉 Certificate verification completed successfully!")
        elif decision == 'SUSPECT':
            st.warning("⚠️ Certificate requires manual review.")
        else:
            st.error("❌ Certificate could not be verified.")
    
    except Exception as e:
        st.error(f"💥 Verification failed: {str(e)}")
        # Clear progress indicators
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()

if __name__ == "__main__":
    main()

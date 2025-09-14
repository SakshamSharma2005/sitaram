# 🎓 AI-Powered Certificate Verification System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47+-red.svg)](https://streamlit.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.7+-orange.svg)](https://pytorch.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12+-green.svg)](https://opencv.org)

An advanced certificate verification system that combines **OCR text extraction**, **database validation**, and **AI-powered seal verification** using Vision Transformer (ViT) models. This system can detect forged certificates by analyzing both textual content and institutional seals/stamps.

## 🚀 Key Features

### 🔍 **Dual Verification System**
- **OCR Text Verification**: Extracts and validates certificate text using OCR.space API
- **AI Seal Verification**: Uses Vision Transformer to classify institutional seals as real or fake
- **Database Cross-Reference**: Validates registration numbers against institutional records
- **Combined Decision Logic**: Makes final authenticity decisions based on multiple verification steps

### 🤖 **Advanced AI Components**
- **Vision Transformer (ViT)**: Fine-tuned `google/vit-base-patch16-224` model for seal classification
- **Computer Vision**: OpenCV-based seal detection with multiple algorithms (HoughCircles, contour analysis)
- **Deep Learning**: 100% validation accuracy on training dataset
- **Real-time Processing**: Fast inference for instant verification results

### 🎯 **Web Interface**
- **Streamlit Dashboard**: User-friendly web interface
- **Real-time Results**: Live verification with progress indicators
- **Visual Feedback**: Step-by-step verification process display
- **Seal Visualization**: Shows detected and cropped seal regions

## 📋 System Architecture

```
Certificate Image → OCR Extraction → Database Verification
                                         ↓
     ← Final Decision ← AI Classification ← Seal Detection
├── train_vit_seal_model.py     # ViT model training script
├── generate_seal_dataset.py    # Seal dataset generation
├── test_complete_system.py     # Complete system testing
├── test_sample.py              # Test suite with sample data
├── requirements.txt            # Python dependencies (includes AI libraries)
├── README.md                   # This file
├── .env                        # Environment variables (create this)
├── certs.db                    # SQLite database (created by init_db.py)
├── vit_seal_checker.pth        # Trained ViT model (created by training)
├── vit_model_info.json         # Model performance info
├── seal_dataset/               # AI training dataset
│   ├── train/
│   │   ├── real/              # Authentic seals (30 images)
│   │   └── fake/              # Fake seals (30 images)
│   └── val/
│       ├── real/              # Validation real seals (10 images)
│       └── fake/              # Validation fake seals (10 images)
├── cropped_seals/              # Detected seal regions
└── sample_certificates/        # Sample certificate images
```eamlit that uses OCR to extract text from certificate images, AI-powered seal verification, and verifies them against a local database.

## 🎯 Features

### Core Verification
- **Streamlit Web Interface**: User-friendly interface for certificate upload and verification
- **OCR Integration**: Uses OCR.space API for text extraction from certificate images
- **Database Verification**: Compares extracted data against a local SQLite database
- **Fuzzy Matching**: Intelligent field comparison with configurable similarity thresholds
- **Confidence Scoring**: Multi-factor confidence scoring with weighted field comparison

### AI-Powered Seal Verification
- **Seal Detection**: Automatic detection of seals, stamps, and signatures using computer vision
- **Vision Transformer (ViT)**: Pre-trained AI model fine-tuned for seal authenticity classification
- **Multi-Method Detection**: Uses circular detection, contour analysis, and template matching
- **Real vs Fake Classification**: Classifies detected seals as authentic or tampered/fake
- **Confidence Analysis**: Provides confidence scores for individual and combined seal results

### User Experience
- **Visual Feedback**: Clear verification results with step-by-step analysis
- **Report Generation**: Downloadable JSON verification reports with OCR and seal results
- **Demo Mode**: Test both OCR and seal verification without API calls
- **Detected Seal Display**: Shows cropped seal images with classification results
- **Final Decision Logic**: Combines OCR and seal verification for overall authenticity decision

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files
cd certificate-verification

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
# Get your free API key from https://ocr.space/ocrapi
OCRSPACE_API_KEY=your_api_key_here
```

### 3. Initialize Database

```bash
python init_db.py
```

This creates `certs.db` with sample certificate records.

### 4. Set Up AI Seal Verification (Optional)

Generate seal dataset and train the ViT model:

```bash
# Generate dummy seal dataset aligned with certificate database
python generate_seal_dataset.py

# Train Vision Transformer model for seal classification
python train_vit_seal_model.py
```

This creates:
- `seal_dataset/` folder with training and validation images
- `vit_seal_checker.pth` - trained ViT model for seal verification
- `vit_model_info.json` - model performance information

### 5. Run the Application

```bash
streamlit run main.py
```

### 6. Test Complete System

```bash
# Test all components together
python test_complete_system.py
```

The web interface will open in your browser at `http://localhost:8501`

### 5. Test the System

```bash
python test_sample.py
```

## 📁 Project Structure

```
certificate-verification/
├── main.py              # Streamlit web interface
├── ocr_client.py        # OCR.space API client
├── verifier.py          # Certificate verification engine
├── init_db.py           # Database initialization script
├── test_sample.py       # Test suite with sample data
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # Environment variables (create this)
└── certs.db            # SQLite database (created by init_db.py)
```

## 🔧 Configuration

### OCR Settings

- **Language**: Support for 18+ languages (English default)
- **Overlay**: Extract text bounding boxes for visual highlighting
- **Engine**: OCR.space Engine 2 (optimized for documents)

### Verification Thresholds

- **Authentic**: Final score ≥ 85%
- **Suspect**: Final score 50-84% (needs manual review)
- **Not Found**: Score < 50% or registration number not in database

### Field Weights

- **Name**: 40% (most important for identity verification)
- **Institution**: 30% (critical for authenticity)
- **Degree**: 20% (important but may have variations)
- **Year**: 10% (least critical, allows some tolerance)

## 📊 How It Works

### 1. OCR Processing
- Upload certificate image (JPG, PNG, PDF)
- OCR.space extracts text and bounding boxes
- Text cleaning and preprocessing

### 2. Registration Number Extraction
- Multiple regex patterns for different formats:
  - `ABC2023001`, `ABC-2023-001`
  - `UNI10009`, `INSTX-555`
  - `REG-2021-345`, `CERT-9001`
  - And more...

### 3. Database Lookup
- Exact match on registration number
- Fuzzy matching fallback (80% similarity threshold)
- Retrieves canonical certificate record

### 4. Field Comparison
- **Name Matching**: Advanced fuzzy matching with multiple algorithms
- **Institution Verification**: Exact and fuzzy matching with institution database
- **Degree Validation**: Flexible matching to handle degree variations
- **Year Verification**: Range checking with tolerance for OCR errors

### 5. Seal Verification (AI-Powered)
- **Seal Detection**: OpenCV-based detection using multiple methods:
  - Circular detection (HoughCircles)
  - Contour analysis for stamp shapes
  - Template matching (if templates available)
- **Image Preprocessing**: Crop detected seal regions with padding
- **ViT Classification**: Vision Transformer model classifies each seal:
  - Real: Authentic institutional seals/stamps
  - Fake: Tampered, forged, or suspicious seals
- **Confidence Scoring**: Individual and combined confidence metrics
- **Multi-Seal Handling**: Processes multiple seals per certificate

### 6. Final Decision Logic
- **Step 1**: OCR text verification (Pass/Fail)
- **Step 2**: Seal verification (Pass/Fail)
- **Final Result**: 
  - ✅ **AUTHENTIC**: Both OCR and Seal verification pass
  - ❌ **FAKE**: Either OCR or Seal verification fails
- **Confidence**: Combined confidence from both verification steps
- **Name**: Fuzzy string matching using RapidFuzz
- **Institution**: Partial ratio matching (handles abbreviations)
- **Degree**: Partial matching (handles formatting differences)
- **Year**: Numeric tolerance (exact match = 100%, ±1 year = 80%)

### 5. Scoring & Decision
- Weighted combination of field scores
- Confidence thresholds for final decision
- Detailed reasoning for transparency

## 🧪 Sample Database

The system includes 10 sample certificate records:

| Registration | Name | Institution | Degree | Year |
|-------------|------|-------------|--------|------|
| ABC2023001 | Saksham Sharma | DevLabs Institute | B.Tech Computer Engg | 2023 |
| ABC2022007 | Prisha Verma | Global Tech University | M.Tech AI | 2022 |
| UNI10009 | Rajeev Kumar | Northfield University | B.Sc Physics | 2019 |
| ... | ... | ... | ... | ... |

## 🚨 Error Handling

The system gracefully handles:
- **OCR Failures**: API timeouts, invalid images, service errors
- **Database Errors**: Missing database, connection issues
- **Invalid Input**: Unsupported file formats, corrupted images
- **API Limits**: Rate limiting, quota exceeded
- **Seal Detection Failures**: No seals detected, corrupted images
- **ViT Model Errors**: Model loading failures, prediction errors
- **AI Dependencies**: Missing PyTorch, transformers, or OpenCV

## 🤖 AI Model Information

### Vision Transformer (ViT) Details
- **Base Model**: google/vit-base-patch16-224 (pre-trained on ImageNet)
- **Fine-tuning**: Custom 2-class classification (Real vs Fake seals)
- **Input Size**: 224x224 RGB images
- **Training Dataset**: 80 images (60 training, 20 validation)
- **Performance**: 100% validation accuracy on dummy dataset
- **Model Size**: ~346MB download + fine-tuned weights

### Seal Detection Algorithms
- **Circular Detection**: HoughCircles for round seals/stamps
- **Contour Analysis**: Shape-based detection for irregular stamps
- **Template Matching**: Custom template comparison (if templates provided)
- **Confidence Thresholds**: Configurable detection sensitivity

## � Troubleshooting

### OCR Issues
- **E301 Errors**: Try Demo Mode or check image quality
- **API Limits**: Free tier allows 25K requests/month
- **Image Quality**: Use high-contrast, well-lit, straight-aligned images

### Seal Verification Issues
- **Model Not Found**: Run `python train_vit_seal_model.py` to train the model
- **No Seals Detected**: Check image quality, try different detection parameters
- **Poor Classification**: Retrain model with better dataset or more images
- **Memory Errors**: ViT model requires ~2GB RAM, reduce batch size if needed

### Dependencies
- **PyTorch Installation**: Use CPU version if no GPU: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`
- **OpenCV Issues**: Try `pip install opencv-python-headless` for server environments
- **Transformers**: Requires internet for first-time model download

## �🔄 Extending the System

### Adding Bounding Box Visualization

1. **Install additional dependencies**:
   ```bash
   pip install opencv-python matplotlib
   ```

2. **Modify `main.py`** to add image annotation:
   ```python
   import cv2
   import numpy as np
   
   def draw_bounding_boxes(image, boxes):
       """Draw bounding boxes on the image"""
       img_array = np.array(image)
       for box in boxes:
           x, y, w, h = box['left'], box['top'], box['width'], box['height']
           cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 2)
           cv2.putText(img_array, box['text'], (x, y - 10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
       return Image.fromarray(img_array)
   ```

3. **Add to verification display**:
   ```python
   if result['bounding_boxes']:
       annotated_image = draw_bounding_boxes(original_image, result['bounding_boxes'])
       st.image(annotated_image, caption="Text Regions Detected")
   ```

### Adding Fallback OCR Provider

1. **Install Google Vision API**:
   ```bash
   pip install google-cloud-vision
   ```

2. **Create fallback client**:
   ```python
   class FallbackOCRClient:
       def __init__(self):
           from google.cloud import vision
           self.client = vision.ImageAnnotatorClient()
       
       def extract_text(self, image_bytes):
           image = vision.Image(content=image_bytes)
           response = self.client.text_detection(image=image)
           return {
               'success': True,
               'extracted_text': response.full_text_annotation.text,
               'bounding_boxes': self._extract_boxes(response)
           }
   ```

3. **Modify verification logic**:
   ```python
   def verify_with_fallback(image_bytes):
       # Try primary OCR
       result = primary_ocr.extract_text(image_bytes)
       
       if not result['success'] or result['confidence'] < 0.6:
           # Fallback to secondary OCR
           result = fallback_ocr.extract_text(image_bytes)
       
       return result
   ```

## 🐛 Troubleshooting

### Common Issues

1. **"OCR API Key not found"**
   - Create `.env` file with `OCRSPACE_API_KEY=your_key`
   - Get free key from https://ocr.space/ocrapi

2. **"Database not found"**
   - Run `python init_db.py` to create the database

3. **"No text extracted"**
   - Check image quality and format
   - Try different OCR language settings
   - Ensure certificate text is clearly visible

4. **"Low confidence scores"**
   - Verify sample data matches your certificate format
   - Adjust field weights in `verifier.py`
   - Check regex patterns for registration numbers

### Debug Mode

Set environment variable for verbose logging:
```bash
export DEBUG=1  # Linux/Mac
set DEBUG=1     # Windows
```

## 📝 License

This project is provided as-is for educational and prototype purposes. Please ensure you have appropriate licenses for OCR services and comply with data privacy regulations when handling certificate data.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system!

---

**Note**: This is a prototype system. For production use, implement additional security measures, user authentication, audit logging, and robust error handling.

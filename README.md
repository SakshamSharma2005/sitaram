# Certificate Verification System

A complete certificate verification prototype built with Python and Streamlit that uses OCR to extract text from certificate images and verifies them against a local database.

## 🎯 Features

- **Streamlit Web Interface**: User-friendly interface for certificate upload and verification
- **OCR Integration**: Uses OCR.space API for text extraction from certificate images
- **Database Verification**: Compares extracted data against a local SQLite database
- **Fuzzy Matching**: Intelligent field comparison with configurable similarity thresholds
- **Confidence Scoring**: Multi-factor confidence scoring with weighted field comparison
- **Visual Feedback**: Clear verification results with detailed reasoning
- **Report Generation**: Downloadable JSON verification reports
- **Bounding Box Support**: Text region highlighting (when supported by OCR service)

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

### 4. Run the Application

```bash
streamlit run main.py
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

## 🔄 Extending the System

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

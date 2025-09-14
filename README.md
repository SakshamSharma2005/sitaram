# 🎓 Certificate Verification System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OCR](https://img.shields.io/badge/OCR-OCR.space-orange.svg)](https://ocr.space)

An intelligent certificate verification system that uses **OCR (Optical Character Recognition)** and **fuzzy matching algorithms** to automatically verify the authenticity of educational certificates against a database of legitimate records.

## ✨ Key Features

🔍 **Smart OCR Processing** - Extracts text from certificate images using OCR.space API  
🧠 **Intelligent Field Extraction** - Uses database-guided matching to identify names, institutions, degrees, and years  
📊 **Advanced Fuzzy Matching** - Multiple algorithms (RapidFuzz) for robust text comparison  
⚡ **Real-time Verification** - Instant authentication with confidence scoring  
🎮 **Demo Mode** - Test the system without requiring OCR API  
📱 **Web Interface** - User-friendly Streamlit dashboard  
📈 **Detailed Analytics** - Field-by-field comparison with reasoning  
📄 **Export Reports** - Downloadable JSON verification reports  

## 🚀 Live Demo

![Certificate Verification Demo](https://via.placeholder.com/800x400/2E86AB/FFFFFF?text=Certificate+Verification+System+Demo)

Try the system with our sample certificates or upload your own!

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SakshamSharma2005/certificatesdetection.git
cd certificatesdetection
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Get OCR API Key (Free)

1. Visit [OCR.space](https://ocr.space/ocrapi) 
2. Sign up for a **free account** (25,000 requests/month)
3. Copy your API key

### 4️⃣ Configure Environment

Create a `.env` file in the project root:

```bash
OCRSPACE_API_KEY=your_api_key_here
```

### 5️⃣ Initialize Database

```bash
python init_db.py
```

This creates `certs.db` with 10 sample certificate records.

### 6️⃣ Launch the Application

```bash
streamlit run main.py
```

🌐 **Open your browser**: http://localhost:8501

### 7️⃣ Test with Sample Certificates

Upload any certificate from the `sample_certificates/` folder or try the **Demo Mode** for instant results!

## 📱 How to Use

1. **Upload Certificate**: Choose JPG/PNG/PDF certificate image
2. **Configure Settings**: Select language, enable bounding boxes
3. **Choose Mode**: Real OCR or Demo Mode for testing
4. **Click Verify**: Watch the magic happen!
5. **Review Results**: See authentication decision and detailed analysis
6. **Download Report**: Get JSON verification report

## 📁 Project Structure

```
certificatesdetection/
├── 📱 main.py                    # Streamlit web interface
├── 🔍 ocr_client.py              # OCR.space API client  
├── 🧠 verifier.py                # Certificate verification engine
├── 🗄️ init_db.py                 # Database initialization
├── 🎨 generate_certificates.py   # Sample certificate generator
├── 🧪 test_sample.py             # Test suite
├── 🔧 test_ocr_api.py            # API key validator
├── 📋 requirements.txt           # Python dependencies
├── 🗃️ certs.db                  # SQLite database (auto-created)
├── 📁 sample_certificates/       # Generated test certificates
│   ├── ABC2023001_Saksham_Sharma.jpg
│   ├── ABC2022007_Prisha_Verma.jpg
│   └── ... (8 more certificates)
├── 📝 README.md                 # This documentation
└── ⚙️ .env                      # Environment config (create this)
```

## 🎯 Sample Database

The system includes **10 pre-loaded certificate records** for testing:

| Registration | Student Name | Institution | Degree | Year |
|-------------|--------------|-------------|--------|------|
| `ABC2023001` | Saksham Sharma | DevLabs Institute | B.Tech Computer Engg | 2023 |
| `ABC2022007` | Prisha Verma | Global Tech University | M.Tech AI | 2022 |
| `UNI10009` | Rajeev Kumar | Northfield University | B.Sc Physics | 2019 |
| `INSTX-555` | Anita Desai | Sunrise Polytechnic | Diploma Civil | 2021 |
| `COLL-7788` | John Doe | WestEnd College | BBA | 2020 |
| *...and 5 more* | | | | |

## 🔬 How It Works

### 1. OCR Text Extraction
```python
# Upload certificate image → OCR.space API → Extract text + bounding boxes
ocr_result = ocr_client.extract_text_from_bytes(image_bytes)
```

### 2. Smart Field Extraction  
```python
# Use database as guide to intelligently extract fields
extracted_fields = verifier.extract_fields_from_ocr(ocr_text, db_record)
```

### 3. Fuzzy Matching & Scoring
```python
# Compare extracted vs database using multiple algorithms
scores = {
    'name': fuzz.token_sort_ratio(db_name, ocr_name),
    'institution': fuzz.partial_ratio(db_inst, ocr_inst),
    'degree': keyword_matching(db_degree, ocr_degree),
    'year': year_tolerance_matching(db_year, ocr_year)
}
```

### 4. Decision Making
- **AUTHENTIC** (75%+ confidence): High probability legitimate certificate
- **SUSPECT** (40-74% confidence): Requires manual review  
- **NOT FOUND** (<40% confidence): Likely fraudulent or not in database

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

## 🎮 Demo Mode

**Don't have an OCR API key?** No problem! Enable **Demo Mode** to test the verification system immediately:

1. Check "Use Demo Mode" in the sidebar
2. Upload any image (content doesn't matter)
3. Watch the verification process with simulated OCR data
4. See real fuzzy matching and confidence scoring in action

## 🛠️ Advanced Configuration

### Custom Thresholds
```python
# In verifier.py - adjust these values
self.authentic_threshold = 0.75    # AUTHENTIC decision
self.suspect_threshold = 0.40      # SUSPECT vs NOT_FOUND
```

### Field Weights  
```python
# Customize importance of each field
self.field_weights = {
    'name': 0.4,        # 40% - Most important
    'institution': 0.3,  # 30% - Very important  
    'degree': 0.2,      # 20% - Moderately important
    'year': 0.1         # 10% - Least important
}
```

### Adding New Certificates
```python
# Add to database
python init_db.py  # or manually insert into certs.db
```

## 🔧 API Testing

Test your OCR.space API key:
```bash
python test_ocr_api.py
```

Run system tests:
```bash
python test_sample.py
```

Generate new sample certificates:
```bash
python generate_certificates.py
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| 🔑 **"OCR API Key not found"** | Create `.env` file with `OCRSPACE_API_KEY=your_key` |
| 🗄️ **"Database not found"** | Run `python init_db.py` |
| 📸 **"OCR failed: E301"** | Try smaller images (<1MB), JPG format, or enable Demo Mode |
| 📊 **"Low confidence scores"** | Use generated sample certificates for better results |
| 🌐 **"Connection errors"** | Check internet connection and API key validity |

**💡 Pro Tip:** Use the generated certificates in `sample_certificates/` folder for best OCR results!

## � Deployment Options

### Local Development
```bash
streamlit run main.py
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

### Cloud Deployment
- **Streamlit Cloud**: Connect your GitHub repo
- **Heroku**: Use the included `requirements.txt`
- **AWS/GCP**: Deploy as containerized application

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🍴 Fork** the repository
2. **🌟 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **💻 Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **📤 Push** to the branch (`git push origin feature/amazing-feature`)
5. **🔄 Open** a Pull Request

### Ideas for Contributions:
- 🎨 **UI/UX improvements** for the Streamlit interface
- 🧠 **Better OCR preprocessing** (noise removal, image correction)
- 📊 **Additional matching algorithms** (semantic similarity, ML-based)
- 🌐 **Multi-language support** for international certificates
- 🔐 **Security enhancements** (input validation, rate limiting)
- 📱 **Mobile-responsive design**
- 🎯 **Batch processing** for multiple certificates

## 📞 Support & Community

- 📧 **Issues**: [GitHub Issues](https://github.com/SakshamSharma2005/certificatesdetection/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/SakshamSharma2005/certificatesdetection/discussions)
- 📖 **Wiki**: [Project Wiki](https://github.com/SakshamSharma2005/certificatesdetection/wiki)

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/SakshamSharma2005/certificatesdetection)
![GitHub forks](https://img.shields.io/github/forks/SakshamSharma2005/certificatesdetection)
![GitHub issues](https://img.shields.io/github/issues/SakshamSharma2005/certificatesdetection)
![GitHub last commit](https://img.shields.io/github/last-commit/SakshamSharma2005/certificatesdetection)

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OCR.space** for providing free OCR API
- **Streamlit** for the amazing web app framework
- **RapidFuzz** for fast fuzzy string matching
- **Pillow** for image processing capabilities

## ⭐ Star This Project

If you found this project helpful, please give it a ⭐ star on GitHub! It helps others discover the project.

---

**🎓 Built for educational verification, powered by AI and OCR technology.**

**Made with ❤️ by [Saksham Sharma](https://github.com/SakshamSharma2005)**

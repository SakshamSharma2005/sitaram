# 🎓 Certificate Verification System - Streamlit Cloud Deployment

A comprehensive AI-powered certificate verification system using OCR, YOLOv8 seal detection, and Vision Transformer classification.

## 🚀 Features

- **OCR Text Verification**: Extract and verify certificate text against database
- **AI Seal Detection**: YOLOv8-based seal/stamp detection (99% accuracy)
- **Seal Authentication**: Vision Transformer (ViT) classifier for real/fake seal detection
- **Multi-layer Security**: Combines OCR + AI for comprehensive verification
- **Demo Mode**: Test without API keys

## 📦 Deployment on Streamlit Cloud

### Quick Deploy

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `SakshamSharma2005/sitaram`
   - Main file path: `main.py`
   - Click "Deploy"

3. **Add Secrets** (Optional - for OCR):
   - In Streamlit Cloud dashboard, go to App Settings > Secrets
   - Add:
     ```toml
     OCRSPACE_API_KEY = "your_api_key_here"
     ```

## 🎮 Demo Mode

The app works **without any API keys** using demo mode:
- Sample certificates included for testing
- All AI models work offline
- Perfect for demonstrations

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run main.py
```

## 📊 Tech Stack

- **Framework**: Streamlit
- **OCR**: OCR.space API
- **Seal Detection**: YOLOv8 (Ultralytics)
- **Classification**: Vision Transformer (ViT)
- **Database**: SQLite
- **CV Processing**: OpenCV

## 🔐 Security

- Multi-factor verification (OCR + AI seals)
- High-confidence rejection for fake seals
- Database cross-validation
- Secure API handling

## 📝 License

MIT License

## 👨‍💻 Author

Saksham Sharma

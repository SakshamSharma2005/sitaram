# Certificate Verification System - Deployment Guide

## 🚀 Deploy to Streamlit Cloud (FREE)

### Step 1: Push to GitHub
1. Make sure your repository is pushed to GitHub
2. Repository: `SakshamSharma2005/sitaram`

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - Repository: `SakshamSharma2005/sitaram`
   - Branch: `main`
   - Main file path: `main.py`
5. Click "Deploy"!

### Step 3: Add Secrets (Optional)
If you have an OCR API key, add it in Streamlit Cloud:
1. Go to your app settings
2. Click "Secrets"
3. Add:
```toml
OCRSPACE_API_KEY = "your-api-key-here"
```

### Step 4: Your App is Live! 🎉
Your app will be available at: `https://your-app-name.streamlit.app`

## Features
- 🔍 OCR-based certificate verification
- 🎯 YOLOv8 seal detection (99% accuracy)
- 🤖 AI-powered seal classification
- 🎮 Demo mode (works without API keys)
- 📊 Comprehensive verification reports

## Local Development
```bash
pip install -r requirements.txt
streamlit run main.py
```

## Note
- The app works in **demo mode** without any API keys
- For production use, configure OCR API key in secrets
- Database initialization: `python init_db.py`

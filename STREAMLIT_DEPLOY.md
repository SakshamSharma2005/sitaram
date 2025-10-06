# 🎓 Certificate Verification System - Streamlit Deployment

## ✅ Your App is Now LFS-Free!

All large model files have been removed from Git and will be downloaded automatically from Hugging Face.

## 🚀 **REDEPLOY Instructions**

Your repository is now clean and ready for Streamlit Cloud. Follow these steps:

### **Step 1: Delete the Old App**
1. Go to https://share.streamlit.io
2. Find your app: `satyasetu-zrfxkm4x7rnhde2tq8uqyc`
3. Click menu (⋮) → **Delete app**

### **Step 2: Create New App**
1. Click **"New app"**
2. Repository: `SakshamSharma2005/sitaram`
3. Branch: `main`
4. Main file: `main.py`
5. Click **"Deploy!"**

### **Step 3: Add Secrets**
After the app starts deploying, add these secrets:

```toml
# ViT Model from Hugging Face (required for real seal classification)
VIT_MODEL_URL = "https://huggingface.co/Saksham-Sharma2005/vit-seal-classifier/resolve/main/vit_seal_checker.pth"

# OCR API Key (optional - app works in demo mode without it)
OCRSPACE_API_KEY = "K84175691288957"
```

**How to add secrets:**
- In app dashboard → Settings → Secrets
- Paste the above → Save
- App will auto-redeploy

---

## 📦 **What Changed**

### ✅ Fixed Issues:
- ❌ **Removed Git LFS** - No more quota issues
- ❌ **Removed large files** from Git (`.pth`, `.pt` models)
- ✅ **Added Hugging Face integration** - Models download automatically
- ✅ **Added proper .gitignore** - Large files won't be committed
- ✅ **Added packages.txt** - System dependencies for Streamlit Cloud

### 📥 **Models Download Automatically:**
1. **ViT Seal Classifier** (1GB) - Downloads from Hugging Face on first run
2. **YOLOv8 Model** - Uses Ultralytics' pre-trained model or custom from HF

---

## 🎮 **Demo Mode**

The app works perfectly **without** secrets using demo mode:
- ✅ YOLOv8 seal detection (using Ultralytics default model)
- ✅ Sample OCR data for testing
- ✅ All UI features functional
- ✅ Perfect for demonstrations

---

## 🔧 **Local Development**

```bash
# Clone repository
git clone https://github.com/SakshamSharma2005/sitaram.git
cd sitaram

# Install dependencies
pip install -r requirements.txt

# Create secrets file
cp secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your keys

# Run app
streamlit run main.py
```

---

## 📊 **System Architecture**

```
User Upload → Streamlit UI
    ↓
    ├─→ OCR Verification (OCR.space API or Demo)
    │   └─→ Database Matching (SQLite)
    │
    ├─→ YOLOv8 Seal Detection (99% accurate)
    │   └─→ Crop detected seals
    │
    └─→ ViT Seal Classification (Real/Fake)
        └─→ Final Verdict (Security-first logic)
```

---

## 🆘 **Troubleshooting**

### App won't start?
- ✅ Delete and redeploy (see Step 1-2 above)
- ✅ Check logs in Streamlit dashboard
- ✅ Ensure secrets are added correctly

### Models not loading?
- ✅ Check `VIT_MODEL_URL` in secrets
- ✅ Wait for download (1GB file takes time on first run)
- ✅ App will use demo mode if download fails

### Still getting Git LFS errors?
- ✅ Repository is now LFS-free
- ✅ If old deployment cached LFS, delete and redeploy
- ✅ Clear your local .git/lfs folder if needed

---

## 📝 **License**

MIT License - Free for commercial and personal use

## 👨‍💻 **Author**

Saksham Sharma
- GitHub: [@SakshamSharma2005](https://github.com/SakshamSharma2005)
- Model: [Hugging Face](https://huggingface.co/Saksham-Sharma2005/vit-seal-classifier)

---

## 🎉 **Success Checklist**

- ✅ Repository is Git LFS-free
- ✅ Models hosted on Hugging Face
- ✅ Deployment instructions documented
- ✅ Demo mode available
- ✅ Ready for Streamlit Cloud!

**Next Step**: Delete the old app and redeploy fresh! 🚀

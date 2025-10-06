# 🚀 Quick Deployment Guide

## Your GitHub Repository
✅ **Successfully Pushed!**
```
Repository: https://github.com/SakshamSharma2005/sitaram
Branch: main
Status: Ready for Render deployment
```

## Deploy to Render (5 Steps)

### 1️⃣ Go to Render
🔗 https://render.com → Sign up with GitHub

### 2️⃣ Create Web Service
- Click "New +" → "Web Service"
- Connect repository: **SakshamSharma2005/sitaram**
- Render auto-detects configuration ✅

### 3️⃣ Add Environment Variable
```
OCR_API_KEY = your_api_key
```
Get free key: https://ocr.space/ocrapi

### 4️⃣ Deploy
Click "Create Web Service" → Wait 5-10 minutes

### 5️⃣ Keep It Awake (UptimeRobot)
🔗 https://uptimerobot.com
- Add HTTP(s) monitor
- URL: `https://your-app.onrender.com/_stcore/health`
- Interval: 5 minutes

## 🎉 Result
```
Your App: https://your-app.onrender.com
Cost: $0/month
Uptime: 24/7
```

## Integration Examples

### JavaScript
```javascript
// Redirect to your verifier
window.location.href = 'https://your-app.onrender.com?redirect_url=' + 
                        encodeURIComponent(window.location.href);
```

### HTML Embed
```html
<iframe 
  src="https://your-app.onrender.com" 
  width="100%" 
  height="600px"
></iframe>
```

### WordPress
```php
[iframe src="https://your-app.onrender.com" width="100%" height="600"]
```

---
**Total Setup Time**: ~15 minutes
**Total Cost**: $0/month 🆓

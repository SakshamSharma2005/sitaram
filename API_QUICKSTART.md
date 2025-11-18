# Certificate Verification API - Quick Start Guide

## 🚀 Test Locally

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-multipart
```

### 2. Run API Server
```bash
python api.py
```

API will be available at: **http://localhost:8000**

### 3. Test Endpoints

**View API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Verify Certificate:**
```bash
curl -X POST http://localhost:8000/api/verify \
  -F "file=@test_certificate.jpg"
```

---

## 🌐 Integrate with Your Website

### HTML/JavaScript
```html
<input type="file" id="cert" accept="image/*">
<button onclick="verify()">Verify</button>
<div id="result"></div>

<script>
async function verify() {
    const file = document.getElementById('cert').files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('YOUR-API-URL/api/verify', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    document.getElementById('result').innerHTML = 
        `Decision: ${result.decision} (${result.confidence})`;
}
</script>
```

### React
```jsx
const CertVerifier = () => {
    const [result, setResult] = useState(null);
    
    const handleUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('YOUR-API-URL/api/verify', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        setResult(data);
    };
    
    return (
        <div>
            <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
            {result && <div>{result.decision}</div>}
        </div>
    );
};
```

### Python
```python
import requests

files = {'file': open('certificate.jpg', 'rb')}
response = requests.post('YOUR-API-URL/api/verify', files=files)
result = response.json()

print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']}")
```

---

## 🚀 Deploy to Render (FREE)

### Option 1: Auto Deploy (Recommended)
1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:** Add `OCRSPACE_API_KEY`
6. Deploy!

### Option 2: Using render-api.yaml
1. Push code with `render-api.yaml` to GitHub
2. Render will auto-detect and deploy

---

## 📡 API Endpoints

### `POST /api/verify`
Verify certificate image

**Request:**
```json
{
  "file": "<image_file>",
  "enable_seal_verification": true
}
```

**Response:**
```json
{
  "success": true,
  "decision": "AUTHENTIC",
  "confidence": 0.92,
  "reason": "Certificate verified successfully",
  "details": {
    "registration_number": "1BG19CS100",
    "database_match": true,
    "ocr_data": {...},
    "seal_verification": {...}
  }
}
```

### `POST /api/verify/simple`
Simplified response (just decision)

**Response:**
```json
{
  "decision": "AUTHENTIC",
  "confidence": 0.92,
  "reason": "Certificate verified"
}
```

### `GET /health`
Check API health

### `GET /api/status`
Detailed component status

### `GET /docs`
Interactive API documentation

---

## ⚡ Keep API Awake 24/7 (FREE)

Use [UptimeRobot](https://uptimerobot.com):
1. Create free account
2. Add monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://your-api.onrender.com/health`
   - **Interval:** 5 minutes
3. API will never sleep!

---

## 🔒 Security (Optional)

### Add API Key Authentication
Uncomment lines in `api.py`:
```python
if api_key != "your-secret-key":
    raise HTTPException(401, "Invalid API key")
```

Then call with header:
```bash
curl -H "X-API-Key: your-secret-key" ...
```

---

## 🎯 Response Examples

### Authentic Certificate
```json
{
  "decision": "AUTHENTIC",
  "confidence": 0.95,
  "reason": "Certificate verified successfully",
  "details": {
    "seal_verification": {
      "status": "Pass",
      "authentic_seals": 2,
      "fake_seals": 0
    }
  }
}
```

### Fake Certificate
```json
{
  "decision": "FAKE",
  "confidence": 0.23,
  "reason": "Rejected due to fake seals",
  "details": {
    "seal_verification": {
      "status": "Fail",
      "authentic_seals": 0,
      "fake_seals": 2
    }
  }
}
```

---

## 🆘 Troubleshooting

**Models not loading?**
- Check logs: `render logs` or view in dashboard
- Ensure Git LFS is pushing model files

**Out of memory?**
- Upgrade to Render $7/mo plan (512MB → 2GB RAM)

**Slow first request?**
- Use UptimeRobot to prevent cold starts

**CORS errors?**
- API has CORS enabled for all origins by default
- Restrict to your domain in production

---

## 📊 Performance

- **First request:** ~10-15s (cold start)
- **Subsequent:** ~4-5s per certificate
- **With UptimeRobot:** Always ~4-5s

---

**Need help?** Open an issue on GitHub!

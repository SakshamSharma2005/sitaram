# 🚀 Certificate Verification API - Integration Guide

## Overview
This API provides REST endpoints for certificate verification that can be integrated with any website frontend.

## 🆓 Free Deployment Options

### Option 1: Render.com (Recommended)
**Free Tier:** 750 hours/month, auto-sleep after inactivity
1. Create `render.yaml` for API:
```yaml
services:
  - type: web
    name: certificate-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Option 2: Railway.app
**Free Tier:** $5 monthly credit
- Deploy directly from GitHub
- Automatic HTTPS

### Option 3: Fly.io
**Free Tier:** 3 shared VMs
- Fast global deployment
- Supports Docker

### Option 4: Heroku (Basic Free)
**Free Tier:** Limited hours/month

## 📡 API Endpoints

### 1. Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "services": {
    "ocr": true,
    "database": true,
    "seal_detector": true,
    "vit_classifier": true
  }
}
```

### 2. Full Verification
```bash
POST /api/verify
Content-Type: multipart/form-data

Parameters:
- file: Certificate image (required)
- language: OCR language, default "eng" (optional)
- enable_seal: Enable seal detection, default true (optional)
```

**Response:**
```json
{
  "success": true,
  "filename": "certificate.jpg",
  "final_decision": "AUTHENTIC",
  "ocr_verification": {
    "decision": "AUTHENTIC",
    "confidence": 0.92,
    "registration_number": "1BG19CS100",
    "extracted_data": {...},
    "reasons": []
  },
  "seal_verification": {
    "total_seals": 2,
    "fake_seals": 0,
    "authentic_seals": 2,
    "confidence": 0.95,
    "status": "Pass"
  }
}
```

### 3. Simple Verification
```bash
POST /api/verify-simple
Content-Type: multipart/form-data

Parameters:
- file: Certificate image (required)
```

**Response:**
```json
{
  "valid": true,
  "confidence": 0.92,
  "registration_number": "1BG19CS100"
}
```

## 🌐 Frontend Integration Examples

### JavaScript/React Example
```javascript
// certificate-verify.js
async function verifyCertificate(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('enable_seal', 'true');
  
  try {
    const response = await fetch('https://your-api.onrender.com/api/verify', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.final_decision === 'AUTHENTIC') {
      console.log('✅ Certificate is authentic!');
      console.log('Confidence:', result.ocr_verification.confidence);
    } else {
      console.log('❌ Certificate verification failed');
      console.log('Reasons:', result.ocr_verification.reasons);
    }
    
    return result;
  } catch (error) {
    console.error('API Error:', error);
  }
}

// React Component
function CertificateUpload() {
  const [result, setResult] = useState(null);
  
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const verification = await verifyCertificate(file);
    setResult(verification);
  };
  
  return (
    <div>
      <input type="file" onChange={handleUpload} accept="image/*" />
      {result && (
        <div className={result.final_decision === 'AUTHENTIC' ? 'success' : 'error'}>
          Status: {result.final_decision}
          <br />
          Confidence: {(result.ocr_verification.confidence * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
```

### HTML/JavaScript Example
```html
<!DOCTYPE html>
<html>
<head>
  <title>Certificate Verification</title>
</head>
<body>
  <h1>Verify Certificate</h1>
  <input type="file" id="certificate" accept="image/*">
  <button onclick="verify()">Verify</button>
  <div id="result"></div>

  <script>
    async function verify() {
      const file = document.getElementById('certificate').files[0];
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('https://your-api.onrender.com/api/verify-simple', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      document.getElementById('result').innerHTML = `
        <h2>${data.valid ? '✅ Valid' : '❌ Invalid'}</h2>
        <p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
        <p>Reg No: ${data.registration_number || 'Not found'}</p>
      `;
    }
  </script>
</body>
</html>
```

### Python Requests Example
```python
import requests

def verify_certificate(image_path, api_url):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'enable_seal': 'true'}
        
        response = requests.post(
            f'{api_url}/api/verify',
            files=files,
            data=data
        )
        
        return response.json()

# Usage
result = verify_certificate(
    'certificate.jpg',
    'https://your-api.onrender.com'
)

print(f"Decision: {result['final_decision']}")
print(f"Confidence: {result['ocr_verification']['confidence']:.2%}")
```

### cURL Example
```bash
# Simple verification
curl -X POST https://your-api.onrender.com/api/verify-simple \
  -F "file=@certificate.jpg"

# Full verification
curl -X POST https://your-api.onrender.com/api/verify \
  -F "file=@certificate.jpg" \
  -F "language=eng" \
  -F "enable_seal=true"
```

## 🚀 Local Testing

1. Install API dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

2. Run the API server:
```bash
python api.py
```

3. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

4. Test with cURL:
```bash
curl -X POST http://localhost:8000/api/verify-simple \
  -F "file=@test_certificate_with_seal.png"
```

## 🔐 Security Best Practices

1. **Rate Limiting:** Add rate limiting to prevent abuse
```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: "global")

@app.post("/api/verify")
@limiter.limit("10/minute")
async def verify_certificate(...):
    ...
```

2. **CORS Configuration:** Restrict origins in production
```python
allow_origins=["https://yourwebsite.com"]  # Instead of ["*"]
```

3. **File Size Limits:** Already handled by FastAPI
```python
app.add_middleware(
    MaxSizeLimitMiddleware,
    max_request_body_size=10_000_000  # 10MB
)
```

4. **API Key Authentication:** Add authentication header
```python
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="X-API-Key")
```

## 📊 Response Status Codes

- `200`: Success
- `400`: Invalid file type or bad request
- `500`: Server error (OCR failed, model error, etc.)

## 🔄 CORS Headers
All responses include CORS headers for cross-origin requests.

## 💰 Cost Comparison (Free Tiers)

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| Render | 750 hrs/month | Auto-sleep after 15min idle |
| Railway | $5/month credit | ~100hrs runtime |
| Fly.io | 3 shared VMs | 2,340 hrs/month |
| Heroku | Limited | Deprecated free tier |

## 📝 Environment Variables

Set these on your hosting platform:
```bash
OCRSPACE_API_KEY=K84175691288957
PORT=8000  # Usually auto-set by platform
```

## 🎯 Next Steps

1. Test API locally
2. Choose deployment platform
3. Deploy using Git push
4. Update CORS origins
5. Integrate with your frontend
6. Monitor usage

## 📞 Support

- API Documentation: `/docs`
- Health Check: `/health`
- GitHub Issues: https://github.com/SakshamSharma2005/sitaram/issues

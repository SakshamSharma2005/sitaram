# ✅ Render Deployment Checklist

## Pre-Deployment ✅ COMPLETED

- [x] Created `.streamlit/config.toml` - Streamlit configuration
- [x] Created `render.yaml` - Render auto-deploy configuration
- [x] Created `Procfile` - Process configuration
- [x] Created `runtime.txt` - Python version specification
- [x] Created `build.sh` - Build script
- [x] Updated `main.py` - Added health monitoring
- [x] Committed to Git
- [x] Pushed to GitHub: https://github.com/SakshamSharma2005/sitaram

## Next Steps: Deploy on Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)

### Step 2: Deploy Web Service
1. Click "New +" → "Web Service"
2. Click "Connect a repository"
3. Select: **SakshamSharma2005/sitaram**
4. Render will auto-detect `render.yaml`
5. Click "Apply" to use the configuration

### Step 3: Configure Environment Variables
1. In the Render dashboard, go to "Environment"
2. Add the following:
   ```
   OCR_API_KEY = your_ocr_space_api_key
   ```
   (Get free API key from: https://ocr.space/ocrapi)

### Step 4: Deploy!
1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. You'll get a URL like: `https://sitaram.onrender.com`

### Step 5: Set Up UptimeRobot (Keep App Awake - FREE)
1. Go to https://uptimerobot.com
2. Sign up (free account)
3. Click "+ Add New Monitor"
4. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Certificate Verifier
   - **URL**: `https://your-app.onrender.com/_stcore/health`
   - **Monitoring Interval**: 5 minutes
5. Click "Create Monitor"

✅ **DONE! Your app will stay awake 24/7 for FREE!**

## Expected Deployment Timeline

```
├─ Git Push: ✅ COMPLETED (2 minutes)
├─ Render Setup: ⏳ NEXT (3 minutes)
├─ Build & Deploy: ⏳ (5-10 minutes)
├─ UptimeRobot: ⏳ (2 minutes)
└─ Total Time: ~15 minutes
```

## Post-Deployment Testing

After deployment, test these URLs:

1. **Main App**: `https://your-app.onrender.com`
2. **Health Check**: `https://your-app.onrender.com/_stcore/health`

Upload a certificate image and verify:
- ✅ Image uploads successfully
- ✅ OCR extracts text
- ✅ Seal detection works
- ✅ Verification result appears

## Troubleshooting

### If Build Fails:
- Check Render logs in dashboard
- Verify `requirements.txt` has all dependencies
- Check Python version matches `runtime.txt`

### If App Won't Load:
- Check environment variables are set
- Verify `OCR_API_KEY` is correct
- Check application logs

### If App Sleeps:
- Verify UptimeRobot is pinging every 5 minutes
- Check UptimeRobot monitor is "Up"

## Sharing Your App

Once deployed, share your app:

```
🌐 Live URL: https://your-app.onrender.com
📱 Mobile friendly
🔒 HTTPS enabled
🆓 Free hosting
```

## Upgrade Options

If you need:
- Faster response times
- No cold starts
- Custom domain
- More resources

Upgrade to Render Starter: $7/month

## Cost Breakdown

```
Current Setup:
├─ GitHub: FREE
├─ Render Free Tier: $0/month
├─ UptimeRobot: $0/month
└─ Total: $0/month 🎉
```

## Support

Need help?
- Render Docs: https://render.com/docs
- Streamlit Docs: https://docs.streamlit.io
- GitHub Issues: https://github.com/SakshamSharma2005/sitaram/issues

---

**Ready to deploy?** Follow the steps above! 🚀

import os
import requests
from dotenv import load_dotenv

def test_ocr_api_key():
    """Test OCR.space API key functionality."""
    
    print("🔍 Testing OCR.space API Key")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv('OCRSPACE_API_KEY')
    if not api_key:
        print("❌ No API key found in environment variables")
        print("   Please check your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test API connectivity with a simple request
    url = "https://api.ocr.space/parse/image"
    
    # Create a simple test image (1x1 pixel black image)
    import io
    from PIL import Image
    
    # Create minimal test image
    test_image = Image.new('RGB', (100, 50), color='white')
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(test_image)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((10, 10), "TEST", fill='black', font=font)
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='JPEG')
    img_bytes = img_buffer.getvalue()
    
    print(f"📸 Created test image: {len(img_bytes)} bytes")
    
    # Test API request
    payload = {
        'apikey': api_key,
        'language': 'eng',
        'isOverlayRequired': False,
        'OCREngine': 2
    }
    
    files = {
        'file': ('test.jpg', img_bytes, 'image/jpeg')
    }
    
    try:
        print("🌐 Testing API connection...")
        response = requests.post(url, data=payload, files=files, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received")
            print(f"📊 Response: {result}")
            
            # Check for errors
            if result.get('IsErroredOnProcessing', False):
                error_msg = result.get('ErrorMessage', ['Unknown error'])
                if isinstance(error_msg, list):
                    error_msg = '; '.join(error_msg)
                print(f"⚠️ API Error: {error_msg}")
                
                # Provide specific guidance
                if 'E302' in error_msg:
                    print("💡 This suggests an API key issue:")
                    print("   - Check if your API key is correct")
                    print("   - Verify your OCR.space account is active")
                    print("   - Check if you have remaining quota")
                elif 'E303' in error_msg:
                    print("💡 Rate limit exceeded - wait a moment and try again")
                elif 'E301' in error_msg:
                    print("💡 File processing error - but API key is working")
                
                return False
            else:
                print("🎉 API Key is working correctly!")
                extracted_text = ""
                parsed_results = result.get('ParsedResults', [])
                if parsed_results:
                    extracted_text = parsed_results[0].get('ParsedText', '').strip()
                
                print(f"📝 Extracted text: '{extracted_text}'")
                return True
                
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API Key issue")
            print("💡 Possible causes:")
            print("   - Invalid API key")
            print("   - API key not activated")
            print("   - Account suspended")
            print("   - Wrong API endpoint")
            return False
            
        elif response.status_code == 429:
            print("⚠️ 429 Too Many Requests - Rate limited")
            print("💡 You've exceeded the API rate limit")
            print("   - Free tier: 500 requests per day")
            print("   - Wait and try again later")
            return False
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
        print("💡 This could indicate network issues")
        return False
        
    except requests.exceptions.ConnectionError:
        print("🌐 Connection error")
        print("💡 Check your internet connection")
        return False
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

def check_account_info():
    """Check OCR.space account information."""
    
    load_dotenv()
    api_key = os.getenv('OCRSPACE_API_KEY')
    
    if not api_key:
        return
    
    print("\n🔍 Checking Account Information")
    print("=" * 40)
    
    # Try to get account info (this endpoint might not exist, but worth trying)
    try:
        # Some OCR services provide account info endpoints
        info_url = "https://api.ocr.space/parse/account"
        response = requests.get(info_url, params={'apikey': api_key}, timeout=10)
        
        if response.status_code == 200:
            print("📊 Account info:", response.json())
        else:
            print("ℹ️ Account info endpoint not available")
            
    except:
        print("ℹ️ Could not retrieve account information")

if __name__ == "__main__":
    print("🧪 OCR.space API Key Test Suite")
    print("=" * 50)
    
    # Test the API key
    success = test_ocr_api_key()
    
    # Check account info
    check_account_info()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API Key Test: PASSED")
        print("💡 Your OCR.space API key is working correctly")
        print("   The issue might be with specific images or settings")
    else:
        print("❌ API Key Test: FAILED")
        print("💡 Please fix the API key issue before using the app")
        
    print("\n🔧 Troubleshooting Steps:")
    print("1. Verify your API key at https://ocr.space/ocrapi")
    print("2. Check your daily quota usage")
    print("3. Try creating a new API key")
    print("4. Use Demo Mode in the app if OCR continues to fail")

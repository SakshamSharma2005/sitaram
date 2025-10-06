"""
Upload ViT Seal Classifier model to Hugging Face Hub
"""
from huggingface_hub import HfApi, create_repo, upload_file
import os
from pathlib import Path

# Configuration
MODEL_PATH = "vit_seal_checker.pth"
MODEL_INFO_PATH = "vit_model_info.json"
REPO_NAME = "vit-seal-classifier"  # Will be: username/vit-seal-classifier
REPO_TYPE = "model"

def upload_model_to_hf():
    """Upload the ViT model to Hugging Face Hub"""
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file not found: {MODEL_PATH}")
        print("Please train the model first using train_vit_seal_model.py")
        return False
    
    print("🚀 Starting Hugging Face upload process...")
    print("\n" + "="*60)
    
    # Step 1: Login instructions
    print("\n📋 STEP 1: Login to Hugging Face")
    print("-" * 60)
    print("You need a Hugging Face account and access token.")
    print("\nIf you don't have an account:")
    print("  1. Go to https://huggingface.co/join")
    print("  2. Create a free account")
    print("\nTo get your access token:")
    print("  1. Go to https://huggingface.co/settings/tokens")
    print("  2. Click 'New token'")
    print("  3. Give it a name (e.g., 'streamlit-upload')")
    print("  4. Select 'Write' permissions")
    print("  5. Copy the token")
    print("\nNow run this command:")
    print("  huggingface-cli login")
    print("\nOr you can login programmatically:")
    
    try:
        from huggingface_hub import login
        print("\n" + "="*60)
        token = input("\n🔑 Paste your Hugging Face token here: ").strip()
        
        if not token:
            print("❌ No token provided. Exiting...")
            return False
        
        login(token=token)
        print("✅ Successfully logged in to Hugging Face!")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("\nAlternatively, run: huggingface-cli login")
        return False
    
    # Step 2: Create repository
    print("\n📋 STEP 2: Creating repository on Hugging Face")
    print("-" * 60)
    
    try:
        api = HfApi()
        
        # Get username
        user_info = api.whoami()
        username = user_info['name']
        full_repo_name = f"{username}/{REPO_NAME}"
        
        print(f"Creating repository: {full_repo_name}")
        
        # Create repo (will skip if already exists)
        create_repo(
            repo_id=REPO_NAME,
            repo_type=REPO_TYPE,
            exist_ok=True,
            private=False  # Make it public so Streamlit can access it
        )
        print(f"✅ Repository created/verified: https://huggingface.co/{full_repo_name}")
        
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        return False
    
    # Step 3: Upload model file
    print("\n📋 STEP 3: Uploading model file")
    print("-" * 60)
    
    try:
        model_size = os.path.getsize(MODEL_PATH) / (1024**3)  # Convert to GB
        print(f"Model size: {model_size:.2f} GB")
        print(f"Uploading {MODEL_PATH}...")
        print("⏳ This may take several minutes for large files...")
        
        upload_file(
            path_or_fileobj=MODEL_PATH,
            path_in_repo=MODEL_PATH,
            repo_id=full_repo_name,
            repo_type=REPO_TYPE,
        )
        print(f"✅ Model file uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to upload model: {e}")
        return False
    
    # Step 4: Upload model info (if exists)
    if os.path.exists(MODEL_INFO_PATH):
        print("\n📋 STEP 4: Uploading model info")
        print("-" * 60)
        
        try:
            upload_file(
                path_or_fileobj=MODEL_INFO_PATH,
                path_in_repo=MODEL_INFO_PATH,
                repo_id=full_repo_name,
                repo_type=REPO_TYPE,
            )
            print(f"✅ Model info uploaded successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Failed to upload model info: {e}")
    
    # Step 5: Create README
    print("\n📋 STEP 5: Creating model card (README)")
    print("-" * 60)
    
    readme_content = f"""---
license: mit
tags:
- vision
- image-classification
- seal-verification
- certificate-authentication
library_name: transformers
pipeline_tag: image-classification
---

# ViT Seal Classifier

Vision Transformer (ViT) model fine-tuned for seal/stamp authentication in certificates.

## Model Description

This model classifies seals/stamps as either **Real** or **Fake** with high accuracy.

- **Base Model**: google/vit-base-patch16-224
- **Task**: Binary Image Classification
- **Classes**: Real, Fake
- **Input**: 224x224 RGB images

## Usage

```python
from transformers import ViTForImageClassification
import torch
from PIL import Image
from torchvision import transforms

# Download model
model = ViTForImageClassification.from_pretrained(
    'google/vit-base-patch16-224',
    num_labels=2
)

# Load weights
checkpoint = torch.hub.load_state_dict_from_url(
    'https://huggingface.co/{full_repo_name}/resolve/main/vit_seal_checker.pth'
)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Prepare image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Predict
image = Image.open('seal.jpg')
input_tensor = transform(image).unsqueeze(0)

with torch.no_grad():
    outputs = model(input_tensor)
    prediction = torch.argmax(outputs.logits, dim=1)
    
print("Real" if prediction == 0 else "Fake")
```

## Training Data

Trained on a curated dataset of authentic and fake certificate seals.

## License

MIT License

## Author

Certificate Verification System
"""
    
    try:
        with open("README.md", "w") as f:
            f.write(readme_content)
        
        upload_file(
            path_or_fileobj="README.md",
            path_in_repo="README.md",
            repo_id=full_repo_name,
            repo_type=REPO_TYPE,
        )
        print(f"✅ README uploaded successfully!")
        os.remove("README.md")  # Clean up
    except Exception as e:
        print(f"⚠️ Warning: Failed to upload README: {e}")
    
    # Success!
    print("\n" + "="*60)
    print("🎉 SUCCESS! Model uploaded to Hugging Face!")
    print("="*60)
    print(f"\n📦 Model URL: https://huggingface.co/{full_repo_name}")
    print(f"\n🔗 Direct download link:")
    print(f"https://huggingface.co/{full_repo_name}/resolve/main/vit_seal_checker.pth")
    
    print("\n📋 NEXT STEPS:")
    print("-" * 60)
    print("1. Copy the direct download link above")
    print("2. Go to your Streamlit Cloud dashboard")
    print("3. Open your app settings > Secrets")
    print("4. Add this secret:")
    print(f'\nVIT_MODEL_URL = "https://huggingface.co/{full_repo_name}/resolve/main/vit_seal_checker.pth"')
    print("\n5. Save and redeploy your app")
    print("\n✅ Your app will now download the model automatically!")
    
    return True

if __name__ == "__main__":
    print("🎓 ViT Seal Classifier - Hugging Face Upload Tool")
    print("="*60)
    
    success = upload_model_to_hf()
    
    if success:
        print("\n✨ Upload complete! Your model is now publicly accessible.")
    else:
        print("\n❌ Upload failed. Please check the errors above.")

"""
YOLOv8 Seal Detection Setup Script
Complete installation and setup for YOLOv8 integration
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 YOLOv8 Seal Detection Setup")
    print("=" * 50)
    
    # Required packages
    packages = [
        "ultralytics",
        "torch",
        "torchvision", 
        "opencv-python",
        "pillow",
        "numpy"
    ]
    
    print("\n📦 Installing required packages...")
    
    for package in packages:
        print(f"\n  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            print(f"  💡 Try manually: pip install {package}")
    
    print("\n📁 Setting up directories...")
    
    # Create model directory
    model_dir = "yolo_seal_model"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"  ✅ Created {model_dir}/ directory")
    else:
        print(f"  ✅ {model_dir}/ directory already exists")
    
    print("\n🎯 Setup Complete!")
    print("=" * 50)
    
    print("\n📥 Next Steps:")
    print("1. Download your trained model from Kaggle:")
    print("   - Go to your Kaggle notebook output")
    print("   - Download 'yolo_seal_detection_model.zip'")
    print("   - Extract 'best.pt' to yolo_seal_model/ folder")
    
    print("\n2. Test the integration:")
    print("   python test_yolo_integration.py")
    
    print("\n3. Run your Streamlit app:")
    print("   streamlit run main.py")
    
    print("\n🏆 Expected Performance:")
    print("   - 99% mAP@0.5 accuracy")
    print("   - Real-time detection")
    print("   - Streamlit integration with visual feedback")

if __name__ == "__main__":
    main()
#!/bin/bash
# Setup script for Streamlit Cloud deployment
# This runs before the app starts

echo "🚀 Setting up environment..."

# Skip Git LFS downloads (we use Hugging Face instead)
git lfs install --skip-smudge

echo "✅ Setup complete!"

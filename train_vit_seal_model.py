"""
Train a Vision Transformer (ViT) model to classify seals and stamps as REAL or FAKE.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from transformers import ViTForImageClassification, ViTConfig
from PIL import Image
import os
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
import json

class SealDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.images = []
        self.labels = []
        
        # Load images and labels
        for class_name in ['real', 'fake']:
            class_dir = os.path.join(data_dir, class_name)
            class_label = 0 if class_name == 'real' else 1  # real=0, fake=1
            
            if os.path.exists(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(class_dir, img_name)
                        self.images.append(img_path)
                        self.labels.append(class_label)
        
        print(f"Loaded {len(self.images)} images from {data_dir}")
        print(f"Real images: {self.labels.count(0)}, Fake images: {self.labels.count(1)}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

def create_transforms():
    """Create data transforms for training and validation."""
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.3),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform

def train_model():
    """Train the ViT model on seal dataset."""
    print("🚀 Starting ViT Seal Classifier Training...")
    
    # Check if dataset exists
    if not os.path.exists('seal_dataset'):
        print("❌ Error: seal_dataset folder not found!")
        print("Please run generate_seal_dataset.py first to create the dataset.")
        return
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create transforms
    train_transform, val_transform = create_transforms()
    
    # Create datasets
    train_dataset = SealDataset('seal_dataset/train', transform=train_transform)
    val_dataset = SealDataset('seal_dataset/val', transform=val_transform)
    
    if len(train_dataset) == 0 or len(val_dataset) == 0:
        print("❌ Error: No images found in dataset!")
        return
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)
    
    # Load pretrained ViT model
    print("Loading pretrained ViT model...")
    try:
        model = ViTForImageClassification.from_pretrained(
            'google/vit-base-patch16-224',
            num_labels=2,
            ignore_mismatched_sizes=True
        )
    except Exception as e:
        print(f"Error loading pretrained model: {e}")
        print("Using a simple ViT configuration instead...")
        config = ViTConfig(
            image_size=224,
            patch_size=16,
            num_channels=3,
            num_labels=2,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12
        )
        model = ViTForImageClassification(config)
    
    model = model.to(device)
    
    # Set up optimizer and loss function
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()
    
    # Training loop
    num_epochs = 3
    best_val_acc = 0.0
    
    print(f"\n🎯 Training for {num_epochs} epochs...")
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        print("-" * 30)
        
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs.logits, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            train_loss += loss.item()
            _, predicted = torch.max(outputs.logits.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
            
            if batch_idx % 5 == 0:
                print(f"Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs.logits, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.logits.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        val_acc = 100 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)
        
        print(f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_accuracy': val_acc,
                'epoch': epoch
            }, 'vit_seal_checker.pth')
            print(f"✅ New best model saved! Validation accuracy: {val_acc:.2f}%")
    
    print(f"\n🎉 Training completed!")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")
    
    # Final evaluation
    print("\n📊 Final Classification Report:")
    print(classification_report(all_labels, all_predictions, 
                              target_names=['Real', 'Fake']))
    
    # Save model info
    model_info = {
        'model_type': 'ViT Seal Classifier',
        'best_accuracy': best_val_acc,
        'num_epochs': num_epochs,
        'classes': ['Real', 'Fake'],
        'input_size': [224, 224],
        'mean': [0.485, 0.456, 0.406],
        'std': [0.229, 0.224, 0.225]
    }
    
    with open('vit_model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("✅ Model training completed and saved as 'vit_seal_checker.pth'")

def evaluate_image(image_path, model_path='vit_seal_checker.pth'):
    """Evaluate a single image using the trained model."""
    if not os.path.exists(model_path):
        return {"error": "Model not found. Please run training first."}
    
    if not os.path.exists(image_path):
        return {"error": f"Image not found: {image_path}"}
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load model
    try:
        model = ViTForImageClassification.from_pretrained(
            'google/vit-base-patch16-224',
            num_labels=2,
            ignore_mismatched_sizes=True
        )
    except:
        config = ViTConfig(
            image_size=224,
            patch_size=16,
            num_channels=3,
            num_labels=2,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12
        )
        model = ViTForImageClassification(config)
    
    # Load trained weights
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    # Load and preprocess image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Make prediction
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        
        result = {
            "prediction": "REAL ✅" if predicted.item() == 0 else "FAKE ❌",
            "confidence": confidence.item(),
            "class": "Real" if predicted.item() == 0 else "Fake",
            "probabilities": {
                "Real": probabilities[0][0].item(),
                "Fake": probabilities[0][1].item()
            }
        }
    
    return result

if __name__ == "__main__":
    # Train the model
    train_model()
    
    # Test evaluation function if model exists
    if os.path.exists('vit_seal_checker.pth'):
        print("\n🧪 Testing evaluation function...")
        # This would test with an actual image if available
        test_result = evaluate_image("test_image.png")
        print(f"Test result: {test_result}")

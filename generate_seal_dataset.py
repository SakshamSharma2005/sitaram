"""
Generate a dummy dataset of seals, stamps, and signatures aligned with our certificate dataset.
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np

def get_institutes_from_db():
    """Get institute names from the certificate database."""
    conn = sqlite3.connect('certs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT institution FROM certificates")
    institutes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return institutes

def create_dataset_structure():
    """Create the dataset folder structure."""
    folders = [
        'seal_dataset/train/real',
        'seal_dataset/train/fake',
        'seal_dataset/val/real',
        'seal_dataset/val/fake'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("Dataset folder structure created!")

def generate_real_seal(institute_name, image_id, folder_path):
    """Generate a realistic seal for a given institute."""
    # Create 224x224 image
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    
    # Seal colors (professional)
    colors = ['#1f4e79', '#d32f2f', '#388e3c', '#7b1fa2']  # Blue, Red, Green, Purple
    seal_color = random.choice(colors)
    
    # Draw outer circle
    draw.ellipse([20, 20, 204, 204], outline=seal_color, width=4)
    draw.ellipse([30, 30, 194, 194], outline=seal_color, width=2)
    
    # Try to load a font, fallback to default if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Institute name at top (curved effect simulation)
    institute_short = institute_name.replace("Institute", "INST").replace("University", "UNIV")
    draw.text((112, 50), institute_short, fill=seal_color, font=font_large, anchor="mm")
    
    # Official seal text in center
    draw.text((112, 90), "OFFICIAL", fill=seal_color, font=font_small, anchor="mm")
    draw.text((112, 110), "SEAL", fill=seal_color, font=font_small, anchor="mm")
    
    # Year at bottom
    current_year = "2024"
    draw.text((112, 150), f"EST. {current_year}", fill=seal_color, font=font_small, anchor="mm")
    
    # Add some authenticity marks
    draw.ellipse([100, 130, 124, 154], outline=seal_color, width=1)
    
    # Save image
    filename = f"real_seal_{institute_name.replace(' ', '_').lower()}_{image_id}.png"
    img.save(os.path.join(folder_path, filename))
    return filename

def generate_fake_seal(institute_name, image_id, folder_path):
    """Generate a fake/tampered seal."""
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    
    # Fake colors (unprofessional)
    fake_colors = ['#ffff00', '#ff6600', '#ff00ff', '#00ffff', '#000000']  # Yellow, Orange, Magenta, Cyan, Black
    seal_color = random.choice(fake_colors)
    
    # Distorted/broken circles
    if random.choice([True, False]):
        # Broken circle
        draw.arc([20, 20, 204, 204], start=0, end=270, fill=seal_color, width=4)
        draw.arc([30, 30, 194, 194], start=45, end=315, fill=seal_color, width=2)
    else:
        # Irregular shape
        draw.polygon([(25, 50), (180, 30), (200, 180), (40, 190), (20, 100)], outline=seal_color, width=3)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Wrong/misspelled institute name
    fake_names = [
        institute_name.replace('Labs', 'Labz'),
        institute_name.replace('Institute', 'Institue'),
        institute_name.replace('Dev', 'Develop'),
        institute_name + " (FAKE)",
        "RANDOM INSTITUTE"
    ]
    fake_name = random.choice(fake_names)
    
    draw.text((112, 50), fake_name[:20], fill=seal_color, font=font_large, anchor="mm")
    
    # Suspicious text
    suspicious_texts = ["COPY", "DUPLICATE", "SAMPLE", "NOT VALID", "FAKE"]
    draw.text((112, 90), random.choice(suspicious_texts), fill=seal_color, font=font_small, anchor="mm")
    
    # Wrong year or no year
    wrong_years = ["1999", "2050", "????", ""]
    draw.text((112, 150), f"EST. {random.choice(wrong_years)}", fill=seal_color, font=font_small, anchor="mm")
    
    # Save image
    filename = f"fake_seal_{institute_name.replace(' ', '_').lower()}_{image_id}.png"
    img.save(os.path.join(folder_path, filename))
    return filename

def generate_signature(is_real, institute_name, image_id, folder_path):
    """Generate signature images."""
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    if is_real:
        # Real signatures - cursive-like
        signatures = [
            f"Dr. {institute_name.split()[0]} Director",
            "Registrar Office",
            "Academic Head",
            "Principal"
        ]
        signature_text = random.choice(signatures)
        
        # Draw signature-like curves
        points = [(50, 120), (80, 100), (120, 110), (160, 95), (180, 105)]
        draw.line(points, fill='#000080', width=2)
        
        draw.text((112, 140), signature_text, fill='#000080', font=font, anchor="mm")
        prefix = "real"
    else:
        # Fake signatures - scribbles or block text
        fake_signatures = ["SCRIBBLE", "FAKE SIGN", "XXX", "INVALID"]
        signature_text = random.choice(fake_signatures)
        
        # Draw messy scribbles
        for _ in range(5):
            start_x, start_y = random.randint(50, 150), random.randint(100, 130)
            end_x, end_y = start_x + random.randint(-30, 30), start_y + random.randint(-20, 20)
            draw.line([(start_x, start_y), (end_x, end_y)], fill='red', width=2)
        
        draw.text((112, 140), signature_text, fill='red', font=font, anchor="mm")
        prefix = "fake"
    
    filename = f"{prefix}_signature_{institute_name.replace(' ', '_').lower()}_{image_id}.png"
    img.save(os.path.join(folder_path, filename))
    return filename

def generate_complete_dataset():
    """Generate the complete seal dataset."""
    print("Generating seal dataset...")
    
    # Create folder structure
    create_dataset_structure()
    
    # Get institutes from database
    institutes = get_institutes_from_db()
    if not institutes:
        institutes = [
            "DevLabs Institute",
            "Tech Academy",
            "Digital Learning Center",
            "Innovation University",
            "Skill Development Institute"
        ]
    
    print(f"Found {len(institutes)} institutes: {institutes}")
    
    # Generate training data
    for split in ['train', 'val']:
        images_per_class = 30 if split == 'train' else 10
        
        print(f"\nGenerating {split} dataset...")
        
        # Real seals and signatures
        real_folder = f'seal_dataset/{split}/real'
        for i in range(images_per_class):
            institute = random.choice(institutes)
            
            # Generate seals (70% of images)
            if i < images_per_class * 0.7:
                filename = generate_real_seal(institute, i, real_folder)
                print(f"Generated real seal: {filename}")
            else:
                # Generate signatures (30% of images)
                filename = generate_signature(True, institute, i, real_folder)
                print(f"Generated real signature: {filename}")
        
        # Fake seals and signatures  
        fake_folder = f'seal_dataset/{split}/fake'
        for i in range(images_per_class):
            institute = random.choice(institutes)
            
            # Generate fake seals (70% of images)
            if i < images_per_class * 0.7:
                filename = generate_fake_seal(institute, i, fake_folder)
                print(f"Generated fake seal: {filename}")
            else:
                # Generate fake signatures (30% of images)
                filename = generate_signature(False, institute, i, fake_folder)
                print(f"Generated fake signature: {filename}")
    
    print("\n✅ Seal dataset generation completed!")
    print("Dataset structure:")
    print("seal_dataset/")
    print("├── train/")
    print("│   ├── real/ (30 images)")
    print("│   └── fake/ (30 images)")
    print("├── val/")
    print("    ├── real/ (10 images)")
    print("    └── fake/ (10 images)")

if __name__ == "__main__":
    generate_complete_dataset()

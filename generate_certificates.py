import sqlite3
from PIL import Image, ImageDraw, ImageFont
import os
import random

def generate_certificate_images():
    """Generate dummy certificate images based on database records."""
    
    # Connect to database
    db_path = "certs.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run 'python init_db.py' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all certificate records
    cursor.execute("SELECT reg_no, name, institution, degree, year FROM certificates")
    records = cursor.fetchall()
    conn.close()
    
    # Create output directory
    output_dir = "sample_certificates"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎨 Generating {len(records)} certificate images...")
    
    # Certificate templates
    templates = [
        "classic",
        "modern", 
        "academic",
        "professional"
    ]
    
    for i, (reg_no, name, institution, degree, year) in enumerate(records):
        template = templates[i % len(templates)]
        
        # Generate certificate image
        image_path = os.path.join(output_dir, f"{reg_no}_{name.replace(' ', '_')}.jpg")
        generate_single_certificate(reg_no, name, institution, degree, year, template, image_path)
        
        print(f"✅ Generated: {image_path}")
    
    print(f"\n🎉 All certificates generated in '{output_dir}' folder!")
    print("\n📋 Generated certificates:")
    for file in os.listdir(output_dir):
        if file.endswith('.jpg'):
            print(f"  📄 {file}")

def generate_single_certificate(reg_no, name, institution, degree, year, template, output_path):
    """Generate a single certificate image."""
    
    # Certificate dimensions (A4 landscape-ish)
    width, height = 1200, 800
    
    # Color schemes by template
    color_schemes = {
        "classic": {"bg": "#f8f5f0", "border": "#8B4513", "title": "#2F4F4F", "text": "#000000"},
        "modern": {"bg": "#ffffff", "border": "#4169E1", "title": "#1E90FF", "text": "#333333"},
        "academic": {"bg": "#fafafa", "border": "#8B0000", "title": "#8B0000", "text": "#2F2F2F"},
        "professional": {"bg": "#f0f8ff", "border": "#000080", "title": "#191970", "text": "#000000"}
    }
    
    colors = color_schemes[template]
    
    # Create image
    image = Image.new('RGB', (width, height), colors["bg"])
    draw = ImageDraw.Draw(image)
    
    # Try to load fonts (fallback to default if not available)
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        header_font = ImageFont.truetype("arial.ttf", 36)
        body_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        # Fallback fonts
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default() 
        small_font = ImageFont.load_default()
    
    # Draw border
    border_width = 15
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline=colors["border"], width=5)
    
    # Inner decorative border
    inner_border = 35
    draw.rectangle([inner_border, inner_border, width-inner_border, height-inner_border], 
                   outline=colors["border"], width=2)
    
    # Certificate title
    title_text = "CERTIFICATE OF COMPLETION"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 80), title_text, fill=colors["title"], font=title_font)
    
    # Decorative line under title
    line_y = 140
    line_margin = 200
    draw.line([line_margin, line_y, width-line_margin, line_y], fill=colors["border"], width=3)
    
    # Main text content
    y_pos = 200
    
    # "This is to certify that" text
    certify_text = "This is to certify that"
    certify_bbox = draw.textbbox((0, 0), certify_text, font=body_font)
    certify_width = certify_bbox[2] - certify_bbox[0]
    certify_x = (width - certify_width) // 2
    draw.text((certify_x, y_pos), certify_text, fill=colors["text"], font=body_font)
    y_pos += 60
    
    # Student name (prominent)
    name_bbox = draw.textbbox((0, 0), name.upper(), font=header_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (width - name_width) // 2
    draw.text((name_x, y_pos), name.upper(), fill=colors["title"], font=header_font)
    
    # Underline for name
    underline_y = y_pos + 45
    underline_margin = (width - name_width) // 2 - 20
    draw.line([underline_margin, underline_y, width-underline_margin, underline_y], 
              fill=colors["text"], width=2)
    y_pos += 80
    
    # "has successfully completed" text
    completed_text = "has successfully completed the program"
    completed_bbox = draw.textbbox((0, 0), completed_text, font=body_font)
    completed_width = completed_bbox[2] - completed_bbox[0]
    completed_x = (width - completed_width) // 2
    draw.text((completed_x, y_pos), completed_text, fill=colors["text"], font=body_font)
    y_pos += 50
    
    # Degree name
    degree_bbox = draw.textbbox((0, 0), degree, font=header_font)
    degree_width = degree_bbox[2] - degree_bbox[0]
    degree_x = (width - degree_width) // 2
    draw.text((degree_x, y_pos), degree, fill=colors["title"], font=header_font)
    y_pos += 60
    
    # Institution name
    institution_text = f"from {institution}"
    inst_bbox = draw.textbbox((0, 0), institution_text, font=body_font)
    inst_width = inst_bbox[2] - inst_bbox[0]
    inst_x = (width - inst_width) // 2
    draw.text((inst_x, y_pos), institution_text, fill=colors["text"], font=body_font)
    y_pos += 50
    
    # Year
    year_text = f"in the year {year}"
    year_bbox = draw.textbbox((0, 0), year_text, font=body_font)
    year_width = year_bbox[2] - year_bbox[0]
    year_x = (width - year_width) // 2
    draw.text((year_x, y_pos), year_text, fill=colors["text"], font=body_font)
    
    # Registration number (bottom section)
    reg_text = f"Registration Number: {reg_no}"
    reg_bbox = draw.textbbox((0, 0), reg_text, font=small_font)
    reg_width = reg_bbox[2] - reg_bbox[0]
    reg_x = (width - reg_width) // 2
    draw.text((reg_x, height-120), reg_text, fill=colors["text"], font=small_font)
    
    # Date of issue
    import datetime
    issue_date = datetime.datetime.now().strftime("%B %Y")
    date_text = f"Date of Issue: {issue_date}"
    date_bbox = draw.textbbox((0, 0), date_text, font=small_font)
    date_width = date_bbox[2] - date_bbox[0]
    date_x = (width - date_width) // 2
    draw.text((date_x, height-90), date_text, fill=colors["text"], font=small_font)
    
    # Add some decorative elements based on template
    if template == "classic":
        # Add corner decorations
        add_corner_decorations(draw, width, height, colors["border"])
    elif template == "modern":
        # Add geometric patterns
        add_geometric_patterns(draw, width, height, colors["border"])
    elif template == "academic":
        # Add academic symbols
        add_academic_symbols(draw, width, height, colors["border"])
    elif template == "professional":
        # Add professional elements
        add_professional_elements(draw, width, height, colors["border"])
    
    # Save image
    image.save(output_path, "JPEG", quality=95)

def add_corner_decorations(draw, width, height, color):
    """Add classic corner decorations."""
    corner_size = 50
    # Top left
    draw.arc([20, 20, 20+corner_size, 20+corner_size], 0, 90, fill=color, width=3)
    # Top right  
    draw.arc([width-20-corner_size, 20, width-20, 20+corner_size], 90, 180, fill=color, width=3)
    # Bottom left
    draw.arc([20, height-20-corner_size, 20+corner_size, height-20], 270, 360, fill=color, width=3)
    # Bottom right
    draw.arc([width-20-corner_size, height-20-corner_size, width-20, height-20], 180, 270, fill=color, width=3)

def add_geometric_patterns(draw, width, height, color):
    """Add modern geometric patterns."""
    # Side triangles
    triangle_size = 30
    # Left triangles
    for i in range(3):
        y = 200 + i * 100
        draw.polygon([(30, y), (30+triangle_size, y+triangle_size//2), (30, y+triangle_size)], 
                    outline=color, width=2)
    # Right triangles
    for i in range(3):
        y = 200 + i * 100
        x = width - 30 - triangle_size
        draw.polygon([(x+triangle_size, y), (x, y+triangle_size//2), (x+triangle_size, y+triangle_size)], 
                    outline=color, width=2)

def add_academic_symbols(draw, width, height, color):
    """Add academic symbols."""
    # Simple star-like symbols in corners
    star_size = 20
    positions = [(80, 80), (width-80, 80), (80, height-80), (width-80, height-80)]
    
    for x, y in positions:
        # Draw a simple star shape
        draw.line([x-star_size, y, x+star_size, y], fill=color, width=2)
        draw.line([x, y-star_size, x, y+star_size], fill=color, width=2)
        draw.line([x-star_size//2, y-star_size//2, x+star_size//2, y+star_size//2], fill=color, width=1)
        draw.line([x-star_size//2, y+star_size//2, x+star_size//2, y-star_size//2], fill=color, width=1)

def add_professional_elements(draw, width, height, color):
    """Add professional elements."""
    # Simple rectangular frames
    frame_width = 60
    frame_height = 30
    
    # Top center
    x = (width - frame_width) // 2
    draw.rectangle([x, 30, x+frame_width, 30+frame_height], outline=color, width=2)
    
    # Bottom center  
    draw.rectangle([x, height-30-frame_height, x+frame_width, height-30], outline=color, width=2)

def create_sample_certificate_info():
    """Create a text file with information about the generated certificates."""
    
    info_content = """# Sample Certificate Dataset

This folder contains dummy certificate images generated based on the database records.

## Certificate Details:

### Database Records Used:
- ABC2023001: Saksham Sharma - DevLabs Institute - B.Tech Computer Engg - 2023
- ABC2022007: Prisha Verma - Global Tech University - M.Tech AI - 2022  
- UNI10009: Rajeev Kumar - Northfield University - B.Sc Physics - 2019
- INSTX-555: Anita Desai - Sunrise Polytechnic - Diploma Civil - 2021
- COLL-7788: John Doe - WestEnd College - BBA - 2020
- CERT-9001: Maya Iyer - Metro University - MSc Maths - 2018
- REG-2021-345: Ram Singh - City College - BCom - 2021
- EDU-3333: Nina Gupta - Coastal Institute - BCA - 2024
- COL-1212: Alex Wong - Global Tech University - B.Tech ECE - 2022
- STU-0007: Liu Chen - International Academy - PhD Chemistry - 2020

### Template Styles:
1. **Classic**: Traditional certificate with decorative corners
2. **Modern**: Clean design with geometric patterns  
3. **Academic**: Formal academic style with star symbols
4. **Professional**: Business-like with rectangular frames

### Usage:
1. Upload any of these images to the Streamlit app
2. Disable "Demo Mode" to use real OCR
3. The system should successfully extract text and verify against database
4. Expected results: HIGH confidence scores and AUTHENTIC decisions

### Testing Tips:
- These images are designed to work well with OCR.space
- All contain clear text and proper registration numbers
- File sizes are optimized for the free OCR tier
- Different templates test various visual styles

Enjoy testing the complete certificate verification pipeline! 🎓
"""
    
    with open("sample_certificates/README.md", "w") as f:
        f.write(info_content)

if __name__ == "__main__":
    print("🎨 Certificate Image Generator")
    print("=" * 40)
    
    generate_certificate_images()
    create_sample_certificate_info()
    
    print("\n✨ Generation complete!")
    print("\n🚀 Next steps:")
    print("1. Check the 'sample_certificates' folder")
    print("2. Upload any image to your Streamlit app")
    print("3. Disable Demo Mode to test real OCR")
    print("4. Watch the verification work with actual certificate images!")

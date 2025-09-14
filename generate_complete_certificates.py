"""
Generate complete certificate images with embedded seals based on the database records.
Creates realistic certificates that can be used for testing the complete verification system.
"""

import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import colorsys

def get_all_certificates():
    """Get all certificate records from the database."""
    conn = sqlite3.connect('certs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT reg_no, name, institution, degree, year, notes FROM certificates")
    certificates = cursor.fetchall()
    conn.close()
    return certificates

def get_institution_colors(institution):
    """Get institution-specific color scheme."""
    color_schemes = {
        'DevLabs Institute': {'primary': '#1f4e79', 'secondary': '#4a90a4', 'accent': '#87ceeb'},
        'Global Tech University': {'primary': '#8b0000', 'secondary': '#cd5c5c', 'accent': '#ffd700'},
        'Northfield University': {'primary': '#006400', 'secondary': '#228b22', 'accent': '#90ee90'},
        'Sunrise Polytechnic': {'primary': '#ff8c00', 'secondary': '#ffa500', 'accent': '#ffe4b5'},
        'WestEnd College': {'primary': '#4b0082', 'secondary': '#8a2be2', 'accent': '#dda0dd'},
        'Metro University': {'primary': '#2f4f4f', 'secondary': '#708090', 'accent': '#b0c4de'},
        'City College': {'primary': '#b22222', 'secondary': '#dc143c', 'accent': '#ffb6c1'},
        'Coastal Institute': {'primary': '#008b8b', 'secondary': '#20b2aa', 'accent': '#afeeee'},
        'International Academy': {'primary': '#800080', 'secondary': '#9932cc', 'accent': '#dda0dd'}
    }
    
    return color_schemes.get(institution, {
        'primary': '#1f4e79', 
        'secondary': '#4a90a4', 
        'accent': '#87ceeb'
    })

def create_decorative_border(draw, width, height, colors, border_width=20):
    """Create a decorative border around the certificate."""
    # Outer border
    draw.rectangle([0, 0, width, height], outline=colors['primary'], width=border_width)
    
    # Inner decorative border
    inner_margin = border_width + 10
    draw.rectangle([inner_margin, inner_margin, width-inner_margin, height-inner_margin], 
                  outline=colors['secondary'], width=5)
    
    # Corner decorations
    corner_size = 40
    corners = [
        (inner_margin-10, inner_margin-10),  # Top-left
        (width-inner_margin-corner_size+10, inner_margin-10),  # Top-right
        (inner_margin-10, height-inner_margin-corner_size+10),  # Bottom-left
        (width-inner_margin-corner_size+10, height-inner_margin-corner_size+10)  # Bottom-right
    ]
    
    for x, y in corners:
        draw.ellipse([x, y, x+corner_size, y+corner_size], 
                    outline=colors['accent'], width=3)

def create_institutional_seal(institution, reg_no, size=120):
    """Create an institutional seal/stamp."""
    seal_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(seal_img)
    
    colors = get_institution_colors(institution)
    
    # Load fonts first
    try:
        font_large = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 10)
        font_tiny = ImageFont.truetype("arial.ttf", 8)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()
    
    # Determine if this should be a real or fake seal (90% real, 10% fake for realism)
    is_authentic = random.random() > 0.1
    
    if is_authentic:
        # Create authentic seal
        seal_color = colors['primary']
        
        # Outer circle
        draw.ellipse([5, 5, size-5, size-5], outline=seal_color, width=4)
        draw.ellipse([15, 15, size-15, size-15], outline=seal_color, width=2)
        

        
        # Top arc - Institution name
        inst_short = institution.replace("Institute", "INST").replace("University", "UNIV").replace("Academy", "ACAD")
        if len(inst_short) > 20:
            inst_short = inst_short[:20]
        
        draw.text((size//2, 25), inst_short, fill=seal_color, font=font_small, anchor="mm")
        
        # Center - Official text
        draw.text((size//2, size//2-10), "OFFICIAL", fill=seal_color, font=font_small, anchor="mm")
        draw.text((size//2, size//2+5), "SEAL", fill=seal_color, font=font_large, anchor="mm")
        
        # Bottom - Year or establishment
        draw.text((size//2, size-30), "EST. 2010", fill=seal_color, font=font_tiny, anchor="mm")
        
        # Center emblem
        emblem_size = 20
        draw.ellipse([size//2-emblem_size//2, size//2+15, size//2+emblem_size//2, size//2+15+emblem_size], 
                    outline=seal_color, width=1)
        
    else:
        # Create fake/suspicious seal
        fake_colors = ['#ff0000', '#ffff00', '#ff00ff', '#00ff00']  # Suspicious colors
        seal_color = random.choice(fake_colors)
        
        # Distorted or broken circle
        if random.choice([True, False]):
            # Broken circle
            draw.arc([5, 5, size-5, size-5], start=0, end=270, fill=seal_color, width=4)
        else:
            # Wrong shape
            draw.polygon([(20, 30), (size-20, 25), (size-15, size-25), (25, size-20)], 
                        outline=seal_color, width=3)
        
        # Suspicious text
        draw.text((size//2, size//2), "COPY", fill=seal_color, font=font_small, anchor="mm")
    
    return seal_img, is_authentic

def create_signature(signer_name="Director", authentic=True):
    """Create a signature image."""
    sig_img = Image.new('RGBA', (200, 60), (255, 255, 255, 0))
    draw = ImageDraw.Draw(sig_img)
    
    # Load font first
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    if authentic:
        # Create realistic signature
        color = '#000080'
        
        # Signature line (cursive-style)
        points = []
        for i in range(0, 180, 5):
            x = 10 + i
            y = 30 + random.randint(-8, 8) + int(5 * (i/50))
            points.append((x, y))
        
        # Draw signature curve
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=2)
        
        # Add name below
        draw.text((100, 45), signer_name, fill=color, font=font, anchor="mm")
        
    else:
        # Fake signature (scribbles or block text)
        color = '#ff0000'
        
        # Random scribbles
        for _ in range(8):
            start_x = random.randint(10, 150)
            start_y = random.randint(20, 40)
            end_x = start_x + random.randint(-20, 20)
            end_y = start_y + random.randint(-10, 10)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=2)
        
        draw.text((100, 45), "FAKE", fill=color, font=font, anchor="mm")
    
    return sig_img, authentic

def create_complete_certificate(cert_data, cert_type="authentic", output_dir="complete_certificates"):
    """Create a complete certificate with all elements."""
    reg_no, name, institution, degree, year, notes = cert_data
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Certificate dimensions
    width, height = 1200, 900
    
    # Create base image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Get colors for this institution
    colors = get_institution_colors(institution)
    
    # Create decorative border
    create_decorative_border(draw, width, height, colors)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_subtitle = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
        font_name = ImageFont.truetype("arial.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_name = ImageFont.load_default()
    
    # Certificate content
    y_pos = 80
    
    # Title
    draw.text((width//2, y_pos), "CERTIFICATE", fill=colors['primary'], font=font_title, anchor="mm")
    y_pos += 60
    
    draw.text((width//2, y_pos), "OF COMPLETION", fill=colors['primary'], font=font_subtitle, anchor="mm")
    y_pos += 80
    
    # Institution logo placeholder (decorative element)
    logo_size = 80
    draw.ellipse([width//2-logo_size//2, y_pos-40, width//2+logo_size//2, y_pos+40], 
                outline=colors['secondary'], width=3)
    draw.text((width//2, y_pos), "LOGO", fill=colors['secondary'], font=font_small, anchor="mm")
    y_pos += 80
    
    # Certification text
    draw.text((width//2, y_pos), "This is to certify that", fill='black', font=font_text, anchor="mm")
    y_pos += 60
    
    # Student name (highlighted)
    draw.text((width//2, y_pos), name.upper(), fill=colors['primary'], font=font_name, anchor="mm")
    y_pos += 80
    
    # Achievement text
    draw.text((width//2, y_pos), "has successfully completed the program", fill='black', font=font_text, anchor="mm")
    y_pos += 50
    
    # Degree (highlighted)
    draw.text((width//2, y_pos), degree, fill=colors['primary'], font=font_subtitle, anchor="mm")
    y_pos += 60
    
    # Institution
    draw.text((width//2, y_pos), f"from {institution}", fill='black', font=font_text, anchor="mm")
    y_pos += 40
    
    # Year
    draw.text((width//2, y_pos), f"in the year {year}", fill='black', font=font_text, anchor="mm")
    y_pos += 80
    
    # Registration number
    reg_text = f"Registration Number: {reg_no}"
    draw.text((width//2, y_pos), reg_text, fill='black', font=font_small, anchor="mm")
    y_pos += 30
    
    # Date of issue
    from datetime import datetime
    issue_date = datetime.now().strftime("%B %Y")
    draw.text((width//2, y_pos), f"Date of Issue: {issue_date}", fill='black', font=font_small, anchor="mm")
    
    # Add institutional seal (bottom right)
    seal_img, seal_authentic = create_institutional_seal(institution, reg_no)
    seal_x, seal_y = width - 200, height - 180
    img.paste(seal_img, (seal_x, seal_y), seal_img)
    
    # Add signature (bottom left)
    sig_img, sig_authentic = create_signature("Director", authentic=(cert_type == "authentic"))
    sig_x, sig_y = 100, height - 120
    img.paste(sig_img, (sig_x, sig_y), sig_img)
    
    # Add signature label
    draw.text((sig_x + 100, sig_y + 70), "Director", fill='black', font=font_small, anchor="mm")
    draw.line([(sig_x, sig_y + 65), (sig_x + 200, sig_y + 65)], fill='black', width=1)
    
    # Add seal label
    draw.text((seal_x + 60, seal_y + 130), "Official Seal", fill='black', font=font_small, anchor="mm")
    
    # Determine certificate authenticity
    is_authentic = (cert_type == "authentic" and seal_authentic and sig_authentic)
    
    # Save certificate
    filename = f"{reg_no}_{name.replace(' ', '_')}_{cert_type}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    
    return filepath, is_authentic

def generate_certificate_dataset():
    """Generate complete certificate dataset with both authentic and tampered versions."""
    print("🎓 Generating Complete Certificate Dataset...")
    print("=" * 60)
    
    # Get all certificate records
    certificates = get_all_certificates()
    
    if not certificates:
        print("❌ No certificates found in database. Please run init_db.py first.")
        return
    
    print(f"Found {len(certificates)} certificate records in database")
    
    generated_files = []
    
    for i, cert_data in enumerate(certificates):
        reg_no, name, institution, degree, year, notes = cert_data
        
        print(f"\n📜 Generating certificate {i+1}/{len(certificates)}: {name}")
        print(f"   Registration: {reg_no}")
        print(f"   Institution: {institution}")
        print(f"   Degree: {degree}")
        print(f"   Year: {year}")
        
        # Generate authentic version
        auth_file, is_auth = create_complete_certificate(cert_data, "authentic")
        generated_files.append({
            'file': auth_file,
            'type': 'authentic',
            'reg_no': reg_no,
            'name': name,
            'authentic': is_auth
        })
        print(f"   ✅ Authentic: {auth_file}")
        
        # Generate tampered version (30% chance)
        if random.random() < 0.3:
            fake_file, is_fake = create_complete_certificate(cert_data, "tampered")
            generated_files.append({
                'file': fake_file,
                'type': 'tampered',
                'reg_no': reg_no,
                'name': name,
                'authentic': is_fake
            })
            print(f"   ⚠️ Tampered: {fake_file}")
    
    print(f"\n🎉 Certificate Generation Complete!")
    print(f"📊 Generated {len(generated_files)} certificate images")
    print(f"📁 Saved in: complete_certificates/")
    
    # Create summary report
    authentic_count = sum(1 for cert in generated_files if cert['type'] == 'authentic')
    tampered_count = sum(1 for cert in generated_files if cert['type'] == 'tampered')
    
    print(f"\n📈 Summary:")
    print(f"   Authentic certificates: {authentic_count}")
    print(f"   Tampered certificates: {tampered_count}")
    print(f"   Total: {len(generated_files)}")
    
    # Save file list for testing
    with open('certificate_test_list.txt', 'w') as f:
        f.write("# Complete Certificate Dataset for Testing\n")
        f.write("# Format: filename, type, reg_no, name, expected_authentic\n\n")
        
        for cert in generated_files:
            f.write(f"{cert['file']}, {cert['type']}, {cert['reg_no']}, {cert['name']}, {cert['authentic']}\n")
    
    print(f"📋 Test file list saved: certificate_test_list.txt")
    
    # Instructions
    print(f"\n💡 Usage Instructions:")
    print(f"1. Start Streamlit app: streamlit run main.py")
    print(f"2. Enable 'Seal Verification' in sidebar")
    print(f"3. Upload certificates from complete_certificates/ folder")
    print(f"4. Test both authentic and tampered certificates")
    print(f"5. Verify that system correctly identifies authentic vs fake")
    
    return generated_files

def create_test_certificates():
    """Create a few specific test certificates for demonstration."""
    print("🧪 Creating Test Certificates...")
    
    # Test cases
    test_cases = [
        ("ABC2023001", "Saksham Sharma", "DevLabs Institute", "B.Tech Computer Engg", "2023", "Sample student"),
        ("ABC2022007", "Prisha Verma", "Global Tech University", "M.Tech AI", "2022", "Sample student"),
        ("UNI10009", "Rajeev Kumar", "Northfield University", "B.Sc Physics", "2019", "Sample student")
    ]
    
    for cert_data in test_cases:
        reg_no, name = cert_data[0], cert_data[1]
        
        # Create authentic version
        auth_file, _ = create_complete_certificate(cert_data, "authentic", "test_certificates")
        print(f"✅ Created: {auth_file}")
        
        # Create tampered version
        fake_file, _ = create_complete_certificate(cert_data, "tampered", "test_certificates")
        print(f"⚠️ Created: {fake_file}")

if __name__ == "__main__":
    # Generate complete dataset
    generated_files = generate_certificate_dataset()
    
    # Also create specific test certificates
    create_test_certificates()
    
    print(f"\n🚀 Ready for Testing!")
    print(f"   Use complete_certificates/ for full dataset testing")
    print(f"   Use test_certificates/ for quick testing")

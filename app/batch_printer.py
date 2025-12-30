"""
Rimberio University ID Card Template Generator (C:\ Drive Version)
Creates the exact template matching the university's portrait design
"""

from PIL import Image, ImageDraw, ImageFont
import math
from pathlib import Path

def create_rimberio_template(width=1050, height=1800):
    """
    Creates Rimberio University ID card template
    Portrait orientation with curved design elements
    """
    
    # Create white canvas
    card = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(card)
    
    # ==================== HEADER SECTION ====================
    # University Logo (laurel wreath circle placeholder)
    logo_center = (140, 100)
    logo_radius = 50
    
    # Outer circle (laurel wreath effect)
    draw.ellipse([logo_center[0]-logo_radius-5, logo_center[1]-logo_radius-5,
                  logo_center[0]+logo_radius+5, logo_center[1]+logo_radius+5],
                 outline='#8B1A1A', width=3)
    
    # Inner circle with graduation cap silhouette
    draw.ellipse([logo_center[0]-logo_radius, logo_center[1]-logo_radius,
                  logo_center[0]+logo_radius, logo_center[1]+logo_radius],
                 fill='#FFFFFF', outline='#8B1A1A', width=2)
    
    # University name text
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 65)
        font_subtitle = ImageFont.truetype("arial.ttf", 28)
    except:
        # Fallback if fonts not found
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
    
    # "RIMBERIO"
    draw.text((280, 70), "RIMBERIO", fill='#2C2C2C', font=font_title)
    # "UNIVERSITY"
    draw.text((280, 135), "UNIVERSITY", fill='#2C2C2C', font=font_title)
    # Website
    draw.text((280, 180), "www.reallygreatsite.com", fill='#666666', font=font_subtitle)
    
    # ==================== CURVED DESIGN ELEMENTS ====================
    # Large decorative circle (top right)
    circle_center = (width - 150, 250)
    circle_radius = 200
    draw.ellipse([circle_center[0]-circle_radius, circle_center[1]-circle_radius,
                  circle_center[0]+circle_radius, circle_center[1]+circle_radius],
                 fill='#8B1A1A')
    
    # Curved flowing lines (right side) - Main dark curve
    curve_points_dark = []
    for i in range(50):
        angle = -math.pi/4 + (i * math.pi * 1.5 / 50)
        x = width - 100 + math.cos(angle) * 200
        y = 400 + i * 25
        curve_points_dark.append((x, y))
    
    # Draw thick dark curve
    for i in range(len(curve_points_dark)-1):
        draw.line([curve_points_dark[i], curve_points_dark[i+1]], 
                  fill='#2C2C2C', width=80)
    
    # Red accent curve (offset)
    curve_points_red = []
    for i in range(50):
        angle = -math.pi/4 + (i * math.pi * 1.5 / 50)
        x = width - 50 + math.cos(angle) * 180
        y = 400 + i * 25
        curve_points_red.append((x, y))
    
    for i in range(len(curve_points_red)-1):
        draw.line([curve_points_red[i], curve_points_red[i+1]], 
                  fill='#C41E3A', width=90)
    
    # White accent line between curves
    curve_points_white = []
    for i in range(50):
        angle = -math.pi/4 + (i * math.pi * 1.5 / 50)
        x = width - 75 + math.cos(angle) * 190
        y = 400 + i * 25
        curve_points_white.append((x, y))
    
    for i in range(len(curve_points_white)-1):
        draw.line([curve_points_white[i], curve_points_white[i+1]], 
                  fill='#FFFFFF', width=15)
    
    # Decorative wave lines (left side background)
    for wave in range(5):
        y_start = 300 + wave * 40
        for i in range(30):
            x = 50 + i * 15
            y = y_start + math.sin(i * 0.3) * 10
            draw.line([(x, y), (x+10, y)], fill='#F5E6E6', width=2)
    
    # ==================== STUDENT INFO SECTION ====================
    # Student name placeholder (will be replaced by actual data)
    name_y = 320
    
    try:
        font_name_first = ImageFont.truetype("arial.ttf", 45)
        font_name_last = ImageFont.truetype("arialbd.ttf", 72)
        font_label = ImageFont.truetype("arialbd.ttf", 38)
        font_data = ImageFont.truetype("arial.ttf", 36)
    except:
        font_name_first = ImageFont.load_default()
        font_name_last = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_data = ImageFont.load_default()
    
    # Placeholder name text (will be replaced)
    draw.text((120, name_y), "SEBASTIAN", fill='#C41E3A', font=font_name_first)
    draw.text((120, name_y + 60), "BENNETT", fill='#2C2C2C', font=font_name_last)
    
    # ==================== PHOTO CIRCLE ====================
    # Large circular photo area
    photo_center_y = 730
    photo_radius = 275
    
    # Draw outer circle (dark red border)
    draw.ellipse([120 - 5, photo_center_y - photo_radius - 5,
                  120 + photo_radius*2 + 5, photo_center_y + photo_radius + 5],
                 fill='#8B1A1A', outline='#8B1A1A')
    
    # Inner white circle (where photo will be pasted)
    draw.ellipse([120, photo_center_y - photo_radius,
                  120 + photo_radius*2, photo_center_y + photo_radius],
                 fill='#FFFFFF', outline='#FFFFFF')
    
    # ==================== INFO FIELDS ====================
    info_y_start = 1050
    
    # ID Number field
    draw.text((120, info_y_start), "ID NUMBER  :", fill='#C41E3A', font=font_label)
    # Placeholder line - will be filled by script
    draw.text((450, info_y_start), "_______________", fill='#2C2C2C', font=font_data)
    
    # Address/Grade field
    draw.text((120, info_y_start + 100), "ADRESS          :", fill='#C41E3A', font=font_label)
    draw.text((450, info_y_start + 100), "_______________", fill='#2C2C2C', font=font_data)
    
    # Additional info line
    draw.text((120, info_y_start + 200), "_______________", fill='#2C2C2C', font=font_data)
    
    # ==================== FOOTER ====================
    footer_y = 1600
    
    try:
        font_footer = ImageFont.truetype("arialbd.ttf", 48)
    except:
        font_footer = ImageFont.load_default()
    
    draw.text((120, footer_y), "STUDENT ID CARD", fill='#C41E3A', font=font_footer)
    
    return card


# Main execution
if __name__ == "__main__":
    print("="*60)
    print("Rimberio University ID Card Template Generator")
    print("="*60)
    print()
    
    # Create template
    print("Generating template...")
    template = create_rimberio_template()
    
    # Save to Templates folder
    output_path = Path(r"C:\School_IDs\Templates\rimberio_template.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(str(output_path), 'PNG', quality=95, dpi=(300, 300))
    
    print(f"✅ Template saved to: {output_path}")
    print()
    print("Template specifications:")
    print("  • Size: 1050 x 1800 pixels (Portrait)")
    print("  • Resolution: 300 DPI")
    print("  • Photo area: Circular, 550px diameter")
    print("  • Colors: Rimberio Red (#C41E3A), Dark Gray (#2C2C2C)")
    print()
    print("✅ Template ready for use with the ID processing system!")
    print("="*60)
"""
Test & Diagnostic Script (C:\ Drive Version)
Run this to test if everything is working
"""

from pathlib import Path
import sys

# Project path for C:\ drive
PROJECT_PATH = Path(r"C:\School_IDs")

print("="*60)
print("RIMBERIO ID SYSTEM - DIAGNOSTIC TEST")
print("="*60)
print()

# Test 1: Check folders
print("1. Checking folder structure...")
folders = ['Input_Raw', 'Output_Ready', 'Print_Sheets', 'Templates']
for folder in folders:
    path = PROJECT_PATH / folder
    if path.exists():
        print(f"   ✅ {folder}")
    else:
        print(f"   ❌ {folder} - MISSING!")
        path.mkdir(parents=True, exist_ok=True)
        print(f"      Created {folder}")

print()

# Test 2: Check template
print("2. Checking template file...")
template_path = PROJECT_PATH / "Templates" / "rimberio_template.png"
if template_path.exists():
    print(f"   ✅ Template exists")
    print(f"   Location: {template_path}")
    # Check file size
    size_kb = template_path.stat().st_size / 1024
    print(f"   Size: {size_kb:.1f} KB")
else:
    print(f"   ❌ Template NOT found!")
    print(f"   Expected at: {template_path}")
    print(f"   Run: python rimberio_template.py")

print()

# Test 3: Check students.csv
print("3. Checking student database...")
csv_path = PROJECT_PATH / "students.csv"
if csv_path.exists():
    print(f"   ✅ students.csv exists")
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        print(f"   Found {len(df)} students:")
        for idx, row in df.iterrows():
            print(f"      - {row['ID_Number']}: {row['Full_Name']}")
    except Exception as e:
        print(f"   ⚠️  Error reading CSV: {e}")
else:
    print(f"   ❌ students.csv NOT found!")
    print(f"   Expected at: {csv_path}")

print()

# Test 4: Check libraries
print("4. Checking required libraries...")
libraries = [
    ('cv2', 'opencv-python'),
    ('PIL', 'pillow'),
    ('pandas', 'pandas'),
    ('qrcode', 'qrcode'),
    ('watchdog', 'watchdog'),
    ('rembg', 'rembg'),
]

for module, package in libraries:
    try:
        __import__(module)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - NOT INSTALLED!")
        print(f"      Run: pip install {package}")

print()

# Test 5: Check for photos in Input_Raw
print("5. Checking Input_Raw folder for photos...")
input_path = PROJECT_PATH / "Input_Raw"
photos = list(input_path.glob("*.jpg")) + list(input_path.glob("*.jpeg")) + list(input_path.glob("*.png"))
if photos:
    print(f"   Found {len(photos)} photo(s):")
    for photo in photos:
        print(f"      - {photo.name}")
else:
    print(f"   ⚠️  No photos found in Input_Raw")
    print(f"   Add a photo named: RU-2024-001.jpg")

print()

# Test 6: Test rembg specifically
print("6. Testing rembg (background removal)...")
try:
    from rembg import remove
    print("   ✅ rembg imported successfully")
    print("   ✅ Background removal ready!")
except Exception as e:
    print(f"   ❌ rembg error: {e}")
    print("      This is likely the onnxruntime issue")

print()

# Test 7: Quick template generation test
print("7. Testing template generation...")
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple test image
    test_img = Image.new('RGB', (1050, 1800), '#FFFFFF')
    draw = ImageDraw.Draw(test_img)
    draw.text((100, 100), "TEST", fill='#000000')
    
    test_path = PROJECT_PATH / "Templates" / "test_template.png"
    test_img.save(test_path)
    
    print(f"   ✅ Template generation works!")
    print(f"   Test template saved to: {test_path}")
    
    # Clean up
    test_path.unlink()
    
except Exception as e:
    print(f"   ❌ Template generation error: {e}")

print()
print("="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print()

# Final recommendations
print("📋 NEXT STEPS:")
print()
if not template_path.exists():
    print("1. Generate template:")
    print("   python rimberio_template.py")
    print()

if not photos:
    print("2. Add a test photo to Input_Raw:")
    print("   - Name it exactly: RU-2024-001.jpg")
    print("   - Must match ID_Number in students.csv")
    print()

print("3. Run the system:")
print("   python school_id_processor.py")
print()
print("4. The system will watch for new photos and process them automatically!")
print()
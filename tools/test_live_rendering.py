"""
LIVE RENDERING TEST - Using Actual Employee Data
================================================
This will render using the EXACT files in data/input/
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.school_id_processor import SchoolIDProcessor
from PIL import Image
import cv2

def main():
    print("=" * 80)
    print("LIVE RENDERING TEST - EMP-2024-013")
    print("=" * 80)
    
    # Initialize processor with minimal config
    config = {
        'INPUT_FOLDER': 'data/input',
        'OUTPUT_FOLDER': 'data/output',
        'TEMPLATE_FOLDER': 'data/templates',
    }
    processor = SchoolIDProcessor(config)
    
    # Load the actual JSON data
    json_path = Path('data/input/EMP-2024-013.json')
    if not json_path.exists():
        print(f"✗ JSON file not found: {json_path}")
        return
    
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    print(f"\n[1] Loaded JSON data:")
    for key, value in json_data.items():
        print(f"   {key}: {value}")
    
    # Call get_student_data to see what the processor extracts
    student_id = "EMP-2024-013"
    data = processor.get_student_data(student_id + ".jpg")
    
    print(f"\n[2] Processed data dictionary:")
    for key in ['name', 'full_name', 'position', 'department', 'id_number']:
        print(f"   {key}: {data.get(key, 'N/A')}")
    
    # Check photo file
    photo_path = Path('data/input/EMP-2024-013.jpg')
    if not photo_path.exists():
        print(f"\n✗ Photo file not found: {photo_path}")
        return
    
    print(f"\n[3] Loading photo: {photo_path}")
    img = cv2.imread(str(photo_path))
    if img is None:
        print("✗ Failed to load photo")
        return
    
    print(f"✓ Photo loaded: {img.shape}")
    
    # Convert to PIL for rendering
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    
    # Render using the layer-based system
    print(f"\n[4] Rendering with layer-based system...")
    front_card, back_card = processor._render_with_layers(data, img_pil)
    
    if front_card and back_card:
        # Save output
        output_dir = Path('data/output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        front_path = output_dir / f"{student_id}_FRONT_TEST.png"
        back_path = output_dir / f"{student_id}_BACK_TEST.png"
        
        front_card.save(front_path)
        back_card.save(back_path)
        
        print(f"✓ Saved: {front_path}")
        print(f"✓ Saved: {back_path}")
        
        print(f"\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"\nOpen the files to verify:")
        print(f"   {front_path}")
        print(f"   {back_path}")
        print(f"\nExpected content:")
        print(f"   Name: {data.get('name', 'N/A')}")
        print(f"   Position: {data.get('position', 'N/A')}")
        print(f"   Department: {data.get('department', 'N/A')}")
        print(f"\nIf you see 'New Text', the template has wrong field names.")
        print(f"If you see the actual values above, data binding works!")
    else:
        print("✗ Rendering failed")

if __name__ == '__main__':
    main()

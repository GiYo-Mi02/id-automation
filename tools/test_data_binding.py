"""
DATA BINDING VERIFICATION TEST
==============================
Tests that text layers correctly substitute dynamic data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.template_renderer import load_active_template, TemplateRenderer
from PIL import Image
import logging

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

def main():
    print("=" * 80)
    print("DATA BINDING VERIFICATION TEST")
    print("=" * 80)
    
    # Test data - simulating a teacher
    test_data = {
        'id': 'EMP-2024-013',
        'type': 'teacher',
        'name': 'JUAN DELA CRUZ',
        'full_name': 'JUAN DELA CRUZ',
        'id_number': 'EMP-2024-013',
        'position': 'TEACHER III',
        'department': 'MATHEMATICS DEPARTMENT',
        'employee_type': 'Teaching Staff',
        'contact_number': '09171234567',
        'emergency_contact': '09171234567',
        'address': '123 Main St, Taguig City',
        'birth_date': '1985-06-15',
        'blood_type': 'O+',
        'school_year': '2025-2026',
    }
    
    print(f"\n[1] Test Data:")
    print(f"   Name: {test_data['name']}")
    print(f"   ID: {test_data['id_number']}")
    print(f"   Position: {test_data['position']}")
    print(f"   Department: {test_data['department']}")
    
    # Load active template
    print(f"\n[2] Loading active template...")
    template = load_active_template()
    
    if not template:
        print("✗ No active template found!")
        return
    
    print(f"✓ Template loaded: {template['templateName']}")
    
    # Check template layers
    front_layers = template.get('front', {}).get('layers', [])
    print(f"\n[3] Analyzing template layers ({len(front_layers)} front layers):")
    
    for i, layer in enumerate(front_layers):
        if layer.get('type') == 'text':
            field = layer.get('field', 'N/A')
            fallback_text = layer.get('text', 'N/A')
            print(f"   [{i}] Text Layer:")
            print(f"       Field: '{field}'")
            print(f"       Fallback Text: '{fallback_text}'")
            
            if field == 'static':
                print(f"       → Will render: '{fallback_text}' (static)")
            else:
                value = test_data.get(field, fallback_text)
                print(f"       → Will render: '{value}' (from data['{field}'])")
    
    # Render
    print(f"\n[4] Rendering with data binding...")
    renderer = TemplateRenderer()
    
    try:
        front_img = renderer.render(template, test_data, photo_image=None, side='front')
        print(f"✓ Front rendered: {front_img.width}x{front_img.height}")
        
        # Save output
        output_path = Path('data/output/TEST_DATA_BINDING.png')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        front_img.save(output_path)
        print(f"\n✓ Saved: {output_path}")
        
        print(f"\n[5] Verification:")
        print(f"   Open {output_path} and check:")
        print(f"   • Name should be: {test_data['name']}")
        print(f"   • ID should be: {test_data['id_number']}")
        print(f"   • Position should be: {test_data['position']}")
        print(f"   • Department should be: {test_data['department']}")
        print(f"\n   If you see 'New Text' or 'UNKNOWN', data binding is broken.")
        print(f"   If you see the actual values above, data binding works! ✓")
        
    except Exception as e:
        print(f"✗ Rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

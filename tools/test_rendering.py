"""
End-to-End Rendering Test
=========================
Tests the complete rendering pipeline from database to output image.
Run this after fixing the blank output bug to verify everything works.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.template_renderer import load_active_template, TemplateRenderer
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

def main():
    print("=" * 80)
    print("END-TO-END RENDERING TEST")
    print("=" * 80)
    
    # Load active template
    print("\n[1] Loading active template...")
    template = load_active_template()
    
    if not template:
        print("✗ No active template found!")
        print("  → Go to Editor and activate a template first")
        return
    
    print(f"✓ Template loaded: {template['templateName']} (ID: {template['id']})")
    
    # Create test data
    test_data = {
        'name': 'Juan Dela Cruz',
        'position': 'Teacher III',
        'department': 'Mathematics',
        'id_number': 'EMP-2024-013',
        'date_issued': '2024-01-01',
        'valid_until': '2025-12-31',
    }
    
    print(f"\n[2] Test data: {test_data['name']} ({test_data['id_number']})")
    
    # Render both sides
    print("\n[3] Rendering template...")
    renderer = TemplateRenderer()
    
    try:
        # Render front
        print("   • Rendering front side...")
        front_img = renderer.render(template, test_data, photo_image=None, side='front')
        print(f"   ✓ Front rendered: {front_img.width}x{front_img.height} {front_img.mode}")
        
        # Render back
        print("   • Rendering back side...")
        back_img = renderer.render(template, test_data, photo_image=None, side='back')
        print(f"   ✓ Back rendered: {back_img.width}x{back_img.height} {back_img.mode}")
        
    except Exception as e:
        print(f"   ✗ Rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check if images are blank (all white)
    print("\n[4] Validating output...")
    
    def is_blank(img):
        """Check if image is all white/single color"""
        extrema = img.convert('L').getextrema()
        return extrema[0] == extrema[1]
    
    front_blank = is_blank(front_img)
    back_blank = is_blank(back_img)
    
    if front_blank:
        print("   ✗ WARNING: Front side appears BLANK (all same color)")
        print("     This means background or layers failed to render!")
    else:
        print("   ✓ Front side has content")
    
    if back_blank:
        print("   ✗ WARNING: Back side appears BLANK (all same color)")
    else:
        print("   ✓ Back side has content")
    
    # Save test output
    print("\n[5] Saving test output...")
    output_dir = Path('data/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    front_path = output_dir / 'TEST_RENDER_FRONT.png'
    back_path = output_dir / 'TEST_RENDER_BACK.png'
    
    front_img.save(front_path)
    back_img.save(back_path)
    
    print(f"   ✓ Saved: {front_path}")
    print(f"   ✓ Saved: {back_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    if front_blank or back_blank:
        print("\n⚠ WARNING: Output appears blank!")
        print("  Check the logs above for ERROR messages about missing backgrounds or layers.")
        print("  Run: python tools/test_template_load.py for detailed diagnostics")
    else:
        print("\n✓ SUCCESS: Template renders correctly!")
        print("  Open the saved files to verify the output matches your Editor design.")
    
    print(f"\nOutput files:")
    print(f"  • {front_path}")
    print(f"  • {back_path}")

if __name__ == '__main__':
    main()

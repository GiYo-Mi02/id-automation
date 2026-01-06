"""
CRITICAL DIAGNOSTIC: Template Save/Load Verification
====================================================
This test will check if layers are being properly saved and loaded.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import db_manager
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def main():
    print("=" * 80)
    print("TEMPLATE SAVE/LOAD VERIFICATION")
    print("=" * 80)
    
    # Get active template
    print("\n[1] Fetching active template from database...")
    query = """
        SELECT id, name, template_type, is_active,
               canvas, front_layers, back_layers
        FROM id_templates
        WHERE is_active = 1
        LIMIT 1
    """
    
    row = db_manager.execute_query(query, None, fetch_one=True)
    
    if not row:
        print("✗ No active template found!")
        print("  → Go to Editor, create a template with layers, and activate it")
        return
    
    print(f"✓ Found active template: {row['name']} (ID: {row['id']})")
    
    # Parse and analyze front_layers
    print("\n[2] Analyzing FRONT layers...")
    front_json = row['front_layers']
    print(f"   Raw type: {type(front_json)}")
    print(f"   Raw length: {len(str(front_json))} characters")
    
    if isinstance(front_json, str):
        print(f"   Raw content (first 200 chars): {front_json[:200]}")
        try:
            front_data = json.loads(front_json)
        except json.JSONDecodeError as e:
            print(f"   ✗ INVALID JSON: {e}")
            return
    else:
        front_data = front_json
    
    print(f"   Parsed type: {type(front_data)}")
    
    if isinstance(front_data, dict):
        bg = front_data.get('backgroundImage')
        layers = front_data.get('layers', [])
        print(f"   ✓ Structure: dict with 'backgroundImage' and 'layers'")
        print(f"   • Background: {bg or 'None'}")
        print(f"   • Layers: {len(layers)}")
        
        if len(layers) == 0:
            print(f"\n   ⚠️  WARNING: ZERO LAYERS IN FRONT!")
            print(f"   This is why your output is blank!")
            print(f"   Expected: At least 1-5 layers (photo, name, ID, etc.)")
        else:
            print(f"\n   ✓ Layers found:")
            for i, layer in enumerate(layers[:5]):  # Show first 5
                print(f"      [{i}] {layer.get('type')} - {layer.get('name')} (ID: {layer.get('id')})")
                print(f"          Field: {layer.get('field')}, Visible: {layer.get('visible', True)}")
    else:
        print(f"   ✗ UNEXPECTED STRUCTURE: {type(front_data)}")
        print(f"   Expected: dict with 'backgroundImage' and 'layers' keys")
        return
    
    # Parse and analyze back_layers
    print("\n[3] Analyzing BACK layers...")
    back_json = row['back_layers']
    
    if isinstance(back_json, str):
        try:
            back_data = json.loads(back_json)
        except json.JSONDecodeError as e:
            print(f"   ✗ INVALID JSON: {e}")
            return
    else:
        back_data = back_json
    
    if isinstance(back_data, dict):
        bg = back_data.get('backgroundImage')
        layers = back_data.get('layers', [])
        print(f"   ✓ Structure: dict with 'backgroundImage' and 'layers'")
        print(f"   • Background: {bg or 'None'}")
        print(f"   • Layers: {len(layers)}")
        
        if len(layers) == 0:
            print(f"\n   ⚠️  WARNING: ZERO LAYERS IN BACK!")
        else:
            print(f"\n   ✓ Layers found:")
            for i, layer in enumerate(layers[:5]):
                print(f"      [{i}] {layer.get('type')} - {layer.get('name')} (ID: {layer.get('id')})")
    
    # Analyze canvas
    print("\n[4] Analyzing CANVAS...")
    canvas_json = row['canvas']
    
    if isinstance(canvas_json, str):
        canvas_data = json.loads(canvas_json)
    else:
        canvas_data = canvas_json
    
    if isinstance(canvas_data, dict):
        print(f"   ✓ Canvas: {canvas_data.get('width')}x{canvas_data.get('height')}")
        print(f"   • Background Color: {canvas_data.get('backgroundColor')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSIS SUMMARY")
    print("=" * 80)
    
    front_layer_count = len(front_data.get('layers', [])) if isinstance(front_data, dict) else 0
    back_layer_count = len(back_data.get('layers', [])) if isinstance(back_data, dict) else 0
    
    if front_layer_count == 0 and back_layer_count == 0:
        print("\n❌ CRITICAL ISSUE: NO LAYERS IN DATABASE!")
        print("\nRoot Cause: The template was saved WITHOUT layers.")
        print("\nPossible Reasons:")
        print("  1. You deleted all layers before saving")
        print("  2. The Editor is not sending layer data to the API")
        print("  3. The backend is not storing layer data correctly")
        print("\nFix:")
        print("  1. Go to Editor → Create NEW template")
        print("  2. Import background")
        print("  3. Add at least ONE text layer (click '+ Text' button)")
        print("  4. Click 'Save'")
        print("  5. Click 'Activate'")
        print("  6. Run this diagnostic again")
        print("\nDEBUG: Check browser console when clicking 'Save':")
        print("  - Look for the PUT request payload")
        print("  - Verify 'front.layers' and 'back.layers' contain layer objects")
    elif front_layer_count == 0 or back_layer_count == 0:
        print(f"\n⚠️  WARNING: Missing layers on one side")
        print(f"   Front: {front_layer_count} layers")
        print(f"   Back: {back_layer_count} layers")
        print("\nThis is OK if you intentionally left one side empty.")
    else:
        print(f"\n✓ LOOKS GOOD!")
        print(f"   Front: {front_layer_count} layers")
        print(f"   Back: {back_layer_count} layers")
        print("\nIf you still get blank output:")
        print("  - Check that layers are VISIBLE (eye icon in Editor)")
        print("  - Run: python tools/test_rendering.py")
        print("  - Check the output PNG files to see if text renders")

if __name__ == '__main__':
    main()

"""
Diagnostic tool to test template loading and path resolution.
Run this to verify your active template is properly structured.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.template_renderer import load_active_template
from app.db.database import db_manager
import logging

# Configure logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

def main():
    print("=" * 80)
    print("TEMPLATE LOAD DIAGNOSTIC TEST")
    print("=" * 80)
    
    # Test 1: Check database connection
    print("\n[1] Testing database connection...")
    try:
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM id_templates", None, fetch_one=True)
        print(f"✓ Database connected. Found {result['count']} templates.")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return
    
    # Test 2: Check for active template
    print("\n[2] Checking for active template...")
    try:
        result = db_manager.execute_query(
            "SELECT id, name, template_type, is_active FROM id_templates WHERE is_active = TRUE",
            None,
            fetch_all=True
        )
        if not result:
            print("✗ NO ACTIVE TEMPLATE FOUND!")
            print("   → Go to Editor and click 'Activate' on a template.")
            return
        
        print(f"✓ Found {len(result)} active template(s):")
        for row in result:
            print(f"   • ID={row['id']}, Name='{row['name']}', Type={row['template_type']}")
    except Exception as e:
        print(f"✗ Query error: {e}")
        return
    
    # Test 3: Load template using renderer
    print("\n[3] Loading template with renderer...")
    try:
        template = load_active_template()
        if not template:
            print("✗ load_active_template() returned None!")
            return
        
        print(f"✓ Template loaded successfully!")
        print(f"   • ID: {template.get('id')}")
        print(f"   • Name: {template.get('templateName')}")
        print(f"   • Type: {template.get('templateType')}")
        print(f"   • Canvas: {template.get('canvas', {}).get('width')}x{template.get('canvas', {}).get('height')}")
        
    except Exception as e:
        print(f"✗ Load error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Check background images
    print("\n[4] Checking background images...")
    for side in ['front', 'back']:
        side_data = template.get(side, {})
        bg_image = side_data.get('backgroundImage')
        layers = side_data.get('layers', [])
        
        print(f"\n   {side.upper()} Side:")
        if bg_image:
            print(f"   • Background: {bg_image}")
            
            # Try to resolve path
            if bg_image.startswith('/api/templates/backgrounds/'):
                parts = bg_image.split('/api/templates/backgrounds/', 1)
                if len(parts) == 2:
                    relative_path = parts[1]
                    full_path = Path('data') / 'templates' / relative_path
                    if full_path.exists():
                        print(f"   ✓ File exists: {full_path}")
                        print(f"     Size: {full_path.stat().st_size} bytes")
                    else:
                        print(f"   ✗ FILE NOT FOUND: {full_path}")
            else:
                print(f"   ⚠ Non-standard path format")
        else:
            print(f"   • Background: None")
        
        print(f"   • Layers: {len(layers)}")
        for i, layer in enumerate(layers):
            print(f"      [{i}] {layer.get('type')} - {layer.get('id')} (visible={layer.get('visible', True)})")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()

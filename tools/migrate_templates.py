"""
Database Migration Script for Template System v2
Migrates from layout.json to database-backed layer templates

Run this script to:
1. Create the new database tables (teachers, id_templates)
2. Add new columns to students table
3. Import existing layout.json as a database template
4. Optionally migrate teacher records from a CSV file

Usage:
    python tools/migrate_templates.py
    python tools/migrate_templates.py --skip-schema  # Skip table creation
    python tools/migrate_templates.py --teachers teachers.csv  # Import teachers
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "school_id_system"),
}

# Schema SQL
SCHEMA_SQL = """
-- Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    specialization VARCHAR(100),
    contact_number VARCHAR(20),
    emergency_contact_name VARCHAR(200),
    emergency_contact_number VARCHAR(20),
    address TEXT,
    photo_path VARCHAR(255),
    birth_date DATE,
    blood_type VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ID Templates Table (Layer-based)
CREATE TABLE IF NOT EXISTS id_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    template_type ENUM('student', 'teacher', 'staff', 'visitor') NOT NULL DEFAULT 'student',
    school_level ENUM('elementary', 'junior_high', 'senior_high', 'college', 'all') DEFAULT 'all',
    is_active BOOLEAN DEFAULT FALSE,
    canvas JSON COMMENT 'Canvas dimensions and background settings',
    front_layers JSON COMMENT 'Array of layer objects for front side',
    back_layers JSON COMMENT 'Array of layer objects for back side',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type_level (template_type, school_level),
    INDEX idx_active (is_active)
);

-- School Settings Table
CREATE TABLE IF NOT EXISTS school_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

# Additional columns for students table
STUDENTS_ALTER_SQL = """
ALTER TABLE students 
    ADD COLUMN IF NOT EXISTS birth_date DATE AFTER address,
    ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10) AFTER birth_date,
    ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(50) AFTER blood_type,
    ADD COLUMN IF NOT EXISTS school_year VARCHAR(20) DEFAULT '2025-2026' AFTER emergency_contact,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER school_year,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
"""


def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def execute_schema(conn):
    """Execute schema creation SQL"""
    cursor = conn.cursor()
    try:
        # Execute multi-statement schema
        for statement in SCHEMA_SQL.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        # Try to add columns to students table (may fail if columns exist)
        try:
            for statement in STUDENTS_ALTER_SQL.split(','):
                statement = statement.strip()
                if statement.startswith('ADD'):
                    try:
                        cursor.execute(f"ALTER TABLE students {statement}")
                    except:
                        pass  # Column probably already exists
        except Exception as e:
            print(f"Note: Student table update skipped: {e}")
        
        conn.commit()
        print("✓ Database schema created/updated successfully")
        return True
    except Error as e:
        print(f"✗ Schema creation error: {e}")
        return False
    finally:
        cursor.close()


def load_legacy_layout():
    """Load the existing layout.json file"""
    layout_path = Path(__file__).parent.parent / "data" / "layout.json"
    if not layout_path.exists():
        print(f"No legacy layout.json found at {layout_path}")
        return None
    
    try:
        with open(layout_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading layout.json: {e}")
        return None


def convert_legacy_to_layers(legacy_layout):
    """Convert old layout format to new layer-based format"""
    front_layers = []
    back_layers = []
    
    z_index = 1
    
    # Convert front elements
    if 'front' in legacy_layout:
        for key, value in legacy_layout['front'].items():
            layer = {
                'id': f'legacy-front-{key}',
                'name': key.replace('_', ' ').title(),
                'field': key,
                'x': value.get('x', 0),
                'y': value.get('y', 0),
                'width': value.get('width', value.get('w', 200)),
                'height': value.get('height', value.get('h', 30)),
                'zIndex': z_index,
                'visible': True,
                'locked': False,
            }
            
            if key == 'photo':
                layer['type'] = 'image'
                layer['objectFit'] = 'cover'
                layer['borderRadius'] = 0
            else:
                layer['type'] = 'text'
                layer['text'] = key.upper()
                layer['fontSize'] = value.get('fontSize', value.get('size', 16))
                layer['fontFamily'] = 'Arial'
                layer['fontWeight'] = value.get('fontWeight', 'normal')
                layer['color'] = value.get('color', '#000000')
                layer['textAlign'] = value.get('align', 'left')
                layer['wordWrap'] = False
            
            front_layers.append(layer)
            z_index += 1
    
    # Reset z_index for back
    z_index = 1
    
    # Convert back elements
    if 'back' in legacy_layout:
        for key, value in legacy_layout['back'].items():
            layer = {
                'id': f'legacy-back-{key}',
                'type': 'text',
                'name': key.replace('_', ' ').title(),
                'field': key,
                'text': key.upper(),
                'x': value.get('x', 0),
                'y': value.get('y', 0),
                'width': value.get('width', 200),
                'height': value.get('height', 30),
                'zIndex': z_index,
                'visible': True,
                'locked': False,
                'fontSize': value.get('fontSize', value.get('size', 16)),
                'fontFamily': 'Arial',
                'fontWeight': value.get('fontWeight', 'normal'),
                'color': value.get('color', '#000000'),
                'textAlign': value.get('align', 'left'),
                'wordWrap': True,
            }
            back_layers.append(layer)
            z_index += 1
    
    return front_layers, back_layers


def import_legacy_template(conn, legacy_layout):
    """Import legacy layout.json as a database template"""
    if not legacy_layout:
        print("No legacy layout to import")
        return False
    
    front_layers, back_layers = convert_legacy_to_layers(legacy_layout)
    
    canvas = {
        'width': 591,
        'height': 1004,
        'backgroundColor': '#FFFFFF',
        'backgroundImage': None
    }
    
    cursor = conn.cursor()
    try:
        # Check if a template already exists
        cursor.execute("SELECT COUNT(*) FROM id_templates WHERE name = 'Imported Legacy Template'")
        if cursor.fetchone()[0] > 0:
            print("Legacy template already imported")
            return True
        
        # Insert the template
        cursor.execute("""
            INSERT INTO id_templates (name, template_type, school_level, is_active, canvas, front_layers, back_layers)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'Imported Legacy Template',
            'student',
            'all',
            True,
            json.dumps(canvas),
            json.dumps(front_layers),
            json.dumps(back_layers)
        ))
        
        conn.commit()
        print(f"✓ Imported legacy template with {len(front_layers)} front layers and {len(back_layers)} back layers")
        return True
    except Error as e:
        print(f"✗ Template import error: {e}")
        return False
    finally:
        cursor.close()


def create_default_template(conn):
    """Create a default student ID template"""
    canvas = {
        'width': 591,
        'height': 1004,
        'backgroundColor': '#FFFFFF',
        'backgroundImage': None
    }
    
    front_layers = [
        {
            'id': 'photo-1',
            'type': 'image',
            'name': 'Photo',
            'field': 'photo',
            'x': 196,
            'y': 180,
            'width': 200,
            'height': 250,
            'zIndex': 1,
            'visible': True,
            'locked': False,
            'objectFit': 'cover',
            'borderRadius': 8,
        },
        {
            'id': 'name-1',
            'type': 'text',
            'name': 'Full Name',
            'field': 'full_name',
            'text': 'STUDENT NAME',
            'x': 50,
            'y': 460,
            'width': 491,
            'height': 40,
            'zIndex': 2,
            'visible': True,
            'locked': False,
            'fontSize': 28,
            'fontFamily': 'Arial',
            'fontWeight': 'bold',
            'color': '#000000',
            'textAlign': 'center',
            'wordWrap': False,
            'uppercase': True,
        },
        {
            'id': 'id-1',
            'type': 'text',
            'name': 'ID Number',
            'field': 'id_number',
            'text': '2024-001',
            'x': 50,
            'y': 510,
            'width': 491,
            'height': 30,
            'zIndex': 3,
            'visible': True,
            'locked': False,
            'fontSize': 22,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#333333',
            'textAlign': 'center',
            'wordWrap': False,
        },
        {
            'id': 'grade-1',
            'type': 'text',
            'name': 'Grade & Section',
            'field': 'grade_level',
            'text': 'Grade 7 - Einstein',
            'x': 50,
            'y': 550,
            'width': 491,
            'height': 25,
            'zIndex': 4,
            'visible': True,
            'locked': False,
            'fontSize': 18,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#555555',
            'textAlign': 'center',
            'wordWrap': False,
        },
    ]
    
    back_layers = [
        {
            'id': 'lrn-1',
            'type': 'text',
            'name': 'LRN',
            'field': 'lrn',
            'text': 'LRN: 123456789012',
            'x': 50,
            'y': 100,
            'width': 491,
            'height': 30,
            'zIndex': 1,
            'visible': True,
            'locked': False,
            'fontSize': 16,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#000000',
            'textAlign': 'left',
            'wordWrap': False,
        },
        {
            'id': 'guardian-1',
            'type': 'text',
            'name': 'Guardian',
            'field': 'guardian_name',
            'text': 'Guardian: PARENT NAME',
            'x': 50,
            'y': 140,
            'width': 491,
            'height': 30,
            'zIndex': 2,
            'visible': True,
            'locked': False,
            'fontSize': 14,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#333333',
            'textAlign': 'left',
            'wordWrap': True,
        },
        {
            'id': 'address-1',
            'type': 'text',
            'name': 'Address',
            'field': 'address',
            'text': 'Address Line Here',
            'x': 50,
            'y': 180,
            'width': 491,
            'height': 50,
            'zIndex': 3,
            'visible': True,
            'locked': False,
            'fontSize': 12,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#333333',
            'textAlign': 'left',
            'wordWrap': True,
        },
        {
            'id': 'contact-1',
            'type': 'text',
            'name': 'Emergency Contact',
            'field': 'emergency_contact',
            'text': 'Emergency: 09171234567',
            'x': 50,
            'y': 240,
            'width': 491,
            'height': 25,
            'zIndex': 4,
            'visible': True,
            'locked': False,
            'fontSize': 14,
            'fontFamily': 'Arial',
            'fontWeight': 'normal',
            'color': '#333333',
            'textAlign': 'left',
            'wordWrap': False,
        },
        {
            'id': 'qr-1',
            'type': 'qr_code',
            'name': 'QR Code',
            'field': 'id_number',
            'x': 220,
            'y': 700,
            'width': 150,
            'height': 150,
            'zIndex': 5,
            'visible': True,
            'locked': False,
            'backgroundColor': '#FFFFFF',
            'foregroundColor': '#000000',
        },
    ]
    
    cursor = conn.cursor()
    try:
        # Check if default template exists
        cursor.execute("SELECT COUNT(*) FROM id_templates WHERE name = 'Default Student Template'")
        if cursor.fetchone()[0] > 0:
            print("Default template already exists")
            return True
        
        cursor.execute("""
            INSERT INTO id_templates (name, template_type, school_level, is_active, canvas, front_layers, back_layers)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'Default Student Template',
            'student',
            'junior_high',
            True,
            json.dumps(canvas),
            json.dumps(front_layers),
            json.dumps(back_layers)
        ))
        
        conn.commit()
        print("✓ Created default student template")
        return True
    except Error as e:
        print(f"✗ Default template creation error: {e}")
        return False
    finally:
        cursor.close()


def import_teachers_csv(conn, csv_path):
    """Import teachers from a CSV file"""
    import csv
    
    if not Path(csv_path).exists():
        print(f"Teachers CSV not found: {csv_path}")
        return False
    
    cursor = conn.cursor()
    imported = 0
    skipped = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cursor.execute("""
                        INSERT INTO teachers (employee_id, full_name, department, position, specialization, 
                                              contact_number, address)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE full_name = VALUES(full_name)
                    """, (
                        row.get('employee_id', ''),
                        row.get('full_name', row.get('name', '')),
                        row.get('department', ''),
                        row.get('position', ''),
                        row.get('specialization', row.get('subject', '')),
                        row.get('contact_number', row.get('phone', '')),
                        row.get('address', ''),
                    ))
                    imported += 1
                except Error as e:
                    skipped += 1
        
        conn.commit()
        print(f"✓ Imported {imported} teachers ({skipped} skipped)")
        return True
    except Exception as e:
        print(f"✗ Teacher import error: {e}")
        return False
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description='Migrate database to template system v2')
    parser.add_argument('--skip-schema', action='store_true', help='Skip schema creation')
    parser.add_argument('--teachers', type=str, help='Path to teachers CSV file')
    parser.add_argument('--skip-default', action='store_true', help='Skip default template creation')
    args = parser.parse_args()
    
    print("=" * 50)
    print("Template System v2 Migration")
    print("=" * 50)
    print()
    
    # Connect to database
    conn = get_connection()
    if not conn:
        print("Failed to connect to database. Check your configuration.")
        return 1
    
    try:
        # Step 1: Create schema
        if not args.skip_schema:
            print("Step 1: Creating database schema...")
            execute_schema(conn)
        else:
            print("Step 1: Schema creation skipped")
        print()
        
        # Step 2: Import legacy layout
        print("Step 2: Importing legacy layout.json...")
        legacy_layout = load_legacy_layout()
        if legacy_layout:
            import_legacy_template(conn, legacy_layout)
        else:
            print("No legacy layout found, skipping import")
        print()
        
        # Step 3: Create default template
        if not args.skip_default:
            print("Step 3: Creating default templates...")
            create_default_template(conn)
        else:
            print("Step 3: Default template creation skipped")
        print()
        
        # Step 4: Import teachers (if specified)
        if args.teachers:
            print("Step 4: Importing teachers...")
            import_teachers_csv(conn, args.teachers)
        else:
            print("Step 4: Teacher import skipped (no file specified)")
        print()
        
        print("=" * 50)
        print("Migration completed!")
        print("=" * 50)
        return 0
        
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to system path to import app config
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    print("[ERROR] 'mysql-connector-python' is not installed. Please install it using pip:")
    print("   pip install mysql-connector-python")
    sys.exit(1)

from app.core.config import get_settings

def execute_statements(cursor, statements: list, step_name: str):
    """Executes a list of SQL statements sequentially."""
    print(f"Executing: {step_name}...")
    stmt_count = 0
    for stmt in statements:
        try:
            cursor.execute(stmt)
            # Consume any result set to clear the buffer
            if cursor.with_rows:
                cursor.fetchall()
            stmt_count += 1
        except MySQLError as e:
            # Ignore duplicate column/key/table errors
            err_msg = str(e)
            if "already exists" in err_msg.lower() or "duplicate" in err_msg.lower() or "Duplicate column name" in err_msg:
                print(f"  [INFO] Skipped statement: {err_msg}")
                continue
            print(f"  [ERROR] Failed to execute statement:\n{stmt[:200]}...\nReason: {e}")
            return False
    print(f"  [OK] Successfully executed {stmt_count} statements.")
    return True

def get_default_student_template() -> tuple:
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
    
    return json.dumps(canvas), json.dumps({"layers": front_layers}), json.dumps({"layers": back_layers})

def get_default_teacher_template() -> tuple:
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
            'text': 'TEACHER NAME',
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
            'id': 'position-1',
            'type': 'text',
            'name': 'Position',
            'field': 'position',
            'text': 'Teacher',
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
    ]
    
    back_layers = [
        {
            'id': 'contact-1',
            'type': 'text',
            'name': 'Emergency Contact',
            'field': 'emergency_contact_number',
            'text': 'Emergency: 09171234567',
            'x': 50,
            'y': 240,
            'width': 491,
            'height': 25,
            'zIndex': 1,
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
            'field': 'employee_id',
            'x': 220,
            'y': 700,
            'width': 150,
            'height': 150,
            'zIndex': 2,
            'visible': True,
            'locked': False,
            'backgroundColor': '#FFFFFF',
            'foregroundColor': '#000000',
        },
    ]
    return json.dumps(canvas), json.dumps({"layers": front_layers}), json.dumps({"layers": back_layers})

def reupload_schema(override_db_name=None):
    settings = get_settings()
    db_config = settings.database
    
    # Determine target database name
    target_db = override_db_name or db_config.database
    
    print("=" * 60)
    print("School ID System - Database Schema Setup/Repair Utility")
    print("=" * 60)
    print(f"Target Database: {target_db}")
    print(f"MySQL Host:      {db_config.host}:{db_config.port}")
    print(f"MySQL User:      {db_config.user}")
    print("=" * 60)
    
    # Connect
    connection_params = {
        "host": db_config.host,
        "port": db_config.port,
        "user": db_config.user,
        "password": db_config.password,
    }
    
    try:
        print("\nStep 1: Connecting to MySQL server...")
        conn = mysql.connector.connect(**connection_params)
        cursor = conn.cursor(dictionary=True)
    except MySQLError as e:
        print(f"[ERROR] Failed to connect to MySQL server: {e}")
        print("Please check your .env configuration and verify that MySQL is running.")
        sys.exit(1)
        
    try:
        # Create database
        print(f"Step 2: Ensuring database '{target_db}' exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        
        cursor.execute(f"USE `{target_db}`")
        print(f"  [OK] Connected to database '{target_db}'")
        
        # 3. Check if id_templates exists and check if it has template_name instead of name
        print("\nStep 3: Checking for legacy or broken 'id_templates' table...")
        cursor.execute("SHOW TABLES LIKE 'id_templates'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            cursor.execute("DESCRIBE id_templates")
            columns = cursor.fetchall()
            has_template_name = any(col['Field'] == 'template_name' for col in columns)
            
            if has_template_name:
                print("  [WARN] Legacy 'id_templates' table detected (contains obsolete 'template_name' column).")
                # Count records
                cursor.execute("SELECT COUNT(*) as c FROM id_templates")
                row_count = cursor.fetchone()['c']
                
                if row_count == 0:
                    print("  [INFO] Legacy table is empty. Dropping it safely...")
                    cursor.execute("DROP TABLE id_templates")
                    conn.commit()
                    print("  [OK] Table dropped.")
                else:
                    backup_name = f"id_templates_backup_{int(datetime.now().timestamp())}"
                    print(f"  [INFO] Legacy table contains {row_count} records. Backing it up to '{backup_name}' and dropping...")
                    cursor.execute(f"RENAME TABLE id_templates TO {backup_name}")
                    conn.commit()
                    print(f"  [OK] Table backed up and dropped.")
            else:
                print("  [OK] 'id_templates' table is up-to-date or already in the correct format.")
                
        # 4. Create target schema tables directly
        print("\nStep 4: Ensuring all tables have the correct schema...")
        
        schema_queries = {
            "students": """
                CREATE TABLE IF NOT EXISTS students (
                    id_number VARCHAR(50) PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    lrn VARCHAR(50),
                    grade_level VARCHAR(20),
                    section VARCHAR(50),
                    guardian_name VARCHAR(100),
                    address VARCHAR(255),
                    guardian_contact VARCHAR(50),
                    photo_path VARCHAR(255),
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    emergency_contact VARCHAR(100),
                    emergency_contact_number VARCHAR(50),
                    school_year VARCHAR(20) DEFAULT '2025-2026',
                    status ENUM('active', 'inactive', 'graduated', 'transferred') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name),
                    INDEX idx_section (section),
                    INDEX idx_grade_level (grade_level),
                    INDEX idx_students_created_at (created_at DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "teachers": """
                CREATE TABLE IF NOT EXISTS teachers (
                    employee_id VARCHAR(50) PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    specialization VARCHAR(150),
                    contact_number VARCHAR(50),
                    emergency_contact_name VARCHAR(100),
                    emergency_contact_number VARCHAR(50),
                    address VARCHAR(255),
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    photo_path VARCHAR(255),
                    hire_date DATE,
                    employment_status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name),
                    INDEX idx_department (department),
                    INDEX idx_position (position),
                    INDEX idx_status (employment_status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "staff": """
                CREATE TABLE IF NOT EXISTS staff (
                    id INT AUTO_INCREMENT,
                    id_number VARCHAR(50) NOT NULL,
                    employee_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    contact_number VARCHAR(50),
                    emergency_contact_name VARCHAR(200),
                    emergency_contact_number VARCHAR(50),
                    address TEXT,
                    birth_date DATE,
                    blood_type VARCHAR(10),
                    photo_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    UNIQUE KEY uk_staff_id_number (id_number),
                    UNIQUE KEY uk_staff_employee_id (employee_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "id_templates": """
                CREATE TABLE IF NOT EXISTS id_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    template_type ENUM('student', 'teacher', 'staff', 'visitor') NOT NULL DEFAULT 'student',
                    school_level ENUM('elementary', 'junior_high', 'senior_high', 'college', 'all') DEFAULT 'all',
                    is_active BOOLEAN DEFAULT FALSE,
                    is_active_for_students BOOLEAN DEFAULT FALSE,
                    is_active_for_teachers BOOLEAN DEFAULT FALSE,
                    is_active_for_staff BOOLEAN DEFAULT FALSE,
                    thumbnail LONGTEXT,
                    canvas JSON COMMENT 'Canvas dimensions and background settings',
                    front_layers JSON COMMENT 'Array of layer objects for front side',
                    back_layers JSON COMMENT 'Array of layer objects for back side',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_type_level (template_type, school_level),
                    INDEX idx_active (is_active),
                    INDEX idx_templates_active_students (is_active_for_students),
                    INDEX idx_templates_active_teachers (is_active_for_teachers),
                    INDEX idx_templates_active_staff (is_active_for_staff)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "generation_history": """
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(100),
                    section VARCHAR(50),
                    lrn VARCHAR(50),
                    guardian_name VARCHAR(100),
                    address VARCHAR(255),
                    guardian_contact VARCHAR(50),
                    file_path VARCHAR(255),
                    status ENUM('success', 'failed', 'pending') DEFAULT 'success',
                    error_message TEXT,
                    processing_time_ms INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_student_id (student_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "teacher_generation_history": """
                CREATE TABLE IF NOT EXISTS teacher_generation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL,
                    full_name VARCHAR(100),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    status ENUM('success', 'failed', 'pending') DEFAULT 'success',
                    error_message TEXT,
                    processing_time_ms INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_employee_id (employee_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "teacher_history": """
                CREATE TABLE IF NOT EXISTS teacher_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_id VARCHAR(50),
                    full_name VARCHAR(200),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    template_id INT,
                    status ENUM('success', 'failed') DEFAULT 'success',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_teacher_history_teacher_id (teacher_id),
                    INDEX idx_teacher_history_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "staff_history": """
                CREATE TABLE IF NOT EXISTS staff_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    staff_id VARCHAR(50),
                    full_name VARCHAR(200),
                    department VARCHAR(100),
                    position VARCHAR(100),
                    file_path VARCHAR(255),
                    template_id INT,
                    status ENUM('success', 'failed') DEFAULT 'success',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_staff_history_staff_id (staff_id),
                    INDEX idx_staff_history_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "school_settings": """
                CREATE TABLE IF NOT EXISTS school_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "v_active_templates_view": """
                CREATE OR REPLACE VIEW v_active_templates AS
                SELECT 
                    id,
                    name,
                    template_type,
                    school_level,
                    canvas,
                    front_layers,
                    back_layers,
                    created_at,
                    updated_at
                FROM id_templates
                WHERE is_active = TRUE
            """
        }
        
        for table_name, query in schema_queries.items():
            if not execute_statements(cursor, [query], f"Table/View: {table_name}"):
                sys.exit(1)
                
        # 5. Insert default settings
        print("\nStep 5: Setting default school settings...")
        settings_queries = [
            """
            INSERT INTO school_settings (setting_key, setting_value, setting_type, description) VALUES
                ('school_name', 'Sample School', 'string', 'Official school name'),
                ('school_address', '123 School Street, City', 'string', 'School address'),
                ('school_contact', '(02) 123-4567', 'string', 'School contact number'),
                ('principal_name', 'Dr. Juan Dela Cruz', 'string', 'Principal name'),
                ('principal_signature_path', '', 'string', 'Path to principal signature image'),
                ('school_year', '2025-2026', 'string', 'Current school year'),
                ('school_logo_path', '', 'string', 'Path to school logo image')
            ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
            """
        ]
        if not execute_statements(cursor, settings_queries, "Default School Settings"):
            sys.exit(1)
            
        # 6. Insert default templates
        print("\nStep 6: Setting up default templates...")
        cursor.execute("SELECT COUNT(*) as c FROM id_templates")
        template_count = cursor.fetchone()['c']
        
        if template_count == 0:
            student_canvas, student_front, student_back = get_default_student_template()
            teacher_canvas, teacher_front, teacher_back = get_default_teacher_template()
            
            insert_template_query = """
                INSERT INTO id_templates (
                    name, template_type, school_level, is_active, 
                    is_active_for_students, is_active_for_teachers, is_active_for_staff,
                    canvas, front_layers, back_layers
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_template_query, (
                'Default Student Template', 'student', 'junior_high', True,
                True, False, False,
                student_canvas, student_front, student_back
            ))
            
            cursor.execute(insert_template_query, (
                'Default Teacher Template', 'teacher', 'all', True,
                False, True, False,
                teacher_canvas, teacher_front, teacher_back
            ))
            
            conn.commit()
            print("  [OK] Default Student and Teacher templates created and activated.")
        else:
            print("  [OK] Template records already exist. Skipping default templates insert.")
            
        conn.commit()
        print("\n" + "=" * 60)
        print("SUCCESS: Database schema set up and repaired successfully!")
        print("=" * 60)
        print(f"Database '{target_db}' is fully set up and ready to use.")
        print(f"Please make sure DB_NAME={target_db} in your .env file.")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during schema repair: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair and set up the MySQL database schema.")
    parser.add_argument("--db-name", type=str, help="Override database name (defaults to DB_NAME from .env)")
    args = parser.parse_args()
    
    reupload_schema(override_db_name=args.db_name)

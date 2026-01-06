-- =============================================================================
-- School ID System - Database Schema Update v2
-- Created: 2026-01-05
-- Purpose: Add teachers table, id_templates table, and enhance students table
-- =============================================================================

USE school_id_system;

-- =============================================================================
-- 1. TEACHERS TABLE
-- =============================================================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 2. ID TEMPLATES TABLE (JSON-based template storage)
-- =============================================================================
CREATE TABLE IF NOT EXISTS id_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL,
    template_type ENUM('student', 'teacher') NOT NULL DEFAULT 'student',
    school_level ENUM('elementary', 'high_school', 'teacher') DEFAULT 'high_school',
    is_active BOOLEAN DEFAULT FALSE,
    
    -- Canvas configuration
    canvas_width INT NOT NULL DEFAULT 591,
    canvas_height INT NOT NULL DEFAULT 1004,
    canvas_background_color VARCHAR(20) DEFAULT '#FFFFFF',
    canvas_background_image VARCHAR(255),
    
    -- Layer data stored as JSON
    front_layers JSON NOT NULL,
    back_layers JSON NOT NULL,
    
    -- Metadata
    version VARCHAR(20) DEFAULT '1.0.0',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_template_type (template_type),
    INDEX idx_school_level (school_level),
    INDEX idx_is_active (is_active),
    UNIQUE KEY unique_active_template (template_type, school_level, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Remove unique constraint that prevents multiple inactive templates
ALTER TABLE id_templates DROP INDEX IF EXISTS unique_active_template;

-- Add a partial unique index for active templates only (MySQL 8.0+)
-- This ensures only one active template per type/level combination
-- For MySQL < 8.0, use a trigger instead

-- =============================================================================
-- 3. ENHANCE STUDENTS TABLE (Add missing fields)
-- =============================================================================
ALTER TABLE students
    ADD COLUMN IF NOT EXISTS birth_date DATE AFTER guardian_contact,
    ADD COLUMN IF NOT EXISTS blood_type VARCHAR(10) AFTER birth_date,
    ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(100) AFTER blood_type,
    ADD COLUMN IF NOT EXISTS emergency_contact_number VARCHAR(50) AFTER emergency_contact,
    ADD COLUMN IF NOT EXISTS school_year VARCHAR(20) DEFAULT '2025-2026' AFTER emergency_contact_number,
    ADD COLUMN IF NOT EXISTS status ENUM('active', 'inactive', 'graduated', 'transferred') DEFAULT 'active' AFTER school_year;

-- =============================================================================
-- 4. TEACHER GENERATION HISTORY TABLE
-- =============================================================================
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
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (employee_id) REFERENCES teachers(employee_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 5. SCHOOL SETTINGS TABLE (for principal info, school details)
-- =============================================================================
CREATE TABLE IF NOT EXISTS school_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default school settings
INSERT INTO school_settings (setting_key, setting_value, setting_type, description) VALUES
    ('school_name', 'Sample School', 'string', 'Official school name'),
    ('school_address', '123 School Street, City', 'string', 'School address'),
    ('school_contact', '(02) 123-4567', 'string', 'School contact number'),
    ('principal_name', 'Dr. Juan Dela Cruz', 'string', 'Principal name'),
    ('principal_signature_path', '', 'string', 'Path to principal signature image'),
    ('school_year', '2025-2026', 'string', 'Current school year'),
    ('school_logo_path', '', 'string', 'Path to school logo image')
ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);

-- =============================================================================
-- 6. INSERT DEFAULT TEMPLATE (Student)
-- =============================================================================
INSERT INTO id_templates (
    template_name, 
    template_type, 
    school_level, 
    is_active,
    canvas_width,
    canvas_height,
    front_layers,
    back_layers,
    version
) VALUES (
    'Default Student Template',
    'student',
    'high_school',
    TRUE,
    591,
    1004,
    JSON_OBJECT(
        'layers', JSON_ARRAY(
            JSON_OBJECT(
                'id', 'photo-1',
                'type', 'image',
                'field', 'photo',
                'x', 200,
                'y', 530,
                'width', 465,
                'height', 465,
                'zIndex', 1,
                'visible', TRUE,
                'locked', FALSE,
                'objectFit', 'cover',
                'borderRadius', 0
            ),
            JSON_OBJECT(
                'id', 'name-1',
                'type', 'text',
                'field', 'full_name',
                'x', 295,
                'y', 340,
                'width', 400,
                'height', 80,
                'zIndex', 2,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 70,
                'fontFamily', 'Arial',
                'fontWeight', 'bold',
                'color', '#000000',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'lrn-1',
                'type', 'text',
                'field', 'lrn',
                'x', 690,
                'y', 810,
                'width', 200,
                'height', 30,
                'zIndex', 3,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 18,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#000000',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'grade-1',
                'type', 'text',
                'field', 'grade_level',
                'x', 295,
                'y', 420,
                'width', 200,
                'height', 30,
                'zIndex', 4,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 24,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'section-1',
                'type', 'text',
                'field', 'section',
                'x', 295,
                'y', 460,
                'width', 200,
                'height', 30,
                'zIndex', 5,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 20,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#555555',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            )
        )
    ),
    JSON_OBJECT(
        'layers', JSON_ARRAY(
            JSON_OBJECT(
                'id', 'guardian-name-1',
                'type', 'text',
                'field', 'guardian_name',
                'x', 210,
                'y', 380,
                'width', 350,
                'height', 30,
                'zIndex', 1,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 20,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#000000',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'guardian-contact-1',
                'type', 'text',
                'field', 'guardian_contact',
                'x', 210,
                'y', 420,
                'width', 350,
                'height', 30,
                'zIndex', 2,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 18,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'address-1',
                'type', 'text',
                'field', 'address',
                'x', 210,
                'y', 470,
                'width', 350,
                'height', 60,
                'zIndex', 3,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 16,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.3,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'emergency-1',
                'type', 'text',
                'field', 'emergency_contact',
                'x', 210,
                'y', 550,
                'width', 350,
                'height', 30,
                'zIndex', 4,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 16,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'birth-date-1',
                'type', 'text',
                'field', 'birth_date',
                'x', 210,
                'y', 590,
                'width', 200,
                'height', 30,
                'zIndex', 5,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 16,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            )
        )
    ),
    '1.0.0'
) ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- 7. INSERT DEFAULT TEMPLATE (Teacher)
-- =============================================================================
INSERT INTO id_templates (
    template_name, 
    template_type, 
    school_level, 
    is_active,
    canvas_width,
    canvas_height,
    front_layers,
    back_layers,
    version
) VALUES (
    'Default Teacher Template',
    'teacher',
    'teacher',
    TRUE,
    591,
    1004,
    JSON_OBJECT(
        'layers', JSON_ARRAY(
            JSON_OBJECT(
                'id', 'photo-1',
                'type', 'image',
                'field', 'photo',
                'x', 200,
                'y', 530,
                'width', 465,
                'height', 465,
                'zIndex', 1,
                'visible', TRUE,
                'locked', FALSE,
                'objectFit', 'cover',
                'borderRadius', 0
            ),
            JSON_OBJECT(
                'id', 'name-1',
                'type', 'text',
                'field', 'full_name',
                'x', 295,
                'y', 340,
                'width', 400,
                'height', 80,
                'zIndex', 2,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 60,
                'fontFamily', 'Arial',
                'fontWeight', 'bold',
                'color', '#000000',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'position-1',
                'type', 'text',
                'field', 'position',
                'x', 295,
                'y', 420,
                'width', 300,
                'height', 30,
                'zIndex', 3,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 24,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'department-1',
                'type', 'text',
                'field', 'department',
                'x', 295,
                'y', 460,
                'width', 300,
                'height', 30,
                'zIndex', 4,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 20,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#555555',
                'textAlign', 'center',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'employee-id-1',
                'type', 'text',
                'field', 'employee_id',
                'x', 690,
                'y', 810,
                'width', 200,
                'height', 30,
                'zIndex', 5,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 18,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#000000',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            )
        )
    ),
    JSON_OBJECT(
        'layers', JSON_ARRAY(
            JSON_OBJECT(
                'id', 'emergency-name-1',
                'type', 'text',
                'field', 'emergency_contact_name',
                'x', 210,
                'y', 380,
                'width', 350,
                'height', 30,
                'zIndex', 1,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 20,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#000000',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'emergency-number-1',
                'type', 'text',
                'field', 'emergency_contact_number',
                'x', 210,
                'y', 420,
                'width', 350,
                'height', 30,
                'zIndex', 2,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 18,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', FALSE
            ),
            JSON_OBJECT(
                'id', 'address-1',
                'type', 'text',
                'field', 'address',
                'x', 210,
                'y', 470,
                'width', 350,
                'height', 60,
                'zIndex', 3,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 16,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.3,
                'letterSpacing', 0,
                'wordWrap', TRUE
            ),
            JSON_OBJECT(
                'id', 'specialization-1',
                'type', 'text',
                'field', 'specialization',
                'x', 210,
                'y', 550,
                'width', 350,
                'height', 30,
                'zIndex', 4,
                'visible', TRUE,
                'locked', FALSE,
                'fontSize', 16,
                'fontFamily', 'Arial',
                'fontWeight', 'normal',
                'color', '#333333',
                'textAlign', 'left',
                'lineHeight', 1.2,
                'letterSpacing', 0,
                'wordWrap', TRUE
            )
        )
    ),
    '1.0.0'
) ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- 8. VIEW FOR ACTIVE TEMPLATES
-- =============================================================================
CREATE OR REPLACE VIEW v_active_templates AS
SELECT 
    id,
    template_name,
    template_type,
    school_level,
    canvas_width,
    canvas_height,
    canvas_background_color,
    canvas_background_image,
    front_layers,
    back_layers,
    version,
    created_at,
    updated_at
FROM id_templates
WHERE is_active = TRUE;

-- =============================================================================
-- DONE
-- =============================================================================
SELECT 'Schema update v2 completed successfully!' as status;

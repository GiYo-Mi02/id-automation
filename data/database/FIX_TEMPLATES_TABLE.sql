-- Fix id_templates table structure
-- Drop and recreate if it has wrong structure

DROP TABLE IF EXISTS id_templates;

CREATE TABLE id_templates (
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

-- Show the new structure
DESCRIBE id_templates;

-- ============================================
-- Schema V3: Staff Support & Enhanced Templates
-- ============================================
-- Run: mysql -u root -p school_id_system < data/database/SCHEMA_V3.sql

-- 1. Create Staff Table
CREATE TABLE IF NOT EXISTS `staff` (
  `id` INT AUTO_INCREMENT,
  `id_number` VARCHAR(50) NOT NULL,
  `employee_id` VARCHAR(50) NOT NULL,
  `full_name` VARCHAR(200) NOT NULL,
  `department` VARCHAR(100),
  `position` VARCHAR(100),
  `contact_number` VARCHAR(50),
  `emergency_contact_name` VARCHAR(200),
  `emergency_contact_number` VARCHAR(50),
  `address` TEXT,
  `birth_date` DATE,
  `blood_type` VARCHAR(10),
  `photo_path` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_staff_id_number` (`id_number`),
  UNIQUE KEY `uk_staff_employee_id` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. Create Staff Generation History
CREATE TABLE IF NOT EXISTS `staff_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `staff_id` VARCHAR(50),
  `full_name` VARCHAR(200),
  `department` VARCHAR(100),
  `position` VARCHAR(100),
  `file_path` VARCHAR(255),
  `template_id` INT,
  `status` ENUM('success', 'failed') DEFAULT 'success',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_staff_history_staff_id` (`staff_id`),
  INDEX `idx_staff_history_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. Create Teacher Generation History (if not exists)
CREATE TABLE IF NOT EXISTS `teacher_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `teacher_id` VARCHAR(50),
  `full_name` VARCHAR(200),
  `department` VARCHAR(100),
  `position` VARCHAR(100),
  `file_path` VARCHAR(255),
  `template_id` INT,
  `status` ENUM('success', 'failed') DEFAULT 'success',
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_teacher_history_teacher_id` (`teacher_id`),
  INDEX `idx_teacher_history_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4. Update id_templates - add entity-specific activation flags
ALTER TABLE id_templates 
  ADD COLUMN IF NOT EXISTS is_active_for_students BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS is_active_for_teachers BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS is_active_for_staff BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS thumbnail LONGTEXT;

-- 5. Update template_type enum to include staff
ALTER TABLE id_templates 
MODIFY COLUMN template_type ENUM('student', 'teacher', 'staff', 'visitor') NOT NULL DEFAULT 'student';

-- 6. Add status column to generation_history if not exists
ALTER TABLE generation_history 
  ADD COLUMN IF NOT EXISTS status ENUM('success', 'failed') DEFAULT 'success';

-- 7. Create indexes for faster lookups
CREATE INDEX idx_templates_active_students ON id_templates(is_active_for_students);
CREATE INDEX idx_templates_active_teachers ON id_templates(is_active_for_teachers);
CREATE INDEX idx_templates_active_staff ON id_templates(is_active_for_staff);

-- 8. Verify structure
SELECT 'Schema V3 applied successfully!' as status;

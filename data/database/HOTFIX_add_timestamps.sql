-- ============================================================================
-- HOTFIX: Add missing timestamp columns to students table
-- ============================================================================
-- Issue: Refactored code expects created_at and updated_at columns
-- These columns don't exist in the legacy database schema
-- ============================================================================

USE school_id_system;

-- Add created_at and updated_at columns
ALTER TABLE students
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER guardian_contact,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- Verify the schema
DESCRIBE students;

-- ============================================================================
-- Expected Result:
-- ============================================================================
-- students table should now have:
--   - id_number (VARCHAR(50), PRIMARY KEY)
--   - full_name (VARCHAR(100))
--   - lrn (VARCHAR(50))
--   - grade_level (VARCHAR(20))
--   - section (VARCHAR(50))
--   - guardian_name (VARCHAR(100))
--   - address (VARCHAR(255))
--   - guardian_contact (VARCHAR(50))
--   - photo_path (VARCHAR(255))
--   - created_at (TIMESTAMP)        <- NEW
--   - updated_at (TIMESTAMP)        <- NEW
-- ============================================================================

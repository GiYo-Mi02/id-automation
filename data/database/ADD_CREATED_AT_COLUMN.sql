-- Add created_at column to students table for proper chronological ordering
-- Run this if upgrading from an older version

-- Check if column exists and add if missing
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'school_id_system'
    AND TABLE_NAME = 'students'
    AND COLUMN_NAME = 'created_at'
);

-- Add column if it doesn't exist
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE students ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP',
    'SELECT "Column created_at already exists" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- For existing records without timestamps, set them to current time
UPDATE students 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_students_created_at ON students(created_at DESC);

SELECT 'Migration completed successfully!' AS status;

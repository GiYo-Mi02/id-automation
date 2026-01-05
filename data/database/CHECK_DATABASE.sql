-- Check database schema and data
USE school_id_system;

-- Show table structure
DESCRIBE students;

-- Count total students
SELECT COUNT(*) as total_students FROM students;

-- Show first 5 students (if any)
SELECT * FROM students LIMIT 5;

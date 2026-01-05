import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import DatabaseManager

# Test database connection and check for data
db = DatabaseManager()

print("\n=== DATABASE DIAGNOSTICS ===\n")

# Test connection
health = db.health_check()
print(f"Database Health: {health}")

# Check if students table exists and has data
with db.get_connection() as conn:
    cursor = conn.cursor(dictionary=True)
    
    # Get table structure
    print("\n--- Students Table Structure ---")
    cursor.execute("DESCRIBE students")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col['Field']}: {col['Type']}")
    
    # Count students
    print("\n--- Student Count ---")
    cursor.execute("SELECT COUNT(*) as count FROM students")
    result = cursor.fetchone()
    print(f"  Total students: {result['count']}")
    
    # Show first 3 students
    if result['count'] > 0:
        print("\n--- Sample Students ---")
        cursor.execute("SELECT * FROM students LIMIT 3")
        students = cursor.fetchall()
        for student in students:
            print(f"  {student}")
    else:
        print("\n  ⚠️ NO STUDENTS FOUND IN DATABASE")
        print("  You need to import student data or add students manually.")
    
    cursor.close()

print("\n=== END DIAGNOSTICS ===\n")

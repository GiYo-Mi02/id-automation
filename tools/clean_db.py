import os
import sys
import csv
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import db_manager, init_database

def clean_and_seed():
    print("WARNING: This will drop students, teachers, staff, and history tables and seed them with mock data!")
    print("It will NOT touch or reset id_templates.")
    
    confirm = input("Type 'CLEAN' to confirm: ")
    if confirm != "CLEAN":
        print("Cancelled.")
        return

    # Tables to drop
    tables_to_drop = [
        "generation_history",
        "teacher_generation_history",
        "teacher_history",
        "staff_history",
        "students",
        "teachers",
        "staff"
    ]
    
    with db_manager.transaction() as conn:
        cursor = conn.cursor()
        
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for table in tables_to_drop:
            print(f"Dropping table {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    print("Reinitializing database tables...")
    init_database()
    
    print("Database schema reinitialized successfully.")
    
    # Seeding Students
    students_csv_path = Path("sample_students.csv")
    if students_csv_path.exists():
        print("Seeding students...")
        with open(students_csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                for row in reader:
                    cursor.execute("""
                        INSERT INTO students (
                            id_number, full_name, lrn, grade_level, section, 
                            guardian_name, address, guardian_contact, school, entry_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['id_number'].strip(),
                        row['full_name'].strip(),
                        row.get('lrn', '').strip(),
                        row.get('grade_level', '').strip(),
                        row.get('section', '').strip(),
                        row.get('guardian_name', '').strip(),
                        row.get('address', '').strip(),
                        row.get('guardian_contact', '').strip(),
                        row.get('school', '').strip(),
                        'import'
                    ))
        print("Students seeded.")
        
    # Seeding Teachers
    teachers_csv_path = Path("sample_teachers.csv")
    if teachers_csv_path.exists():
        print("Seeding teachers...")
        with open(teachers_csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                for row in reader:
                    cursor.execute("""
                        INSERT INTO teachers (
                            employee_id, full_name, department, position, specialization, 
                            contact_number, emergency_contact_name, emergency_contact_number, 
                            address, birth_date, blood_type, school, entry_type, employment_status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['employee_id'].strip(),
                        row['full_name'].strip(),
                        row.get('department', '').strip(),
                        row.get('position', '').strip(),
                        row.get('specialization', '').strip(),
                        row.get('contact_number', '').strip(),
                        row.get('emergency_contact_name', '').strip(),
                        row.get('emergency_contact_number', '').strip(),
                        row.get('address', '').strip(),
                        row.get('birth_date', '').strip() or None,
                        row.get('blood_type', '').strip() or None,
                        row.get('school', '').strip(),
                        'import',
                        'active'
                    ))
        print("Teachers seeded.")
        
    # Seeding Staff
    staff_csv_path = Path("sample_staff.csv")
    if staff_csv_path.exists():
        print("Seeding staff...")
        with open(staff_csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            with db_manager.transaction() as conn:
                cursor = conn.cursor()
                for row in reader:
                    cursor.execute("""
                        INSERT INTO staff (
                            id_number, employee_id, full_name, department, position, 
                            contact_number, emergency_contact_name, emergency_contact_number, 
                            address, birth_date, blood_type, school, entry_type
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['id_number'].strip(),
                        row['employee_id'].strip(),
                        row['full_name'].strip(),
                        row.get('department', '').strip(),
                        row.get('position', '').strip(),
                        row.get('contact_number', '').strip(),
                        row.get('emergency_contact_name', '').strip(),
                        row.get('emergency_contact_number', '').strip(),
                        row.get('address', '').strip(),
                        row.get('birth_date', '').strip() or None,
                        row.get('blood_type', '').strip() or None,
                        row.get('school', '').strip(),
                        'import'
                    ))
        print("Staff seeded.")
        
    print("\nDatabase reset and seeding successfully completed!")

if __name__ == "__main__":
    clean_and_seed()

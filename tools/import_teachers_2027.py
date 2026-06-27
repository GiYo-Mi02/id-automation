import csv
import os
import app.database as database

CSV_PATH = r"sample_teachers_2027.csv"

def import_teachers():
    print(f"[INFO] Reading from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Error: {CSV_PATH} not found!")
        return

    conn = database.get_db_connection()
    if not conn:
        print("[ERROR] Could not establish database connection!")
        return
    cursor = conn.cursor()
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            
            print("[INFO] Syncing teachers to database...")
            for row in reader:
                sql = """
                    INSERT INTO teachers 
                    (
                        employee_id, full_name, department, position, specialization, 
                        contact_number, emergency_contact_name, emergency_contact_number, 
                        address, birth_date, blood_type, school
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE 
                    full_name = VALUES(full_name), 
                    department = VALUES(department),
                    position = VALUES(position), 
                    specialization = VALUES(specialization),
                    contact_number = VALUES(contact_number),
                    emergency_contact_name = VALUES(emergency_contact_name),
                    emergency_contact_number = VALUES(emergency_contact_number),
                    address = VALUES(address),
                    birth_date = VALUES(birth_date),
                    blood_type = VALUES(blood_type),
                    school = VALUES(school)
                """
                val = (
                    row['employee_id'],
                    row['full_name'],
                    row['department'],
                    row['position'],
                    row['specialization'],
                    row['contact_number'],
                    row['emergency_contact_name'],
                    row['emergency_contact_number'],
                    row['address'],
                    row.get('birth_date') or None,
                    row.get('blood_type') or None,
                    row['school']
                )
                cursor.execute(sql, val)
                count += 1

        conn.commit()
        print(f"[SUCCESS] Successfully imported {count} teachers to database.")

    except Exception as e:
        print(f"[ERROR] Error during teacher import: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_teachers()

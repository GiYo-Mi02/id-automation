import csv
import app.database as database
import os

CSV_PATH = r"C:\School_IDs\students.csv"

def sync_csv_to_db():
    print(f"📂 Reading from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        print("❌ Error: students.csv file not found!")
        return

    conn = database.get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            
            print("🔄 Syncing data...")
            for row in reader:
                sql = """
                    INSERT INTO students 
                    (id_number, full_name, lrn, section, guardian_name, address, guardian_contact) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s) 
                    ON DUPLICATE KEY UPDATE 
                    full_name = VALUES(full_name), 
                    lrn = VALUES(lrn), 
                    section = VALUES(section),
                    guardian_name = VALUES(guardian_name),
                    address = VALUES(address),
                    guardian_contact = VALUES(guardian_contact)
                """
                val = (
                    row['ID_Number'], row['Full_Name'], row['LRN'], row['Section'],
                    row['Guardian_Name'], row['Address'], row['Guardian_Contact']
                )
                cursor.execute(sql, val)
                count += 1

        conn.commit()
        print(f"✅ SUCCESS: Processed {count} students.")

    except Exception as e:
        print(f"❌ Error during import: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sync_csv_to_db()
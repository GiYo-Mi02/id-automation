import mysql.connector
import csv
import os
from pathlib import Path

# ==================== CONFIGURATION ====================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',         # Default XAMPP password is empty
    'database': 'school_id_system'
}

CSV_PATH = r"C:\School_IDs\students.csv"
# =======================================================

def get_db_connection():
    """Opens a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ DATABASE ERROR: {e}")
        return None

def init_db():
    """Initializes tables and imports CSV if empty."""
    conn = get_db_connection()
    if not conn: return

    cursor = conn.cursor()

    # 1. Create Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id_number VARCHAR(20) PRIMARY KEY,
            full_name VARCHAR(100),
            role VARCHAR(50),
            email VARCHAR(100),
            phone VARCHAR(20)
        )
    ''')
    
    # 2. Create Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20),
            action VARCHAR(50),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id_number)
        )
    ''')

    # 3. Check if empty -> Import CSV
    cursor.execute('SELECT count(*) FROM students')
    count = cursor.fetchone()[0]
    
    if count == 0 and os.path.exists(CSV_PATH):
        print("📥 MySQL: Importing students from CSV...")
        try:
            with open(CSV_PATH, 'r') as f:
                reader = csv.DictReader(f)
                data = []
                for row in reader:
                    data.append((
                        row['ID_Number'], 
                        row['Full_Name'], 
                        row['Role'], 
                        row['Email'], 
                        row['Phone']
                    ))
            
            sql = "INSERT IGNORE INTO students (id_number, full_name, role, email, phone) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(sql, data)
            conn.commit()
            print(f"✅ Imported {len(data)} students into MySQL.")
        except Exception as e:
            print(f"⚠️ CSV Import Failed: {e}")

    conn.close()

def get_student(student_id):
    """Safely fetch a student (Returns Dictionary)."""
    conn = get_db_connection()
    if not conn: return None
    
    # dictionary=True makes it behave like the previous SQLite version
    cursor = conn.cursor(dictionary=True) 
    cursor.execute('SELECT * FROM students WHERE id_number = %s', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_all_students():
    """Fetch all students for the dropdown."""
    conn = get_db_connection()
    if not conn: return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id_number, full_name FROM students')
    students = cursor.fetchall()
    conn.close()
    return students

def log_generation(student_id, file_path):
    """Record that we made an ID card."""
    conn = get_db_connection()
    if not conn: return

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO logs (student_id, action, file_path) VALUES (%s, %s, %s)', 
        (student_id, "GENERATED", str(file_path))
    )
    conn.commit()
    conn.close()

def get_recent_history(limit=10):
    """Get the last generated IDs."""
    conn = get_db_connection()
    if not conn: return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT logs.student_id, logs.timestamp, students.full_name, logs.file_path
        FROM logs 
        LEFT JOIN students ON logs.student_id = students.id_number
        ORDER BY logs.timestamp DESC LIMIT %s
    ''', (limit,))
    logs = cursor.fetchall()
    conn.close()
    return logs

# Initialize on import
if __name__ != "__main__":
    init_db()
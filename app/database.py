import mysql.connector
from datetime import datetime
import json
from pathlib import Path

# Database Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'school_id_system'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # If DB doesn't exist, try to create it
        if err.errno == 1049:
            create_database()
            return mysql.connector.connect(**DB_CONFIG)
        else:
            print(f"❌ DB Connection Error: {err}")
            return None

def create_database():
    try:
        temp_config = DB_CONFIG.copy()
        del temp_config['database']
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.close()
        print("✨ Database created successfully")
    except Exception as e:
        print(f"❌ Failed to create DB: {e}")

def init_db():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    # Create Students Table (New Structure)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id_number VARCHAR(50) PRIMARY KEY,
        full_name VARCHAR(100),
        lrn VARCHAR(50),
        section VARCHAR(50),
        guardian_name VARCHAR(100),
        address VARCHAR(255),
        guardian_contact VARCHAR(50)
    )
    """)
    
    # Create History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generation_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50),
        file_path VARCHAR(255),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def get_student(student_id):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_all_students():
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def log_generation(student_id, file_path):
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO generation_history (student_id, file_path) VALUES (%s, %s)", (student_id, str(file_path)))
    conn.commit()
    conn.close()

def get_recent_history(limit=50):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    # Join with students table to get latest names
    sql = """
    SELECT h.timestamp, h.student_id, s.full_name, s.section, s.lrn, 
           s.guardian_name, s.address, s.guardian_contact 
    FROM generation_history h
    LEFT JOIN students s ON h.student_id = s.id_number
    ORDER BY h.timestamp DESC LIMIT %s
    """
    cursor.execute(sql, (limit,))
    history = cursor.fetchall()
    conn.close()
    return history
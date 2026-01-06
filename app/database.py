import mysql.connector
from datetime import datetime
import json
import os
from pathlib import Path

# Database Config (with environment variable support)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'school_id_system')
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
    
    # Create Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id_number VARCHAR(50) PRIMARY KEY,
        full_name VARCHAR(100),
        lrn VARCHAR(50),
        grade_level VARCHAR(20),
        section VARCHAR(50),
        guardian_name VARCHAR(100),
        address VARCHAR(255),
        guardian_contact VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

def get_teacher(employee_id):
    """Query teachers table by employee_id."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE employee_id = %s", (employee_id,))
    teacher = cursor.fetchone()
    conn.close()
    return teacher

def get_all_students(order_by='created_at', order_dir='DESC', limit=None):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    
    # Build query with ordering
    query = "SELECT * FROM students"
    
    # Validate order_by column to prevent SQL injection
    valid_columns = ['id_number', 'full_name', 'created_at', 'grade_level', 'section']
    if order_by in valid_columns:
        order_direction = 'DESC' if order_dir.upper() == 'DESC' else 'ASC'
        query += f" ORDER BY {order_by} {order_direction}"
    
    if limit:
        query += f" LIMIT {int(limit)}"
    
    cursor.execute(query)
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
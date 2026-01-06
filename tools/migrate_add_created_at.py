"""
Database Migration: Add created_at column to students table
============================================================
Run this script to add timestamp tracking for proper chronological ordering.
"""

import mysql.connector
import os
from datetime import datetime

# Database Config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'school_id_system')
}

def migrate():
    """Add created_at column to students table if it doesn't exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 Checking students table structure...")
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'students' 
            AND COLUMN_NAME = 'created_at'
        """, (DB_CONFIG['database'],))
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✅ Column 'created_at' already exists in students table")
        else:
            print("➕ Adding 'created_at' column to students table...")
            cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("✅ Column added successfully")
            
            # Set timestamps for existing records
            print("🔄 Updating existing records...")
            cursor.execute("""
                UPDATE students 
                SET created_at = CURRENT_TIMESTAMP 
                WHERE created_at IS NULL
            """)
            conn.commit()
            print(f"✅ Updated {cursor.rowcount} existing records")
        
        # Add index for better performance
        print("📊 Adding index for performance...")
        try:
            cursor.execute("""
                CREATE INDEX idx_students_created_at 
                ON students(created_at DESC)
            """)
            conn.commit()
            print("✅ Index created successfully")
        except mysql.connector.Error as e:
            if e.errno == 1061:  # Duplicate key name
                print("ℹ️  Index already exists")
            else:
                raise
        
        cursor.close()
        conn.close()
        
        print("\n✨ Migration completed successfully!")
        print("📝 Students will now be ordered by creation date (newest first)")
        
    except mysql.connector.Error as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Add created_at column")
    print("=" * 60)
    migrate()

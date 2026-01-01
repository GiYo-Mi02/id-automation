import app.database as database

def reset_database():
    print("WARNING: This will DELETE all data and add the 'GRADE_LEVEL' column!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        return

    conn = database.get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS students")
        
        print("Creating new table with Grade Level & Section...")
        # NEW STRUCTURE: Separated Grade and Section
        sql = """
        CREATE TABLE students (
            id_number VARCHAR(50) PRIMARY KEY,
            full_name VARCHAR(100),
            lrn VARCHAR(50),
            grade_level VARCHAR(20),  
            section VARCHAR(50),
            guardian_name VARCHAR(100),
            address VARCHAR(255),
            guardian_contact VARCHAR(50)
        )
        """
        cursor.execute(sql)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("SUCCESS! Database updated.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database()
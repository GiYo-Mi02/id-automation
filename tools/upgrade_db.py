import app.database as database

def upgrade():
    print("Connecting to Database...")
    conn = database.get_db_connection()
    if not conn: return

    cursor = conn.cursor()
    
    commands = [
        "ALTER TABLE students ADD COLUMN lrn VARCHAR(50)",
        "ALTER TABLE students ADD COLUMN section VARCHAR(50)",
        "ALTER TABLE students ADD COLUMN guardian_name VARCHAR(100)",
        "ALTER TABLE students ADD COLUMN address VARCHAR(255)",
        "ALTER TABLE students ADD COLUMN guardian_contact VARCHAR(50)",
        # We can drop old columns if you want, but better to keep them just in case
        # "ALTER TABLE students DROP COLUMN role", 
        # "ALTER TABLE students DROP COLUMN email"
    ]
    
    print("Upgrading tables...")
    for sql in commands:
        try:
            cursor.execute(sql)
            print(f"   Executed: {sql}")
        except Exception as e:
            # Ignore error if column already exists
            print(f"   Skipped (might already exist): {sql}")

    conn.commit()
    conn.close()
    print("\nDatabase Upgrade Complete!")

if __name__ == "__main__":
    upgrade()
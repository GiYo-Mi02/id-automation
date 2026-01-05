"""Test generation_history table"""
import mysql.connector
from app.core.config import get_settings

settings = get_settings()

# Connect to database
conn = mysql.connector.connect(
    host=settings.database.host,
    user=settings.database.user,
    password=settings.database.password,
    database=settings.database.database
)

cursor = conn.cursor(dictionary=True)

print("\n=== GENERATION_HISTORY TABLE ===")
cursor.execute("SELECT COUNT(*) as count FROM generation_history")
count = cursor.fetchone()['count']
print(f"Total records: {count}")

if count > 0:
    cursor.execute("SELECT * FROM generation_history ORDER BY timestamp DESC LIMIT 5")
    records = cursor.fetchall()
    print("\nSample records:")
    for record in records:
        print(f"  - {record}")
else:
    print("⚠️ No records in generation_history table")
    print("\nThis table stores ID generation history.")
    print("It's filled when you generate IDs in the system.")
    print("\nFor the Dashboard to show data, you need to either:")
    print("1. Change Dashboard to fetch from /api/students instead")
    print("2. Or populate generation_history when students are added")

conn.close()

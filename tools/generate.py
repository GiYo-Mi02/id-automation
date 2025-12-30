import csv
import os

# Configuration
folder_path = r"C:\School_IDs"
file_path = os.path.join(folder_path, "students.csv")

# Ensure the directory exists
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Data Configuration
base_name = "Gio Joshua Gonzales"
role = "Student"
phone = "0917-123-4567"

print(f"Generating database for: {base_name}...")

# Create the CSV file
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write Header
    writer.writerow(["ID_Number", "Full_Name", "Role", "Email", "Phone"])
    
    # Generate 50 rows
    for i in range(51, 101):
        # Format ID as 2024-001, 2024-002, etc.
        student_id = f"2024-{i:03d}"
        
        # Auto-generate email
        email = f"gio.gonzales.{i:03d}@wardiere.edu"
        
        # Write the row
        writer.writerow([student_id, base_name, role, email, phone])

print(f"✅ Successfully created 'students.csv' with 50 entries at: {file_path}")
print("You can now drop photos named '2024-001.jpg', '2024-002.jpg', etc.")
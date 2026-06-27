import csv

def generate_csv():
    teachers = []
    
    # Generate 50 entries with identical teacher details except for employee_id (prefixed with TCH-)
    for i in range(201, 251):
        employee_id = f"TCH-2027-{i}"
        teachers.append({
            "employee_id": employee_id,
            "full_name": "GONZALES GIO JOSHUA C.",
            "department": "ICT DEPARTMENT",
            "position": "TEACHER I",
            "specialization": "INFORMATION TECHNOLOGY",
            "contact_number": "09950558771",
            "emergency_contact_name": "GAMALIEL P. GONZALES",
            "emergency_contact_number": "09950558771",
            "address": "BLK 84 LOT 4 SPRING BEAUTY ST. BRGY RIZAL, TAGUIG CITY",
            "birth_date": "1995-01-01",
            "blood_type": "O+",
            "school": "TAGUIG SCIENCE HIGH SCHOOL"
        })

    # Write to CSV
    output_path = "sample_teachers_2027.csv"
    headers = [
        "employee_id", "full_name", "department", "position", "specialization", 
        "contact_number", "emergency_contact_name", "emergency_contact_number", 
        "address", "birth_date", "blood_type", "school"
    ]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(teachers)
        
    print(f"Successfully generated {len(teachers)} teacher records with TCH- prefix in '{output_path}'.")

if __name__ == "__main__":
    generate_csv()

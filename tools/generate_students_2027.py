import csv

def generate_csv():
    students = []
    
    # Generate 50 entries with identical details except for the incrementing ID
    for i in range(201, 251):
        id_number = f"2027-{i}"
        students.append({
            "id_number": id_number,
            "full_name": "GONZALES GIO JOSHUA C.",
            "lrn": "123456789201",
            "grade_level": "GRADE 10",
            "section": "STEPHENSON",
            "guardian_name": "GAMALIEL P. GONZALES",
            "address": "BLK 84 LOT 4 SPRING BEAUTY ST. BRGY RIZAL, TAGUIG CITY",
            "guardian_contact": "09950558771",
            "school": "TAGUIG SCIENCE HIGH SCHOOL"
        })

    # Write to CSV
    output_path = "sample_students_2027.csv"
    headers = ["id_number", "full_name", "lrn", "grade_level", "section", "guardian_name", "address", "guardian_contact", "school"]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(students)
        
    print(f"Successfully generated {len(students)} student records with identical details (except ID) in '{output_path}'.")

if __name__ == "__main__":
    generate_csv()

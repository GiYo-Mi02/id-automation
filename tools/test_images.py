"""Test if image URLs are being added to student responses"""
import requests

# Test the API
response = requests.get('http://localhost:8000/api/students?page=1&page_size=10', 
                       headers={'X-API-Key': 'hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU'})

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Got {len(data['students'])} students")
    print(f"Total students: {data['total']}\n")
    
    students_with_images = 0
    for student in data['students'][:5]:
        print(f"ID: {student['id_number']}")
        print(f"  Name: {student['full_name']}")
        if student.get('front_image'):
            print(f"  ✅ Front: {student['front_image']}")
            students_with_images += 1
        else:
            print(f"  ❌ No front image")
        if student.get('back_image'):
            print(f"  ✅ Back: {student['back_image']}")
        print()
    
    print(f"\n📊 Students with images: {students_with_images} / {len(data['students'][:5])}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

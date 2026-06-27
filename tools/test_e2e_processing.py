import os
import sys
import shutil
from pathlib import Path
from PIL import Image

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.school_id_processor import SchoolIDProcessor, CONFIG
from app.db.database import db_manager

def create_dummy_image(path):
    # Create a simple 200x200 solid color dummy image
    img = Image.new('RGB', (200, 200), color=(73, 109, 137))
    img.save(path)
    print(f"Created dummy image: {path}")

def run_e2e_test():
    print("🧪 Starting E2E ID Processor File Naming & Path Test...")
    print("=" * 60)
    
    # Check/Activate a teacher template if none is active
    active_teacher_tpl = db_manager.execute_query("SELECT id FROM id_templates WHERE template_type = 'teacher' AND is_active = 1", fetch_one=True)
    deactivate_later = False
    temp_active_id = None
    
    if not active_teacher_tpl:
        # Find any teacher template to temporarily activate
        any_teacher_tpl = db_manager.execute_query("SELECT id FROM id_templates WHERE template_type = 'teacher' LIMIT 1", fetch_one=True)
        if any_teacher_tpl:
            temp_active_id = any_teacher_tpl['id']
            print(f"Activating teacher template ID {temp_active_id} temporarily for the test...")
            db_manager.execute_query("UPDATE id_templates SET is_active = 1 WHERE id = %s", (temp_active_id,), fetch_all=False)
            deactivate_later = True
        else:
            print("Warning: No teacher template found in database to activate.")
    
    # Initialize processor
    processor = SchoolIDProcessor(CONFIG)
    
    input_dir = Path(CONFIG['INPUT_FOLDER'])
    output_dir = Path(CONFIG['OUTPUT_FOLDER'])
    
    # 1. TEST STUDENT WITH LRN (using seeded student 2026-0001 / LRN 123456789012)
    student_id = "2026-0001"
    student_lrn = "123456789012"
    student_photo = input_dir / f"{student_id}.jpg"
    
    create_dummy_image(student_photo)
    
    # Run processing
    print(f"Processing photo for student {student_id}...")
    success = processor.process_photo(str(student_photo))
    
    # Verify outputs
    expected_front_student = output_dir / "front-id" / f"{student_lrn}.png"
    expected_back_student = output_dir / "back0id" / f"{student_lrn}.png"
    
    print("\nVerifying student output paths...")
    print(f"Expected Front: {expected_front_student}")
    print(f"Expected Back:  {expected_back_student}")
    
    student_passed = False
    if expected_front_student.exists() and expected_back_student.exists():
        print("✅ Student ID cards successfully created and named after LRN!")
        student_passed = True
    else:
        print("❌ Student ID cards not found at expected paths!")
        
    # Clean up student dummy input & output
    if student_photo.exists():
        student_photo.unlink()
    if expected_front_student.exists():
        expected_front_student.unlink()
    if expected_back_student.exists():
        expected_back_student.unlink()
        
    # 2. TEST TEACHER (using seeded teacher TCH-2026-001)
    teacher_id = "TCH-2026-001"
    teacher_photo = input_dir / f"{teacher_id}.jpg"
    
    create_dummy_image(teacher_photo)
    
    # Run processing
    print(f"Processing photo for teacher {teacher_id}...")
    success = processor.process_photo(str(teacher_photo))
    
    # Verify outputs
    expected_front_teacher = output_dir / "front-id" / f"{teacher_id}.png"
    expected_back_teacher = output_dir / "back0id" / f"{teacher_id}.png"
    
    print("\nVerifying teacher output paths...")
    print(f"Expected Front: {expected_front_teacher}")
    print(f"Expected Back:  {expected_back_teacher}")
    
    teacher_passed = False
    if expected_front_teacher.exists() and expected_back_teacher.exists():
        print("✅ Teacher ID cards successfully created and named after Employee ID!")
        teacher_passed = True
    else:
        print("❌ Teacher ID cards not found at expected paths!")
        
    # Clean up teacher dummy input & output
    if teacher_photo.exists():
        teacher_photo.unlink()
    if expected_front_teacher.exists():
        expected_front_teacher.unlink()
    if expected_back_teacher.exists():
        expected_back_teacher.unlink()
        
    # Deactivate the temporary template if needed
    if deactivate_later and temp_active_id:
        print(f"Restoring teacher template ID {temp_active_id} to inactive...")
        db_manager.execute_query("UPDATE id_templates SET is_active = 0 WHERE id = %s", (temp_active_id,), fetch_all=False)
        
    print("=" * 60)
    if student_passed and teacher_passed:
        print("🎉 ALL E2E PROCESSING PATH AND NAMING TESTS PASSED!")
        return True
    else:
        print("❌ SOME E2E TESTS FAILED.")
        return False

if __name__ == "__main__":
    success = run_e2e_test()
    if not success:
        sys.exit(1)

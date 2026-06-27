import os
import sys
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from PIL import Image

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.database import get_db_connection

API_KEY = "hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU"
BASE_URL = "http://localhost:8000"

def create_dummy_front_id(settings, filename):
    output_dir = Path(settings.paths.output_dir)
    front_dir = output_dir / "front-id"
    front_dir.mkdir(parents=True, exist_ok=True)
    img_path = front_dir / f"{filename}.png"
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    img.save(img_path)
    return img_path

def run_request(url, headers=None, method="GET"):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read(), response.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers

def test_endpoints():
    print("[TEST] Running Live System Endpoints Validation Tests...")
    print("=" * 60)
    
    settings = get_settings()
    headers = {"X-API-Key": API_KEY}
    
    # 1. Test history cap limits validation
    print("1. Testing history limit validation...")
    
    # Test limit=200
    code, body, _ = run_request(f"{BASE_URL}/api/history?limit=200", headers)
    print(f"limit=200 status: {code}")
    assert code == 200, f"Expected 200, got {code}"
    
    # Test limit=10000
    code, body, _ = run_request(f"{BASE_URL}/api/history?limit=10000", headers)
    print(f"limit=10000 status: {code}")
    assert code == 200, f"Expected 200, got {code}"
    
    # Test limit=10001 (should fail validation)
    code, body, _ = run_request(f"{BASE_URL}/api/history?limit=10001", headers)
    print(f"limit=10001 status: {code} (expected 422)")
    assert code == 422, f"Expected 422, got {code}"
    
    # 2. Test export-pdf security
    print("\n2. Testing export-pdf endpoint authorization...")
    
    # Unauthorized
    code, _, _ = run_request(f"{BASE_URL}/api/system/export-pdf")
    print(f"No key status: {code} (expected 401)")
    assert code == 401, f"Expected 401, got {code}"
    
    # Forbidden
    code, _, _ = run_request(f"{BASE_URL}/api/system/export-pdf", {"X-API-Key": "wrong_key"})
    print(f"Wrong key status: {code} (expected 403)")
    assert code == 403, f"Expected 403, got {code}"
    # Test missing school param (should return 200 or 404 because it is now optional and falls back to all schools)
    code, _, _ = run_request(f"{BASE_URL}/api/system/export-pdf", headers)
    print(f"Missing school status: {code} (expected 200 or 404)")
    assert code in (200, 404), f"Expected 200 or 404, got {code}"

    # Test empty school param (should return 200 or 404 because it falls back to all schools)
    code, _, _ = run_request(f"{BASE_URL}/api/system/export-pdf?school=", headers)
    print(f"Empty school status: {code} (expected 200 or 404)")
    assert code in (200, 404), f"Expected 200 or 404, got {code}"

    # Test 'All Schools' param (should return 200 or 404 instead of 400)
    code, _, _ = run_request(f"{BASE_URL}/api/system/export-pdf?school=All+Schools", headers)
    print(f"All Schools school status: {code} (expected 200 or 404)")
    assert code in (200, 404), f"Expected 200 or 404, got {code}"
    
    # 3. Test export-pdf with students and missing images
    print("\n3. Testing export-pdf with matching students but missing front-id images...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_number, lrn, school FROM students LIMIT 1")
    student = cursor.fetchone()
    
    if not student:
        # Insert a dummy student for the test
        cursor.execute(
            """
            INSERT INTO students (id_number, full_name, lrn, school)
            VALUES ('TEST-ST-001', 'Test Student', '999999999999', 'Test Science High School')
            """
        )
        conn.commit()
        cursor.execute("SELECT id_number, lrn, school FROM students WHERE id_number = 'TEST-ST-001'")
        student = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    school_param = student['school']
    encoded_school = urllib.parse.quote(school_param)
    
    # Now call export-pdf for a school that does not exist in DB (should fail 404)
    code, body, _ = run_request(f"{BASE_URL}/api/system/export-pdf?school=NonExistentSchool", headers)
    print(f"Export PDF with non-existent school status: {code} (expected 404)")
    assert code == 404, f"Expected 404, got {code}"
    
    # 4. Create dummy front-id image and test successful compilation
    print("\n4. Testing export-pdf with generated front-id image...")
    filename_base = student['lrn'] if student.get('lrn') else student['id_number']
    dummy_img_path = create_dummy_front_id(settings, filename_base)
    
    try:
        # Test export PDF
        code, body, resp_headers = run_request(f"{BASE_URL}/api/system/export-pdf?school={encoded_school}", headers)
        print(f"Export PDF status: {code} (expected 200)")
        content_type = resp_headers.get('content-type')
        print(f"Response Content-Type: {content_type}")
        assert code == 200, f"Expected 200, got {code}"
        assert content_type == 'application/pdf', "Expected application/pdf content type"
        print(f"PDF download size: {len(body)} bytes")
        
        # Test export ZIP
        code_zip, body_zip, resp_headers_zip = run_request(f"{BASE_URL}/api/system/export-zip?school={encoded_school}", headers)
        print(f"Export ZIP status: {code_zip} (expected 200)")
        content_type_zip = resp_headers_zip.get('content-type')
        print(f"Response Content-Type: {content_type_zip}")
        assert code_zip == 200, f"Expected 200, got {code_zip}"
        assert content_type_zip == 'application/zip', "Expected application/zip content type"
        print(f"ZIP download size: {len(body_zip)} bytes")
        
        # Verify the file was served and background task cleaned it up
        time.sleep(0.5)
        temp_files = list((Path(settings.paths.data_dir) / "temp").glob("*.*"))
        print(f"Temp files remaining after download: {len(temp_files)}")
        assert len(temp_files) == 0, "Temporary export files were not cleaned up!"
        print("Background cleanup verified successfully!")
        
    finally:
        # Clean up dummy image
        if dummy_img_path.exists():
            dummy_img_path.unlink()
            
        # Clean up dummy student
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id_number = 'TEST-ST-001'")
        conn.commit()
        cursor.close()
        conn.close()

    print("=" * 60)
    print("ALL ENDPOINT AND CAP CAP LIMIT TESTS PASSED!")

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print(f"Test failed with exception: {e}")
        sys.exit(1)

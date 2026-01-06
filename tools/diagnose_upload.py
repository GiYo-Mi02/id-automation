"""
Image Upload Diagnostic
========================
Check if the server has the correct routes and mounts loaded.
"""

import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🔍 IMAGE UPLOAD DIAGNOSTICS")
print("=" * 70)
print()

# 1. Check if uploads directory exists
uploads_dir = Path("data/uploads")
print(f"1️⃣  Directory Check: data/uploads")
if uploads_dir.exists():
    files = list(uploads_dir.glob("*"))
    print(f"   ✅ Directory exists")
    print(f"   📁 Files: {len(files)}")
    for f in files[:5]:
        print(f"      • {f.name}")
else:
    print(f"   ❌ Directory does NOT exist")
    print(f"   Creating it now...")
    uploads_dir.mkdir(parents=True, exist_ok=True)

print()

# 2. Check if upload endpoint exists
print(f"2️⃣  Upload Endpoint: POST /api/upload/image")
try:
    response = requests.post(f"{BASE_URL}/api/upload/image", timeout=2)
    if response.status_code == 422:
        print(f"   ✅ Endpoint EXISTS (422 = missing file parameter)")
    elif response.status_code == 404:
        print(f"   ❌ Endpoint NOT FOUND (404)")
        print(f"   ⚠️  Server needs restart!")
    else:
        print(f"   ⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot reach server: {e}")

print()

# 3. Check if static mounts are working
print(f"3️⃣  Static Mounts:")

# Check if any file exists to test with
test_files = list(uploads_dir.glob("*.png")) + list(uploads_dir.glob("*.jpg"))
if test_files:
    test_file = test_files[0].name
    
    # Test /uploads path
    print(f"   Testing: /uploads/{test_file}")
    try:
        response = requests.get(f"{BASE_URL}/uploads/{test_file}", timeout=2)
        if response.status_code == 200:
            print(f"   ✅ /uploads mount WORKS")
        else:
            print(f"   ❌ /uploads mount FAILED ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test /static/uploads path
    print(f"   Testing: /static/uploads/{test_file}")
    try:
        response = requests.get(f"{BASE_URL}/static/uploads/{test_file}", timeout=2)
        if response.status_code == 200:
            print(f"   ✅ /static/uploads mount WORKS")
        else:
            print(f"   ❌ /static/uploads mount FAILED ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print(f"   ⚠️  No uploaded files to test with")
    print(f"   Upload an image first, then run this again")

print()
print("=" * 70)
print("📋 SUMMARY")
print("=" * 70)
print()
print("The mounts ARE in the code (main.py lines 288-289):")
print("  • app.mount('/uploads', StaticFiles(...))")
print("  • app.mount('/static/uploads', StaticFiles(...))")
print()
print("If you're getting 404 errors, the issue is:")
print("  ⚠️  SERVER IS RUNNING OLD CODE - RESTART REQUIRED!")
print()
print("=" * 70)
print("🔄 TO FIX:")
print("=" * 70)
print("1. Stop server: Ctrl+C")
print("2. Restart: python run.py")
print("3. Run this diagnostic again")
print("=" * 70)

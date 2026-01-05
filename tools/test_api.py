import requests

API_KEY = "hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU"
BASE_URL = "http://localhost:8000"

print("\n=== TESTING API ENDPOINTS ===\n")

# Test 1: GET /api/students (list all)
print("1. Testing GET /api/students...")
try:
    response = requests.get(
        f"{BASE_URL}/api/students",
        headers={"X-API-Key": API_KEY}
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ SUCCESS: Got {len(data.get('students', []))} students")
        if data.get('students'):
            print(f"   Sample: {data['students'][0]['full_name']}")
    else:
        print(f"   ❌ ERROR: {response.text}")
except Exception as e:
    print(f"   ❌ EXCEPTION: {e}")

# Test 2: GET /api/students/search
print("\n2. Testing GET /api/students/search...")
try:
    response = requests.get(
        f"{BASE_URL}/api/students/search?q=MARK",
        headers={"X-API-Key": API_KEY}
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✅ SUCCESS: Found {len(data.get('results', []))} results")
    else:
        print(f"   ❌ ERROR: {response.text}")
except Exception as e:
    print(f"   ❌ EXCEPTION: {e}")

# Test 3: Without API key (should fail)
print("\n3. Testing WITHOUT API key (should fail)...")
try:
    response = requests.get(f"{BASE_URL}/api/students")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ✅ Correctly rejecting unauthenticated requests")
    else:
        print(f"   ⚠️ UNEXPECTED: {response.text}")
except Exception as e:
    print(f"   ❌ EXCEPTION: {e}")

print("\n=== END API TESTS ===\n")

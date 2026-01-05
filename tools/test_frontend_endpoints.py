"""Test all frontend API endpoints for authentication and functionality"""
import requests
import os
from pathlib import Path

API_KEY = "hE_wZo2nC99rrJoz2teepVl22MX3T9vsOnZgZGgKtTU"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY}

def test_endpoint(name, method, url, **kwargs):
    """Test an endpoint and return result"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{url}", headers=HEADERS, **kwargs)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{url}", headers=HEADERS, **kwargs)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{url}", headers=HEADERS, **kwargs)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{url}", headers=HEADERS, **kwargs)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code >= 400:
            print(f"   Error: {response.text[:200]}")
        return response.status_code < 400
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

print("\n=== FRONTEND ENDPOINT AUDIT ===\n")

# Student endpoints
print("📚 STUDENT ENDPOINTS")
test_endpoint("Get Students", "GET", "/api/students?page=1&page_size=10")
test_endpoint("Search Students", "GET", "/api/students/search?q=MARK")
test_endpoint("Get Student by ID", "GET", "/api/students/2025-003")

# History endpoints  
print("\n📋 HISTORY ENDPOINTS")
test_endpoint("Get History", "GET", "/api/history?limit=5")

# Import endpoints
print("\n📥 IMPORT ENDPOINTS")
# Create a test CSV
csv_content = b"id_number,full_name\\n2026-001,TEST STUDENT"
files = {"file": ("test.csv", csv_content, "text/csv")}
test_endpoint("Import Preview", "POST", "/api/students/import/preview", files=files)

# Template endpoints
print("\n🎨 TEMPLATE ENDPOINTS")
test_endpoint("Get Templates", "GET", "/api/templates")
test_endpoint("List Templates", "GET", "/api/templates/list")

# Settings endpoints
print("\n⚙️ SETTINGS ENDPOINTS")
test_endpoint("Get Settings", "GET", "/api/settings")
test_endpoint("Get Layout", "GET", "/api/layout")

# System endpoints
print("\n🖥️ SYSTEM ENDPOINTS")
test_endpoint("System Stats", "GET", "/api/system/stats")
test_endpoint("Health Check", "GET", "/api/health")

# Stats endpoint
print("\n📊 STATS ENDPOINTS")
test_endpoint("Get Stats", "GET", "/api/stats")

print("\n=== AUDIT COMPLETE ===\n")

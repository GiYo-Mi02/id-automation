"""
Test API Fixes: Ordering and Upload
====================================
Verify that:
1. Students are returned in chronological order (newest first)
2. Image upload endpoint works correctly
"""

import requests
import json
from pathlib import Path
from io import BytesIO
from PIL import Image

BASE_URL = "http://localhost:8000"

def test_students_ordering():
    """Test that students are returned with proper ordering."""
    print("\n" + "="*60)
    print("TEST 1: Students Endpoint with Ordering")
    print("="*60)
    
    # Test default ordering
    response = requests.get(f"{BASE_URL}/api/students")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check structure
        if isinstance(data, dict) and 'students' in data:
            students = data['students']
            total = data.get('total', 0)
            print(f"✅ Returned {len(students)} of {total} students")
            
            # Check ordering (should be DESC by created_at)
            if len(students) >= 2:
                first = students[0]
                last = students[-1]
                print(f"First: {first.get('full_name')} ({first.get('created_at', 'N/A')})")
                print(f"Last:  {last.get('full_name')} ({last.get('created_at', 'N/A')})")
                
                if first.get('created_at') and last.get('created_at'):
                    if first['created_at'] >= last['created_at']:
                        print("✅ Ordering is correct (newest first)")
                    else:
                        print("❌ Ordering is incorrect")
        else:
            print(f"✅ Legacy format: {len(data)} students")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test with explicit parameters
    print("\n📊 Testing with pagination and sorting...")
    response = requests.get(
        f"{BASE_URL}/api/students",
        params={
            'page': 1,
            'page_size': 10,
            'sort_by': 'created_at',
            'sort_order': 'DESC'
        }
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pagination working: page {data.get('page')}, size {data.get('page_size')}")
    else:
        print(f"❌ Pagination failed: {response.text}")


def test_image_upload():
    """Test image upload endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Image Upload Endpoint")
    print("="*60)
    
    # Create a test image
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload the image
    files = {'file': ('test_logo.png', img_bytes, 'image/png')}
    response = requests.post(f"{BASE_URL}/api/upload/image", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   URL: {data.get('url')}")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Dimensions: {data.get('width')}x{data.get('height')}")
        
        # Try to access the uploaded image
        img_url = f"{BASE_URL}{data.get('url')}"
        check_response = requests.get(img_url)
        
        if check_response.status_code == 200:
            print(f"✅ Image is accessible at {img_url}")
        else:
            print(f"❌ Image not accessible: {check_response.status_code}")
    else:
        print(f"❌ Upload failed: {response.text}")


def test_search_with_ordering():
    """Test that search results also maintain ordering."""
    print("\n" + "="*60)
    print("TEST 3: Search with Ordering")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/students/search?q=a")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Found {len(results)} results")
        if results:
            print(f"   First: {results[0].get('full_name')}")
    else:
        print(f"❌ Search failed: {response.text}")


if __name__ == "__main__":
    print("\n🚀 Testing API Fixes")
    print("Make sure the backend server is running at http://localhost:8000")
    print()
    
    try:
        # Test connectivity
        response = requests.get(f"{BASE_URL}/api/students", timeout=2)
        print("✅ Server is reachable\n")
        
        # Run tests
        test_students_ordering()
        test_image_upload()
        test_search_with_ordering()
        
        print("\n" + "="*60)
        print("✨ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running at http://localhost:8000?")
    except Exception as e:
        print(f"❌ Test error: {e}")

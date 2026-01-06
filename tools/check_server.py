"""
Backend Server Restart & Verification
======================================
Use this to restart your server and verify the upload endpoint is loaded.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_server():
    """Check if server is running and has the upload endpoint."""
    import requests
    try:
        # Check if server is up
        response = requests.get("http://localhost:8000/api/students", timeout=2)
        print("✅ Server is running")
        
        # Try to access upload endpoint (should get 422 without file, not 404)
        response = requests.post("http://localhost:8000/api/upload/image", timeout=2)
        if response.status_code == 422:
            print("✅ Upload endpoint exists (returned 422 - missing file, which is expected)")
            return True
        elif response.status_code == 404:
            print("❌ Upload endpoint NOT FOUND (404)")
            print("   The server needs to be restarted to load the new code")
            return False
        else:
            print(f"⚠️  Upload endpoint returned unexpected status: {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is NOT running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BACKEND SERVER STATUS CHECK")
    print("=" * 60)
    print()
    
    is_ok = check_server()
    
    print()
    print("=" * 60)
    
    if not is_ok:
        print("\n⚠️  ACTION REQUIRED:")
        print("\n1. Stop your current backend server (Ctrl+C)")
        print("\n2. Restart it with one of these commands:")
        print("   • python run.py")
        print("   • uvicorn app.api:app --reload")
        print("   • python app/main.py")
        print("\n3. Run this script again to verify")
        print("\n4. Then run: python tools/test_api_fixes.py")
    else:
        print("\n✅ Server is ready!")
        print("\nRun the tests: python tools/test_api_fixes.py")
    
    print("=" * 60)

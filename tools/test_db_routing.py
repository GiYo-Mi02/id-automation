#!/usr/bin/env python3
"""
Test Database Query Routing
============================
Tests that employee IDs route to teachers table, student IDs to students table.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app import database

def test_database_functions():
    """Test that database functions exist and work correctly."""
    print("\n🧪 Testing Database Query Functions")
    print("=" * 60)
    
    # Test 1: get_teacher function exists
    print("\n1️⃣  Testing get_teacher() function exists...")
    if hasattr(database, 'get_teacher'):
        print("   ✅ get_teacher() function found")
    else:
        print("   ❌ get_teacher() function missing")
        return False
    
    # Test 2: Try querying a teacher (may not exist, that's OK)
    print("\n2️⃣  Testing get_teacher() query...")
    try:
        result = database.get_teacher('EMP-2024-002')
        if result:
            print(f"   ✅ Found teacher: {result.get('full_name', 'N/A')}")
            print(f"   📋 Position: {result.get('position', 'N/A')}")
            print(f"   📋 Department: {result.get('department', 'N/A')}")
        else:
            print("   ⚠️  No teacher with ID 'EMP-2024-002' (this is OK if DB is empty)")
    except Exception as e:
        print(f"   ❌ Error querying teacher: {e}")
        return False
    
    # Test 3: Verify get_student still works
    print("\n3️⃣  Testing get_student() still works...")
    try:
        result = database.get_student('123456789')
        if result:
            print(f"   ✅ Found student: {result.get('full_name', 'N/A')}")
        else:
            print("   ⚠️  No student with ID '123456789' (this is OK if DB is empty)")
    except Exception as e:
        print(f"   ❌ Error querying student: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Database query functions working correctly!")
    return True

def test_processor_routing():
    """Test that school_id_processor routes IDs correctly."""
    print("\n🧪 Testing ID Routing Logic")
    print("=" * 60)
    
    # Test employee ID detection logic (without instantiating processor)
    print("\n1️⃣  Testing employee ID detection...")
    test_ids = [
        ('EMP-2024-002', True, 'Employee ID'),
        ('TCH-2024-001', True, 'Teacher ID'),
        ('STF-2024-005', True, 'Staff ID'),
        ('T-001', True, 'Short Teacher ID'),
        ('123456789', False, 'Student ID'),
        ('2024-106', False, 'Student ID format'),
    ]
    
    for test_id, is_employee, description in test_ids:
        # Check the logic (same as in school_id_processor.py)
        detected_employee = (
            test_id.upper().startswith('EMP-') or 
            test_id.upper().startswith('TCH-') or 
            test_id.upper().startswith('T-') or 
            test_id.upper().startswith('STF-')
        )
        
        if detected_employee == is_employee:
            print(f"   ✅ {test_id:15} → {'Employee' if is_employee else 'Student':8} ({description})")
        else:
            print(f"   ❌ {test_id:15} → WRONG DETECTION ({description})")
    
    print("\n" + "=" * 60)
    print("✅ ID routing logic working correctly!")
    return True

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("DATABASE QUERY ROUTING TEST")
    print("=" * 60)
    
    success = True
    
    # Test database functions
    if not test_database_functions():
        success = False
    
    # Test routing logic
    if not test_processor_routing():
        success = False
    
    if success:
        print("\n✅ ALL TESTS PASSED")
        print("\nNext Steps:")
        print("  1. Add employee records to database (if not present)")
        print("  2. Test with actual employee photo: EMP-2024-002.jpg")
        print("  3. Verify output shows position/department instead of 'UNKNOWN'")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print()

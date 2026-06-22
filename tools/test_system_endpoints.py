import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import db_manager
from app.routes.system import get_database_status, analyze_storage, ClearDataRequest, clear_database_data

async def run_tests():
    print("🧪 Starting in-memory system endpoints test...")
    print("=" * 60)
    
    # 1. Test database status mapping
    print("\n1️⃣  Testing get_database_status()...")
    status_res = await get_database_status(db_manager)
    print(f"   Status Response: {status_res}")
    
    # Assertions
    assert "status" in status_res
    assert "total_students" in status_res
    assert "total_teachers" in status_res
    assert "total_staff" in status_res
    assert "total_history" in status_res
    print("   ✅ get_database_status structure is correct!")
    print(f"      Total Students: {status_res['total_students']}")
    print(f"      Total Teachers: {status_res['total_teachers']}")
    print(f"      Total Staff:    {status_res['total_staff']}")
    print(f"      Total History:  {status_res['total_history']}")
    
    # 2. Test storage analysis mapping
    print("\n2️⃣  Testing analyze_storage()...")
    storage_res = await analyze_storage()
    print("   Storage Response summary:")
    print(f"      Total files: {storage_res.get('total_files')}")
    print(f"      Linked files: {storage_res.get('linked_files')}")
    print(f"      Orphaned files count: {len(storage_res.get('orphaned_files', []))}")
    print(f"      Orphaned total size: {storage_res.get('orphaned_total_size')}")
    
    # Assertions
    assert "total_files" in storage_res
    assert "linked_files" in storage_res
    assert "orphaned_files" in storage_res
    assert "orphaned_total_size" in storage_res
    
    # Verify shape of orphaned files list elements
    orphaned_list = storage_res.get('orphaned_files', [])
    if len(orphaned_list) > 0:
        first_orphan = orphaned_list[0]
        print(f"      Sample Orphan shape: {first_orphan}")
        assert "name" in first_orphan
        assert "path" in first_orphan
        assert "size" in first_orphan
        assert "modified" in first_orphan
        print("   ✅ orphaned_files element structure is correct!")
    else:
        print("   ⚠️  No orphaned files found, skipping shape verification")
    
    # 3. Test database clear verification
    print("\n3️⃣  Testing clear_database_data() dry-run validation...")
    
    # Test wrong confirm text
    invalid_req = ClearDataRequest(
        entity_type="history",
        clear_type="history",
        confirm_text="WRONG CONFIRMATION"
    )
    try:
        await clear_database_data(invalid_req)
        print("   ❌ Error: expected HTTPException for invalid confirmation, but got success")
        return False
    except Exception as e:
        print(f"   ✅ Got expected error for invalid confirmation: {e}")
        
    # 4. Test student service get_generation_history
    print("\n4️⃣  Testing student_service.get_generation_history()...")
    from app.services.student_service import get_student_service
    service = get_student_service()
    history_res = service.get_generation_history(limit=5)
    print(f"   History total: {history_res.total}, limit: {history_res.limit}")
    if len(history_res.history) > 0:
        first_hist = history_res.history[0]
        print(f"      First Entry: id_number={first_hist.student_id}, name={first_hist.full_name}, user_type={first_hist.user_type}, grade_level={first_hist.grade_level}, position={first_hist.position}, department={first_hist.department}")
        assert hasattr(first_hist, "user_type")
        assert hasattr(first_hist, "grade_level")
        assert hasattr(first_hist, "position")
        assert hasattr(first_hist, "department")
        print("   ✅ get_generation_history element structure is correct!")
    else:
        print("   ⚠️  No history records found, skipping verification")
        
    print("\n" + "=" * 60)
    print("🎉 ALL IN-MEMORY ROUTE TESTS PASSED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    # Ensure correct event loop policy on Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(run_tests())
    if not success:
        sys.exit(1)

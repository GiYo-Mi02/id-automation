"""
System & Import Routes
======================
System statistics, unified activity, database management, and CSV import functionality.
"""

import io
import os
import csv
import logging
import psutil
import shutil
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Body
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.services.student_service import StudentService, get_student_service
from app.db.database import DatabaseManager, get_db
from app.database import get_db_connection

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM ROUTER
# =============================================================================

system_router = APIRouter(
    prefix="/api/system",
    tags=["system"],
)


@system_router.get(
    "/stats",
    summary="Get system statistics",
    description="Returns system resource usage and database statistics."
)
async def get_system_stats(
    service: StudentService = Depends(get_student_service),
    db: DatabaseManager = Depends(get_db)
):
    """Get system and database statistics."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database health
        db_health = db.health_check()
        
        # Student statistics
        student_stats = service.get_stats()
        
        return {
            "system": {
                "cpu_usage": round(cpu_percent, 1),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": round(memory.percent, 1),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": round(disk.percent, 1),
            },
            "database": {
                "status": db_health.get("status"),
                "pool_name": db_health.get("pool_name"),
                "pool_size": db_health.get("pool_size"),
            },
            "students": student_stats,
        }
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {
            "system": {
                "cpu_usage": 0,
                "memory_percent": 0,
                "disk_percent": 0,
            },
            "database": {"status": "unknown"},
            "students": {},
        }


# =============================================================================
# UNIFIED ACTIVITY ENDPOINT
# =============================================================================

@system_router.get(
    "/activity/recent",
    summary="Get recent activity across all entity types",
    description="Returns unified recent ID generation activity for students, teachers, and staff."
)
async def get_recent_activity(
    entity_type: Optional[Literal["all", "student", "teacher", "staff"]] = Query("all"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """Get recent activity across all entity types with pagination."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        # Build query based on entity type
        if entity_type == "all":
            # Union query across all history tables
            query = """
                SELECT 
                    id,
                    student_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'student' as entity_type,
                    NULL as department,
                    NULL as position
                FROM generation_history
                WHERE student_id IS NOT NULL
                
                UNION ALL
                
                SELECT 
                    id,
                    teacher_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'teacher' as entity_type,
                    department,
                    position
                FROM teacher_history
                WHERE teacher_id IS NOT NULL
                
                UNION ALL
                
                SELECT 
                    id,
                    staff_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'staff' as entity_type,
                    department,
                    position
                FROM staff_history
                WHERE staff_id IS NOT NULL
                
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, [per_page, offset])
            items = cursor.fetchall()
            
            # Get total counts
            cursor.execute("SELECT COUNT(*) as c FROM generation_history WHERE student_id IS NOT NULL")
            student_count = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM teacher_history WHERE teacher_id IS NOT NULL")
            teacher_count = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM staff_history WHERE staff_id IS NOT NULL")
            staff_count = cursor.fetchone()['c']
            total = student_count + teacher_count + staff_count
            
        elif entity_type == "student":
            cursor.execute("""
                SELECT 
                    id,
                    student_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'student' as entity_type,
                    NULL as department,
                    NULL as position
                FROM generation_history
                WHERE student_id IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """, [per_page, offset])
            items = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) as c FROM generation_history WHERE student_id IS NOT NULL")
            total = cursor.fetchone()['c']
            student_count = total
            teacher_count = 0
            staff_count = 0
            
        elif entity_type == "teacher":
            cursor.execute("""
                SELECT 
                    id,
                    teacher_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'teacher' as entity_type,
                    department,
                    position
                FROM teacher_history
                WHERE teacher_id IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """, [per_page, offset])
            items = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) as c FROM teacher_history WHERE teacher_id IS NOT NULL")
            total = cursor.fetchone()['c']
            student_count = 0
            teacher_count = total
            staff_count = 0
            
        else:  # staff
            cursor.execute("""
                SELECT 
                    id,
                    staff_id as entity_id,
                    full_name,
                    file_path,
                    COALESCE(status, 'success') as status,
                    timestamp,
                    'staff' as entity_type,
                    department,
                    position
                FROM staff_history
                WHERE staff_id IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """, [per_page, offset])
            items = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) as c FROM staff_history WHERE staff_id IS NOT NULL")
            total = cursor.fetchone()['c']
            student_count = 0
            teacher_count = 0
            staff_count = total
        
        import math
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "counts": {
                "students": student_count,
                "teachers": teacher_count,
                "staff": staff_count,
                "all": student_count + teacher_count + staff_count
            }
        }
    except Exception as e:
        logger.error(f"Failed to get recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# DATABASE MANAGEMENT ENDPOINTS
# =============================================================================

class ClearDataRequest(BaseModel):
    entity_type: Literal["students", "teachers", "staff", "all"]
    confirm_text: str
    admin_password: Optional[str] = None


@system_router.get(
    "/database/status",
    summary="Get database connection status"
)
async def get_database_status(db: DatabaseManager = Depends(get_db)):
    """Test database connection and return status."""
    try:
        health = db.health_check()
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get record counts
            counts = {}
            for table in ['students', 'teachers', 'staff', 'id_templates', 'generation_history']:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    counts[table] = cursor.fetchone()['count']
                except:
                    counts[table] = 0
            
            cursor.close()
            conn.close()
            
            return {
                "status": "connected",
                "latency_ms": health.get("latency_ms", 0),
                "pool_size": health.get("pool_size", 0),
                "counts": counts
            }
        else:
            return {"status": "disconnected", "error": "Could not establish connection"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@system_router.post(
    "/database/clear",
    summary="Clear data from database"
)
async def clear_database_data(request: ClearDataRequest):
    """
    Clear data from database with confirmation.
    
    Requires matching confirm_text:
    - students: "DELETE STUDENTS"
    - teachers: "DELETE TEACHERS"
    - staff: "DELETE STAFF"
    - all: "RESET SYSTEM" (also requires admin_password)
    """
    # Validate confirmation text
    expected_confirms = {
        "students": "DELETE STUDENTS",
        "teachers": "DELETE TEACHERS",
        "staff": "DELETE STAFF",
        "all": "RESET SYSTEM"
    }
    
    expected = expected_confirms.get(request.entity_type)
    if request.confirm_text != expected:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid confirmation. Expected: '{expected}'"
        )
    
    # For "all", require admin password
    if request.entity_type == "all":
        # Simple password check (in production, use proper auth)
        if request.admin_password != "admin123":
            raise HTTPException(status_code=403, detail="Invalid admin password")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        deleted_counts = {}
        
        if request.entity_type in ["students", "all"]:
            cursor.execute("SELECT COUNT(*) FROM students")
            deleted_counts["students"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM generation_history")
            cursor.execute("DELETE FROM students")
            
        if request.entity_type in ["teachers", "all"]:
            cursor.execute("SELECT COUNT(*) FROM teachers")
            deleted_counts["teachers"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM teacher_history")
            cursor.execute("DELETE FROM teachers")
            
        if request.entity_type in ["staff", "all"]:
            cursor.execute("SELECT COUNT(*) FROM staff")
            deleted_counts["staff"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM staff_history")
            cursor.execute("DELETE FROM staff")
        
        if request.entity_type == "all":
            # Also clear templates if full reset
            cursor.execute("SELECT COUNT(*) FROM id_templates")
            deleted_counts["templates"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM id_templates")
        
        conn.commit()
        
        return {
            "success": True,
            "deleted": deleted_counts,
            "message": f"Successfully cleared {request.entity_type} data"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# STORAGE MANAGEMENT ENDPOINTS
# =============================================================================

@system_router.get(
    "/storage/analyze",
    summary="Analyze storage usage"
)
async def analyze_storage():
    """Analyze storage usage across all data directories."""
    base_path = Path("data")
    
    def get_dir_size(path: Path) -> int:
        total = 0
        if path.exists():
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        return total
    
    def count_files(path: Path, extensions: list = None) -> int:
        count = 0
        if path.exists():
            for item in path.rglob("*"):
                if item.is_file():
                    if extensions is None or item.suffix.lower() in extensions:
                        count += 1
        return count
    
    # Calculate sizes
    output_size = get_dir_size(base_path / "output")
    input_size = get_dir_size(base_path / "input")
    templates_size = get_dir_size(base_path / "Templates")
    print_sheets_size = get_dir_size(base_path / "Print_Sheets")
    models_size = get_dir_size(base_path / "models")
    database_size = get_dir_size(base_path / "database")
    
    total_size = output_size + input_size + templates_size + print_sheets_size + models_size + database_size
    
    # Count files
    output_count = count_files(base_path / "output", [".png", ".jpg", ".jpeg"])
    input_count = count_files(base_path / "input", [".png", ".jpg", ".jpeg", ".json"])
    template_count = count_files(base_path / "Templates", [".png", ".jpg", ".jpeg"])
    
    # Find orphaned files (files in output not linked to any history)
    orphaned_files = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get all file paths from history
            cursor.execute("SELECT file_path FROM generation_history WHERE file_path IS NOT NULL")
            db_files = set(row['file_path'] for row in cursor.fetchall())
            
            cursor.execute("SELECT file_path FROM teacher_history WHERE file_path IS NOT NULL")
            db_files.update(row['file_path'] for row in cursor.fetchall())
            
            cursor.execute("SELECT file_path FROM staff_history WHERE file_path IS NOT NULL")
            db_files.update(row['file_path'] for row in cursor.fetchall())
            
            # Check output directory
            output_path = base_path / "output"
            if output_path.exists():
                for f in output_path.glob("*.png"):
                    if str(f) not in db_files and f.name not in [Path(p).name for p in db_files]:
                        orphaned_files.append(str(f))
            
            cursor.close()
        except Exception as e:
            logger.error(f"Error finding orphaned files: {e}")
        finally:
            conn.close()
    
    orphaned_size = sum(Path(f).stat().st_size for f in orphaned_files if Path(f).exists())
    
    return {
        "total_bytes": total_size,
        "total_formatted": format_bytes(total_size),
        "breakdown": {
            "generated_ids": {
                "bytes": output_size,
                "formatted": format_bytes(output_size),
                "count": output_count
            },
            "input_photos": {
                "bytes": input_size,
                "formatted": format_bytes(input_size),
                "count": input_count
            },
            "templates": {
                "bytes": templates_size,
                "formatted": format_bytes(templates_size),
                "count": template_count
            },
            "print_sheets": {
                "bytes": print_sheets_size,
                "formatted": format_bytes(print_sheets_size)
            },
            "ai_models": {
                "bytes": models_size,
                "formatted": format_bytes(models_size)
            }
        },
        "orphaned": {
            "bytes": orphaned_size,
            "formatted": format_bytes(orphaned_size),
            "count": len(orphaned_files),
            "files": orphaned_files[:20]  # Limit to first 20
        }
    }


def format_bytes(size: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


@system_router.post(
    "/storage/cleanup",
    summary="Clean up orphaned files"
)
async def cleanup_storage(confirm: bool = Query(False)):
    """Delete orphaned files from storage."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Add ?confirm=true to actually delete files"
        )
    
    # Get orphaned files
    analysis = await analyze_storage()
    orphaned = analysis.get("orphaned", {}).get("files", [])
    
    deleted = []
    errors = []
    
    for file_path in orphaned:
        try:
            if Path(file_path).exists():
                Path(file_path).unlink()
                deleted.append(file_path)
        except Exception as e:
            errors.append({"file": file_path, "error": str(e)})
    
    return {
        "success": True,
        "deleted_count": len(deleted),
        "deleted_files": deleted,
        "errors": errors
    }


# =============================================================================
# IMPORT ROUTER
# =============================================================================

import_router = APIRouter(
    prefix="/api/students/import",
    tags=["import"]
)


@import_router.post(
    "/preview",
    summary="Preview CSV import",
    description="Upload a CSV file and preview the first few rows."
)
async def preview_csv_import(
    file: UploadFile = File(...),
    service: StudentService = Depends(get_student_service)
):
    """
    Preview CSV file before importing.
    
    Returns first 5 rows with column mapping validation.
    """
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8-sig')  # Handle BOM
        
        # Parse CSV
        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)
        
        # Get headers
        headers = reader.fieldnames or []
        
        # Required columns for student import
        required_columns = ['id_number', 'full_name']
        optional_columns = ['lrn', 'grade_level', 'section', 'guardian_name', 'address', 'guardian_contact']
        
        # Check for missing required columns
        missing_columns = [col for col in required_columns if col not in headers]
        
        # Read first 5 rows as preview
        preview_data = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            preview_data.append(row)
        
        # Count total rows
        csv_file.seek(0)
        total_rows = sum(1 for _ in csv.DictReader(csv_file)) - 1  # Exclude header
        
        return {
            "total_rows": total_rows,
            "headers": headers,
            "required_columns": required_columns,
            "optional_columns": optional_columns,
            "missing_columns": missing_columns,
            "preview_data": preview_data,
            "valid": len(missing_columns) == 0,
            "message": "Ready to import" if len(missing_columns) == 0 else f"Missing required columns: {', '.join(missing_columns)}"
        }
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding error. Please use UTF-8 encoding."
        )
    except csv.Error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV parsing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"CSV preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}"
        )


@import_router.post(
    "",
    summary="Import students from CSV",
    description="Import student records from CSV file."
)
async def import_students_csv(
    file: UploadFile = File(...),
    service: StudentService = Depends(get_student_service)
):
    """
    Import students from CSV file.
    
    Creates or updates student records from CSV data.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8-sig')
        
        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)
        
        imported = 0
        errors = []
        
        for i, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
            try:
                # Validate required fields
                if not row.get('id_number') or not row.get('full_name'):
                    errors.append({
                        "row": i,
                        "error": "Missing id_number or full_name"
                    })
                    continue
                
                # Create student data
                from app.models.student import StudentCreateRequest
                student_data = StudentCreateRequest(
                    id_number=row['id_number'].strip(),
                    full_name=row['full_name'].strip(),
                    lrn=row.get('lrn', '').strip(),
                    grade_level=row.get('grade_level', '').strip(),
                    section=row.get('section', '').strip(),
                    guardian_name=row.get('guardian_name', '').strip(),
                    address=row.get('address', '').strip(),
                    guardian_contact=row.get('guardian_contact', '').strip(),
                )
                
                # Try to create (will fail if exists)
                try:
                    service.create_student(student_data)
                    imported += 1
                except Exception as create_error:
                    # If exists, try update
                    if "already exists" in str(create_error).lower():
                        from app.models.student import StudentUpdateRequest
                        update_data = StudentUpdateRequest(
                            full_name=row['full_name'].strip(),
                            lrn=row.get('lrn', '').strip(),
                            grade_level=row.get('grade_level', '').strip(),
                            section=row.get('section', '').strip(),
                            guardian_name=row.get('guardian_name', '').strip(),
                            address=row.get('address', '').strip(),
                            guardian_contact=row.get('guardian_contact', '').strip(),
                        )
                        service.update_student(row['id_number'].strip(), update_data)
                        imported += 1
                    else:
                        raise
                        
            except Exception as e:
                errors.append({
                    "row": i,
                    "data": row,
                    "error": str(e)
                })
        
        total_rows = sum(1 for _ in csv.DictReader(io.StringIO(content_str)))
        
        return {
            "status": "success" if not errors else "partial",
            "imported": imported,
            "total": total_rows,
            "errors": errors[:10],  # Limit to first 10 errors
            "error_count": len(errors)
        }
        
    except Exception as e:
        logger.error(f"CSV import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

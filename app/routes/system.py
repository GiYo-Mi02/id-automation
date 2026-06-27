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
import time
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Body, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image

from app.core.config import get_settings
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
            "storageUsed": round(disk.used / (1024**3), 2),
            "storageTotal": round(disk.total / (1024**3), 2),
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
    entity_type: Optional[Literal["students", "teachers", "staff", "history", "all"]] = None
    clear_type: Optional[Literal["students", "teachers", "staff", "history", "all"]] = None
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
                "counts": counts,
                "total_students": counts.get("students", 0),
                "total_teachers": counts.get("teachers", 0),
                "total_staff": counts.get("staff", 0),
                "total_history": counts.get("generation_history", 0)
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
    
    Supports:
    - students: "DELETE STUDENTS"
    - teachers: "DELETE TEACHERS"
    - staff: "DELETE STAFF"
    - history: "DELETE HISTORY"
    - all: "RESET SYSTEM"
    """
    target_type = request.entity_type or request.clear_type
    if not target_type:
        raise HTTPException(
            status_code=400,
            detail="Either entity_type or clear_type must be specified"
        )
        
    # Validate confirmation text
    expected_confirms = {
        "students": "DELETE STUDENTS",
        "teachers": "DELETE TEACHERS",
        "staff": "DELETE STAFF",
        "history": "DELETE HISTORY",
        "all": "RESET SYSTEM"
    }
    
    expected = expected_confirms.get(target_type)
    if request.confirm_text != expected:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid confirmation. Expected: '{expected}'"
        )
    
    # Simple password check for full system reset (optional in dev)
    if target_type == "all" and request.admin_password:
        if request.admin_password != "admin123":
            raise HTTPException(status_code=403, detail="Invalid admin password")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        deleted_counts = {}
        
        if target_type in ["students", "all"]:
            cursor.execute("SELECT COUNT(*) FROM students")
            deleted_counts["students"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM generation_history")
            cursor.execute("DELETE FROM students")
            
        if target_type in ["teachers", "all"]:
            cursor.execute("SELECT COUNT(*) FROM teachers")
            deleted_counts["teachers"] = cursor.fetchone()[0]
            try: cursor.execute("DELETE FROM teacher_history")
            except: pass
            try: cursor.execute("DELETE FROM teacher_generation_history")
            except: pass
            cursor.execute("DELETE FROM teachers")
            
        if target_type in ["staff", "all"]:
            cursor.execute("SELECT COUNT(*) FROM staff")
            deleted_counts["staff"] = cursor.fetchone()[0]
            try: cursor.execute("DELETE FROM staff_history")
            except: pass
            cursor.execute("DELETE FROM staff")
            
        if target_type == "history":
            cursor.execute("SELECT COUNT(*) FROM generation_history")
            deleted_counts["history"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM generation_history")
            try: cursor.execute("DELETE FROM teacher_history")
            except: pass
            try: cursor.execute("DELETE FROM teacher_generation_history")
            except: pass
            try: cursor.execute("DELETE FROM staff_history")
            except: pass
        
        if target_type == "all":
            # Also clear templates if full reset
            cursor.execute("SELECT COUNT(*) FROM id_templates")
            deleted_counts["templates"] = cursor.fetchone()[0]
            cursor.execute("DELETE FROM id_templates")
        
        conn.commit()
        
        return {
            "success": True,
            "deleted": deleted_counts,
            "message": f"Successfully cleared {target_type} data"
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

class CleanupStorageRequest(BaseModel):
    files: list[str]


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
            
            try:
                cursor.execute("SELECT file_path FROM teacher_history WHERE file_path IS NOT NULL")
                db_files.update(row['file_path'] for row in cursor.fetchall())
            except:
                pass
                
            try:
                cursor.execute("SELECT file_path FROM staff_history WHERE file_path IS NOT NULL")
                db_files.update(row['file_path'] for row in cursor.fetchall())
            except:
                pass
            
            # Check output directory
            output_path = base_path / "output"
            if output_path.exists():
                for f in output_path.glob("*.png"):
                    if str(f) not in db_files and f.name not in [Path(p).name for p in db_files]:
                        try:
                            stat = f.stat()
                            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            orphaned_files.append({
                                "name": f.name,
                                "path": str(f),
                                "size": stat.st_size,
                                "modified": mod_time
                            })
                        except Exception as e:
                            logger.error(f"Error accessing file stats: {e}")
            
            cursor.close()
        except Exception as e:
            logger.error(f"Error finding orphaned files: {e}")
        finally:
            conn.close()
    
    orphaned_size = sum(f["size"] for f in orphaned_files)
    
    return {
        "total_files": output_count + input_count + template_count,
        "linked_files": len(db_files) if conn else 0,
        "orphaned_files": orphaned_files,
        "orphaned_total_size": orphaned_size,
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
            "files": orphaned_files[:20]  # Limit to first 20 for legacy compatibility
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
async def cleanup_storage(
    request: CleanupStorageRequest = Body(default=None),
    confirm: bool = Query(True)
):
    """Delete orphaned files from storage."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Add ?confirm=true to actually delete files"
        )
    
    # Determine files to delete
    if request and request.files:
        files_to_delete = request.files
    else:
        # Fallback to analyzing storage and finding all orphans
        analysis = await analyze_storage()
        files_to_delete = [f["path"] for f in analysis.get("orphaned_files", [])]
    
    deleted = []
    errors = []
    
    for file_path in files_to_delete:
        try:
            p = Path(file_path)
            if p.exists():
                p.unlink()
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


def _remove_temp_file(path: Path):
    """Safely remove a temporary file."""
    try:
        if path.exists():
            path.unlink()
            logger.info(f"Cleaned up temporary export file: {path}")
    except Exception as e:
        logger.error(f"Failed to remove temporary file {path}: {e}")


@system_router.get(
    "/export-pdf",
    summary="Export student/employee IDs to single PDF",
    description="Compile student and employee front/back IDs into a single PDF, filtered by school."
)
async def export_pdf(
    background_tasks: BackgroundTasks,
    school: Optional[str] = Query(None),
    side: Literal["front", "back"] = Query("front"),
    api_key: str = Depends(verify_api_key)
):
    settings = get_settings()
    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Query students
        query_students = "SELECT id_number, lrn FROM students"
        params_students = []
        if school and school != "All Schools" and school.strip() != "":
            query_students += " WHERE school = %s"
            params_students.append(school)
        cursor.execute(query_students, params_students)
        students = cursor.fetchall()
        
        # Query teachers
        query_teachers = "SELECT employee_id as id_number, NULL as lrn FROM teachers"
        params_teachers = []
        if school and school != "All Schools" and school.strip() != "":
            query_teachers += " WHERE school = %s"
            params_teachers.append(school)
        cursor.execute(query_teachers, params_teachers)
        teachers = cursor.fetchall()
        
        # Query staff
        query_staff = "SELECT employee_id as id_number, NULL as lrn FROM staff"
        params_staff = []
        if school and school != "All Schools" and school.strip() != "":
            query_staff += " WHERE school = %s"
            params_staff.append(school)
        cursor.execute(query_staff, params_staff)
        staff = cursor.fetchall()
        
        cursor.close()
    finally:
        conn.close()

    all_entities = students + teachers + staff

    if not all_entities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students or employees found matching filters"
        )

    # Locate the card files
    output_dir = Path(settings.paths.output_dir)
    folder_name = "front-id" if side == "front" else "back0id"
    image_paths = []
    for s in all_entities:
        lrn = s.get("lrn")
        student_id = s.get("id_number")
        filename_base = lrn if lrn else student_id
        card_file = output_dir / folder_name / f"{filename_base}.png"
        if card_file.exists():
            image_paths.append(card_file)

    if not image_paths:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {side}-side images generated yet for the selected students/employees"
        )

    # Compile images using Pillow
    try:
        images_to_save = []
        for img_path in image_paths:
            img = Image.open(img_path)
            # PNG may have transparency (RGBA), convert/paste to white RGB background
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    bg.paste(img, (0, 0), img)
                else:
                    bg.paste(img.convert("RGBA"), (0, 0), img.convert("RGBA"))
            else:
                bg = img.convert("RGB")
            
            # Draw cutting border around the card edge
            from PIL import ImageDraw
            draw = ImageDraw.Draw(bg)
            draw.rectangle(
                [(0, 0), (bg.size[0] - 1, bg.size[1] - 1)],
                outline=(0, 0, 0),
                width=1
            )
            images_to_save.append(bg)
        
        # Save to temporary file
        temp_dir = Path(settings.paths.data_dir) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Unique file name with timestamp
        timestamp = int(time.time())
        school_slug = "".join([c if c.isalnum() else "_" for c in school]).lower() if school and school != "All Schools" else "all_schools"
        pdf_filename = f"{side}_ids_{school_slug}_{timestamp}.pdf"
        pdf_path = temp_dir / pdf_filename

        # Save first image and append remaining
        first_img = images_to_save[0]
        first_img.save(
            pdf_path,
            "PDF",
            save_all=True,
            append_images=images_to_save[1:]
        )
        
        # Close images
        for img in images_to_save:
            img.close()

        # Add background cleanup task
        background_tasks.add_task(_remove_temp_file, pdf_path)
        
        return FileResponse(
            path=str(pdf_path),
            filename=pdf_filename,
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Failed to compile PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile PDF: {str(e)}"
        )


@system_router.get(
    "/export-zip",
    summary="Export student/employee IDs to ZIP archive",
    description="Compile student and employee front/back IDs into a ZIP archive, filtered by school."
)
async def export_zip(
    background_tasks: BackgroundTasks,
    school: Optional[str] = Query(None),
    side: Literal["front", "back"] = Query("front"),
    api_key: str = Depends(verify_api_key)
):
    settings = get_settings()
    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Query students
        query_students = "SELECT id_number, lrn FROM students"
        params_students = []
        if school and school != "All Schools" and school.strip() != "":
            query_students += " WHERE school = %s"
            params_students.append(school)
        cursor.execute(query_students, params_students)
        students = cursor.fetchall()
        
        # Query teachers
        query_teachers = "SELECT employee_id as id_number, NULL as lrn FROM teachers"
        params_teachers = []
        if school and school != "All Schools" and school.strip() != "":
            query_teachers += " WHERE school = %s"
            params_teachers.append(school)
        cursor.execute(query_teachers, params_teachers)
        teachers = cursor.fetchall()
        
        # Query staff
        query_staff = "SELECT employee_id as id_number, NULL as lrn FROM staff"
        params_staff = []
        if school and school != "All Schools" and school.strip() != "":
            query_staff += " WHERE school = %s"
            params_staff.append(school)
        cursor.execute(query_staff, params_staff)
        staff = cursor.fetchall()
        
        cursor.close()
    finally:
        conn.close()

    all_entities = students + teachers + staff

    if not all_entities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students or employees found matching filters"
        )

    # Locate the card files
    output_dir = Path(settings.paths.output_dir)
    folder_name = "front-id" if side == "front" else "back0id"
    image_paths = []
    for s in all_entities:
        lrn = s.get("lrn")
        student_id = s.get("id_number")
        filename_base = lrn if lrn else student_id
        card_file = output_dir / folder_name / f"{filename_base}.png"
        if card_file.exists():
            image_paths.append(card_file)

    if not image_paths:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {side}-side images generated yet for the selected students/employees"
        )

    # Create temporary zip archive
    try:
        import zipfile
        temp_dir = Path(settings.paths.data_dir) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        school_slug = "".join([c if c.isalnum() else "_" for c in school]).lower() if school and school != "All Schools" else "all_schools"
        zip_filename = f"{side}_ids_{school_slug}_{timestamp}.zip"
        zip_path = temp_dir / zip_filename

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img_path in image_paths:
                # Add file to ZIP, using its basename to prevent full paths in zip
                zip_file.write(img_path, img_path.name)
        
        # Add background cleanup task
        background_tasks.add_task(_remove_temp_file, zip_path)
        
        return FileResponse(
            path=str(zip_path),
            filename=zip_filename,
            media_type="application/zip"
        )
    except Exception as e:
        logger.error(f"Failed to compile ZIP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile ZIP: {str(e)}"
        )

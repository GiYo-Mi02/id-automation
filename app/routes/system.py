"""
System & Import Routes
======================
System statistics and CSV import functionality.
"""

import io
import csv
import logging
import psutil
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.core.security import verify_api_key
from app.services.student_service import StudentService, get_student_service
from app.db.database import DatabaseManager, get_db

logger = logging.getLogger(__name__)


# =============================================================================
# SYSTEM ROUTER
# =============================================================================

system_router = APIRouter(
    prefix="/api/system",
    tags=["system"],
    dependencies=[Depends(verify_api_key)]
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
# IMPORT ROUTER
# =============================================================================

import_router = APIRouter(
    prefix="/api/students/import",
    tags=["import"],
    dependencies=[Depends(verify_api_key)]
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

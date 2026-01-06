import io
import csv
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Body, Query, UploadFile, File, status

from app.db.database import db_manager, QueryError
from app.models.teacher import (
    TeacherCreateRequest,
    TeacherUpdateRequest,
    TeacherResponse,
    TeacherListResponse,
    TeacherSearchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/teachers", tags=["teachers"])


# =============================================================================
# CRUD ENDPOINTS
# =============================================================================

@router.get("", response_model=TeacherListResponse)
def list_teachers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "full_name",
    sort_order: str = "asc",
):
    """List all teachers with pagination and filtering."""
    try:
        # Count total
        count_query = "SELECT COUNT(*) as total FROM teachers WHERE 1=1"
        count_params = []
        
        if department:
            count_query += " AND department = %s"
            count_params.append(department)
        
        if status:
            count_query += " AND employment_status = %s"
            count_params.append(status)
        
        count_result = db_manager.execute_query(
            count_query, 
            tuple(count_params) if count_params else None, 
            fetch_one=True
        )
        total = count_result['total'] if count_result else 0
        
        # Fetch page
        valid_sort_cols = ['full_name', 'employee_id', 'department', 'position', 'created_at']
        if sort_by not in valid_sort_cols:
            sort_by = 'full_name'
        
        order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        offset = (page - 1) * per_page
        
        query = f"""
            SELECT employee_id, full_name, department, position, specialization,
                   contact_number, emergency_contact_name, emergency_contact_number,
                   address, birth_date, blood_type, hire_date, employment_status,
                   photo_path, created_at, updated_at
            FROM teachers
            WHERE 1=1
        """
        params = []
        
        if department:
            query += " AND department = %s"
            params.append(department)
        
        if status:
            query += " AND employment_status = %s"
            params.append(status)
        
        query += f" ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        rows = db_manager.execute_query(query, tuple(params))
        
        teachers = []
        for row in (rows or []):
            teacher = TeacherResponse(
                employee_id=row['employee_id'],
                full_name=row['full_name'],
                department=row.get('department') or '',
                position=row.get('position') or '',
                specialization=row.get('specialization') or '',
                contact_number=row.get('contact_number') or '',
                emergency_contact_name=row.get('emergency_contact_name') or '',
                emergency_contact_number=row.get('emergency_contact_number') or '',
                address=row.get('address') or '',
                birth_date=row.get('birth_date'),
                blood_type=row.get('blood_type') or '',
                hire_date=row.get('hire_date'),
                employment_status=row.get('employment_status') or 'active',
                photo_path=row.get('photo_path'),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at'),
                front_image=f"/output/{row['employee_id']}_FRONT.png",
                back_image=f"/output/{row['employee_id']}_BACK.png",
            )
            teachers.append(teacher)
        
        return TeacherListResponse(
            teachers=teachers,
            total=total,
            page=page,
            page_size=per_page,
        )
    
    except QueryError as e:
        logger.error(f"Failed to list teachers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve teachers")


@router.get("/search", response_model=TeacherSearchResponse)
def search_teachers(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100)):
    """Search teachers by name or employee ID."""
    try:
        search_term = f"%{q}%"
        query = """
            SELECT employee_id, full_name, department, position, specialization,
                   contact_number, emergency_contact_name, emergency_contact_number,
                   address, birth_date, blood_type, photo_path
            FROM teachers
            WHERE full_name LIKE %s OR employee_id LIKE %s OR department LIKE %s
            LIMIT %s
        """
        
        rows = db_manager.execute_query(query, (search_term, search_term, search_term, limit))
        
        results = []
        for row in (rows or []):
            results.append(TeacherResponse(
                employee_id=row['employee_id'],
                full_name=row['full_name'],
                department=row.get('department') or '',
                position=row.get('position') or '',
                specialization=row.get('specialization') or '',
                contact_number=row.get('contact_number') or '',
                emergency_contact_name=row.get('emergency_contact_name') or '',
                emergency_contact_number=row.get('emergency_contact_number') or '',
                address=row.get('address') or '',
                birth_date=row.get('birth_date'),
                blood_type=row.get('blood_type') or '',
                front_image=f"/output/{row['employee_id']}_FRONT.png",
                back_image=f"/output/{row['employee_id']}_BACK.png",
            ))
        
        return TeacherSearchResponse(
            results=results,
            query=q,
            total=len(results),
        )
    
    except QueryError as e:
        logger.error(f"Failed to search teachers: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/{employee_id}", response_model=TeacherResponse)
def get_teacher(employee_id: str):
    """Get a specific teacher by employee ID."""
    try:
        query = """
            SELECT employee_id, full_name, department, position, specialization,
                   contact_number, emergency_contact_name, emergency_contact_number,
                   address, birth_date, blood_type, hire_date, employment_status,
                   photo_path, created_at, updated_at
            FROM teachers
            WHERE employee_id = %s
        """
        
        row = db_manager.execute_query(query, (employee_id,), fetch_one=True)
        
        if not row:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        return TeacherResponse(
            employee_id=row['employee_id'],
            full_name=row['full_name'],
            department=row.get('department') or '',
            position=row.get('position') or '',
            specialization=row.get('specialization') or '',
            contact_number=row.get('contact_number') or '',
            emergency_contact_name=row.get('emergency_contact_name') or '',
            emergency_contact_number=row.get('emergency_contact_number') or '',
            address=row.get('address') or '',
            birth_date=row.get('birth_date'),
            blood_type=row.get('blood_type') or '',
            hire_date=row.get('hire_date'),
            employment_status=row.get('employment_status') or 'active',
            photo_path=row.get('photo_path'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            front_image=f"/output/{row['employee_id']}_FRONT.png",
            back_image=f"/output/{row['employee_id']}_BACK.png",
        )
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to get teacher {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve teacher")


@router.post("", response_model=TeacherResponse)
def create_teacher(teacher: TeacherCreateRequest):
    """Create a new teacher."""
    try:
        # Check if employee_id already exists
        check_query = "SELECT employee_id FROM teachers WHERE employee_id = %s"
        existing = db_manager.execute_query(check_query, (teacher.employee_id,), fetch_one=True)
        
        if existing:
            raise HTTPException(status_code=409, detail="Employee ID already exists")
        
        insert_query = """
            INSERT INTO teachers (
                employee_id, full_name, department, position, specialization,
                contact_number, emergency_contact_name, emergency_contact_number,
                address, birth_date, blood_type, hire_date, employment_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            teacher.employee_id,
            teacher.full_name,
            teacher.department,
            teacher.position,
            teacher.specialization,
            teacher.contact_number,
            teacher.emergency_contact_name,
            teacher.emergency_contact_number,
            teacher.address,
            teacher.birth_date,
            teacher.blood_type,
            teacher.hire_date,
            teacher.employment_status,
        )
        
        db_manager.execute_query(insert_query, params, fetch_all=False)
        
        return get_teacher(teacher.employee_id)
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to create teacher: {e}")
        raise HTTPException(status_code=500, detail="Failed to create teacher")


@router.put("/{employee_id}", response_model=TeacherResponse)
def update_teacher(employee_id: str, updates: TeacherUpdateRequest):
    """Update an existing teacher."""
    try:
        # Check exists
        get_teacher(employee_id)
        
        update_dict = updates.get_update_dict()
        if not update_dict:
            return get_teacher(employee_id)
        
        # Build update query
        update_fields = []
        params = []
        
        field_mapping = {
            'full_name': 'full_name',
            'department': 'department',
            'position': 'position',
            'specialization': 'specialization',
            'contact_number': 'contact_number',
            'emergency_contact_name': 'emergency_contact_name',
            'emergency_contact_number': 'emergency_contact_number',
            'address': 'address',
            'birth_date': 'birth_date',
            'blood_type': 'blood_type',
            'hire_date': 'hire_date',
            'employment_status': 'employment_status',
        }
        
        for key, col in field_mapping.items():
            if key in update_dict:
                update_fields.append(f"{col} = %s")
                params.append(update_dict[key])
        
        if not update_fields:
            return get_teacher(employee_id)
        
        params.append(employee_id)
        update_query = f"""
            UPDATE teachers 
            SET {', '.join(update_fields)}
            WHERE employee_id = %s
        """
        
        db_manager.execute_query(update_query, tuple(params), fetch_all=False)
        
        return get_teacher(employee_id)
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to update teacher {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update teacher")


@router.delete("/{employee_id}")
def delete_teacher(employee_id: str):
    """Delete a teacher."""
    try:
        # Check exists
        get_teacher(employee_id)
        
        delete_query = "DELETE FROM teachers WHERE employee_id = %s"
        db_manager.execute_query(delete_query, (employee_id,), fetch_all=False)
        
        return {"status": "deleted", "employee_id": employee_id}
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to delete teacher {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete teacher")


# =============================================================================
# GENERATION HISTORY
# =============================================================================

@router.get("/{employee_id}/history")
def get_teacher_history(employee_id: str, limit: int = Query(20, ge=1, le=100)):
    """Get generation history for a teacher."""
    try:
        query = """
            SELECT id, employee_id, full_name, department, position,
                   file_path, status, error_message, processing_time_ms, timestamp
            FROM teacher_generation_history
            WHERE employee_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        rows = db_manager.execute_query(query, (employee_id, limit))
        
        return {
            "employee_id": employee_id,
            "history": rows or [],
            "total": len(rows or []),
        }
    
    except QueryError as e:
        logger.error(f"Failed to get history for teacher {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


# =============================================================================
# IMPORT ENDPOINTS
# =============================================================================

@router.post("/import/preview", summary="Preview CSV import for teachers")
async def preview_teacher_csv_import(file: UploadFile = File(...)):
    """Preview CSV file before importing teachers."""
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
        
        headers = reader.fieldnames or []
        
        required_columns = ['employee_id', 'full_name']
        optional_columns = ['department', 'position', 'specialization', 'contact_number', 'address', 'birth_date', 'blood_type']
        
        missing_columns = [col for col in required_columns if col not in headers]
        
        preview_data = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            preview_data.append(row)
        
        csv_file.seek(0)
        total_rows = sum(1 for _ in csv.DictReader(csv_file))
        
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
        
    except Exception as e:
        logger.error(f"Teacher CSV preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}"
        )


@router.post("/import", summary="Import teachers from CSV")
async def import_teachers_csv(file: UploadFile = File(...)):
    """Import teacher records from CSV file."""
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
        
        for i, row in enumerate(reader, start=2):
            try:
                if not row.get('employee_id') or not row.get('full_name'):
                    errors.append({"row": i, "error": "Missing employee_id or full_name"})
                    continue
                
                teacher_data = TeacherCreateRequest(
                    employee_id=row['employee_id'].strip(),
                    full_name=row['full_name'].strip(),
                    department=row.get('department', '').strip(),
                    position=row.get('position', '').strip(),
                    specialization=row.get('specialization', '').strip(),
                    contact_number=row.get('contact_number', '').strip(),
                    address=row.get('address', '').strip(),
                    birth_date=row.get('birth_date', '').strip() or None,
                    blood_type=row.get('blood_type', '').strip() or None,
                )
                
                try:
                    create_teacher(teacher_data)
                    imported += 1
                except Exception as create_error:
                    if "already exists" in str(create_error).lower():
                        update_data = TeacherUpdateRequest(
                            full_name=row['full_name'].strip(),
                            department=row.get('department', '').strip(),
                            position=row.get('position', '').strip(),
                            specialization=row.get('specialization', '').strip(),
                            contact_number=row.get('contact_number', '').strip(),
                            address=row.get('address', '').strip(),
                            birth_date=row.get('birth_date', '').strip() or None,
                            blood_type=row.get('blood_type', '').strip() or None,
                        )
                        update_teacher(row['employee_id'].strip(), update_data)
                        imported += 1
                    else:
                        raise
                        
            except Exception as e:
                errors.append({"row": i, "data": row, "error": str(e)})
        
        total_rows = sum(1 for _ in csv.DictReader(io.StringIO(content_str)))
        
        return {
            "status": "success" if not errors else "partial",
            "imported": imported,
            "total": total_rows,
            "errors": errors[:10],
            "error_count": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Teacher CSV import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

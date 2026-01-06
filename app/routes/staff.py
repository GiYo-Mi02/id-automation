"""
Staff API Routes
CRUD operations for staff members
"""

import io
import csv
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, status
from typing import Optional
import math

from ..models.staff import (
    StaffCreateRequest,
    StaffUpdateRequest,
    StaffResponse,
    StaffListResponse,
    StaffSearchResponse,
    StaffHistoryResponse,
    StaffHistoryItem
)
from ..database import get_db_connection
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/staff", tags=["Staff"])


@router.get("", response_model=StaffListResponse)
async def list_staff(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    department: Optional[str] = None
):
    """List all staff with pagination"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Build query
        where_clause = ""
        params = []
        if department:
            where_clause = "WHERE department = %s"
            params.append(department)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as total FROM staff {where_clause}", params)
        total = cursor.fetchone()['total']
        
        # Get paginated results
        offset = (page - 1) * per_page
        cursor.execute(f"""
            SELECT * FROM staff {where_clause}
            ORDER BY full_name ASC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        items = cursor.fetchall()
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return StaffListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/search", response_model=StaffSearchResponse)
async def search_staff(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search staff by name, ID, or department"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        search_term = f"%{q}%"
        
        cursor.execute("""
            SELECT * FROM staff
            WHERE full_name LIKE %s 
               OR id_number LIKE %s 
               OR employee_id LIKE %s
               OR department LIKE %s
               OR position LIKE %s
            ORDER BY full_name ASC
            LIMIT %s
        """, [search_term, search_term, search_term, search_term, search_term, limit])
        
        results = cursor.fetchall()
        
        return StaffSearchResponse(
            results=results,
            query=q,
            count=len(results)
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/{id_number}", response_model=StaffResponse)
async def get_staff(id_number: str):
    """Get a single staff member by ID number"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM staff WHERE id_number = %s", [id_number])
        staff = cursor.fetchone()
        
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        return staff
    finally:
        cursor.close()
        conn.close()


@router.post("/", response_model=StaffResponse)
async def create_staff(staff: StaffCreateRequest):
    """Create a new staff member"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check for duplicate
        cursor.execute(
            "SELECT id FROM staff WHERE id_number = %s OR employee_id = %s",
            [staff.id_number, staff.employee_id]
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Staff with this ID already exists")
        
        # Insert
        cursor.execute("""
            INSERT INTO staff (id_number, employee_id, full_name, department, position,
                              contact_number, emergency_contact_name, emergency_contact_number,
                              address, birth_date, blood_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            staff.id_number, staff.employee_id, staff.full_name, staff.department,
            staff.position, staff.contact_number, staff.emergency_contact_name,
            staff.emergency_contact_number, staff.address, staff.birth_date, staff.blood_type
        ])
        
        conn.commit()
        
        # Fetch created record
        cursor.execute("SELECT * FROM staff WHERE id_number = %s", [staff.id_number])
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


@router.put("/{id_number}", response_model=StaffResponse)
async def update_staff(id_number: str, updates: StaffUpdateRequest):
    """Update a staff member"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check exists
        cursor.execute("SELECT id FROM staff WHERE id_number = %s", [id_number])
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Staff not found")
        
        # Build update query
        update_fields = []
        values = []
        update_data = updates.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if update_fields:
            values.append(id_number)
            cursor.execute(f"""
                UPDATE staff SET {', '.join(update_fields)}
                WHERE id_number = %s
            """, values)
            conn.commit()
        
        # Fetch updated record
        new_id = updates.id_number if updates.id_number else id_number
        cursor.execute("SELECT * FROM staff WHERE id_number = %s", [new_id])
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id_number}")
async def delete_staff(id_number: str):
    """Delete a staff member"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        
        # Check exists
        cursor.execute("SELECT id FROM staff WHERE id_number = %s", [id_number])
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Staff not found")
        
        cursor.execute("DELETE FROM staff WHERE id_number = %s", [id_number])
        conn.commit()
        
        return {"success": True, "message": "Staff deleted successfully"}
    finally:
        cursor.close()
        conn.close()


@router.get("/{id_number}/history", response_model=StaffHistoryResponse)
async def get_staff_history(id_number: str, limit: int = Query(50, ge=1, le=200)):
    """Get ID generation history for a staff member"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM staff_history
            WHERE staff_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, [id_number, limit])
        
        items = cursor.fetchall()
        
        return StaffHistoryResponse(
            items=items,
            total=len(items)
        )
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# IMPORT ENDPOINTS
# =============================================================================

@router.post("/import/preview", summary="Preview CSV import for staff")
async def preview_staff_csv_import(file: UploadFile = File(...)):
    """Preview CSV file before importing staff."""
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
        
        required_columns = ['id_number', 'employee_id', 'full_name']
        optional_columns = ['department', 'position', 'contact_number', 'address', 'birth_date', 'blood_type']
        
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
        logger.error(f"Staff CSV preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}"
        )


@router.post("/import", summary="Import staff from CSV")
async def import_staff_csv(file: UploadFile = File(...)):
    """Import staff records from CSV file."""
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
        
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            cursor = conn.cursor()
            
            for i, row in enumerate(reader, start=2):
                try:
                    if not row.get('id_number') or not row.get('employee_id') or not row.get('full_name'):
                        errors.append({"row": i, "error": "Missing id_number, employee_id, or full_name"})
                        continue
                    
                    # Try to insert
                    cursor.execute("""
                        INSERT INTO staff (id_number, employee_id, full_name, department, position, 
                                          contact_number, address, birth_date, blood_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            full_name = VALUES(full_name),
                            department = VALUES(department),
                            position = VALUES(position),
                            contact_number = VALUES(contact_number),
                            address = VALUES(address),
                            birth_date = VALUES(birth_date),
                            blood_type = VALUES(blood_type)
                    """, (
                        row['id_number'].strip(),
                        row['employee_id'].strip(),
                        row['full_name'].strip(),
                        row.get('department', '').strip(),
                        row.get('position', '').strip(),
                        row.get('contact_number', '').strip(),
                        row.get('address', '').strip(),
                        row.get('birth_date', '').strip() or None,
                        row.get('blood_type', '').strip() or None,
                    ))
                    imported += 1
                            
                except Exception as e:
                    errors.append({"row": i, "data": row, "error": str(e)})
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
        
        total_rows = sum(1 for _ in csv.DictReader(io.StringIO(content_str)))
        
        return {
            "status": "success" if not errors else "partial",
            "imported": imported,
            "total": total_rows,
            "errors": errors[:10],
            "error_count": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Staff CSV import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

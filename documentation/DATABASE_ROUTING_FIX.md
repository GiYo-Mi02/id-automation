# Database Query Routing Bug Fix

## Date: January 6, 2025

## Summary
Fixed critical bug where employee IDs were queried against the students table, causing all employee ID cards to display "UNKNOWN" when JSON sidecar files were missing.

---

## Root Cause Analysis

### The Bug
When processing employee photos (e.g., `EMP-2024-002.jpg`), the system's database fallback logic unconditionally queried the `students` table:

```python
# OLD CODE (BROKEN)
student = database.get_student(student_id)  # Always queries students table!
```

**Problem:**
- Employee IDs like `EMP-2024-002` were queried: `SELECT * FROM students WHERE id_number = 'EMP-2024-002'`
- Query returned `NULL` (employee not in students table)
- System created blank fallback object with student fields: `{'name': 'UNKNOWN', 'lrn': '', 'grade_level': '', 'section': ''}`
- Rendered ID card displayed "UNKNOWN" with student-specific fields instead of employee data

### Why It Went Unnoticed
The system worked correctly when JSON sidecar files existed (e.g., `EMP-2024-002.json`), masking the database fallback bug. Only when processing photos WITHOUT accompanying JSON files did the issue surface.

---

## Solution Implemented

### 1. Added `get_teacher()` Function
**File:** `app/database.py`

```python
def get_teacher(employee_id):
    """Query teachers table by employee_id."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE employee_id = %s", (employee_id,))
    teacher = cursor.fetchone()
    conn.close()
    return teacher
```

### 2. Added ID Prefix Detection & Routing
**File:** `app/school_id_processor.py` (Lines 145-210)

```python
# Detect entity type from ID prefix
is_employee = (
    student_id.upper().startswith('EMP-') or 
    student_id.upper().startswith('TCH-') or 
    student_id.upper().startswith('T-') or 
    student_id.upper().startswith('STF-')
)

if is_employee:
    # Query teachers table
    employee = database.get_teacher(student_id)
    
    if not employee:
        # Return blank employee object
        return {
            'id': student_id, 'name': 'UNKNOWN',
            'employee_id': student_id,
            'position': '', 'department': '',
            'type': 'teacher'
        }
    
    # Map employee database fields to template format
    return {
        'id': str(employee['employee_id']),
        'name': str(employee['full_name']).upper(),
        'position': str(employee.get('position', '') or '').upper(),
        'department': str(employee.get('department', '') or '').upper(),
        'employee_id': str(employee['employee_id']),
        'type': 'teacher',
        # ... more fields
    }
else:
    # Query students table (original logic)
    student = database.get_student(student_id)
    # ... student mapping
```

---

## ID Prefix Detection Logic

The system now correctly identifies entity type based on ID prefix:

| ID Format       | Example         | Detected As | Table Queried |
|-----------------|-----------------|-------------|---------------|
| `EMP-*`         | `EMP-2024-002`  | Employee    | `teachers`    |
| `TCH-*`         | `TCH-2024-001`  | Employee    | `teachers`    |
| `T-*`           | `T-001`         | Employee    | `teachers`    |
| `STF-*`         | `STF-2024-005`  | Employee    | `teachers`    |
| Numeric         | `123456789`     | Student     | `students`    |
| Other           | `2024-106`      | Student     | `students`    |

---

## Testing & Verification

### Test Scripts Created
1. **`test_db_routing.py`** - Tests database query functions and ID detection logic
2. **`test_employee_e2e.py`** - End-to-end test simulating employee photo processing

### Test Results
```
✅ get_teacher() function created and working
✅ Employee query returns correct data: JUAN DELA CRUZ
✅ ID prefix detection correctly routes all formats
✅ Field mapping includes position, department, employee_id
✅ Critical fields verified: name='JUAN DELA CRUZ', position='SENIOR TEACHER'
```

**Database Query Confirmed:**
```
Input: EMP-2024-002.jpg (no JSON file)
Detection: Prefix 'EMP-' → Route to teachers table
Query: SELECT * FROM teachers WHERE employee_id = 'EMP-2024-002'
Result: Found employee record
Output: name='JUAN DELA CRUZ', position='SENIOR TEACHER', department='MATHEMATICS DEPARTMENT'
```

---

## Before vs After Comparison

### 🔴 BEFORE (Bug)
```
Input:  EMP-2024-002.jpg
Query:  SELECT * FROM students WHERE id_number = 'EMP-2024-002'
Result: NULL (not found in students table)
Output: {'name': 'UNKNOWN', 'lrn': '', 'grade_level': '', 'section': ''}
Card:   Displays "UNKNOWN" with blank student fields
```

### 🟢 AFTER (Fixed)
```
Input:  EMP-2024-002.jpg
Query:  SELECT * FROM teachers WHERE employee_id = 'EMP-2024-002'
Result: Found employee: JUAN DELA CRUZ
Output: {'name': 'JUAN DELA CRUZ', 'position': 'SENIOR TEACHER', 'department': 'MATHEMATICS DEPARTMENT'}
Card:   Displays actual employee name, position, and department
```

---

## Database Schema Reference

### Teachers Table (from SCHEMA_UPDATE_v2.sql)
```sql
CREATE TABLE IF NOT EXISTS teachers (
    employee_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    specialization VARCHAR(150),
    contact_number VARCHAR(50),
    emergency_contact_name VARCHAR(100),
    emergency_contact_number VARCHAR(50),
    address VARCHAR(255),
    birth_date DATE,
    blood_type VARCHAR(10),
    hire_date DATE,
    employment_status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## Impact Assessment

### Fixed Issues
- ✅ Employee IDs no longer display "UNKNOWN"
- ✅ Correct table queried based on ID format
- ✅ Employee-specific fields (position, department) now populated
- ✅ Database fallback works for both students and employees
- ✅ System maintains backward compatibility with JSON sidecar files

### Affected Components
- `app/database.py` - Added `get_teacher()` function
- `app/school_id_processor.py` - Enhanced `get_student_data()` with routing logic

### No Breaking Changes
- Student ID processing unchanged
- JSON sidecar file processing unchanged
- Template rendering unchanged
- API endpoints unchanged

---

## Verification Steps for Production

1. **Test with Employee Photo (No JSON):**
   ```powershell
   # Place employee photo in data/input/
   Copy-Item "EMP-2024-002.jpg" "data/input/"
   
   # Run processing
   python run.py
   
   # Verify output shows employee data
   ```

2. **Test with Student Photo (No JSON):**
   ```powershell
   # Ensure student exists in database
   # Process student photo
   # Verify output shows student data
   ```

3. **Test with JSON Sidecar:**
   ```powershell
   # Ensure both photo and JSON exist
   # Process with JSON
   # Verify JSON data takes precedence
   ```

---

## Related Files

- `app/database.py` - Database query helper functions
- `app/school_id_processor.py` - Photo processing and data loading
- `app/models/teacher.py` - Teacher Pydantic models
- `data/database/SCHEMA_UPDATE_v2.sql` - Database schema definition
- `test_db_routing.py` - Database routing test script
- `test_employee_e2e.py` - End-to-end employee test script

---

## Technical Notes

### Why This Bug Was Critical
This bug blocked all employee ID card generation when:
- Employee photos were processed WITHOUT JSON sidecar files
- System relied on database fallback for employee data
- Common scenario in batch processing or direct photo uploads

### Design Decision: Single `get_teacher()` Function
Currently, all employees are stored in the `teachers` table regardless of role. If future requirements separate staff into a different table, add:

```python
def get_staff(employee_id):
    """Query staff table by employee_id."""
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM staff WHERE employee_id = %s", (employee_id,))
    staff = cursor.fetchone()
    conn.close()
    return staff
```

Then update routing logic to try both tables:
```python
if is_employee:
    employee = database.get_teacher(student_id)
    if not employee:
        employee = database.get_staff(student_id)
```

---

## Conclusion

The database query routing bug has been successfully fixed. The system now correctly:

1. **Detects entity type** from ID prefix
2. **Routes to correct table** (teachers vs students)
3. **Maps appropriate fields** (position/department vs lrn/grade_level)
4. **Maintains backward compatibility** with existing workflows

Employee ID cards will now display actual employee data instead of "UNKNOWN" when processed through database fallback.

---

**Status:** ✅ **RESOLVED**  
**Priority:** CRITICAL  
**Complexity:** Medium  
**Testing:** Verified via unit tests and end-to-end tests

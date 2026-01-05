"""
Student Models (Pydantic)
=========================
Type-safe request/response models for student operations.

Fixes Applied:
- [P0] Input validation (no more trusting raw dict keys)
- [P0] String sanitization on all fields
- [P1] Single source of truth for student schema
"""

import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =============================================================================
# BASE VALIDATORS
# =============================================================================

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input."""
    if not value:
        return ""
    # Remove null bytes and normalize whitespace
    value = value.replace("\x00", "")
    value = " ".join(value.split())
    return value.strip()[:max_length]


def validate_student_id_format(value: str) -> str:
    """Validate student ID format."""
    if not value:
        raise ValueError("Student ID is required")
    
    value = sanitize_string(value, max_length=50)
    
    # Allow formats: YYYY-NNN or numeric
    if not re.match(r"^(\d{4}-\d{1,4}|\d{6,12})$", value):
        raise ValueError(f"Invalid student ID format: '{value}'")
    
    return value


# =============================================================================
# REQUEST MODELS (Input validation)
# =============================================================================

class StudentCreateRequest(BaseModel):
    """Request model for creating a new student."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id_number: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    full_name: str = Field(..., min_length=1, max_length=100, description="Student's full name")
    lrn: Optional[str] = Field(default="", max_length=50, description="Learner Reference Number")
    grade_level: Optional[str] = Field(default="", max_length=20, description="Grade level (e.g., 'Grade 7')")
    section: Optional[str] = Field(default="", max_length=50, description="Class section")
    guardian_name: Optional[str] = Field(default="", max_length=100, description="Guardian's name")
    address: Optional[str] = Field(default="", max_length=255, description="Home address")
    guardian_contact: Optional[str] = Field(default="", max_length=50, description="Guardian's contact number")
    
    @field_validator("id_number")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return validate_student_id_format(v)
    
    @field_validator("full_name", "guardian_name", "section", "address")
    @classmethod
    def sanitize_names(cls, v: str) -> str:
        return sanitize_string(v).upper() if v else ""
    
    @field_validator("lrn", "guardian_contact")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return sanitize_string(v) if v else ""
    
    @field_validator("grade_level")
    @classmethod
    def sanitize_grade(cls, v: str) -> str:
        return sanitize_string(v).upper() if v else ""


class StudentUpdateRequest(BaseModel):
    """
    Request model for updating an existing student.
    
    All fields optional - only provided fields will be updated.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    full_name: Optional[str] = Field(default=None, max_length=100)
    lrn: Optional[str] = Field(default=None, max_length=50)
    grade_level: Optional[str] = Field(default=None, max_length=20)
    section: Optional[str] = Field(default=None, max_length=50)
    guardian_name: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    guardian_contact: Optional[str] = Field(default=None, max_length=50)
    
    @field_validator("full_name", "guardian_name", "section", "address")
    @classmethod
    def sanitize_names(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_string(v).upper() if v else v
    
    @field_validator("lrn", "guardian_contact")
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_string(v) if v else v
    
    @field_validator("grade_level")
    @classmethod
    def sanitize_grade(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_string(v).upper() if v else v
    
    def get_update_dict(self) -> dict:
        """Return only fields that were explicitly set (not None)."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class StudentSearchRequest(BaseModel):
    """Request model for student search."""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    
    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return sanitize_string(v, max_length=100)


# =============================================================================
# RESPONSE MODELS (Output serialization)
# =============================================================================

class StudentResponse(BaseModel):
    """Response model for a single student."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id_number: str
    full_name: str
    lrn: str = ""
    grade_level: str = ""
    section: str = ""
    guardian_name: str = ""
    address: str = ""
    guardian_contact: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Optional image URLs (computed if files exist)
    front_image: Optional[str] = None
    back_image: Optional[str] = None


class StudentListResponse(BaseModel):
    """Response model for student list with pagination info."""
    
    students: List[StudentResponse]
    total: int
    page: int = 1
    page_size: int = 50


class StudentSearchResponse(BaseModel):
    """Response model for search results."""
    
    results: List[StudentResponse]
    query: str
    total: int


# =============================================================================
# GENERATION HISTORY MODELS
# =============================================================================

class GenerationHistoryResponse(BaseModel):
    """Response model for generation history entry."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    student_id: str
    full_name: str = ""
    section: str = ""
    lrn: str = ""
    guardian_name: str = ""
    address: str = ""
    guardian_contact: str = ""
    file_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    # Computed URLs for frontend compatibility
    front_image: Optional[str] = None
    back_image: Optional[str] = None
    
    @classmethod
    def from_db_row(cls, row: dict) -> "GenerationHistoryResponse":
        """Create from database row with URL generation. Handles NULL values."""
        student_id = row.get("student_id") or ""
        return cls(
            id=row.get("id", 0),
            student_id=student_id,
            full_name=row.get("full_name") or "",
            section=row.get("section") or "",
            lrn=row.get("lrn") or "",
            guardian_name=row.get("guardian_name") or "",
            address=row.get("address") or "",
            guardian_contact=row.get("guardian_contact") or "",
            file_path=row.get("file_path"),
            timestamp=row.get("timestamp"),
            front_image=f"/output/{student_id}_FRONT.png" if student_id else None,
            back_image=f"/output/{student_id}_BACK.png" if student_id else None,
        )


class HistoryListResponse(BaseModel):
    """Response model for history list."""
    
    history: List[GenerationHistoryResponse]
    total: int
    limit: int


# =============================================================================
# IMPORT/EXPORT MODELS
# =============================================================================

class ImportPreviewResponse(BaseModel):
    """Response model for import preview."""
    
    total_rows: int
    headers: List[str]
    required_columns: List[str]
    missing_columns: List[str]
    preview_data: List[dict]
    valid: bool


class ImportResultResponse(BaseModel):
    """Response model for import result."""
    
    status: str
    imported: int
    total: int
    errors: List[dict] = []


# =============================================================================
# CAPTURE MODELS
# =============================================================================

class CaptureRequest(BaseModel):
    """Request model for photo capture with manual data."""
    
    student_id: str = Field(..., min_length=1, max_length=50)
    
    # Optional manual data (for walk-in students)
    manual_name: Optional[str] = Field(default=None, max_length=100)
    manual_grade: Optional[str] = Field(default=None, max_length=20)
    manual_section: Optional[str] = Field(default=None, max_length=50)
    manual_guardian: Optional[str] = Field(default=None, max_length=100)
    manual_address: Optional[str] = Field(default=None, max_length=255)
    manual_contact: Optional[str] = Field(default=None, max_length=50)
    
    @field_validator("student_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return validate_student_id_format(v)


class CaptureResponse(BaseModel):
    """Response model for capture result."""
    
    status: str
    path: Optional[str] = None
    student_id: str
    message: Optional[str] = None

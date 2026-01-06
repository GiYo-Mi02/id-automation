"""
Teacher Models (Pydantic)
=========================
Type-safe request/response models for teacher operations.
"""

import re
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict


# =============================================================================
# VALIDATORS (reuse from student module)
# =============================================================================

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input."""
    if not value:
        return ""
    value = value.replace("\x00", "")
    value = " ".join(value.split())
    return value.strip()[:max_length]


def validate_employee_id_format(value: str) -> str:
    """Validate employee ID format."""
    if not value:
        raise ValueError("Employee ID is required")
    
    value = sanitize_string(value, max_length=50)
    
    # Allow formats: alphanumeric with optional dashes
    if not re.match(r"^[A-Za-z0-9\-]{3,50}$", value):
        raise ValueError(f"Invalid employee ID format: '{value}'")
    
    return value


# =============================================================================
# REQUEST MODELS
# =============================================================================

class TeacherCreateRequest(BaseModel):
    """Request model for creating a new teacher."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    employee_id: str = Field(..., min_length=1, max_length=50, description="Unique employee identifier")
    full_name: str = Field(..., min_length=1, max_length=100, description="Teacher's full name")
    department: Optional[str] = Field(default="", max_length=100, description="Department name")
    position: Optional[str] = Field(default="", max_length=100, description="Position/Title")
    specialization: Optional[str] = Field(default="", max_length=150, description="Area of specialization")
    contact_number: Optional[str] = Field(default="", max_length=50, description="Contact number")
    emergency_contact_name: Optional[str] = Field(default="", max_length=100, description="Emergency contact name")
    emergency_contact_number: Optional[str] = Field(default="", max_length=50, description="Emergency contact number")
    address: Optional[str] = Field(default="", max_length=255, description="Home address")
    birth_date: Optional[date] = Field(default=None, description="Date of birth")
    blood_type: Optional[str] = Field(default="", max_length=10, description="Blood type")
    hire_date: Optional[date] = Field(default=None, description="Date of hire")
    employment_status: Optional[str] = Field(default="active", description="Employment status")
    
    @field_validator("employee_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return validate_employee_id_format(v)
    
    @field_validator("full_name", "department", "position", "emergency_contact_name")
    @classmethod
    def sanitize_names(cls, v: str) -> str:
        return sanitize_string(v).upper() if v else ""
    
    @field_validator("address", "specialization")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        return sanitize_string(v) if v else ""
    
    @field_validator("contact_number", "emergency_contact_number")
    @classmethod
    def sanitize_contacts(cls, v: str) -> str:
        return sanitize_string(v) if v else ""


class TeacherUpdateRequest(BaseModel):
    """Request model for updating an existing teacher."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    full_name: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    specialization: Optional[str] = Field(default=None, max_length=150)
    contact_number: Optional[str] = Field(default=None, max_length=50)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_number: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=255)
    birth_date: Optional[date] = Field(default=None)
    blood_type: Optional[str] = Field(default=None, max_length=10)
    hire_date: Optional[date] = Field(default=None)
    employment_status: Optional[str] = Field(default=None)
    
    @field_validator("full_name", "department", "position", "emergency_contact_name")
    @classmethod
    def sanitize_names(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_string(v).upper() if v else v
    
    @field_validator("address", "specialization")
    @classmethod
    def sanitize_text(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_string(v) if v else v
    
    def get_update_dict(self) -> dict:
        """Return only fields that were explicitly set (not None)."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class TeacherSearchRequest(BaseModel):
    """Request model for teacher search."""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    
    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return sanitize_string(v, max_length=100)


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class TeacherResponse(BaseModel):
    """Response model for a single teacher."""
    
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: str
    full_name: str
    department: str = ""
    position: str = ""
    specialization: str = ""
    contact_number: str = ""
    emergency_contact_name: str = ""
    emergency_contact_number: str = ""
    address: str = ""
    birth_date: Optional[date] = None
    blood_type: str = ""
    hire_date: Optional[date] = None
    employment_status: str = "active"
    photo_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Computed image URLs
    front_image: Optional[str] = None
    back_image: Optional[str] = None


class TeacherListResponse(BaseModel):
    """Response model for teacher list with pagination info."""
    
    teachers: List[TeacherResponse]
    total: int
    page: int = 1
    page_size: int = 50


class TeacherSearchResponse(BaseModel):
    """Response model for search results."""
    
    results: List[TeacherResponse]
    query: str
    total: int


# =============================================================================
# GENERATION HISTORY MODELS
# =============================================================================

class TeacherGenerationHistoryResponse(BaseModel):
    """Response model for teacher generation history entry."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: str
    full_name: str = ""
    department: str = ""
    position: str = ""
    file_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    front_image: Optional[str] = None
    back_image: Optional[str] = None
    
    @classmethod
    def from_db_row(cls, row: dict) -> "TeacherGenerationHistoryResponse":
        """Create from database row with URL generation."""
        employee_id = row.get("employee_id") or ""
        return cls(
            id=row.get("id", 0),
            employee_id=employee_id,
            full_name=row.get("full_name") or "",
            department=row.get("department") or "",
            position=row.get("position") or "",
            file_path=row.get("file_path"),
            timestamp=row.get("timestamp"),
            front_image=f"/output/{employee_id}_FRONT.png" if employee_id else None,
            back_image=f"/output/{employee_id}_BACK.png" if employee_id else None,
        )

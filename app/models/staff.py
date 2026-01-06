"""
Staff Pydantic Models
Handles CRUD operations for staff members
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class StaffBase(BaseModel):
    """Base staff fields"""
    id_number: str = Field(..., min_length=1, max_length=50)
    employee_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=200)
    department: Optional[str] = None
    position: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    blood_type: Optional[str] = None


class StaffCreateRequest(StaffBase):
    """Request model for creating staff"""
    pass


class StaffUpdateRequest(BaseModel):
    """Request model for updating staff (all fields optional)"""
    id_number: Optional[str] = None
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    blood_type: Optional[str] = None


class StaffResponse(StaffBase):
    """Response model for staff"""
    id: int
    photo_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StaffListResponse(BaseModel):
    """Paginated list of staff"""
    items: List[StaffResponse]
    total: int
    page: int
    per_page: int
    pages: int


class StaffSearchResponse(BaseModel):
    """Search results for staff"""
    results: List[StaffResponse]
    query: str
    count: int


class StaffHistoryItem(BaseModel):
    """Single staff generation history entry"""
    id: int
    staff_id: str
    full_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    file_path: Optional[str] = None
    template_id: Optional[int] = None
    status: str = "success"
    timestamp: datetime


class StaffHistoryResponse(BaseModel):
    """Staff generation history response"""
    items: List[StaffHistoryItem]
    total: int

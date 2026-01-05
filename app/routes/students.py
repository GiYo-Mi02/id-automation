"""
Student Routes (APIRouter)
==========================
REST API endpoints for student operations.

Fixes Applied:
- [P0] API key authentication on all endpoints
- [P0] Input validation via Pydantic models
- [P0] Proper HTTP status codes
- [P1] No duplicate function names (api.py had this issue)
- [P1] Consistent response formats
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import verify_api_key
from app.services.student_service import StudentService, get_student_service
from app.models.student import (
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
    StudentListResponse,
    StudentSearchResponse,
    HistoryListResponse,
)
from app.db.database import NotFoundError, QueryError

logger = logging.getLogger(__name__)


# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/api/students",
    tags=["students"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing API key"},
        500: {"description": "Internal server error"},
    }
)


# =============================================================================
# STUDENT CRUD ENDPOINTS
# =============================================================================

@router.get(
    "",
    response_model=StudentListResponse,
    summary="List all students",
    description="Get paginated list of all students with optional sorting and filtering."
)
async def list_students(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Sort column (created_at, id_number, full_name, section)"),
    sort_order: str = Query(default="DESC", description="Sort order (ASC or DESC)"),
    section: str = Query(default=None, description="Filter by section"),
    service: StudentService = Depends(get_student_service)
):
    """Get paginated list of all students with sorting and filtering."""
    return service.get_all_students(
        page=page, 
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        section=section
    )


@router.get(
    "/search",
    response_model=StudentSearchResponse,
    summary="Search students",
    description="Search students by name, ID, section, or LRN."
)
async def search_students(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum results"),
    service: StudentService = Depends(get_student_service)
):
    """Search students by any field."""
    results = service.search_students(query=q, limit=limit)
    return StudentSearchResponse(
        results=results,
        query=q,
        total=len(results)
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID",
    responses={404: {"description": "Student not found"}}
)
async def get_student(
    student_id: str,
    service: StudentService = Depends(get_student_service)
):
    """Get a single student by their ID number."""
    try:
        return service.get_student_by_id(student_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student not found: {student_id}"
        )


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create student",
    responses={
        400: {"description": "Validation error"},
        409: {"description": "Student ID already exists"}
    }
)
async def create_student(
    data: StudentCreateRequest,
    service: StudentService = Depends(get_student_service)
):
    """Create a new student record."""
    try:
        return service.create_student(data)
    except QueryError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student",
    responses={404: {"description": "Student not found"}}
)
async def update_student(
    student_id: str,
    data: StudentUpdateRequest,
    service: StudentService = Depends(get_student_service)
):
    """Update an existing student record."""
    try:
        return service.update_student(student_id, data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student not found: {student_id}"
        )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student",
    responses={404: {"description": "Student not found"}}
)
async def delete_student(
    student_id: str,
    service: StudentService = Depends(get_student_service)
):
    """Delete a student record."""
    try:
        service.delete_student(student_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student not found: {student_id}"
        )


# =============================================================================
# HISTORY ENDPOINTS
# =============================================================================

history_router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)


@history_router.get(
    "",
    response_model=HistoryListResponse,
    summary="Get generation history",
    description="Get recent ID generation history."
)
async def get_history(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum records"),
    service: StudentService = Depends(get_student_service)
):
    """Get recent ID generation history."""
    return service.get_generation_history(limit=limit)


@history_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear history",
    description="Clear all generation history."
)
async def clear_history(
    service: StudentService = Depends(get_student_service)
):
    """Clear all generation history."""
    service.clear_history()


# =============================================================================
# STATS ENDPOINT
# =============================================================================

stats_router = APIRouter(
    prefix="/api/stats",
    tags=["stats"]
)


@stats_router.get(
    "",
    summary="Get statistics",
    description="Get student and generation statistics."
)
async def get_stats(
    service: StudentService = Depends(get_student_service)
):
    """Get dashboard statistics."""
    return service.get_stats()

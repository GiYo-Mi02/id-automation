"""
Template API Routes
===================
CRUD operations for ID templates with database persistence.
"""

import json
import logging
from typing import Optional, List
from pathlib import Path
import uuid
from fastapi import APIRouter, HTTPException, Body, Query, UploadFile, File, Form
from pydantic import BaseModel

from app.db.database import db_manager, QueryError, NotFoundError
from app.models.template import (
    IDTemplateCreate,
    IDTemplateUpdate,
    IDTemplateResponse,
    TemplateListResponse,
    get_fields_for_template_type,
    STUDENT_FIELDS,
    TEACHER_FIELDS,
    SCHOOL_FIELDS,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates/db", tags=["templates"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def template_from_row(row: dict) -> IDTemplateResponse:
    """Convert database row to response model."""
    return IDTemplateResponse.from_db_row(row)


# =============================================================================
# CRUD ENDPOINTS
# =============================================================================

@router.get("", response_model=TemplateListResponse)
def list_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type (student/teacher)"),
    school_level: Optional[str] = Query(None, description="Filter by school level"),
    active_only: bool = Query(False, description="Only return active templates"),
):
    """List all templates with optional filters."""
    try:
        query = """
            SELECT id, name, template_type, school_level, is_active,
                   canvas, front_layers, back_layers, created_at, updated_at
            FROM id_templates
            WHERE 1=1
        """
        params = []
        
        if template_type:
            query += " AND template_type = %s"
            params.append(template_type)
        
        if school_level:
            query += " AND school_level = %s"
            params.append(school_level)
        
        if active_only:
            query += " AND is_active = TRUE"
        
        query += " ORDER BY updated_at DESC"
        
        rows = db_manager.execute_query(query, tuple(params) if params else None)
        templates = [template_from_row(row) for row in (rows or [])]
        
        return TemplateListResponse(templates=templates, total=len(templates))
    
    except QueryError as e:
        logger.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")


@router.get("/active/{template_type}")
def get_active_template(template_type: str, school_level: Optional[str] = None):
    """Get the active template for a specific type."""
    try:
        query = """
            SELECT id, name, template_type, school_level, is_active,
                   canvas, front_layers, back_layers, created_at, updated_at
            FROM id_templates
            WHERE template_type = %s AND is_active = TRUE
        """
        params = [template_type]
        
        if school_level:
            query += " AND school_level = %s"
            params.append(school_level)
        
        query += " LIMIT 1"
        
        row = db_manager.execute_query(query, tuple(params), fetch_one=True)
        
        if not row:
            raise HTTPException(status_code=404, detail=f"No active {template_type} template found")
        
        return template_from_row(row)
    
    except QueryError as e:
        logger.error(f"Failed to get active template: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")


@router.get("/{template_id}", response_model=IDTemplateResponse)
def get_template(template_id: int):
    """Get a specific template by ID."""
    try:
        query = """
            SELECT id, name, template_type, school_level, is_active,
                   canvas, front_layers, back_layers, created_at, updated_at
            FROM id_templates
            WHERE id = %s
        """
        row = db_manager.execute_query(query, (template_id,), fetch_one=True)
        
        if not row:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return template_from_row(row)
    
    except QueryError as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")


@router.post("", response_model=IDTemplateResponse)
def create_template(template: IDTemplateCreate):
    """Create a new template."""
    try:
        # If setting as active, deactivate other templates of same type
        if template.isActive:
            deactivate_query = """
                UPDATE id_templates 
                SET is_active = FALSE 
                WHERE template_type = %s AND school_level = %s
            """
            db_manager.execute_query(
                deactivate_query, 
                (template.templateType, template.schoolLevel),
                fetch_all=False
            )
        
        # Serialize layers to JSON (include side-specific background images)
        front_json = json.dumps({
            "backgroundImage": template.front.backgroundImage,
            "layers": template.front.layers
        })
        back_json = json.dumps({
            "backgroundImage": template.back.backgroundImage,
            "layers": template.back.layers
        })
        
        # Serialize canvas to JSON (no backgroundImage - moved to sides)
        canvas_json = json.dumps({
            "width": template.canvas.width,
            "height": template.canvas.height,
            "backgroundColor": template.canvas.backgroundColor,
        })
        
        insert_query = """
            INSERT INTO id_templates (
                name, template_type, school_level, is_active,
                canvas, front_layers, back_layers
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            template.templateName,
            template.templateType,
            template.schoolLevel,
            template.isActive,
            canvas_json,
            front_json,
            back_json,
        )
        
        with db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(insert_query, params)
            template_id = cursor.lastrowid
            cursor.close()
        
        # Fetch and return the created template
        return get_template(template_id)
    
    except QueryError as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.put("/{template_id}", response_model=IDTemplateResponse)
def update_template(template_id: int, updates: IDTemplateUpdate):
    """Update an existing template."""
    try:
        # Check template exists
        existing = get_template(template_id)
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        update_dict = updates.get_update_dict()
        
        if 'templateName' in update_dict:
            update_fields.append("name = %s")
            params.append(update_dict['templateName'])
        
        if 'templateType' in update_dict:
            update_fields.append("template_type = %s")
            params.append(update_dict['templateType'])
        
        if 'schoolLevel' in update_dict:
            update_fields.append("school_level = %s")
            params.append(update_dict['schoolLevel'])
        
        if 'isActive' in update_dict:
            # If activating, deactivate others first
            if update_dict['isActive']:
                t_type = update_dict.get('templateType', existing.templateType)
                s_level = update_dict.get('schoolLevel', existing.schoolLevel)
                deactivate_query = """
                    UPDATE id_templates 
                    SET is_active = FALSE 
                    WHERE template_type = %s AND school_level = %s AND id != %s
                """
                db_manager.execute_query(
                    deactivate_query, 
                    (t_type, s_level, template_id),
                    fetch_all=False
                )
            update_fields.append("is_active = %s")
            params.append(update_dict['isActive'])
        
        if 'canvas' in update_dict and update_dict['canvas']:
            canvas = update_dict['canvas']
            canvas_json = json.dumps(canvas if isinstance(canvas, dict) else {
                "width": canvas.width if hasattr(canvas, 'width') else 800,
                "height": canvas.height if hasattr(canvas, 'height') else 500,
                "backgroundColor": canvas.backgroundColor if hasattr(canvas, 'backgroundColor') else '#ffffff',
            })
            update_fields.append("canvas = %s")
            params.append(canvas_json)
        
        if 'front' in update_dict and update_dict['front']:
            front = update_dict['front']
            if isinstance(front, dict):
                front_json = json.dumps({
                    "backgroundImage": front.get('backgroundImage'),
                    "layers": front.get('layers', [])
                })
            else:
                front_json = json.dumps({
                    "backgroundImage": front.backgroundImage if hasattr(front, 'backgroundImage') else None,
                    "layers": front.layers if hasattr(front, 'layers') else []
                })
            update_fields.append("front_layers = %s")
            params.append(front_json)
        
        if 'back' in update_dict and update_dict['back']:
            back = update_dict['back']
            if isinstance(back, dict):
                back_json = json.dumps({
                    "backgroundImage": back.get('backgroundImage'),
                    "layers": back.get('layers', [])
                })
            else:
                back_json = json.dumps({
                    "backgroundImage": back.backgroundImage if hasattr(back, 'backgroundImage') else None,
                    "layers": back.layers if hasattr(back, 'layers') else []
                })
            update_fields.append("back_layers = %s")
            params.append(back_json)
        
        if not update_fields:
            return existing
        
        params.append(template_id)
        update_query = f"""
            UPDATE id_templates 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        db_manager.execute_query(update_query, tuple(params), fetch_all=False)
        
        return get_template(template_id)
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to update template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")


@router.delete("/{template_id}")
def delete_template(template_id: int):
    """Delete a template."""
    try:
        # Check exists
        get_template(template_id)
        
        delete_query = "DELETE FROM id_templates WHERE id = %s"
        db_manager.execute_query(delete_query, (template_id,), fetch_all=False)
        
        return {"status": "deleted", "id": template_id}
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to delete template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")


@router.post("/{template_id}/activate")
def activate_template(template_id: int):
    """Set a template as the active template for its type."""
    try:
        # First, get the template to verify it exists
        template = get_template(template_id)
        
        # Step 1: Deactivate ALL other templates (global reset)
        # This ensures only ONE template is active across the entire system
        deactivate_all_query = "UPDATE id_templates SET is_active = FALSE"
        db_manager.execute_query(deactivate_all_query, fetch_all=False)
        
        # Step 2: Activate ONLY this template
        activate_query = "UPDATE id_templates SET is_active = TRUE WHERE id = %s"
        db_manager.execute_query(activate_query, (template_id,), fetch_all=False)
        
        # Step 3: Return success with template name
        return {
            "status": "success",
            "message": "Template activated",
            "id": template_id,
            "name": template.templateName,
            "template": template
        }
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to activate template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate template")


class EntityActivationRequest(BaseModel):
    """Request model for entity-specific template activation."""
    entity_types: List[str]  # e.g., ["student", "teacher", "staff"]


@router.post("/{template_id}/activate-for-entity")
def activate_template_for_entity(template_id: int, request: EntityActivationRequest):
    """
    Activate a template for specific entity types.
    
    This allows one template to be active for students but not teachers, etc.
    """
    try:
        template = get_template(template_id)
        valid_entities = {"student", "teacher", "staff"}
        
        # Validate entity types
        for entity in request.entity_types:
            if entity not in valid_entities:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid entity type: {entity}. Valid types: {valid_entities}"
                )
        
        # Build update query for entity-specific activation
        update_fields = []
        params = []
        
        for entity in valid_entities:
            is_active = entity in request.entity_types
            if entity == "student":
                update_fields.append("is_active_for_students = %s")
            elif entity == "teacher":
                update_fields.append("is_active_for_teachers = %s")
            else:
                update_fields.append("is_active_for_staff = %s")
            params.append(is_active)
        
        params.append(template_id)
        
        update_query = f"""
            UPDATE id_templates 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        db_manager.execute_query(update_query, tuple(params), fetch_all=False)
        
        return {
            "status": "updated",
            "id": template_id,
            "active_for": request.entity_types
        }
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to update entity activation for template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template activation")


@router.get("/active-for/{entity_type}")
def get_active_template_for_entity(entity_type: str, school_level: Optional[str] = None):
    """Get the active template for a specific entity type (student/teacher/staff)."""
    try:
        valid_entities = {"student", "teacher", "staff"}
        if entity_type not in valid_entities:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid entity type: {entity_type}. Valid types: {valid_entities}"
            )
        
        # Build column name based on entity type
        entity_column = f"is_active_for_{entity_type}s"
        
        query = f"""
            SELECT id, name, template_type, school_level, is_active,
                   canvas, front_layers, back_layers, created_at, updated_at
            FROM id_templates
            WHERE {entity_column} = TRUE
        """
        params = []
        
        if school_level:
            query += " AND school_level = %s"
            params.append(school_level)
        
        query += " ORDER BY updated_at DESC LIMIT 1"
        
        row = db_manager.execute_query(query, tuple(params) if params else None, fetch_one=True)
        
        if not row:
            raise HTTPException(
                status_code=404, 
                detail=f"No active template found for {entity_type}"
            )
        
        return template_from_row(row)
    
    except HTTPException:
        raise
    except QueryError as e:
        logger.error(f"Failed to get active template for {entity_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")


@router.post("/{template_id}/duplicate", response_model=IDTemplateResponse)
def duplicate_template(template_id: int, new_name: Optional[str] = None):
    """Duplicate an existing template."""
    try:
        original = get_template(template_id)
        
        # Create new template based on original
        new_template = IDTemplateCreate(
            templateName=new_name or f"{original.templateName} (Copy)",
            templateType=original.templateType,
            schoolLevel=original.schoolLevel,
            isActive=False,  # Don't auto-activate duplicates
            canvas=original.canvas,
            front=original.front,
            back=original.back,
            metadata=original.metadata,
        )
        
        return create_template(new_template)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to duplicate template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to duplicate template")


# =============================================================================
# FIELD DEFINITION ENDPOINTS
# =============================================================================

@router.get("/fields/student")
def get_student_fields():
    """Get available fields for student templates."""
    return [f.model_dump() for f in STUDENT_FIELDS]


@router.get("/fields/teacher")
def get_teacher_fields():
    """Get available fields for teacher templates."""
    return [f.model_dump() for f in TEACHER_FIELDS]


@router.get("/fields/school")
def get_school_fields():
    """Get available school-wide fields."""
    return [f.model_dump() for f in SCHOOL_FIELDS]


@router.get("/fields/{template_type}")
def get_fields_by_type(template_type: str):
    """Get all available fields for a template type."""
    if template_type not in ('student', 'teacher'):
        raise HTTPException(status_code=400, detail="Invalid template type")
    
    fields = get_fields_for_template_type(template_type)
    return [f.model_dump() for f in fields]


# =============================================================================
# BACKGROUND IMAGE UPLOAD
# =============================================================================

@router.post("/upload-background")
async def upload_background_image(
    file: UploadFile = File(...),
    category: str = Form('student'),
):
    """
    Upload a background image for templates.
    
    The image will be saved to data/templates/<category>/ and can be
    used as a canvas background in the template editor.
    """
    try:
        # Validate file type
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: PNG, JPEG. Got: {file.content_type}"
            )
        
        # Create directory structure
        templates_dir = Path("data/templates")
        category_dir = templates_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        extension = Path(file.filename).suffix or '.png'
        unique_filename = f"{category}_{uuid.uuid4().hex[:8]}{extension}"
        file_path = category_dir / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Return URL for frontend
        relative_path = f"templates/{category}/{unique_filename}"
        
        logger.info(f"Background image uploaded: {unique_filename} for category {category}")
        
        return {
            "success": True,
            "filename": unique_filename,
            "url": f"/api/templates/backgrounds/{category}/{unique_filename}",
            "path": relative_path,
            "category": category,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload background image: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/backgrounds/{category}/{filename}")
async def get_background_image(category: str, filename: str):
    """Serve a background image file."""
    try:
        file_path = Path("data/templates") / category / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Security check - ensure path is within templates directory
        templates_dir = Path("data/templates").resolve()
        if not file_path.resolve().is_relative_to(templates_dir):
            raise HTTPException(status_code=403, detail="Access denied")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(file_path),
            media_type=f"image/{file_path.suffix[1:]}",
            filename=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve background image: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve image")

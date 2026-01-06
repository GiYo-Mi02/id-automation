"""
Template Models (Pydantic)
==========================
Type-safe request/response models for ID template operations.
"""

from typing import Optional, List, Any, Dict, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
import json


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

TemplateType = Literal['student', 'teacher', 'staff', 'visitor']
SchoolLevel = Literal['elementary', 'junior_high', 'senior_high', 'college', 'all']
LayerType = Literal['text', 'image', 'shape', 'qr_code']
TextAlign = Literal['left', 'center', 'right', 'justify']
FontWeight = Literal['normal', 'bold', '100', '200', '300', '400', '500', '600', '700', '800', '900']
ObjectFit = Literal['cover', 'contain', 'fill', 'none']
ShapeType = Literal['rectangle', 'circle', 'line']
BorderStyle = Literal['solid', 'dashed', 'dotted']


# =============================================================================
# LAYER MODELS
# =============================================================================

class BorderConfig(BaseModel):
    width: int = 1
    color: str = "#000000"
    style: BorderStyle = "solid"


class ShadowConfig(BaseModel):
    offsetX: int = 0
    offsetY: int = 2
    blur: int = 4
    spread: int = 0
    color: str = "rgba(0,0,0,0.25)"


class TextShadowConfig(BaseModel):
    offsetX: int = 0
    offsetY: int = 1
    blur: int = 2
    color: str = "rgba(0,0,0,0.25)"


class BaseLayer(BaseModel):
    """Base properties for all layer types."""
    id: str
    type: LayerType
    x: float
    y: float
    width: float
    height: float
    zIndex: int = 1
    visible: bool = True
    locked: bool = False
    rotation: float = 0
    opacity: float = 1.0
    name: Optional[str] = None


class TextLayer(BaseLayer):
    """Text layer configuration."""
    type: Literal['text'] = 'text'
    field: str  # Database field name or 'static'
    text: Optional[str] = None  # Static text or fallback
    fontSize: int = 16
    fontFamily: str = "Arial"
    fontWeight: FontWeight = "normal"
    color: str = "#000000"
    textAlign: TextAlign = "left"
    lineHeight: float = 1.2
    letterSpacing: float = 0
    wordWrap: bool = False
    maxWidth: Optional[float] = None
    uppercase: bool = False
    lowercase: bool = False
    textDecoration: Literal['none', 'underline', 'line-through'] = 'none'
    textShadow: Optional[TextShadowConfig] = None


class ImageLayer(BaseLayer):
    """Image layer configuration."""
    type: Literal['image'] = 'image'
    field: Optional[str] = None  # 'photo' for dynamic image
    src: Optional[str] = None  # Static image path
    objectFit: ObjectFit = "cover"
    borderRadius: float = 0
    border: Optional[BorderConfig] = None
    shadow: Optional[ShadowConfig] = None


class ShapeLayer(BaseLayer):
    """Shape layer configuration."""
    type: Literal['shape'] = 'shape'
    shape: ShapeType = "rectangle"
    fill: Optional[str] = "#cccccc"
    stroke: Optional[str] = None
    strokeWidth: float = 0
    borderRadius: float = 0


class QRCodeLayer(BaseLayer):
    """QR code layer configuration."""
    type: Literal['qr_code'] = 'qr_code'
    field: str  # Field to encode
    foregroundColor: str = "#000000"
    backgroundColor: str = "#ffffff"
    errorCorrectionLevel: Literal['L', 'M', 'Q', 'H'] = 'M'


# Union type for any layer
Layer = Union[TextLayer, ImageLayer, ShapeLayer, QRCodeLayer]


# =============================================================================
# TEMPLATE MODELS
# =============================================================================

class CanvasConfig(BaseModel):
    """Canvas configuration."""
    width: int = 591
    height: int = 1004
    backgroundColor: str = "#FFFFFF"
    backgroundImage: Optional[str] = None


class TemplateSide(BaseModel):
    """Single side (front or back) of the template."""
    backgroundImage: Optional[str] = None
    layers: List[Dict[str, Any]] = []  # Using Dict for flexibility with different layer types


class TemplateMetadata(BaseModel):
    """Template metadata."""
    createdBy: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    version: str = "1.0.0"


class IDTemplateCreate(BaseModel):
    """Request model for creating a new template."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    templateName: str = Field(..., min_length=1, max_length=100)
    templateType: TemplateType = "student"
    schoolLevel: SchoolLevel = "all"
    isActive: bool = False
    canvas: CanvasConfig = Field(default_factory=CanvasConfig)
    front: TemplateSide = Field(default_factory=TemplateSide)
    back: TemplateSide = Field(default_factory=TemplateSide)
    metadata: TemplateMetadata = Field(default_factory=TemplateMetadata)


class IDTemplateUpdate(BaseModel):
    """Request model for updating an existing template."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    templateName: Optional[str] = Field(default=None, max_length=100)
    templateType: Optional[TemplateType] = None
    schoolLevel: Optional[SchoolLevel] = None
    isActive: Optional[bool] = None
    canvas: Optional[CanvasConfig] = None
    front: Optional[TemplateSide] = None
    back: Optional[TemplateSide] = None
    metadata: Optional[TemplateMetadata] = None
    
    def get_update_dict(self) -> dict:
        """Return only fields that were explicitly set."""
        return {k: v for k, v in self.model_dump(exclude_none=True).items()}


class IDTemplateResponse(BaseModel):
    """Response model for a template."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    templateName: str
    templateType: TemplateType
    schoolLevel: SchoolLevel
    isActive: bool
    canvas: CanvasConfig
    front: TemplateSide
    back: TemplateSide
    metadata: TemplateMetadata
    
    @classmethod
    def from_db_row(cls, row: dict) -> "IDTemplateResponse":
        """Create from database row."""
        # Parse JSON fields
        front_data = row.get('front_layers', '{}')
        back_data = row.get('back_layers', '{}')
        canvas_data = row.get('canvas', '{}')
        
        if isinstance(front_data, str):
            front_data = json.loads(front_data)
        if isinstance(back_data, str):
            back_data = json.loads(back_data)
        if isinstance(canvas_data, str):
            canvas_data = json.loads(canvas_data)
        
        # Handle layers data - can be either list or dict with 'layers' key
        if isinstance(front_data, list):
            front_layers = front_data
            front_bg = None
        elif isinstance(front_data, dict):
            front_layers = front_data.get('layers', [])
            front_bg = front_data.get('backgroundImage')
        else:
            front_layers = []
            front_bg = None
        
        if isinstance(back_data, list):
            back_layers = back_data
            back_bg = None
        elif isinstance(back_data, dict):
            back_layers = back_data.get('layers', [])
            back_bg = back_data.get('backgroundImage')
        else:
            back_layers = []
            back_bg = None
        
        # Parse canvas JSON into CanvasConfig - handle both dict and empty cases
        if isinstance(canvas_data, dict):
            canvas_config = CanvasConfig(
                width=canvas_data.get('width', 591),
                height=canvas_data.get('height', 1004),
                backgroundColor=canvas_data.get('backgroundColor', '#FFFFFF'),
                backgroundImage=canvas_data.get('backgroundImage'),
            )
        else:
            canvas_config = CanvasConfig()  # Use defaults
        
        return cls(
            id=row.get('id', 0),
            templateName=row.get('name', ''),  # Database uses 'name' not 'template_name'
            templateType=row.get('template_type', 'student'),
            schoolLevel=row.get('school_level', 'all'),
            isActive=bool(row.get('is_active', False)),
            canvas=canvas_config,
            front=TemplateSide(backgroundImage=front_bg, layers=front_layers),
            back=TemplateSide(backgroundImage=back_bg, layers=back_layers),
            metadata=TemplateMetadata(
                createdBy=None,  # Not in database schema
                createdAt=str(row.get('created_at', '')) if row.get('created_at') else None,
                updatedAt=str(row.get('updated_at', '')) if row.get('updated_at') else None,
                version='1.0.0',  # Not in database schema
            )
        )


class TemplateListResponse(BaseModel):
    """Response model for template list."""
    
    templates: List[IDTemplateResponse]
    total: int


# =============================================================================
# FIELD MAPPING
# =============================================================================

class FieldDefinition(BaseModel):
    """Definition of a data field for templates."""
    key: str
    label: str
    type: Literal['text', 'date', 'image', 'number', 'computed']
    category: Literal['student', 'teacher', 'school', 'common']
    format: Optional[str] = None  # Format string for dates, numbers


# Student fields
STUDENT_FIELDS = [
    FieldDefinition(key='full_name', label='Full Name', type='text', category='student'),
    FieldDefinition(key='id_number', label='ID Number', type='text', category='student'),
    FieldDefinition(key='lrn', label='LRN', type='text', category='student'),
    FieldDefinition(key='grade_level', label='Grade Level', type='text', category='student'),
    FieldDefinition(key='section', label='Section', type='text', category='student'),
    FieldDefinition(key='guardian_name', label='Guardian Name', type='text', category='student'),
    FieldDefinition(key='guardian_contact', label='Guardian Contact', type='text', category='student'),
    FieldDefinition(key='address', label='Address', type='text', category='student'),
    FieldDefinition(key='birth_date', label='Birth Date', type='date', category='student'),
    FieldDefinition(key='blood_type', label='Blood Type', type='text', category='student'),
    FieldDefinition(key='emergency_contact', label='Emergency Contact', type='text', category='student'),
    FieldDefinition(key='school_year', label='School Year', type='text', category='student'),
    FieldDefinition(key='photo', label='Photo', type='image', category='student'),
]

# Teacher fields
TEACHER_FIELDS = [
    FieldDefinition(key='full_name', label='Full Name', type='text', category='teacher'),
    FieldDefinition(key='employee_id', label='Employee ID', type='text', category='teacher'),
    FieldDefinition(key='department', label='Department', type='text', category='teacher'),
    FieldDefinition(key='position', label='Position', type='text', category='teacher'),
    FieldDefinition(key='specialization', label='Specialization', type='text', category='teacher'),
    FieldDefinition(key='contact_number', label='Contact Number', type='text', category='teacher'),
    FieldDefinition(key='emergency_contact_name', label='Emergency Contact Name', type='text', category='teacher'),
    FieldDefinition(key='emergency_contact_number', label='Emergency Contact Number', type='text', category='teacher'),
    FieldDefinition(key='address', label='Address', type='text', category='teacher'),
    FieldDefinition(key='birth_date', label='Birth Date', type='date', category='teacher'),
    FieldDefinition(key='blood_type', label='Blood Type', type='text', category='teacher'),
    FieldDefinition(key='photo', label='Photo', type='image', category='teacher'),
]

# School fields (available for both template types)
SCHOOL_FIELDS = [
    FieldDefinition(key='school_name', label='School Name', type='text', category='school'),
    FieldDefinition(key='school_address', label='School Address', type='text', category='school'),
    FieldDefinition(key='school_contact', label='School Contact', type='text', category='school'),
    FieldDefinition(key='principal_name', label='Principal Name', type='text', category='school'),
    FieldDefinition(key='principal_signature', label='Principal Signature', type='image', category='school'),
    FieldDefinition(key='school_year', label='School Year', type='text', category='school'),
    FieldDefinition(key='school_logo', label='School Logo', type='image', category='school'),
]


def get_fields_for_template_type(template_type: TemplateType) -> List[FieldDefinition]:
    """Get available fields for a template type."""
    base_fields = SCHOOL_FIELDS.copy()
    if template_type == 'student':
        return STUDENT_FIELDS + base_fields
    return TEACHER_FIELDS + base_fields

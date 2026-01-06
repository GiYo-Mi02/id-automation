# Template System v2 Implementation Guide

## Overview

This document describes the implementation of the new layer-based template system for the School ID Generator. This system addresses the following issues:

1. **Template Rendering Mismatch** - Generated IDs didn't match editor preview
2. **Template Persistence** - Save button didn't persist changes to database
3. **Incomplete Data Mapping** - Missing principal signature, emergency contact, school official fields
4. **Photo Positioning Issues** - Photos not rendering correctly
5. **Editor Limitations** - No text alignment, word wrap, font size adjustment, layer ordering
6. **Missing Teacher Database** - No schema for teacher records
7. **Template Type Management** - Need different data sources based on template type

## New Files Created

### Backend (Python)

| File | Description |
|------|-------------|
| `app/models/teacher.py` | Pydantic models for teacher CRUD operations |
| `app/models/template.py` | Pydantic models for layer-based templates |
| `app/routes/templates.py` | Template CRUD API endpoints (prefix: `/api/templates/db`) |
| `app/routes/teachers.py` | Teacher CRUD API endpoints (prefix: `/api/teachers`) |
| `app/template_renderer.py` | WYSIWYG-compatible rendering engine |
| `tools/migrate_templates.py` | Database migration script |
| `data/database/SCHEMA_UPDATE_v2.sql` | SQL schema for new tables |

### Frontend (React)

| File | Description |
|------|-------------|
| `UI/src/types/template.ts` | TypeScript interfaces for templates |
| `UI/src/components/editor/EnhancedPropertiesPanel.jsx` | Layer properties editor with alignment controls |
| `UI/src/components/editor/EnhancedLayersPanel.jsx` | Layer management with drag-to-reorder |
| `UI/src/components/editor/LayerBasedCanvas.jsx` | Canvas renderer matching backend |

### Modified Files

| File | Changes |
|------|---------|
| `app/api.py` | Added routers for templates and teachers |
| `app/school_id_processor.py` | Integrated new layer-based renderer |
| `UI/src/services/api.js` | Added templateAPI, teacherAPI, studentAPI modules |
| `UI/src/pages/EditorPage.jsx` | Complete rewrite with layer-based system |

## Database Schema

### New Tables

```sql
-- Teachers table
CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    specialization VARCHAR(100),
    contact_number VARCHAR(20),
    emergency_contact_name VARCHAR(200),
    emergency_contact_number VARCHAR(20),
    address TEXT,
    photo_path VARCHAR(255),
    birth_date DATE,
    blood_type VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Templates table (layer-based)
CREATE TABLE id_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    template_type ENUM('student', 'teacher', 'staff', 'visitor') NOT NULL DEFAULT 'student',
    school_level ENUM('elementary', 'junior_high', 'senior_high', 'college', 'all') DEFAULT 'all',
    is_active BOOLEAN DEFAULT FALSE,
    canvas JSON,           -- { width, height, backgroundColor, backgroundImage }
    front_layers JSON,     -- Array of layer objects
    back_layers JSON,      -- Array of layer objects
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Students Table Updates

New columns added:
- `birth_date` DATE
- `blood_type` VARCHAR(10)
- `emergency_contact` VARCHAR(50)
- `school_year` VARCHAR(20)
- `created_at` TIMESTAMP
- `updated_at` TIMESTAMP

## Layer Structure

Each layer is a JSON object with the following properties:

### Common Properties (All Layer Types)
```json
{
    "id": "unique-id",
    "type": "text|image|shape|qr_code",
    "name": "Layer Name",
    "field": "data_field_name|static",
    "x": 0,
    "y": 0,
    "width": 100,
    "height": 50,
    "zIndex": 1,
    "visible": true,
    "locked": false,
    "opacity": 1.0,
    "rotation": 0
}
```

### Text Layer Properties
```json
{
    "type": "text",
    "text": "Static text content",
    "fontSize": 16,
    "fontFamily": "Arial",
    "fontWeight": "normal|bold",
    "color": "#000000",
    "textAlign": "left|center|right|justify",
    "lineHeight": 1.2,
    "letterSpacing": 0,
    "wordWrap": true,
    "maxWidth": null,
    "uppercase": false,
    "lowercase": false
}
```

### Image Layer Properties
```json
{
    "type": "image",
    "src": "path/to/image.png",
    "objectFit": "cover|contain|fill|none",
    "borderRadius": 0,
    "border": {
        "width": 1,
        "style": "solid",
        "color": "#000000"
    }
}
```

### Shape Layer Properties
```json
{
    "type": "shape",
    "shape": "rectangle|circle|line",
    "fill": "#3B82F6",
    "stroke": "#000000",
    "strokeWidth": 1,
    "borderRadius": 0
}
```

### QR Code Layer Properties
```json
{
    "type": "qr_code",
    "backgroundColor": "#FFFFFF",
    "foregroundColor": "#000000"
}
```

## Available Data Fields

### Student Fields
- `full_name` - Student's full name
- `id_number` - Student ID
- `lrn` - Learner Reference Number
- `grade_level` - Grade/Year level
- `section` - Section name
- `guardian_name` - Parent/Guardian name
- `guardian_contact` - Guardian contact number
- `emergency_contact` - Emergency contact number
- `address` - Home address
- `birth_date` - Date of birth
- `blood_type` - Blood type
- `school_year` - Academic year
- `photo` - Student photo (for image layers)

### Teacher Fields
- `full_name` - Teacher's full name
- `employee_id` - Employee ID
- `department` - Department name
- `position` - Job position
- `specialization` - Subject specialization
- `contact_number` - Contact number
- `emergency_contact_name` - Emergency contact person
- `emergency_contact_number` - Emergency contact number
- `address` - Home address
- `birth_date` - Date of birth
- `blood_type` - Blood type
- `photo` - Teacher photo

### School Fields (Static)
- `school_name` - School name
- `school_address` - School address
- `principal_name` - Principal's name
- `principal_signature` - Principal's signature image

## API Endpoints

### Template API (`/api/templates/db`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all templates |
| GET | `/active` | Get active template by type |
| GET | `/{id}` | Get template by ID |
| POST | `/` | Create new template |
| PUT | `/{id}` | Update template |
| DELETE | `/{id}` | Delete template |
| POST | `/{id}/activate` | Set template as active |
| POST | `/{id}/duplicate` | Duplicate template |
| GET | `/fields/{type}` | Get available fields for type |

### Teacher API (`/api/teachers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all teachers |
| GET | `/search` | Search teachers |
| GET | `/{id}` | Get teacher by ID |
| POST | `/` | Create new teacher |
| PUT | `/{id}` | Update teacher |
| DELETE | `/{id}` | Delete teacher |
| GET | `/{id}/history` | Get generation history |

## Migration Steps

### 1. Run Database Schema Update

```bash
# Using MySQL client
mysql -u root -p school_id_system < data/database/SCHEMA_UPDATE_v2.sql
```

### 2. Run Migration Script

```bash
cd c:\School_IDs
python tools/migrate_templates.py
```

Options:
- `--skip-schema` - Skip table creation (if already done)
- `--teachers teachers.csv` - Import teachers from CSV
- `--skip-default` - Skip default template creation

### 3. Restart the Backend Server

```bash
python run.py
```

### 4. Rebuild the Frontend

```bash
cd UI
npm run build
```

## How Rendering Works

### Editor (Frontend)
1. User designs template in the layer-based editor
2. Layers are rendered in real-time on canvas
3. Z-index determines layer stacking order
4. Text alignment, word wrap, and typography match backend

### ID Generation (Backend)
1. When a photo is processed, `school_id_processor.py` checks for layer renderer
2. If available, loads active template from database
3. `template_renderer.py` processes each layer:
   - Sorts by z-index
   - Applies text formatting (alignment, wrap, etc.)
   - Positions images with objectFit
   - Generates QR codes from data fields
4. Falls back to legacy `layout.json` if layer renderer unavailable

## Backward Compatibility

- Legacy `layout.json` is still supported as fallback
- Migration script imports existing layouts as database templates
- `school_id_processor.py` tries layer rendering first, falls back to legacy
- Old API endpoints (`/api/layout`) still work

## Testing

1. **Editor Test**: Create/edit templates, verify layers render correctly
2. **Persistence Test**: Save template, refresh page, verify template persists
3. **Generation Test**: Generate ID card, compare with editor preview
4. **Field Mapping Test**: Verify all data fields populate correctly
5. **Teacher Test**: Create teacher record, generate teacher ID

## Troubleshooting

### Template not saving
- Check browser console for API errors
- Verify database connection
- Check `id_templates` table for records

### Rendering mismatch
- Ensure fonts are available on both frontend and backend
- Check z-index ordering matches between editor and renderer
- Verify text alignment settings are preserved

### Migration errors
- Run schema SQL manually first
- Check for existing tables with conflicting structures
- Verify database permissions

## Future Enhancements

1. **Image upload for layers** - Allow custom images beyond photos
2. **Template versioning** - Track template changes over time
3. **Template sharing** - Export/import templates as JSON
4. **Preview with real data** - Load actual student/teacher data in editor
5. **Batch template application** - Apply template to multiple records

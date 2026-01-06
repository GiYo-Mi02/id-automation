// =============================================================================
// Template Type Definitions for School ID System
// =============================================================================

// Base Types
export type TemplateType = 'student' | 'teacher';
export type SchoolLevel = 'elementary' | 'high_school' | 'teacher';
export type LayerType = 'text' | 'image' | 'shape' | 'qr_code';
export type TextAlign = 'left' | 'center' | 'right' | 'justify';
export type FontWeight = 'normal' | 'bold' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900';
export type ObjectFit = 'cover' | 'contain' | 'fill' | 'none';
export type ShapeType = 'rectangle' | 'circle' | 'line';
export type BorderStyle = 'solid' | 'dashed' | 'dotted';

// =============================================================================
// Layer Interfaces
// =============================================================================

export interface BaseLayer {
  id: string;
  type: LayerType;
  x: number;
  y: number;
  width: number;
  height: number;
  zIndex: number;
  visible: boolean;
  locked: boolean;
  rotation?: number;
  opacity?: number;
  name?: string; // User-friendly layer name
}

export interface TextLayer extends BaseLayer {
  type: 'text';
  field: string; // Database field name or 'static' for static text
  text?: string; // Static text content or fallback
  fontSize: number;
  fontFamily: string;
  fontWeight: FontWeight;
  color: string;
  textAlign: TextAlign;
  lineHeight: number;
  letterSpacing: number;
  wordWrap: boolean;
  maxWidth?: number;
  uppercase?: boolean;
  lowercase?: boolean;
  textDecoration?: 'none' | 'underline' | 'line-through';
  textShadow?: {
    offsetX: number;
    offsetY: number;
    blur: number;
    color: string;
  };
}

export interface ImageLayer extends BaseLayer {
  type: 'image';
  field?: string; // 'photo' for dynamic image from database
  src?: string; // Static image URL/path
  objectFit: ObjectFit;
  borderRadius?: number;
  border?: {
    width: number;
    color: string;
    style: BorderStyle;
  };
  shadow?: {
    offsetX: number;
    offsetY: number;
    blur: number;
    spread: number;
    color: string;
  };
}

export interface ShapeLayer extends BaseLayer {
  type: 'shape';
  shape: ShapeType;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  borderRadius?: number;
}

export interface QRCodeLayer extends BaseLayer {
  type: 'qr_code';
  field: string; // Field to encode in QR code
  foregroundColor: string;
  backgroundColor: string;
  errorCorrectionLevel?: 'L' | 'M' | 'Q' | 'H';
}

export type Layer = TextLayer | ImageLayer | ShapeLayer | QRCodeLayer;

// =============================================================================
// Template Structure
// =============================================================================

export interface CanvasConfig {
  width: number;
  height: number;
  backgroundColor: string;
  backgroundImage?: string;
}

export interface TemplateSide {
  layers: Layer[];
}

export interface TemplateMetadata {
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
  version: string;
}

export interface IDTemplate {
  id?: number;
  templateName: string;
  templateType: TemplateType;
  schoolLevel: SchoolLevel;
  isActive: boolean;
  canvas: CanvasConfig;
  front: TemplateSide;
  back: TemplateSide;
  metadata: TemplateMetadata;
}

// =============================================================================
// Data Interfaces
// =============================================================================

export interface StudentData {
  id_number: string;
  full_name: string;
  lrn: string;
  grade_level: string;
  section: string;
  guardian_name: string;
  address: string;
  guardian_contact: string;
  birth_date?: string;
  blood_type?: string;
  emergency_contact?: string;
  emergency_contact_number?: string;
  school_year?: string;
  photo_path?: string;
  status?: 'active' | 'inactive' | 'graduated' | 'transferred';
  created_at?: string;
  updated_at?: string;
}

export interface TeacherData {
  employee_id: string;
  full_name: string;
  department: string;
  position: string;
  specialization: string;
  contact_number: string;
  emergency_contact_name: string;
  emergency_contact_number: string;
  address: string;
  birth_date?: string;
  blood_type?: string;
  hire_date?: string;
  employment_status?: 'active' | 'inactive' | 'on_leave';
  photo_path?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SchoolSettings {
  school_name: string;
  school_address: string;
  school_contact: string;
  principal_name: string;
  principal_signature_path?: string;
  school_year: string;
  school_logo_path?: string;
}

// Union type for any person data
export type PersonData = StudentData | TeacherData;

// =============================================================================
// Editor State
// =============================================================================

export interface EditorState {
  template: IDTemplate;
  selectedLayerId: string | null;
  currentSide: 'front' | 'back';
  zoom: number;
  isDirty: boolean;
  showGrid: boolean;
  snapToGrid: boolean;
  gridSize: number;
  history: IDTemplate[];
  historyIndex: number;
}

export interface EditorAction {
  type: string;
  payload?: any;
}

// =============================================================================
// API Response Types
// =============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface TemplateListResponse {
  templates: IDTemplate[];
  total: number;
}

export interface TemplateResponse extends ApiResponse<IDTemplate> {}

export interface StudentListResponse extends ApiResponse<StudentData[]> {
  total?: number;
  page?: number;
  pageSize?: number;
}

export interface TeacherListResponse extends ApiResponse<TeacherData[]> {
  total?: number;
  page?: number;
  pageSize?: number;
}

// =============================================================================
// Field Mapping System
// =============================================================================

export interface FieldDefinition {
  key: string;
  label: string;
  type: 'text' | 'date' | 'image' | 'number' | 'computed';
  category: 'student' | 'teacher' | 'school' | 'common';
  format?: (value: any) => string;
  computeFrom?: string[]; // For computed fields
}

export const STUDENT_FIELDS: FieldDefinition[] = [
  { key: 'full_name', label: 'Full Name', type: 'text', category: 'student' },
  { key: 'id_number', label: 'ID Number', type: 'text', category: 'student' },
  { key: 'lrn', label: 'LRN', type: 'text', category: 'student' },
  { key: 'grade_level', label: 'Grade Level', type: 'text', category: 'student' },
  { key: 'section', label: 'Section', type: 'text', category: 'student' },
  { key: 'guardian_name', label: 'Guardian Name', type: 'text', category: 'student' },
  { key: 'guardian_contact', label: 'Guardian Contact', type: 'text', category: 'student' },
  { key: 'address', label: 'Address', type: 'text', category: 'student' },
  { key: 'birth_date', label: 'Birth Date', type: 'date', category: 'student' },
  { key: 'blood_type', label: 'Blood Type', type: 'text', category: 'student' },
  { key: 'emergency_contact', label: 'Emergency Contact', type: 'text', category: 'student' },
  { key: 'school_year', label: 'School Year', type: 'text', category: 'student' },
  { key: 'photo', label: 'Photo', type: 'image', category: 'student' },
];

export const TEACHER_FIELDS: FieldDefinition[] = [
  { key: 'full_name', label: 'Full Name', type: 'text', category: 'teacher' },
  { key: 'employee_id', label: 'Employee ID', type: 'text', category: 'teacher' },
  { key: 'department', label: 'Department', type: 'text', category: 'teacher' },
  { key: 'position', label: 'Position', type: 'text', category: 'teacher' },
  { key: 'specialization', label: 'Specialization', type: 'text', category: 'teacher' },
  { key: 'contact_number', label: 'Contact Number', type: 'text', category: 'teacher' },
  { key: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', category: 'teacher' },
  { key: 'emergency_contact_number', label: 'Emergency Contact Number', type: 'text', category: 'teacher' },
  { key: 'address', label: 'Address', type: 'text', category: 'teacher' },
  { key: 'birth_date', label: 'Birth Date', type: 'date', category: 'teacher' },
  { key: 'blood_type', label: 'Blood Type', type: 'text', category: 'teacher' },
  { key: 'hire_date', label: 'Hire Date', type: 'date', category: 'teacher' },
  { key: 'photo', label: 'Photo', type: 'image', category: 'teacher' },
];

export const SCHOOL_FIELDS: FieldDefinition[] = [
  { key: 'school_name', label: 'School Name', type: 'text', category: 'school' },
  { key: 'school_address', label: 'School Address', type: 'text', category: 'school' },
  { key: 'school_contact', label: 'School Contact', type: 'text', category: 'school' },
  { key: 'principal_name', label: 'Principal Name', type: 'text', category: 'school' },
  { key: 'principal_signature', label: 'Principal Signature', type: 'image', category: 'school' },
  { key: 'school_year', label: 'School Year', type: 'text', category: 'school' },
  { key: 'school_logo', label: 'School Logo', type: 'image', category: 'school' },
];

// =============================================================================
// Utility Functions
// =============================================================================

export function getFieldsForTemplateType(templateType: TemplateType): FieldDefinition[] {
  const baseFields = [...SCHOOL_FIELDS];
  if (templateType === 'student') {
    return [...STUDENT_FIELDS, ...baseFields];
  }
  return [...TEACHER_FIELDS, ...baseFields];
}

export function createDefaultLayer(type: LayerType, id: string): Layer {
  const base: BaseLayer = {
    id,
    type,
    x: 100,
    y: 100,
    width: 200,
    height: type === 'text' ? 40 : 200,
    zIndex: 1,
    visible: true,
    locked: false,
  };

  switch (type) {
    case 'text':
      return {
        ...base,
        type: 'text',
        field: 'static',
        text: 'New Text',
        fontSize: 24,
        fontFamily: 'Arial',
        fontWeight: 'normal',
        color: '#000000',
        textAlign: 'left',
        lineHeight: 1.2,
        letterSpacing: 0,
        wordWrap: false,
      } as TextLayer;
    case 'image':
      return {
        ...base,
        type: 'image',
        objectFit: 'cover',
        borderRadius: 0,
      } as ImageLayer;
    case 'shape':
      return {
        ...base,
        type: 'shape',
        shape: 'rectangle',
        fill: '#cccccc',
        stroke: '#000000',
        strokeWidth: 1,
      } as ShapeLayer;
    case 'qr_code':
      return {
        ...base,
        type: 'qr_code',
        field: 'id_number',
        foregroundColor: '#000000',
        backgroundColor: '#ffffff',
      } as QRCodeLayer;
    default:
      throw new Error(`Unknown layer type: ${type}`);
  }
}

export function createDefaultTemplate(templateType: TemplateType): IDTemplate {
  return {
    templateName: `New ${templateType} Template`,
    templateType,
    schoolLevel: templateType === 'teacher' ? 'teacher' : 'high_school',
    isActive: false,
    canvas: {
      width: 591,
      height: 1004,
      backgroundColor: '#FFFFFF',
    },
    front: { layers: [] },
    back: { layers: [] },
    metadata: {
      version: '1.0.0',
      createdAt: new Date().toISOString(),
    },
  };
}

// Generate unique layer ID
export function generateLayerId(type: LayerType): string {
  return `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

import os
import cv2
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from rembg import remove, new_session 

# --- FIXED IMPORTS ---
from . import database  
# ---------------------

# Import new template renderer for layer-based rendering
try:
    from .template_renderer import TemplateRenderer, load_active_template
    LAYER_RENDERER_AVAILABLE = True
except ImportError:
    LAYER_RENDERER_AVAILABLE = False
    print("Layer-based template renderer not available. Using legacy rendering.")

# 1. TRY LOADING GLAM ENGINE (MediaPipe)
GLAM_AVAILABLE = False
try:
    from .glam_engine import GlamEngine 
    import mediapipe as mp
    if hasattr(mp, 'solutions'): GLAM_AVAILABLE = True
except: pass

# 2. TRY LOADING GFPGAN (Face Restore)
GFPGAN_AVAILABLE = False
try:
    from gfpgan import GFPGANer
    GFPGAN_AVAILABLE = True
except ImportError:
    print("GFPGAN not installed. Face restoration disabled.")

CONFIG = {
    'INPUT_FOLDER': r'data/input',
    'OUTPUT_FOLDER': r'data/output',
    'TEMPLATE_FOLDER': r'data/templates',  # lowercase normalized
    'LAYOUT_FILE': r'data/layout.json',
    'SETTINGS_FILE': r'data/settings.json',
    'CARD_SIZE': (591, 1004), 
}

class SchoolIDProcessor:
    def __init__(self, config):
        self.config = config
        self._ensure_folders()
        
        # Initialize Background Remover
        try: self.rembg_session = new_session("u2net_human_seg")
        except: self.rembg_session = new_session("u2net")
        
        # Initialize Glam Engine (Makeup)
        self.glam = GlamEngine() if GLAM_AVAILABLE else None
        
        # Initialize GFPGAN (Face Restore)
        self.face_restorer = None
        if GFPGAN_AVAILABLE:
            try:
                # This will automatically download the model if missing
                self.face_restorer = GFPGANer(
                    model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth',
                    upscale=1,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=None
                )
                print("Face Restore Engine: ONLINE (GFPGANv1.4)")
            except Exception as e:
                print(f"Face Restore Failed to Load: {e}")

        self.settings = self.load_settings()

    def _ensure_folders(self):
        for folder in [self.config['INPUT_FOLDER'], self.config['OUTPUT_FOLDER'], self.config['TEMPLATE_FOLDER']]:
            Path(folder).mkdir(parents=True, exist_ok=True)

    def load_settings(self):
        try:
            with open(self.config['SETTINGS_FILE'], 'r') as f: return json.load(f)
        except: return {"active_template_front": "rizal_front.png", "active_template_back": "rizal_back.png", "smooth_strength": 5}

    def reload_config(self): self.settings = self.load_settings()

    def load_layout(self):
        try:
            with open(self.config['LAYOUT_FILE'], 'r') as f: return json.load(f)
        except: return {}

    def get_student_data(self, filename):
        student_id = Path(filename).stem
        
        # Check for Manual Sidecar JSON first
        json_path = Path(self.config['INPUT_FOLDER']) / f"{student_id}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                # Determine entity type from ID prefix or data
                entity_type = 'student'
                if student_id.startswith('EMP-') or student_id.startswith('TCH-'):
                    entity_type = 'teacher'
                elif student_id.startswith('STF-'):
                    entity_type = 'staff'
                
                # Build comprehensive data dictionary with all possible fields
                result = {
                    'id': str(data.get('id_number', data.get('employee_id', student_id))),
                    'type': entity_type,
                    
                    # Common fields
                    'name': str(data.get('full_name', data.get('name', 'UNKNOWN'))).upper(),
                    'full_name': str(data.get('full_name', data.get('name', 'UNKNOWN'))).upper(),
                    'id_number': str(data.get('id_number', data.get('employee_id', student_id))),
                    
                    # Student-specific fields
                    'lrn': str(data.get('lrn', '')),
                    'grade_level': str(data.get('grade_level', '')).upper(),
                    'section': str(data.get('section', '')).upper(),
                    'guardian_name': str(data.get('guardian_name', '')).upper(),
                    'guardian_contact': str(data.get('guardian_contact', '')),
                    
                    # Teacher/Staff-specific fields
                    'position': str(data.get('position', data.get('job_title', ''))).upper(),
                    'department': str(data.get('department', data.get('office', ''))).upper(),
                    'employee_id': str(data.get('employee_id', data.get('id_number', student_id))),
                    'employee_type': str(data.get('employee_type', '')),
                    
                    # Common additional fields
                    'address': str(data.get('address', '')),
                    'emergency_contact': str(data.get('emergency_contact', data.get('guardian_contact', data.get('contact_number', '')))),
                    'contact_number': str(data.get('contact_number', data.get('guardian_contact', ''))),
                    'birth_date': str(data.get('birth_date', data.get('date_of_birth', ''))),
                    'blood_type': str(data.get('blood_type', '')),
                    'school_year': str(data.get('school_year', data.get('academic_year', '2025-2026'))),
                }
                print(f"   Loaded from JSON - Type: {entity_type}, Name: {result['name']}, Position: {result.get('position', 'N/A')}")
                return result
            except Exception as e:
                print(f"   JSON parse error: {e}")
                pass

        # DB Fallback
        # Detect entity type from ID prefix
        is_employee = (
            student_id.upper().startswith('EMP-') or 
            student_id.upper().startswith('TCH-') or 
            student_id.upper().startswith('T-') or 
            student_id.upper().startswith('STF-')
        )
        
        if is_employee:
            # Query teachers table for employee data
            employee = database.get_teacher(student_id)
            
            if not employee:
                print(f"   ⚠️ Employee {student_id} not found in teachers table")
                return {
                    'id': student_id, 'name': 'UNKNOWN', 
                    'full_name': 'UNKNOWN', 'id_number': student_id,
                    'employee_id': student_id,
                    'position': '', 'department': '',
                    'address': '', 'contact_number': '',
                    'emergency_contact': '', 'birth_date': '', 'blood_type': '',
                    'school_year': '2025-2026', 'type': 'teacher'
                }
            
            # Map employee database fields to expected format
            result = {
                'id': str(employee['employee_id']),
                'name': str(employee['full_name']).upper(),
                'full_name': str(employee['full_name']).upper(),
                'id_number': str(employee['employee_id']),
                'employee_id': str(employee['employee_id']),
                
                # Employee-specific fields
                'position': str(employee.get('position', '') or '').upper(),
                'department': str(employee.get('department', '') or '').upper(),
                'specialization': str(employee.get('specialization', '') or ''),
                'hire_date': str(employee.get('hire_date', '') or ''),
                'employment_status': str(employee.get('employment_status', 'active') or ''),
                
                # Common fields
                'address': str(employee.get('address', '') or ''),
                'contact_number': str(employee.get('contact_number', '') or ''),
                'emergency_contact': str(employee.get('emergency_contact_name', '') or ''),
                'birth_date': str(employee.get('birth_date', '') or ''),
                'blood_type': str(employee.get('blood_type', '') or ''),
                'school_year': '2025-2026',
                'type': 'teacher'
            }
            print(f"   ✅ Loaded from DB - Type: teacher, Name: {result['name']}, Position: {result['position']}, Department: {result['department']}")
            return result
        else:
            # Query students table for student data
            student = database.get_student(student_id)
            if not student: 
                return {
                    'id': student_id, 'name': 'UNKNOWN', 
                    'full_name': 'UNKNOWN', 'id_number': student_id,
                    'lrn': '', 'grade_level': '', 'section': '', 
                    'guardian_name': '', 'address': '', 'guardian_contact': '',
                    'emergency_contact': '', 'birth_date': '', 'blood_type': '',
                    'school_year': '2025-2026',
                }
            return {
                'id': str(student['id_number']),
                'name': str(student['full_name']).upper(),
                'full_name': str(student['full_name']).upper(),
                'id_number': str(student['id_number']),
                'lrn': str(student.get('lrn', '') or ''),
                'grade_level': str(student.get('grade_level', '') or '').upper(),
                'section': str(student.get('section', '') or '').upper(),
                'guardian_name': str(student.get('guardian_name', '') or '').upper(),
            'address': str(student.get('address', '') or ''),
            'guardian_contact': str(student.get('guardian_contact', '') or ''),
            'emergency_contact': str(student.get('emergency_contact', student.get('guardian_contact', '')) or ''),
            'birth_date': str(student.get('birth_date', '') or ''),
            'blood_type': str(student.get('blood_type', '') or ''),
            'school_year': str(student.get('school_year', '2025-2026') or '2025-2026'),
        }

    def draw_text(self, draw, text, item_config, card_w):
        if not text: return
        try: font = ImageFont.truetype("arialbd.ttf" if item_config.get('bold') else "arial.ttf", item_config['size'])
        except: font = ImageFont.load_default()
        
        x, y = item_config['x'], item_config['y']
        color = item_config.get('color', 'black')
        
        if item_config.get('align') == 'center':
            text_w = font.getbbox(text)[2]
            x = x - (text_w // 2)
        
        draw.text((x, y), text, fill=color, font=font)

    def process_photo(self, filepath):
        print(f"\nProcessing: {Path(filepath).name}")
        self.reload_config()
        layout = self.load_layout()
        
        try:
            img = cv2.imread(filepath)
            if img is None: 
                return False
            
            # OPTIMIZED ORDER:
            # 1. Hair cleanup FIRST (before background removal)
            if self.glam:
                try:
                    img = self.glam._advanced_hair_cleanup(img)
                    print("   Hair cleaned")
                except Exception as e:
                    print(f"   Hair cleanup: {e}")
            
            # 2. Face Restoration
            if self.face_restorer:
                try:
                    _, _, img = self.face_restorer.enhance(
                        img, has_aligned=False, only_center_face=True, 
                        paste_back=True, weight=0.8
                    )
                    print("   Face restored")
                except Exception as e:
                    print(f"   Restore: {e}")
            
            # 3. Light overall smoothing
            smooth_strength = min(self.settings.get('smooth_strength', 5), 7)
            try:
                img = cv2.bilateralFilter(img, smooth_strength, 50, 50)
            except:
                pass
            
            # 4. Makeup effects (skip hair, already done)
            if self.glam:
                try:
                    img = self.glam._smooth_skin(img, intensity=0.5)
                    img = self.glam._apply_makeup_effects(img, 0.4, 0.2)
                    img = self.glam._color_correction(img, boost=False)
                except:
                    pass
                
            # 5. Background removal
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            
            try:
                out = remove(img_pil, session=self.rembg_session, alpha_matting=True)
            except:
                out = img_pil
            
            # Add white background at bottom
            w, h = out.size
            mask = Image.new("L", (w, h), 0)
            draw_m = ImageDraw.Draw(mask)
            draw_m.rectangle([w*0.2, h*0.85, w*0.8, h+20], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(20))
            out.paste(img_pil.convert("RGBA"), (0, 0), mask=mask)
            img_final = out
    
            # Get student data
            data = self.get_student_data(Path(filepath).name)
    
            # Check if we should use layer-based rendering
            if LAYER_RENDERER_AVAILABLE:
                try:
                    front_card, back_card = self._render_with_layers(data, img_final)
                    if front_card and back_card:
                        front_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_FRONT.png"
                        back_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_BACK.png"
                        front_card.filter(ImageFilter.SHARPEN).save(front_path)
                        back_card.save(back_path)
                        database.log_generation(data['id'], front_path)
                        print(f"Saved (Layer): {front_path}")
                        return True
                    else:
                        print("ERROR: Template rendering failed. No active template or rendering error.")
                        return False
                except Exception as e:
                    print(f"Layer rendering error: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("ERROR: Layer renderer not available. Check imports.")
                return False
    
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _render_with_layers(self, data, photo_image):
        """Render ID card using the new layer-based template system from database"""
        try:
            # Load active template from database
            template = load_active_template(data.get('type', 'student'))
            if not template:
                print("ERROR: No active template found in database. Please activate a template in the Editor.")
                return None, None
            
            print(f"Using template: {template.get('templateName')} (ID: {template.get('id')})")
            print(f"Data available for substitution: {list(data.keys())}")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   ID: {data.get('id_number', 'N/A')}")
            print(f"   Position: {data.get('position', 'N/A')}")
            print(f"   Department: {data.get('department', 'N/A')}")
            
            # Create renderer (TemplateRenderer doesn't need template_folder for DB templates)
            renderer = TemplateRenderer()
            
            # Render both sides
            front_card = renderer.render(template, data, photo_image, 'front')
            back_card = renderer.render(template, data, photo_image, 'back')
            
            return front_card, back_card
        except Exception as e:
            print(f"Layer render error: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def _render_legacy(self, data, img_final, layout):
        """Original legacy rendering using layout.json"""
        try:
            # --- FRONT CARD ---
            tpl_front = Path(self.config['TEMPLATE_FOLDER']) / self.settings.get('active_template_front', 'rizal_front.png')
            try:
                card = Image.open(tpl_front).convert('RGBA')
            except:
                card = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
            card = card.resize(self.config['CARD_SIZE'])
    
            if 'photo' in layout.get('front', {}):
                p = layout['front']['photo']
                pf = ImageOps.fit(img_final, (p['w'], p['h']), centering=(0.5, 0.5))
                card.paste(pf, (p['x'], p['y']), mask=pf)
    
            draw = ImageDraw.Draw(card)
            front_layout = layout.get('front', {})
            for key in ['name', 'lrn', 'grade_level', 'section']:
                if key in front_layout:
                    config = front_layout[key].copy()
                    self.draw_text(draw, data.get(key, ''), config, self.config['CARD_SIZE'][0])
    
            front_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_FRONT.png"
            card.filter(ImageFilter.SHARPEN).save(front_path)
    
            # --- BACK CARD ---
            tpl_back = Path(self.config['TEMPLATE_FOLDER']) / self.settings.get('active_template_back', 'rizal_back.png')
            try:
                back = Image.open(tpl_back).convert('RGBA')
            except:
                back = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
            back = back.resize(self.config['CARD_SIZE'])
    
            draw_b = ImageDraw.Draw(back)
            for key in ['guardian_name', 'address', 'guardian_contact']:
                if key in layout.get('back', {}):
                    self.draw_text(draw_b, data.get(key, ''), layout['back'][key], self.config['CARD_SIZE'][0])
    
            back_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_BACK.png"
            back.save(back_path)
    
            database.log_generation(data['id'], front_path)
            print(f"Saved: {front_path}")
            return True
        except Exception as e:
            print(f"Legacy render error: {e}")
            return False
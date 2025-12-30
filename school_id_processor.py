"""
School ID Automation System - Wardiere Edition (MySQL Connected + Glam Engine)
"""

import os
import time
import cv2
import numpy as np
import database
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from rembg import remove, new_session 

# ==================== GLAM ENGINE SAFETY CHECK ====================
# We wrap this in a generic try/except so the system NEVER crashes
# even if MediaPipe/GlamEngine is broken.
GLAM_AVAILABLE = False
try:
    from glam_engine import GlamEngine
    # Test if it actually works by trying to access the library
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        raise ImportError("MediaPipe broken")
    GLAM_AVAILABLE = True
except Exception as e:
    print(f"⚠️ GLAM ENGINE DISABLED: Could not load auto-contour ({e})")
    print("   (System will run in standard mode)")
    GLAM_AVAILABLE = False
# ==================================================================

# ==================== CONFIGURATION ====================
CONFIG = {
    'INPUT_FOLDER': r'C:\School_IDs\Input_Raw',
    'OUTPUT_FOLDER': r'C:\School_IDs\Output_Ready',
    'TEMPLATE_PATH': r'C:\School_IDs\Templates\wardiere_template.png',
    
    'CARD_SIZE': (591, 1004),
    'PHOTO_W': 293, 'PHOTO_H': 320,
    'PHOTO_X': 149, 'PHOTO_Y': 165,
    'NAME_Y': 540, 'ROLE_Y': 590,
    'SMOOTH_STRENGTH': 5,
}

class SchoolIDProcessor:
    def __init__(self, config):
        self.config = config
        self._ensure_folders()
        
        # Initialize Rembg Session (Optimized for Humans)
        try:
            self.rembg_session = new_session("u2net_human_seg")
        except:
            self.rembg_session = new_session("u2net")

        # Initialize Glam Engine if available
        self.glam = None
        if GLAM_AVAILABLE:
            try:
                self.glam = GlamEngine()
                print("✨ Glam Engine (Auto-Contour) Loaded Successfully")
            except Exception as e:
                print(f"⚠️ Glam Engine Failed to Initialize: {e}")
        
    def _ensure_folders(self):
        for folder in [self.config['INPUT_FOLDER'], self.config['OUTPUT_FOLDER']]:
            Path(folder).mkdir(parents=True, exist_ok=True)

    def apply_beauty_filter(self, img):
        print("  → Applying skin smoothing...")
        try:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            lower_skin = np.array([0, 133, 77], dtype=np.uint8)
            upper_skin = np.array([255, 173, 127], dtype=np.uint8)
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
            smooth = cv2.bilateralFilter(img, self.config['SMOOTH_STRENGTH'], 75, 75)
            skin_mask_3ch = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR) / 255.0
            return (img * (1 - skin_mask_3ch) + smooth * skin_mask_3ch).astype(np.uint8)
        except:
            return img

    def remove_background(self, img):
        print("  → Removing background (with Torso Protection)...")
        
        # Convert to PIL
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # 1. AI Background Removal
        try:
             out = remove(img_pil, session=self.rembg_session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10)
        except Exception as e:
             print(f"Background Removal Error: {e}")
             return img_pil # Return original if AI fails

        # 2. TORSO SAFETY GUARD
        # Sometimes AI removes the shirt if it's dark. We force the bottom-center 
        # of the image to stay opaque using the original photo.
        
        w, h = out.size
        safety_mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(safety_mask)
        
        # Define the "Safe Zone" (Bottom 15% of image, middle 60% width)
        left = w * 0.2
        right = w * 0.8
        top = h * 0.85
        bottom = h + 20
        
        draw.rectangle([left, top, right, bottom], fill=255)
        
        # Blur the mask so the "forced" area blends smoothly
        safety_mask = safety_mask.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Paste the ORIGINAL image onto the RESULT where the mask is white
        orig_rgba = img_pil.convert("RGBA")
        out.paste(orig_rgba, (0, 0), mask=safety_mask)
        
        return out

    def get_student_data(self, filename):
        print("  → Fetching student data from MySQL...")
        student_id = Path(filename).stem
        
        student = database.get_student(student_id)
        
        if not student:
            print(f"  ⚠️ ID MISMATCH: '{student_id}' not found in Database.")
            return {
                'id': student_id,
                'name': 'UNKNOWN STUDENT',
                'role': 'VISITOR',
                'email': 'N/A', 'phone': 'N/A'
            }
        
        return {
            'id': str(student['id_number']),
            'name': str(student['full_name']).upper(),
            'role': str(student['role']).upper(),
            'email': str(student['email']),
            'phone': str(student['phone'])
        }
    
    def apply_template(self, photo, student_data):
        print("  → Applying Wardiere ID template...")
        try:
            card = Image.open(self.config['TEMPLATE_PATH']).convert('RGBA')
            if card.size != self.config['CARD_SIZE']:
                card = card.resize(self.config['CARD_SIZE'])
        except:
            card = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
            
        if photo.mode != 'RGBA': photo = photo.convert('RGBA')
        target_size = (self.config['PHOTO_W'], self.config['PHOTO_H'])
        photo_fitted = ImageOps.fit(photo, target_size, centering=(0.5, 0.5))
        card.paste(photo_fitted, (self.config['PHOTO_X'], self.config['PHOTO_Y']), mask=photo_fitted)

        draw = ImageDraw.Draw(card)
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 32)
            font_role = ImageFont.truetype("arial.ttf", 24)
            font_data = ImageFont.truetype("arial.ttf", 20)
        except:
            font_name = ImageFont.load_default()
            font_role = font_name
            font_data = font_name
            
        width = self.config['CARD_SIZE'][0]
        name_x = (width - font_name.getbbox(student_data['name'])[2]) // 2
        draw.text((name_x, self.config['NAME_Y']), student_data['name'], fill='#0033CC', font=font_name)

        role_x = (width - font_role.getbbox(student_data['role'])[2]) // 2
        draw.text((role_x, self.config['ROLE_Y']), student_data['role'], fill='#2C2C2C', font=font_role)

        draw.text((180, 655), student_data['id'], fill='#0033CC', font=font_data)
        draw.text((180, 685), student_data['email'], fill='#0033CC', font=font_data)
        draw.text((180, 715), student_data['phone'], fill='#0033CC', font=font_data)
        
        return card

    def process_photo(self, filepath):
        print(f"\n{'='*60}")
        print(f"Processing: {Path(filepath).name}")
        
        try:
            # 1. Read Image
            img = cv2.imread(filepath)
            if img is None: return False
            
            # 2. Apply Basic Beauty Filter (REDUCED STRENGTH)
            # We use the config value we lowered to 5
            img = self.apply_beauty_filter(img)

            # 3. Apply Glam Engine (ONLY IF AVAILABLE)
            if self.glam:
                try:
                    img = self.glam.apply_glam(img, contour_intensity=0.35, eye_pop=0.15)
                except Exception as e:
                    print(f"  ⚠️ Glam Engine Error (Skipping): {e}")

            # 4. Remove Background
            img_no_bg = self.remove_background(img)
            
            # 5. Fetch Data
            student_data = self.get_student_data(Path(filepath).name)
            
            # 6. Generate Card
            final_card = self.apply_template(img_no_bg, student_data)
            
            # === NEW: SHARPEN THE FINAL RESULT ===
            # This makes the text and face look crisp
            final_card = final_card.filter(ImageFilter.SHARPEN)
            
            output_filename = f"{student_data['id']}_FINAL.png"
            output_path = Path(self.config['OUTPUT_FOLDER']) / output_filename
            final_card.save(output_path, 'PNG', quality=95)
            
            # 7. Log to Database
            database.log_generation(student_data['id'], output_path)
            
            print(f"✅ SUCCESS! Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
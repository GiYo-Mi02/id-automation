import os
import cv2
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from rembg import remove, new_session 

# --- FIXED IMPORTS ---
from . import database  # Relative import
# ---------------------

GLAM_AVAILABLE = False
try:
    from .glam_engine import GlamEngine # Relative import
    import mediapipe as mp
    if hasattr(mp, 'solutions'): GLAM_AVAILABLE = True
except: pass

# --- CONFIG UPDATED FOR 'data/' FOLDER ---
CONFIG = {
    'INPUT_FOLDER': r'data/input',
    'OUTPUT_FOLDER': r'data/output',
    'TEMPLATE_FOLDER': r'data/templates',
    'LAYOUT_FILE': r'data/layout.json',
    'SETTINGS_FILE': r'data/settings.json',
    'CARD_SIZE': (591, 1004), 
}

class SchoolIDProcessor:
    def __init__(self, config):
        self.config = config
        self._ensure_folders()
        try: self.rembg_session = new_session("u2net_human_seg")
        except: self.rembg_session = new_session("u2net")
        self.glam = GlamEngine() if GLAM_AVAILABLE else None
        self.settings = self.load_settings()

    def _ensure_folders(self):
        for folder in [self.config['INPUT_FOLDER'], self.config['OUTPUT_FOLDER']]:
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
        student = database.get_student(student_id)
        if not student: 
            return {
                'id': student_id, 'name': 'UNKNOWN', 
                'lrn': '', 'grade_level': '', 'section': '', 
                'guardian_name': '', 'address': '', 'guardian_contact': ''
            }
        return {
            'id': str(student['id_number']),
            'name': str(student['full_name']).upper(),
            'lrn': str(student.get('lrn', '') or ''),
            'grade_level': str(student.get('grade_level', '') or '').upper(),
            'section': str(student.get('section', '') or '').upper(),
            'guardian_name': str(student.get('guardian_name', '') or '').upper(),
            'address': str(student.get('address', '') or ''),
            'guardian_contact': str(student.get('guardian_contact', '') or '')
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
            if img is None: return False
            try: img = cv2.bilateralFilter(img, self.settings.get('smooth_strength', 5), 75, 75)
            except: pass
            if self.glam:
                try: img = self.glam.apply_glam(img)
                except: pass
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            try: out = remove(img_pil, session=self.rembg_session, alpha_matting=True)
            except: out = img_pil
            
            w, h = out.size
            mask = Image.new("L", (w, h), 0)
            draw_m = ImageDraw.Draw(mask)
            draw_m.rectangle([w*0.2, h*0.85, w*0.8, h+20], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(20))
            out.paste(img_pil.convert("RGBA"), (0,0), mask=mask)
            img_final = out

            data = self.get_student_data(Path(filepath).name)

            # --- FRONT CARD ---
            tpl_front = Path(self.config['TEMPLATE_FOLDER']) / self.settings.get('active_template_front', 'rizal_front.png')
            try: card = Image.open(tpl_front).convert('RGBA')
            except: card = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
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
                    if key == 'section':
                        if '5' in data['grade_level']: config['y'] += 45
                        if '6' in data['grade_level']: config['y'] += 90
                    self.draw_text(draw, data[key], config, self.config['CARD_SIZE'][0])

            front_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_FRONT.png"
            card.filter(ImageFilter.SHARPEN).save(front_path)

            # --- BACK CARD ---
            tpl_back = Path(self.config['TEMPLATE_FOLDER']) / self.settings.get('active_template_back', 'rizal_back.png')
            try: back = Image.open(tpl_back).convert('RGBA')
            except: back = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
            back = back.resize(self.config['CARD_SIZE'])

            draw_b = ImageDraw.Draw(back)
            for key in ['guardian_name', 'address', 'guardian_contact']:
                if key in layout.get('back', {}):
                    self.draw_text(draw_b, data[key], layout['back'][key], self.config['CARD_SIZE'][0])

            back_path = Path(self.config['OUTPUT_FOLDER']) / f"{data['id']}_BACK.png"
            back.save(back_path)

            database.log_generation(data['id'], front_path)
            print(f"✅ Saved: {front_path}")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False
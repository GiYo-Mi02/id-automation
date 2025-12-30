"""
School ID Automation System - Wardiere Edition (Debug Mode)
"""

import os
import time
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from rembg import remove
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ==================== CONFIGURATION ====================
CONFIG = {
    'INPUT_FOLDER': r'C:\School_IDs\Input_Raw',
    'OUTPUT_FOLDER': r'C:\School_IDs\Output_Ready',
    'TEMPLATE_PATH': r'C:\School_IDs\Templates\wardiere_template.png',
    'STUDENT_DB': r'C:\School_IDs\students.csv',
    
    # Wardiere ID Card dimensions
    'CARD_SIZE': (591, 1004),
    
    # Photo Box Configuration
    'PHOTO_W': 293,
    'PHOTO_H': 320,
    'PHOTO_X': 149,
    'PHOTO_Y': 165,
    
    # === ALIGNMENT SETTINGS (Edit these!) ===
    # Decreasing = Moves UP
    # Increasing = Moves DOWN
    'NAME_Y': 535,   
    'ROLE_Y': 580,   
    
    # Processing settings
    'SMOOTH_STRENGTH': 9,
}

class SchoolIDProcessor:
    def __init__(self, config):
        self.config = config
        self._ensure_folders()
        
    def _ensure_folders(self):
        for folder in [self.config['INPUT_FOLDER'], self.config['OUTPUT_FOLDER']]:
            Path(folder).mkdir(parents=True, exist_ok=True)

    # STEP A: Beauty Filter
    def apply_beauty_filter(self, img):
        print("  → Applying beauty filter...")
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

    # STEP B: Background Removal
    def remove_background(self, img):
        print("  → Removing background...")
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return remove(img_pil)

    # STEP D: Data Merging
    def get_student_data(self, filename):
        print("  → Fetching student data...")
        student_id = Path(filename).stem
        
        try:
            df = pd.read_csv(self.config['STUDENT_DB'])
            df['ID_Number'] = df['ID_Number'].astype(str)
        except Exception as e:
            print(f"  ⚠️ CSV ERROR: Could not read students.csv. ({e})")
            return self._get_default_data(student_id)

        student = df[df['ID_Number'] == student_id]
        
        if student.empty:
            print(f"  ⚠️ ID MISMATCH: Filename '{student_id}' not found in CSV.")
            return self._get_default_data(student_id)
        
        row = student.iloc[0]
        return {
            'id': student_id,
            'name': str(row.get('Full_Name', 'Unknown')).upper(),
            'role': str(row.get('Role', 'STUDENT')).upper(),
            'email': str(row.get('Email', f"{student_id}@wardiere.edu")),
            'phone': str(row.get('Phone', 'N/A'))
        }

    def _get_default_data(self, student_id):
        return {
            'id': student_id,
            'name': 'UNKNOWN STUDENT',
            'role': 'STUDENT',
            'email': f'{student_id}@wardiere.edu',
            'phone': 'N/A'
        }
    
    # STEP E: Template Application
    def apply_template(self, photo, student_data):
        print("  → Applying Wardiere ID template...")
        try:
            card = Image.open(self.config['TEMPLATE_PATH']).convert('RGBA')
            if card.size != self.config['CARD_SIZE']:
                card = card.resize(self.config['CARD_SIZE'])
        except:
            card = Image.new('RGBA', self.config['CARD_SIZE'], 'white')
            
        # Paste Photo
        if photo.mode != 'RGBA': photo = photo.convert('RGBA')
        target_size = (self.config['PHOTO_W'], self.config['PHOTO_H'])
        photo_fitted = ImageOps.fit(photo, target_size, centering=(0.5, 0.5))
        card.paste(photo_fitted, (self.config['PHOTO_X'], self.config['PHOTO_Y']), mask=photo_fitted)

        # Draw Text
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

        # --- Name (Uses Config) ---
        name_y = self.config['NAME_Y']
        print(f"  DEBUG: Placing Name at Y={name_y}") # <--- CHECK THIS IN CONSOLE
        name_x = (width - font_name.getbbox(student_data['name'])[2]) // 2
        draw.text((name_x, name_y), student_data['name'], fill='#0033CC', font=font_name)

        # --- Role (Uses Config) ---
        role_y = self.config['ROLE_Y']
        print(f"  DEBUG: Placing Role at Y={role_y}") # <--- CHECK THIS IN CONSOLE
        role_x = (width - font_role.getbbox(student_data['role'])[2]) // 2
        draw.text((role_x, role_y), student_data['role'], fill='#2C2C2C', font=font_role)

        # --- Details ---
        draw.text((180, 655), student_data['id'], fill='#0033CC', font=font_data)
        draw.text((180, 685), student_data['email'], fill='#0033CC', font=font_data)
        draw.text((180, 715), student_data['phone'], fill='#0033CC', font=font_data)
        
        return card

    def process_photo(self, filepath):
        print(f"\n{'='*60}")
        print(f"Processing: {Path(filepath).name}")
        
        try:
            img = cv2.imread(filepath)
            if img is None: return False
            
            img = self.apply_beauty_filter(img)
            img_no_bg = self.remove_background(img)
            student_data = self.get_student_data(Path(filepath).name)
            
            final_card = self.apply_template(img_no_bg, student_data)
            
            output_path = Path(self.config['OUTPUT_FOLDER']) / f"{student_data['id']}_FINAL.png"
            final_card.save(output_path, 'PNG', quality=95)
            
            print(f"✅ SUCCESS! Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# File Watcher
class PhotoWatcher(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor
        self.processing = set()
    def on_created(self, event):
        if event.is_directory: return
        filepath = event.src_path
        if not filepath.lower().endswith(('.jpg', '.jpeg', '.png')): return
        if filepath in self.processing: return
        time.sleep(1)
        self.processing.add(filepath)
        print(f"\n🔔 New photo detected: {Path(filepath).name}")
        self.processor.process_photo(filepath)
        self.processing.remove(filepath)

if __name__ == "__main__":
    print("="*60)
    print("System Starting... (Press Ctrl+C to stop)")
    print(f"Database: {CONFIG['STUDENT_DB']}")
    print("="*60)
    
    processor = SchoolIDProcessor(CONFIG)
    observer = Observer()
    observer.schedule(PhotoWatcher(processor), CONFIG['INPUT_FOLDER'], recursive=False)
    observer.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
import cv2
import numpy as np
import os
import torch
import pathlib

# --- 1. SETUP MEDIAPIPE (OPTIONAL & SAFE) ---
MP_AVAILABLE = False
try:
    import mediapipe as mp
    if hasattr(mp, 'solutions'):
        MP_AVAILABLE = True
    else:
        print("⚠️ MediaPipe loaded but 'solutions' missing. Makeup features disabled.")
except ImportError:
    print("⚠️ MediaPipe library not found. Makeup features disabled.")

# --- 2. SETUP AI MODEL (GFPGAN) ---
AI_AVAILABLE = False
AI_MODEL = None

try:
    from gfpgan import GFPGANer
    AI_AVAILABLE = True
    AI_MODEL = "GFPGAN"
except ImportError:
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
        AI_AVAILABLE = True
        AI_MODEL = "REALESRGAN"
    except ImportError:
        AI_MODEL = None

# --- CONFIGURATION: UPDATED FOR V1.4 ---
MODEL_FILE_NAME = "GFPGANv1.4.pth"  
MODEL_PATH = os.path.join("data", "models", MODEL_FILE_NAME)

class AIGlamEngine:
    def __init__(self, use_ai=True):
        """
        Robust Glam Engine (v1.4 Ready):
        - Safe imports: Won't crash if libraries are missing.
        - Uses GFPGAN v1.4 for best restoration.
        """
        self.mp_available = MP_AVAILABLE
        
        # Initialize MediaPipe ONLY if available
        if self.mp_available:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
                
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5
                )
                self.segmenter = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
                print("Makeup & Hair Engine: ONLINE")
            except Exception as e:
                print(f"Makeup Engine Error: {e}")
                self.mp_available = False
        else:
            print("Makeup & Hair Engine: OFFLINE (MediaPipe missing)")

        # Initialize AI Model
        self.use_ai = use_ai and AI_AVAILABLE
        self.ai_enhancer = None
        
        if self.use_ai:
            self._init_ai_model()

    def _init_ai_model(self):
        try:
            if not os.path.exists(MODEL_PATH):
                print(f"AI Model missing at: {MODEL_PATH}")
                print(f"   (Make sure you downloaded '{MODEL_FILE_NAME}')")
                self.use_ai = False
                return

            if AI_MODEL == "GFPGAN":
                self.ai_enhancer = GFPGANer(
                    model_path=MODEL_PATH, upscale=1, arch='clean', 
                    channel_multiplier=2, bg_upsampler=None
                )
                print(f"Face Restore Engine: ONLINE ({MODEL_FILE_NAME})")
                
            elif AI_MODEL == "REALESRGAN":
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                               num_block=23, num_grow_ch=32, scale=1)
                self.ai_enhancer = RealESRGANer(
                    scale=1, model_path=MODEL_PATH, model=model, tile=0, 
                    tile_pad=10, pre_pad=0, half=False
                )
                print("AI Upscaler: ONLINE")
                
        except Exception as e:
            print(f"AI Init Failed: {e}")
            self.use_ai = False

    def apply_glam(self, image, mode='balanced', contour_intensity=0.4, eye_pop=0.2):
        print(f"\nProcessing Photo with AI...")
        
        # 1. AI FACE RESTORE (Priority #1)
        if self.use_ai:
            image = self._ai_enhance_face(image)
        
        # 2. MEDIAPIPE EFFECTS (Only if working)
        if self.mp_available:
            try:
                # Hair Cleanup
                image = self._advanced_hair_cleanup(image)
                
                # Skin Smoothing
                intensity = 0.5 if mode == 'balanced' else 0.7
                if mode == 'natural': intensity = 0.3
                image = self._smooth_skin(image, intensity=intensity)
                
                # Makeup
                if mode != 'natural':
                    image = self._apply_makeup_effects(image, contour_intensity, eye_pop)
            except Exception as e:
                print(f"Effect skipped: {e}")
        
        # 3. GLOBAL EFFECTS (Always working)
        image = self._color_correction(image, boost=(mode=='maximum'))
        image = self._traditional_sharpen(image, strength=0.3)
        
        return image

    def _ai_enhance_face(self, image):
        if not self.ai_enhancer: return image
        
        # FIXED INDENTATION HERE
        try:
            print("   Running AI Face Restoration (v1.4)...")
            
            # Suppress performance warnings from Cholesky decomposition
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                warnings.filterwarnings('ignore', message='.*Cholesky.*')
                warnings.filterwarnings('ignore', message='.*incomplete Cholesky.*')
                
                if AI_MODEL == "GFPGAN":
                    _, _, output = self.ai_enhancer.enhance(
                        image, has_aligned=False, only_center_face=True, paste_back=True, weight=1.0
                    )
                    print("   Face restored")
                    return output
                elif AI_MODEL == "REALESRGAN":
                    output, _ = self.ai_enhancer.enhance(image)
                    return output
        except Exception as e: 
            print(f"   AI Restoration Failed: {e}")
            return image
        
        return image

    # --- HELPER FUNCTIONS ---
    def _traditional_sharpen(self, image, strength=0.3):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) * strength
        kernel[1, 1] = 1 + (4 * strength)
        return cv2.filter2D(image, -1, kernel)

    def _color_correction(self, image, boost=False):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
        mult = 1.08 if boost else 1.05
        lab[:, :, 0] = np.clip(lab[:, :, 0] * mult + 2, 0, 255)
        lab[:, :, 1] = np.clip(lab[:, :, 1] * 0.95, 0, 255)
        lab[:, :, 2] = np.clip(lab[:, :, 2] * 1.02, 0, 255)
        return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    # --- MEDIAPIPE DEPENDENT FUNCTIONS ---
    def _advanced_hair_cleanup(self, image):
        """
        AGGRESSIVE Hair Cleanup v3.0 - "Virtual Haircut":
        - Removes ALL flyaways and stray strands
        - Creates clean, professional silhouette
        - Maintains natural texture in remaining hair
        """
        h, w, _ = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # --- 1. SEGMENTATION ---
        results = self.segmenter.process(rgb)
        if results.segmentation_mask is None: 
            return image

        # Use HIGH confidence threshold - only keep very certain pixels
        person_core = (results.segmentation_mask > 0.85).astype(np.uint8) * 255
        person_soft = (results.segmentation_mask > 0.5).astype(np.uint8) * 255

        # --- 2. PROTECT FACE REGION ---
        face_results = self.face_mesh.process(rgb)
        face_zone = np.zeros((h, w), dtype=np.uint8)

        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            face_zone = self._create_face_mask(landmarks, w, h)

            # Expand face protection significantly
            kernel_face = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40))
            face_zone = cv2.dilate(face_zone, kernel_face, iterations=3)

        # --- 3. THE AGGRESSIVE "HAIRCUT" ---
        # Start with soft person mask
        person_trimmed = person_soft.copy()

        # Erode HEAVILY to cut off all flyaways (this is the key!)
        trim_amount = 18  # INCREASED from 8 to 18 pixels
        kernel_cut = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (trim_amount, trim_amount))
        person_trimmed = cv2.erode(person_trimmed, kernel_cut, iterations=2)

        # Restore the face (so we don't cut the chin/ears)
        person_trimmed = cv2.bitwise_or(person_trimmed, face_zone)

        # --- 4. SMOOTH THE CUT EDGE ---
        # Slightly expand then contract to smooth the silhouette
        kernel_smooth = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        person_trimmed = cv2.morphologyEx(person_trimmed, cv2.MORPH_CLOSE, kernel_smooth)

        # --- 5. CREATE SOFT TRANSITION MASK ---
        # This prevents hard edges
        person_trimmed_blur = cv2.GaussianBlur(person_trimmed, (15, 15), 0)

        # --- 6. IDENTIFY "TRASH" REGIONS (Flyaways to delete) ---
        trash_mask = cv2.subtract(person_soft, person_trimmed)

        # --- 7. HAIR TEXTURE SMOOTHING ---
        # For the hair that remains, smooth it heavily
        hair_region = cv2.subtract(person_trimmed, face_zone)

        # Ultra-smooth the hair body
        super_smooth = cv2.bilateralFilter(image, d=25, sigmaColor=250, sigmaSpace=250)

        # Additional Gaussian blur for extra smoothness
        super_smooth = cv2.GaussianBlur(super_smooth, (5, 5), 0)

        # --- 8. BACKGROUND PREPARATION ---
        # Pure white background (best for ID cards)
        bg_white = np.full_like(image, 250, dtype=np.uint8)

        # Alternative: Heavy blur of original
        bg_blur = cv2.GaussianBlur(image, (99, 99), 0)

        # Choose background (white is recommended)
        bg_final = bg_white  # Change to bg_blur if you prefer

        # --- 9. COMPOSITING ---
        final = bg_final.copy()

        # A. Paint the smoothed hair
        hair_norm = hair_region.astype(float) / 255.0
        hair_3d = np.stack([hair_norm] * 3, axis=-1)
        final = (final * (1 - hair_3d) + super_smooth * hair_3d).astype(np.uint8)

        # B. Paint the face (original, untouched)
        face_norm = face_zone.astype(float) / 255.0
        face_3d = np.stack([face_norm] * 3, axis=-1)
        final = (final * (1 - face_3d) + image * face_3d).astype(np.uint8)

        # C. Ensure trash regions are completely white/background
        trash_norm = trash_mask.astype(float) / 255.0
        trash_3d = np.stack([trash_norm] * 3, axis=-1)
        final = (final * (1 - trash_3d) + bg_final * trash_3d).astype(np.uint8)

        # --- 10. FINAL EDGE SHARPENING ---
        # Sharpen the silhouette edge for crisp cutout
        person_edge = cv2.Canny(person_trimmed, 50, 150)
        kernel_edge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        person_edge = cv2.dilate(person_edge, kernel_edge, iterations=1)

        edge_mask = person_edge.astype(float) / 255.0
        edge_3d = np.stack([edge_mask] * 3, axis=-1)

        # Sharpen kernel
        kernel_sharp = np.array([[-1, -1, -1],
                                 [-1,  9, -1],
                                 [-1, -1, -1]])
        sharpened = cv2.filter2D(final, -1, kernel_sharp)
        final = (final * (1 - edge_3d * 0.5) + sharpened * edge_3d * 0.5).astype(np.uint8)

        return final
    
    def _inpaint_flyaways(self, image):
        """
        Alternative Method: Use OpenCV inpainting to "paint over" flyaways
        This can work well if the above approach isn't aggressive enough
        """
        h, w, _ = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get segmentation
        results = self.segmenter.process(rgb)
        if results.segmentation_mask is None:
            return image
        
        # High confidence mask
        person_solid = (results.segmentation_mask > 0.8).astype(np.uint8) * 255
        
        # Detect face
        face_results = self.face_mesh.process(rgb)
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            face_mask = self._create_face_mask(landmarks, w, h)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
            face_mask = cv2.dilate(face_mask, kernel, iterations=2)
        else:
            face_mask = np.zeros((h, w), dtype=np.uint8)
        
        # Erode person mask
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        person_trimmed = cv2.erode(person_solid, kernel_erode, iterations=2)
        
        # Restore face
        person_trimmed = cv2.bitwise_or(person_trimmed, face_mask)
        
        # Create inpaint mask (areas to "paint over")
        full_person = (results.segmentation_mask > 0.3).astype(np.uint8) * 255
        inpaint_mask = cv2.subtract(full_person, person_trimmed)
        
        # Inpaint the flyaway regions
        result = cv2.inpaint(image, inpaint_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        
        return result

    def _apply_glam_no_hair(self, image):
        """
        Apply glam effects WITHOUT hair cleanup (for optimized workflow)
        """
        # FIXED: Refer to 'self', not 'self.glam'
        if not self.mp_available:
            return image

        try:
            # Only skin smoothing and makeup, skip hair processing
            image = self._smooth_skin(image, intensity=0.5)
            image = self._apply_makeup_effects(image, 0.4, 0.2)
            image = self._color_correction(image, boost=False)
        except Exception as e:
            print(f"   ⚠️ Glam effect skipped: {e}")

        return image
    
    def _smooth_skin(self, image, intensity=0.5):
        h, w, _ = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        if not results.multi_face_landmarks: return image

        landmarks = results.multi_face_landmarks[0].landmark
        face_mask = self._create_face_mask(landmarks, w, h)
        d = int(9 + (intensity * 12))
        smoothed = cv2.bilateralFilter(image, d, 75, 75)
        face_mask_norm = face_mask.astype(float) / 255.0
        face_mask_3d = np.stack([face_mask_norm] * 3, axis=-1)
        return (image * (1 - face_mask_3d * intensity) + smoothed * face_mask_3d * intensity).astype(np.uint8)

    def _apply_makeup_effects(self, image, contour_intensity, eye_pop):
        h, w, _ = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        if not results.multi_face_landmarks: return image
        landmarks = results.multi_face_landmarks[0].landmark
        overlay = image.copy()
        left_cheek = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152]
        right_cheek = [454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152]
        self._paint_poly(overlay, landmarks, left_cheek, w, h, (20, 15, 10), contour_intensity * 0.4)
        self._paint_poly(overlay, landmarks, right_cheek, w, h, (20, 15, 10), contour_intensity * 0.4)
        return cv2.addWeighted(overlay, 0.4, image, 0.6, 0)

    def _paint_poly(self, img, landmarks, indices, w, h, color, intensity):
        points = []
        for idx in indices:
            if idx < len(landmarks):
                points.append((int(landmarks[idx].x * w), int(landmarks[idx].y * h)))
        if len(points) > 2:
            pts = np.array(points, np.int32)
            mask = np.zeros_like(img)
            cv2.fillPoly(mask, [pts], color)
            mask = cv2.GaussianBlur(mask, (51, 51), 0)
            img[:] = cv2.addWeighted(img, 1.0, mask, intensity, 0)

    def _create_face_mask(self, landmarks, w, h):
        face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        points = []
        for idx in face_oval:
            points.append([int(landmarks[idx].x * w), int(landmarks[idx].y * h)])
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(points, np.int32)], 255)
        return cv2.GaussianBlur(mask, (21, 21), 11)

# Alias
GlamEngine = AIGlamEngine
import cv2
import numpy as np
import mediapipe as mp

class GlamEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # Initialize MediaPipe Face Mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def apply_glam(self, image, contour_intensity=0.4, eye_pop=0.2):
        """
        Applies:
        1. Auto Contour (Cheek/Jaw shadows)
        2. T-Zone Highlight
        3. Eye Brightening
        """
        h, w, c = image.shape
        # MediaPipe needs RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            print("  ⚠️ No face detected for glam. Skipping.")
            return image

        landmarks = results.multi_face_landmarks[0].landmark
        
        # Create a transparent overlay layer
        overlay = image.copy()
        
        # --- 1. CHEEKBONE CONTOUR (Shadows) ---
        # Approximate cheek/jaw areas based on MediaPipe indices
        left_cheek_indices = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152]
        right_cheek_indices = [454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152]
        
        self._apply_makeup(overlay, landmarks, left_cheek_indices, w, h, (30, 30, 30), contour_intensity)
        self._apply_makeup(overlay, landmarks, right_cheek_indices, w, h, (30, 30, 30), contour_intensity)

        # --- 2. HIGHLIGHTS (Nose/Forehead) ---
        # Simpler nose bridge line for highlight
        nose_bridge = [6, 197, 195, 5, 4]
        self._apply_makeup(overlay, landmarks, nose_bridge, w, h, (255, 255, 255), contour_intensity * 0.7)

        # Blend the overlay with the original image (Soft Light effect)
        # We use simple weighted addition here for speed
        glam_shot = cv2.addWeighted(overlay, contour_intensity, image, 1 - contour_intensity, 0)

        # --- 3. EYE POP (Sharpen & Brighten Eyes) ---
        glam_shot = self._enhance_eyes(glam_shot, landmarks, w, h, eye_pop)

        return glam_shot

    def _apply_makeup(self, img, landmarks, indices, w, h, color, intensity):
        """Paints a soft polygon on the face"""
        points = []
        for idx in indices:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            points.append((x, y))
        
        if points:
            points_np = np.array(points, np.int32)
            # Draw filled shape
            mask = np.zeros_like(img)
            cv2.fillPoly(mask, [points_np], color)
            # Blur heavily to make it look like airbrushed makeup
            mask = cv2.GaussianBlur(mask, (51, 51), 0)
            
            # Blend only where the mask is drawn
            mask_bool = np.any(mask > 0, axis=-1)
            img[mask_bool] = cv2.addWeighted(img, 1.0, mask, 0.5, 0)[mask_bool]

    def _enhance_eyes(self, img, landmarks, w, h, intensity):
        """Local contrast boost for eyes"""
        # Simple implementation: Boost saturation/contrast globally slightly to pop
        # A more advanced version would mask the eyes specifically
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] *= (1.0 + intensity) # Boost Saturation
        hsv[..., 2] *= (1.0 + (intensity * 0.5)) # Boost Brightness slightly
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
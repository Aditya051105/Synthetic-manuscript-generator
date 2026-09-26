import cv2
import numpy as np
from PIL import Image

def apply_deformation(image, config):
    """
    Applies page level geometric distortions.
    """
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = img_cv.shape[:2]
    
    deform_cfg = config.get('deformation', {})
    
    # Rotation
    rot_max = deform_cfg.get('rotation_max', 1.5)
    if rot_max > 0:
        angle = np.random.uniform(-rot_max, rot_max)
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        img_cv = cv2.warpAffine(img_cv, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
    # Perspective distortion
    p_dist = deform_cfg.get('perspective_distortion', 0.02)
    if p_dist > 0:
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        
        # small random shifts
        shift = p_dist * min(w, h)
        pts2 = np.float32([
            [0 + np.random.uniform(-shift, shift), 0 + np.random.uniform(-shift, shift)],
            [w + np.random.uniform(-shift, shift), 0 + np.random.uniform(-shift, shift)],
            [0 + np.random.uniform(-shift, shift), h + np.random.uniform(-shift, shift)],
            [w + np.random.uniform(-shift, shift), h + np.random.uniform(-shift, shift)]
        ])
        
        M_p = cv2.getPerspectiveTransform(pts1, pts2)
        img_cv = cv2.warpPerspective(img_cv, M_p, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
    # Uneven Illumination Simulation (Curved page)
    if deform_cfg.get('curved_page', True):
        # Create a wavy dark/light pattern
        Y, X = np.ogrid[:h, :w]
        wave = np.sin((X / w) * np.pi) * 0.15 + 0.85 
        wave_pattern = np.stack([wave]*3, axis=-1)
        img_cv = np.clip(img_cv * wave_pattern, 0, 255).astype(np.uint8)
        
    if deform_cfg.get('uneven_illumination', True):
        # Apply a global lighting gradient
        shadow_mask = np.ones((h, w, 3), dtype=np.float32)
        shadow_intensity = np.random.uniform(0.6, 0.9)
        if np.random.rand() > 0.5: # shadow from left
            shadow_mask *= np.linspace(shadow_intensity, 1.0, w)[np.newaxis, :, np.newaxis]
        else: # shadow from right
            shadow_mask *= np.linspace(1.0, shadow_intensity, w)[np.newaxis, :, np.newaxis]
            
        img_cv = np.clip(img_cv * shadow_mask, 0, 255).astype(np.uint8)

    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

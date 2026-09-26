import cv2
import numpy as np
from PIL import Image

def apply_ink_effects(image, config):
    """
    Applies ink degradation effects to the rendered image.
    Note: These apply to the whole image, but we tune them to affect dark lines (ink).
    """
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    effects = config.get('ink_effects', {})
    
    fading = effects.get('fading', 0.2)
    bleeding = effects.get('bleeding', 0.1)
    smudging = effects.get('smudging', 0.05)
    
    if smudging > 0 and np.random.rand() < smudging * 5:
        # A small directional motion blur to simulate smudging
        kernel_size = np.random.choice([3, 5])
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
        kernel = kernel / kernel_size
        img_cv = cv2.filter2D(img_cv, -1, kernel)
        
    if bleeding > 0 and np.random.rand() < bleeding * 5:
        # Morphological dilation for ink bleed (assuming text is darker than background)
        # Using a slight blur instead of strict morph to keep it realistic
        img_cv = cv2.GaussianBlur(img_cv, (3, 3), 0)
        
    if fading > 0 and np.random.rand() < fading * 5:
        # Add random light noise where text might be faded
        # We blend a slightly lighter version in patches
        fade_mask = np.random.rand(img_cv.shape[0], img_cv.shape[1]) < 0.1
        img_cv[fade_mask] = np.clip(img_cv[fade_mask] + 30, 0, 255).astype(np.uint8)

    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

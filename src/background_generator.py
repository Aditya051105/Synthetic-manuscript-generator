import cv2
import numpy as np
from PIL import Image
import random

def create_background(config):
    """
    Generate a realistic historical manuscript background.
    Supports aged handmade paper or palm-leaf style with noise, stains, and scratches.
    """
    width = config['image']['width']
    height = config['image']['height']
    
    # Base color from config (e.g. yellowish-brown)
    base_color = config['background'].get('base_color', [240, 220, 180])
    
    # Variate base color slightly for uniqueness
    color_variation = np.random.randint(-15, 15, size=(3,))
    current_color = np.clip(np.array(base_color) + color_variation, 0, 255).astype(np.uint8)
    
    # Create solid base image
    bg = np.full((height, width, 3), current_color, dtype=np.uint8)

    # 1. Texture (Noise)
    if config['background'].get('texture', True):
        noise = np.random.normal(0, 15, (height, width, 3)).astype(np.int16)
        bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Apply slight blur to soften noise
        bg = cv2.GaussianBlur(bg, (5, 5), 0)

    # 2. Lighting gradient (edges darker)
    # create 2x2 grid of corners and resize
    corners = np.array([
        [np.random.uniform(0.6, 0.9), np.random.uniform(0.6, 0.9)],
        [np.random.uniform(0.6, 0.9), np.random.uniform(0.6, 0.9)]
    ], dtype=np.float32)
    gradient = cv2.resize(corners, (width, height), interpolation=cv2.INTER_CUBIC)
    
    # Apply gradient (center brighter, edges darker)
    center_y, center_x = height // 2, width // 2
    Y, X = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    max_dist = np.sqrt(center_x**2 + center_y**2)
    radial_grad = 1 - 0.4 * (dist_from_center / max_dist)
    
    gradient = gradient * radial_grad
    
    bg = np.clip(bg * gradient[..., np.newaxis], 0, 255).astype(np.uint8)

    # 3. Stains (perlin-like noise or random blobs)
    if config['background'].get('stains', True):
        for _ in range(random.randint(1, 5)):
            stain_x = random.randint(0, width)
            stain_y = random.randint(0, height)
            stain_r = random.randint(20, 150)
            
            # create a soft blob
            blob = np.zeros((height, width), dtype=np.float32)
            cv2.circle(blob, (stain_x, stain_y), stain_r, 1.0, -1)
            stain_ksize = stain_r if stain_r % 2 != 0 else stain_r + 1
            blob = cv2.GaussianBlur(blob, (stain_ksize, stain_ksize), 0)
            
            # darken where blob is
            darken_factor = random.uniform(0.7, 0.9)
            bg_f = bg.astype(np.float32)
            bg_f = bg_f * (1.0 - blob[..., np.newaxis] * (1.0 - darken_factor))
            bg = np.clip(bg_f, 0, 255).astype(np.uint8)

    # 4. Scratches
    if config['background'].get('scratches', True):
        for _ in range(random.randint(5, 20)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            length = random.randint(20, 200)
            angle = random.uniform(0, 3.14)
            x2 = int(x1 + length * np.cos(angle))
            y2 = int(y1 + length * np.sin(angle))
            
            color = random.choice([0, 50, 100, 200]) # dark or light scratches
            thickness = random.randint(1, 2)
            
            # Draw faded line
            scratch = np.zeros((height, width), dtype=np.uint8)
            cv2.line(scratch, (x1, y1), (x2, y2), 1, thickness)
            
            mask = scratch > 0
            bg[mask] = bg[mask] * 0.8 + color * 0.2
            
    # Return as PIL Image for PIL-based text rendering
    return Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))

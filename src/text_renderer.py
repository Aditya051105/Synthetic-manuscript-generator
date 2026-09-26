import random
from PIL import ImageDraw, ImageFont

def render_text_on_image(image, text_lines, layout_boxes, font_path, config):
    """
    Renders multiple lines of text onto the background image according to layout_boxes.
    Applies baseline waviness and uneven spacing.
    Returns the drawn image and the exact text rendered.
    """
    draw = ImageDraw.Draw(image)
    
    font_size = config['layout']['font_size']
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        # Fallback for testing if font doesn't exist
        font = ImageFont.load_default()
        
    color_config = config['text'].get('color', [30, 30, 25])
    
    # We will introduce variation in color per word
    base_color = tuple(color_config)
    
    rendered_text_list = []
    
    for i, (line, box) in enumerate(zip(text_lines, layout_boxes)):
        x, y, max_w, max_h = box
        
        words = line.split()
        current_x = x
        
        rendered_words = []
        for word in words:
            # Check length to avoid overflow
            # ImageFont.getbbox is standard in newer Pillow
            bbox = font.getbbox(word)
            word_w = bbox[2] - bbox[0]
            word_h = bbox[3] - bbox[1]
            
            if current_x + word_w > x + max_w:
                # Can't fit this word on the line
                break
                
            # Random y displacement (baseline waviness)
            y_offset = 0
            if config['text'].get('baseline_waviness', True):
                y_offset = random.randint(-2, 2)
                
            # Ink color variation
            color_variation = random.randint(-10, 20)
            word_color = tuple(max(0, min(255, c + color_variation)) for c in base_color)
            
            # Draw word
            draw.text((current_x, y + y_offset), word, font=font, fill=word_color)
            rendered_words.append(word)
            
            # Move x forward with irregular spacing
            space_bbox = font.getbbox(" ")
            space_w = space_bbox[2] - space_bbox[0]
            irregular_spacing = random.randint(-1, 3) 
            current_x += word_w + space_w + irregular_spacing
            
        if rendered_words:
            rendered_text_list.append(" ".join(rendered_words))
            
    return image, "\n".join(rendered_text_list)

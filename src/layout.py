import random

def generate_layout(config, num_lines, image_width, image_height, font_size):
    """
    Generates layout bounding boxes for a given number of text lines.
    Handles margins and line spacing.
    Returns a list of boxes: (x, y, max_line_width, max_line_height).
    """
    m_top = config['layout']['margins']['top']
    m_bot = config['layout']['margins']['bottom']
    m_left = config['layout']['margins']['left']
    m_right = config['layout']['margins']['right']
    
    line_spacing = config['layout']['line_spacing']
    
    max_w = image_width - m_left - m_right
    available_h = image_height - m_top - m_bot
    
    line_total_h = font_size * line_spacing
    
    # Check if lines exceed available height, readjust if necessary
    if num_lines * line_total_h > available_h:
        num_lines = int(available_h // line_total_h)
        
    boxes = []
    
    current_y = m_top
    for _ in range(num_lines):
        # Slightly irregular starting x for paragraphs or uneven lines
        x_start = m_left + random.randint(0, 15)
        
        boxes.append((x_start, current_y, max_w - (x_start - m_left), font_size))
        current_y += line_total_h
        
    return boxes

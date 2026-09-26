import os
from tqdm import tqdm
from .utils import ensure_dir
from .text_generator import load_text_corpus, sample_text_lines
from .background_generator import create_background
from .layout import generate_layout
from .text_renderer import render_text_on_image
from .ink_effects import apply_ink_effects
from .deformation import apply_deformation
from .annotation import write_annotation
import glob
import io

def find_font(script_name):
    """Find a .ttf or .otf font for the given script inside fonts/script_name/"""
    font_dir = os.path.join("fonts", script_name)
    if not os.path.exists(font_dir):
        return None
    fonts = glob.glob(os.path.join(font_dir, "*.ttf")) + glob.glob(os.path.join(font_dir, "*.otf"))
    if not fonts:
        return None
    return fonts[0] # Pick the first available

def generate_script_images_memory(config, script_name, count, font_path, custom_text=None):
    """
    Runs generation for a limited count and returns BytesIO streams for Vercel deployment.
    """
    if custom_text:
        corpus = [line.strip() for line in custom_text.splitlines() if line.strip()]
    else:
        corpus = load_text_corpus(script_name)
        
    image_width = config['image']['width']
    image_height = config['image']['height']
    font_size = config['layout']['font_size']
    
    results = []
    
    for _ in range(count):
        bg_img = create_background(config)
        lines = sample_text_lines(corpus, config)
        boxes = generate_layout(config, len(lines), image_width, image_height, font_size)
        rendered_layer, exact_text = render_text_on_image(bg_img, lines, boxes, font_path, config)
        img_with_ink = apply_ink_effects(rendered_layer, config)
        final_image = apply_deformation(img_with_ink, config)
        
        img_byte_arr = io.BytesIO()
        final_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        results.append((img_byte_arr, exact_text))
        
    return results

def generate_script_dataset(config, script_name, count_override=None):
    """
    Main pipeline function to generate a dataset for a single script.
    """
    dataset_splits = config['generation']['dataset_splits']
    
    if count_override is not None:
        total = count_override
        # roughly proportional splits if overriden
        train_count = int(total * 0.85)
        val_count = int(total * 0.10)
        test_count = total - train_count - val_count
    else:
        train_count = dataset_splits.get('train', 85)
        val_count = dataset_splits.get('validation', 10)
        test_count = dataset_splits.get('test', 5)
        total = train_count + val_count + test_count

    splits = []
    splits.extend(['train'] * train_count)
    splits.extend(['validation'] * val_count)
    splits.extend(['test'] * test_count)

    out_base = os.path.join(config['generation']['output_dir'], script_name)
    ensure_dir(os.path.join(out_base, 'train'))
    ensure_dir(os.path.join(out_base, 'validation'))
    ensure_dir(os.path.join(out_base, 'test'))

    corpus = load_text_corpus(script_name)
    font_path = find_font(script_name)
    if font_path is None:
        print(f"Warning: No valid .ttf or .otf font found for {script_name} in fonts/{script_name}. Using default.")
        font_path = "" # Pillow will use default internal font

    image_width = config['image']['width']
    image_height = config['image']['height']
    font_size = config['layout']['font_size']

    print(f"Generating {total} images for script: {script_name}")
    for idx, split in enumerate(tqdm(splits)):
        # 1. Background
        bg_img = create_background(config)
        
        # 2. Text layout & Sampling
        lines = sample_text_lines(corpus, config)
        boxes = generate_layout(config, len(lines), image_width, image_height, font_size)
        
        # 3. Rendering
        rendered_layer, exact_text = render_text_on_image(bg_img, lines, boxes, font_path, config)
        
        # 4. Ink Degradation
        img_with_ink = apply_ink_effects(rendered_layer, config)
        
        # 5. Page Deformation
        final_image = apply_deformation(img_with_ink, config)
        
        # 6. Save outputs
        base_filename = f"Image_{idx+1:03d}"
        png_path = os.path.join(out_base, split, f"{base_filename}.png")
        md_path = os.path.join(out_base, split, f"{base_filename}.md")
        
        final_image.save(png_path)
        write_annotation(md_path, exact_text)

    return total

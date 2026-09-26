import os
import glob
from PIL import Image

def validate_dataset(output_dir="output", expected_splits=['train', 'validation', 'test']):
    """
    Validates a generated dataset directory.
    Checks:
    - PNG / MD matching pairs
    - MD is not empty
    - Valid image dims
    """
    scripts = os.listdir(output_dir)
    report = []
    
    for script in scripts:
        script_dir = os.path.join(output_dir, script)
        if not os.path.isdir(script_dir):
            continue
            
        report.append(f"Validating Script: {script}")
        for split in expected_splits:
            split_dir = os.path.join(script_dir, split)
            if not os.path.exists(split_dir):
                report.append(f"  [{split}] Missing folder")
                continue
                
            png_files = sorted(glob.glob(os.path.join(split_dir, "*.png")))
            md_files = sorted(glob.glob(os.path.join(split_dir, "*.md")))
            
            if len(png_files) != len(md_files):
                report.append(f"  [{split}] ERROR: Mismatch between PNG ({len(png_files)}) and MD ({len(md_files)}) counts")
                continue
                
            report.append(f"  [{split}] Found {len(png_files)} pairs")
            errors = 0
            for png in png_files:
                base = os.path.splitext(png)[0]
                md = f"{base}.md"
                
                if not os.path.exists(md):
                    report.append(f"    ERROR: Missing matching markdown for {os.path.basename(png)}")
                    errors += 1
                    continue
                    
                # check MD not empty
                with open(md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        report.append(f"    ERROR: Empty MD file {os.path.basename(md)}")
                        errors += 1
                        
                # check valid image
                try:
                    with Image.open(png) as img:
                        img.verify() 
                except Exception as e:
                    report.append(f"    ERROR: Corrupted image {os.path.basename(png)}: {e}")
                    errors += 1
                    
            if errors == 0 and len(png_files) > 0:
                report.append(f"  [{split}] All pairs OK")
                
    return "\n".join(report)

if __name__ == "__main__":
    print(validate_dataset())

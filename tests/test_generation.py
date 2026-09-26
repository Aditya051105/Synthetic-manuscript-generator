import os
import pytest
import yaml
from src.dataset import generate_script_dataset
from src.validation import validate_dataset
from src.utils import ensure_dir
from src.layout import generate_layout
import shutil

@pytest.fixture(scope="module")
def setup_env():
    # Make sure we have mock data and config
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    out_dir = "tests/test_output"
    config['generation']['output_dir'] = out_dir
    config['generation']['dataset_splits'] = {'train': 2, 'validation': 1, 'test': 0}
    
    yield config
    
    # cleanup
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

def test_layout_logic():
    config = {
        'layout': {
            'margins': {'top': 10, 'bottom': 10, 'left': 10, 'right': 10},
            'line_spacing': 1.0
        }
    }
    
    # Should fit max 8 lines of height 10 in 100-20 height
    boxes = generate_layout(config, 10, 100, 100, 10)
    assert len(boxes) == 8
    assert boxes[0][1] == 10 # y position starts at top margin

def test_full_pipeline(setup_env):
    config = setup_env
    # We will test devanagari pipeline, should generate 3 images total
    
    total = generate_script_dataset(config, 'devanagari', count_override=3)
    assert total == 3
    
    # Run validation
    report = validate_dataset(output_dir=config['generation']['output_dir'], expected_splits=['train', 'validation', 'test'])
    
    assert "ERROR" not in report
    
    out_path = os.path.join(config['generation']['output_dir'], 'devanagari', 'train')
    assert os.path.exists(os.path.join(out_path, "Image_001.png"))
    assert os.path.exists(os.path.join(out_path, "Image_001.md"))

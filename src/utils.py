import os
import random
import numpy as np

def set_seed(seed):
    """Set the seed for reproducible random outputs."""
    random.seed(seed)
    np.random.seed(seed)

def ensure_dir(directory):
    """Ensure that a directory exists."""
    os.makedirs(directory, exist_ok=True)

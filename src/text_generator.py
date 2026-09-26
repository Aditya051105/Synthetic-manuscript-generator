import random
import os

def load_text_corpus(script_name, data_dir="data/text"):
    """
    Loads text corpus from the designated text file.
    """
    filename = os.path.join(data_dir, f"{script_name}.txt")
    if not os.path.exists(filename):
        return ["Sample Text Placeholder"]
        
    with open(filename, 'r', encoding='utf-8') as f:
        # read lines, filtering out empty ones
        lines = [line.strip() for line in f.read().splitlines() if line.strip()]
        
    if not lines:
        return ["Sample Text Placeholder"]
    return lines

def sample_text_lines(corpus, config):
    """
    Randomly samples consecutive lines from the corpus according to config line count limits.
    """
    min_lines = config['layout']['min_lines']
    max_lines = config['layout']['max_lines']
    
    num_lines = random.randint(min_lines, max_lines)
    
    if len(corpus) <= num_lines:
        return corpus.copy()
        
    start_idx = random.randint(0, len(corpus) - num_lines)
    return corpus[start_idx : start_idx + num_lines]

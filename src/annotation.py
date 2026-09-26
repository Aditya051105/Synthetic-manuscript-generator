import os

def write_annotation(filepath, text):
    """
    Writes the rendered text verbatim to a .md file.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

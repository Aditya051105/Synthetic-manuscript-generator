# Synthetic Manuscript Generator

An automated pipeline that takes Indic text (Devanagari, Modi, Sharada) and generates realistic-looking historical manuscript images along with mapping `.md` ground-truth files for OCR training.

## Features

- **Realistic Backgrounds**: Aged handmade paper, palm-leaf styles, stains, scratches, and noise.
- **Organic Text Formatting**: Character displacement, wavy baselines, uneven line spacing, and boundary checks.
- **Ink Degradation**: Smudges, bleeding, broken strokes, and variable ink intensity.
- **Physical Deformation**: Folds, curling, rotational, and perspective distortions.
- **Automated Validation**: Verifies generated output and dataset pairs.
- **HuggingFace Ready**: Push-button dataset publishing.

## Installation

```bash
# Clone the repository
git clone <your-repo-link>
cd synthetic-manuscript-generator

# Create a virtual environment and load dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Setup & Files Needed

### 1. Fonts
To properly render Indic typography, you must provide `.ttf` or `.otf` fonts. Place them in the designated directories:
- **Devanagari**: `fonts/devanagari/your-font.ttf`
- **Modi**: `fonts/modi/your-font.ttf`
- **Sharada**: `fonts/sharada/your-font.ttf`

### 2. Source Texts
Place the exact text you want to synthesize inside `data/text/`:
- `data/text/devanagari.txt`
- `data/text/modi.txt`
- `data/text/sharada.txt`

## Configuration

Adjust `config/config.yaml` to modify generation constraints:
- Image width/height
- Data split counts (Train/Validation/Test totals)
- Effect severity (scratches, stains, smudges, distortion)

## Usage

Generate all configured scripts based on `config.yaml`:
```bash
python generate.py --all
```

Generate a specific script with a reproducible seed and override the count:
```bash
python generate.py --script devanagari --count 300 --seed 42
```

## Validate Dataset

To ensure all files rendered out accurately, use the validation script:
```bash
python src/validation.py
```

## Output Structure

Results are formatted ready for use in typical Machine Learning pipelines:

```
output/
├── devanagari/
│   ├── train/
│   │   ├── Image_001.png
│   │   ├── Image_001.md
│   ├── validation/
│   └── test/
├── modi/
│   ├── train/
...
```

## Testing

Ensure your configurations and layout engines function without explicit data:
```bash
pytest tests/
```

## Upload to Hugging Face

Ensure you have your environment token set (`HF_TOKEN`). **Never hardcode your token.**
```bash
# Linux / macOS
export HF_TOKEN="your_hf_token_here"
# Windows PowerShell
$env:HF_TOKEN="your_hf_token_here"

python scripts/upload_huggingface.py --repo_id "your_username/manuscript-ocr-dataset"
```

## Limitations & Future Improvements

- Conjuncts spanning multiple heights might overlap if margin bounding is strict.
- Current bleeding simulates blur morphing. Upgraded models could use GAN-based degradation.
- No embedded handling of complex script shaping modifiers outside standard font ligatures.

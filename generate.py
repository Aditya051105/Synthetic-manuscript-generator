import argparse
import yaml
from src.dataset import generate_script_dataset
from src.utils import set_seed

def parse_args():
    parser = argparse.ArgumentParser(description="Synthetic Manuscript Generator")
    parser.add_argument('--script', type=str, choices=['devanagari', 'modi', 'sharada'], help="Which script to generate")
    parser.add_argument('--all', action='store_true', help="Generate for all scripts")
    parser.add_argument('--seed', type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument('--count', type=int, default=None, help="Override total image count per script")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    return parser.parse_args()

def main():
    args = parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    if args.seed is not None:
        config['generation']['random_seed'] = args.seed
        
    set_seed(config['generation']['random_seed'])

    scripts_to_run = []
    if args.all:
        scripts_to_run = ['devanagari', 'modi', 'sharada']
    elif args.script:
        scripts_to_run = [args.script]
    else:
        # Default behavior if nothing is specified
        parser = argparse.ArgumentParser()
        print("Please specify a script using --script <name> or use --all.")
        return

    for script in scripts_to_run:
        generate_script_dataset(config, script, args.count)

if __name__ == "__main__":
    main()

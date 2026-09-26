import os
import argparse
from huggingface_hub import HfApi, create_repo

def parse_args():
    parser = argparse.ArgumentParser(description="Upload dataset to HuggingFace")
    parser.add_argument('--repo_id', type=str, required=True, help="HF repository ID (e.g., username/manuscript-dataset)")
    parser.add_argument('--data_dir', type=str, default="output", help="Directory containing the generated dataset")
    return parser.parse_args()

def main():
    args = parse_args()
    
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable is not set. Please set it before uploading.")
        return

    api = HfApi()

    print(f"Creating/Checking repository: {args.repo_id}")
    try:
        create_repo(repo_id=args.repo_id, repo_type="dataset", token=token, exist_ok=True, private=False)
    except Exception as e:
        print(f"Error creating/checking repo: {e}")
        return
        
    print(f"Uploading files from {args.data_dir} to {args.repo_id}...")
    
    try:
        api.upload_folder(
            folder_path=args.data_dir,
            repo_id=args.repo_id,
            repo_type="dataset",
            token=token
        )
        print("Upload completed successfully!")
    except Exception as e:
        print(f"Failed to upload: {e}")

if __name__ == "__main__":
    main()

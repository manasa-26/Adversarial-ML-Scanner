import argparse
from gather_files import gather_files
from categorize_files import categorize_files
from preprocess import preprocess_files
from ats_scanning import adversarial_threat_scan

def main():
    parser = argparse.ArgumentParser(description="Adversarial Threat Scanner")
    parser.add_argument("--local_path", help="Local file or directory to scan.")
    parser.add_argument("--huggingface_repo", help="Hugging Face repo ID.")
    parser.add_argument("--s3_bucket", help="S3 bucket name to gather from.")
    parser.add_argument("--s3_prefix", help="S3 prefix (folder path) to gather from.", default="")
    args = parser.parse_args()

    # Build sources
    sources = []
    if args.local_path:
        sources.append({"type": "local", "path": args.local_path})
    if args.huggingface_repo:
        sources.append({"type": "huggingface", "repo_id": args.huggingface_repo})
    if args.s3_bucket:
        sources.append({"type": "s3", "bucket": args.s3_bucket, "prefix": args.s3_prefix})

    if not sources:
        print("[ERROR] No sources provided. Use --local_path, --huggingface_repo, or --s3_bucket.")
        return

    # 1. Gather files
    file_records = gather_files(sources)

    # 2. Categorize
    categorized = categorize_files(file_records)

    # 3. Preprocess
    preprocessed = preprocess_files(categorized)

    # 4. Scan
    adversarial_threat_scan(preprocessed)

    print("[INFO] Workflow complete. All files have been scanned.")

if __name__ == "__main__":
    main()

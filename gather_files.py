import os
import requests
import boto3
from huggingface_hub import HfApi, hf_hub_download

def gather_files(sources):
    """
    Gathers files from multiple sources and returns
    a list of dicts, each containing at least:
      {
        "source_type": "local"|"s3",
        "path": string,   # e.g. local path or S3 URI
        "size": int,      # actual file size in bytes
      }
    :param sources: List of dicts like:
        [
          {"type": "local", "path": "/path/to/local/file/or/dir"},
          {"type": "huggingface", "repo_id": "facebook/opt-125m"},
          {"type": "s3", "bucket": "mybucket", "prefix": "my/prefix"},
          ...
        ]
    :return: List of file records.
    """
    all_file_records = []
    s3_client = boto3.client("s3")
    hf_api = HfApi()

    for src in sources:
        stype = src.get("type")

        if stype == "local":
            #################################################
            # 1) LOCAL FILES
            #################################################
            local_path = src["path"]

            if os.path.isfile(local_path):
                size = os.path.getsize(local_path)
                record = {
                    "source_type": "local",
                    "path": local_path,
                    "size": size
                }
                all_file_records.append(record)

            elif os.path.isdir(local_path):
                # Example: non-recursive listing
                for filename in os.listdir(local_path):
                    full_path = os.path.join(local_path, filename)
                    if os.path.isfile(full_path):
                        size = os.path.getsize(full_path)
                        record = {
                            "source_type": "local",
                            "path": full_path,
                            "size": size
                        }
                        all_file_records.append(record)

        elif stype == "s3":
            #################################################
            # 2) S3 BUCKET
            #################################################
            bucket = src["bucket"]
            prefix = src.get("prefix", "")
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            contents = response.get("Contents", [])

            for obj in contents:
                key = obj["Key"]
                size = obj["Size"]
                s3_uri = f"s3://{bucket}/{key}"
                record = {
                    "source_type": "s3",
                    "path": s3_uri,
                    "size": size
                }
                all_file_records.append(record)

            print(f"[INFO] Gathered {len(contents)} files from S3 bucket '{bucket}' prefix '{prefix}'.")

        elif stype == "huggingface":
            #################################################
            # 3) HUGGING FACE REPO (DOWNLOAD LOCALLY)
            #################################################
            repo_id = src["repo_id"]
            # Directory where we store downloaded files
            download_dir = os.path.join("huggingface_models", repo_id.replace("/", "_"))
            os.makedirs(download_dir, exist_ok=True)

            # Retrieve file list from the Hugging Face repo
            info = hf_api.repo_info(repo_id=repo_id)
            siblings = info.siblings

            downloaded_count = 0
            for sibling in siblings:
                # Each file in the repo
                try:
                    local_path = hf_hub_download(
                        repo_id=repo_id,
                        filename=sibling.rfilename,
                        revision="main",
                        cache_dir=download_dir
                    )
                    size = os.path.getsize(local_path)

                    record = {
                        "source_type": "local",  # We now have a local copy
                        "path": local_path,
                        "size": size
                    }
                    all_file_records.append(record)
                    downloaded_count += 1

                except Exception as e:
                    print(f"⚠️ WARNING: Failed to download '{sibling.rfilename}' from {repo_id}: {e}")

            print(f"[INFO] Gathered {downloaded_count} files from Hugging Face repo '{repo_id}', stored in '{download_dir}'.")

        else:
            print(f"[WARNING] Unrecognized source type: {stype}")

    return all_file_records

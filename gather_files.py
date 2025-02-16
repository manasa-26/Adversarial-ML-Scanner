import os
import requests
import boto3
from huggingface_hub import HfApi

def gather_files(sources):
    """
    Gathers files from multiple sources and returns
    a list of dicts, each containing at least:
      {
        "source_type": "local"|"huggingface"|"s3",
        "path": string,   # e.g. local path, S3 URI, or HF direct download URL
        "size": int,      # actual file size in bytes, if known
      }
    :param sources: List of dicts like:
        [
          {"type": "local", "path": "/path/to/local/file/or/dir"},
          {"type": "huggingface", "repo_id": "mistralai/Mistral-Small-24B-Instruct-2501"},
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

        elif stype == "huggingface":
            repo_id = src["repo_id"]
            info = hf_api.repo_info(repo_id=repo_id)
            siblings = info.siblings

            for sibling in siblings:
                # Construct the direct download URL for each file
                hf_url = f"https://huggingface.co/{repo_id}/resolve/main/{sibling.rfilename}"

                # Attempt HEAD request to get content-length
                try:
                    resp = requests.head(hf_url, allow_redirects=True)
                    content_length = resp.headers.get("content-length")
                except Exception as e:
                    print(f"[WARNING] HEAD request failed for {hf_url}: {e}")
                    content_length = None

                if content_length is not None:
                    size = int(content_length)
                else:
                    size = 0  # fallback if missing

                record = {
                    "source_type": "huggingface",
                    "path": hf_url,
                    "size": size
                }
                all_file_records.append(record)

            print(f"[INFO] Gathered {len(siblings)} files from 'https://huggingface.co/{repo_id}'.")

        elif stype == "s3":
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

        else:
            print(f"[WARNING] Unrecognized source type: {stype}")

    return all_file_records

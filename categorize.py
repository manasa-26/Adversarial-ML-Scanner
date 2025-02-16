import os

SERIALIZED_EXTENSIONS = [".pkl", ".h5", ".pb", ".onnx", ".tf", ".keras"]
CODE_EXTENSIONS = [".py", ".ipynb"]
DEPENDENCY_FILES = ["requirements.txt", "package.json"]
OTHER_FILES = ["Readme", "config.json", ".gitattributes"]

def categorize_files(file_records):
    """
    Categorizes each file record into known types.
    file_records: [
       {"source_type": "local"|"huggingface"|"s3", "path": "...", "size": int},
       ...
    ]
    Returns a dict of lists, keyed by category:
      {
         "safe_tensors": [...],
         "serialized_models": [...],
         "code_files": [...],
         "dependency_files": [...],
         "others": [...]
      }
    """
    categories = {
        "safe_tensors": [],
        "serialized_models": [],
        "code_files": [],
        "dependency_files": [],
        "others": []
    }

    for record in file_records:
        # 'record' is a dict with "path" and "size"
        fpath = record["path"]
        file_name = os.path.basename(fpath)
        _, ext = os.path.splitext(file_name)

        if ext == ".safetensors":
            categories["safe_tensors"].append(record)
        elif ext in SERIALIZED_EXTENSIONS:
            categories["serialized_models"].append(record)
        elif ext in CODE_EXTENSIONS:
            categories["code_files"].append(record)
        elif file_name in DEPENDENCY_FILES:
            categories["dependency_files"].append(record)
        else:
            categories["others"].append(record)

    # Print summary
    print("[INFO] Categorized files:")
    print(f"  SafeTensors: {len(categories['safe_tensors'])}")
    print(f"  Serialized Models: {len(categories['serialized_models'])}")
    print(f"  Code Files: {len(categories['code_files'])}")
    print(f"  Dependency Files: {len(categories['dependency_files'])}")
    print(f"  Others: {len(categories['others'])}")

    return categories

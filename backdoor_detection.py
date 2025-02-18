def run_backdoor_detection(file_path, file_bytes):
    """
    Detects potential backdoor triggers in a model file.
    Handles both text and binary files correctly.
    """
    warnings = []

    # Ensure we are working with bytes for binary files
    if isinstance(file_bytes, str):
        file_bytes = file_bytes.encode("utf-8", errors="ignore")  # Convert to bytes if needed

    # Naive example: Check for known "TRIGGER" patterns in model files
    if b"TRIGGER" in file_bytes:
        warnings.append(f"⚠️ Potential backdoor trigger found in {file_path}!")

    return warnings


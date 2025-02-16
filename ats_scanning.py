import os
import logging

# 1. Configure Logging
logger = logging.getLogger("adversarial_scanner")
logger.setLevel(logging.INFO)

# Optional: Configure a console handler with a specific format
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Import your analysis modules
from analysis.secrets_detection import run_secrets_detection
from analysis.pii_detection import run_pii_detection
from analysis.backdoor_detection import run_backdoor_detection
from analysis.dependency_vuln import run_dependency_vuln_check
from analysis.code_injection import run_code_injection_check
from analysis.threat_signature import run_threat_signature_check

def adversarial_threat_scan(categorized_files):
    """
    Integrates various security checks and logs with Python's logging module
    at INFO or WARNING levels.
    """
    logger.info("Starting Adversarial Threat Scanning...")

    for category, file_records in categorized_files.items():
        for record in file_records:
            path = record["path"]
            size = record["size"]  # from gather_files
            logger.info(f"Scanning {path} (Category: {category})...")
            logger.info(f"File size: {size} bytes.")

            warnings = []

            # Decide how to read the file: text vs. binary
            if category in ["code_files", "dependency_files", "others"]:
                # Attempt text read
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except:
                    content = ""
            else:
                # For model weights or other binary data
                try:
                    with open(path, "rb") as f:
                        content = f.read()
                except:
                    content = b""

            # --- 1. Secrets detection (detect-secrets / truffleHog) ---
            if os.path.isfile(path):
                warnings += run_secrets_detection(path, content)  # FIXED: Passing both arguments

            # --- 2. PII detection (Presidio or naive) ---
            if isinstance(content, bytes):
                text_for_pii = content.decode("utf-8", errors="ignore")
            else:
                text_for_pii = content
            warnings += run_pii_detection(path, text_for_pii)

            # --- 3. Backdoor detection (if it's a model) ---
            if category in ["safe_tensors", "serialized_models"]:
                warnings += run_backdoor_detection(path, content)  # FIXED: Pass content as well

            # --- 4. Dependency vulnerabilities (Safety / pip-audit) ---
            if category == "dependency_files":
                if isinstance(content, bytes):
                    text_for_dep = content.decode("utf-8", errors="ignore")
                else:
                    text_for_dep = content
                warnings += run_dependency_vuln_check(path, text_for_dep)

            # --- 5. Code injection (Bandit) ---
            if category == "code_files":
                if isinstance(content, bytes):
                    text_for_code = content.decode("utf-8", errors="ignore")
                else:
                    text_for_code = content
                warnings += run_code_injection_check(path, text_for_code)

            # --- 6. Threat signature matching ---
            warnings += run_threat_signature_check(path, content)  # FIXED: Ensure content is passed

            # Log warnings
            for w in warnings:
                logger.warning(w)

            logger.info(f"File {path} passed all scans (warnings above if any).")

    logger.info("Workflow complete. All files have been scanned.")

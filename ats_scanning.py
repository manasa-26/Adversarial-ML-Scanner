import os
import logging

# Configure Logging
logger = logging.getLogger("adversarial_scanner")
logger.setLevel(logging.INFO)

# Import security scan modules
from analysis.secrets_detection import run_secrets_detection
from analysis.pii_detection import run_pii_detection
from analysis.backdoor_detection import run_backdoor_detection
from analysis.dependency_vuln import run_dependency_vuln_check
from analysis.code_injection import run_code_injection_check
from analysis.threat_signature import run_threat_signature_check

# Categorization Dictionary
risk_categories = {
    "Total Notebook & Requirement files Vulnerabilities Found": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
    "Total Model Vulnerabilities Found": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
}

# Risk Level Mapping
def categorize_risk(warning):
    """Classifies the warning into Critical, High, Medium, or Low severity."""
    if any(term in warning for term in ["eval", "exec", "compile(", "subprocess", "leaked API key", "wget"]):
        return "Critical"
    elif any(term in warning for term in ["Ignore previous instructions", "Bypass security measures", "Generate fake news"]):
        return "High"
    elif any(term in warning for term in ["Outdated dependency", "Phone numbers", "Emails found"]):
        return "Medium"
    else:
        return "Low"

def adversarial_threat_scan(categorized_files):
    """Runs security checks on scanned files and logs warnings."""
    logger.info(" Starting Adversarial Threat Scanning...")

    for category, file_records in categorized_files.items():
        for record in file_records:
            path = record["path"]
            size = record["size"]
            logger.info(f" Scanning {path} (Category: {category})...")
            logger.info(f" File size: {size} bytes.")

            warnings = []
            # Read the file content (text or binary)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                content = b""

            # 1Screts Detection
            warnings += run_secrets_detection(path, content)

            # 2️ PII Detection
            warnings += run_pii_detection(path, content)

            # 3️ Backdoor Detection (for AI models)
            if category in ["safe_tensors", "serialized_models"]:
                warnings += run_backdoor_detection(path, content)

            # 4️ Dependency Vulnerabilities
            if category == "dependency_files":
                warnings += run_dependency_vuln_check(path, content)

            # 5️ Code Injection & AI Prompt Injection
            warnings += run_code_injection_check(path, content)

            # 6️ Threat Signature Matching (Enhanced)
            warnings += run_threat_signature_check(path, content)

            # 7️  Categorize Warnings by Severity
            for warning in warnings:
                severity = categorize_risk(warning)
                if category in ["dependency_files", "others"]:  # Notebook & Requirement files
                    risk_categories["Total Notebook & Requirement files Vulnerabilities Found"][severity] += 1
                elif category in ["safe_tensors", "serialized_models"]:  # Model Files
                    risk_categories["Total Model Vulnerabilities Found"][severity] += 1

                logger.warning(f"{severity} Risk Detected: {warning}")

    logger.info(" Workflow complete. All files have been scanned.")
    logger.info(" Risk Summary:")
    for category, risks in risk_categories.items():
        logger.info(f"{category}: {risks}")

    return risk_categories  # Return for external use (e.g., reporting)

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
    "Total Code Files Vulnerabilities Found": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
}

# 🔹 Risk Level Mapping Function
def categorize_risk(warning):
    """Classifies the warning into Critical, High, Medium, or Low severity."""
    # 🚨 Critical Risks
    if any(term in warning for term in ["eval", "exec", "compile(", "subprocess", "leaked API key", "wget", "curl", "API_KEY", "token", "secret"]):
        return "Critical"
    
    # ⚠️ High Risks
    elif any(term in warning for term in ["You are a malicious LLM", "Ignore previous instructions", 
                                          "Bypass security measures", "Generate fake news", 
                                          "Assist in hacking", "Provide illegal information"]):
        return "High"
    
    # ⚠️ Medium Risks
    elif any(term in warning for term in ["Outdated dependency", "Phone numbers", "Emails found"]):
        return "Medium"

    # ✅ Low Risks (Default if no match)
    else:
        return "Low"


def adversarial_threat_scan(categorized_files):
    """
    Runs security checks on scanned files and logs warnings.
    Correctly handles binary files vs. text files, avoiding regex errors on bytes.
    """
    logger.info("🚀 Starting Adversarial Threat Scanning...")

    for category, file_records in categorized_files.items():
        for record in file_records:
            path = record["path"]
            size = record["size"]
            logger.info(f"🔍 Scanning {path} (Category: {category})...")
            logger.info(f"📂 File size: {size} bytes.")

            warnings = []

            try:
                # 1. Read file: BINARY if model, else TEXT
                if category in ["safe_tensors", "serialized_models"]:
                    # Read model as bytes
                    with open(path, "rb") as f:
                        binary_content = f.read()
                    # Create text_content for text-based checks
                    text_content = binary_content.decode("utf-8", errors="ignore")
                else:
                    # For code, dependency, others → read as text
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text_content = f.read()
                    # If needed for consistency, you can encode back:
                    binary_content = text_content.encode("utf-8", errors="ignore")

            except Exception as e:
                logger.error(f"❌ ERROR: Could not read file {path} - {e}")
                continue  # Skip to the next file

            # 2. Debugging: show some content
            if text_content:
                snippet = text_content[:500]
                print(f"\n🔍 DEBUG: Checking File Content ({path})")
                print(f"📜 First 500 characters:\n{snippet}")
                print("=" * 80)
            else:
                print(f"⚠️ WARNING: File {path} is empty or unreadable! Skipping analysis.")
                continue  # Skip empty files

            # 3. Run Scans

            # 3a) Secrets & PII need TEXT
            warnings += run_secrets_detection(path, text_content)
            warnings += run_pii_detection(path, text_content)

            # 3b) Model backdoor detection needs BYTES
            if category in ["safe_tensors", "serialized_models"]:
                warnings += run_backdoor_detection(path, binary_content)

            # 3c) Dependency vulnerabilities (TEXT-based)
            if category == "dependency_files":
                warnings += run_dependency_vuln_check(path, text_content)

            # 3d) Code injection & AI prompt injection (TEXT-based)
            warnings += run_code_injection_check(path, text_content)

            # 3e) Threat signature check
            # Decide if your threat_signature can handle bytes or text. 
            # If it's doing regex or phrase matching, pass text_content. 
            warnings += run_threat_signature_check(path, text_content)

            # 4. Categorize Warnings
            for warning in warnings:
                severity = categorize_risk(warning)

                # Assign risks to the correct category
                if category in ["dependency_files", "others"]:
                    risk_categories["Total Notebook & Requirement files Vulnerabilities Found"][severity] += 1
                elif category in ["safe_tensors", "serialized_models"]:
                    risk_categories["Total Model Vulnerabilities Found"][severity] += 1
                else:
                    risk_categories["Total Code Files Vulnerabilities Found"][severity] += 1

                logger.warning(f"⚠️ {severity} Risk Detected: {warning}")

    # 5. Print Final Summary
    logger.info("\n📊 [INFO] Final Risk Summary:")
    print("\n📊 [INFO] Final Risk Summary:")
    print("=" * 50)

    for cat, risks in risk_categories.items():
        print(f"\n📝 {cat}:")
        for sev, count in risks.items():
            print(f"   🔹 {sev}: {count}")

    print("\n✅ [INFO] Workflow complete. All files have been scanned.")
    print("=" * 50)

    return risk_categories  # Return for external use (e.g., reporting)

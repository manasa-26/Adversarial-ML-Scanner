import re

# Example naive regex for emails & phone numbers.
# Real PII detection might use Presidio or other advanced techniques.
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

def run_pii_detection(file_path, file_content):
    """
    Checks if file content might contain PII (e.g., email, phone).
    In real usage, you'd:
      1) Call Presidio or other library
      2) Possibly do dynamic tests (adversarial inputs)
    Returns a list of warning messages if found.
    """
    warnings = []
    emails = EMAIL_REGEX.findall(file_content)
    phones = PHONE_REGEX.findall(file_content)

    if emails:
        warnings.append(f"Possible email addresses in {file_path}: {emails}")
    if phones:
        warnings.append(f"Possible phone numbers in {file_path}: {phones}")

    return warnings

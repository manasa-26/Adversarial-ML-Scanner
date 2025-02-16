RISKY_CALLS = ["eval", "exec", "compile(", "os.system", "subprocess"]

def run_code_injection_check(file_path, file_content):
    """
    Looks for usage of eval, exec, or other risky calls.
    Real solutions might parse Python AST or use Bandit.
    """
    warnings = []
    for call in RISKY_CALLS:
        if call in file_content:
            warnings.append(f"Potential code injection risk in {file_path}: found '{call}'")
    return warnings

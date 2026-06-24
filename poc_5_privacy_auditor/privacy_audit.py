import os
import re
import sys

# ==============================================================================
# ANTIGRAVITY LESSON 6: Static Code Analysis & Regulatory Compliance
# 1. Static Code Analysis: Reading code files line-by-line *without* running them,
#    using pattern matching to find security or compliance issues before release.
# 2. Privacy Compliance (GDPR / CCPA / HIPAA): Laws in Europe, California, and the
#    US that impose massive fines (up to 4% of global revenue) if companies leak 
#    personal user data (PII) or store passwords and keys in plain text.
# ==============================================================================

# Regular expressions (Regex) to detect compliance issues
PATTERNS = {
    # 1. Hardcoded Secrets (finding things like API_KEY = "12345", supporting special characters like !)
    "Hardcoded Secret / API Key": re.compile(
        r'(?i)(api_key|secret|password|passwd|private_key|token|auth_token)\s*[:=]\s*["\'][a-zA-Z0-9_\-!@#\$%\^&\*\(\)\+]{8,}["\']'
    ),
    
    # 2. Sensitive Data Logging (finding logs that print passwords, cards, emails, SSNs)
    # Supports console.log, print, logger.debug, logger.info, logger.error, etc.
    "Sensitive Data Logging": re.compile(
        r'(?i)(console\.log|print|logger\.(info|debug|error|warn|log)|log\.(info|debug|error|warn))\(.*?(password|credit_card|card_num|ssn|social_security|email|auth|token).*?\)'
    ),
    
    # 3. Non-secure Cookie Settings (cookies missing Secure or HttpOnly flags)
    "Insecure Cookie Configuration": re.compile(
        r'(?i)document\.cookie\s*=\s*["\'](?!.*;\s*secure)(?!.*;\s*httponly).*["\']'
    )
}

TARGET_DIR = "sample_project"
REPORT_DIR = "reports"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def create_sample_project_files():
    """
    Generates dummy code files with intentional privacy leaks
    so the compliance scanner has real files to audit.
    """
    auth_js_content = """// Sample Authentication File
const db = require("./db");

const API_KEY = "DUMMY_SECRET_KEY_FOR_TESTING_PURPOSES_ONLY"; // Leak: Hardcoded API Key

function loginUser(username, password) {
    console.log("Attempting login for user: " + username);
    
    if (db.verify(username, password)) {
        // Leak: Logging raw user password! (Severe GDPR/CCPA violation)
        console.log(`Login successful. User session started with password: ${password}`);
        return true;
    }
    return false;
}

// Leak: Insecure Cookie without Secure or HttpOnly flags
document.cookie = "session_token=xyz123; path=/;";
"""

    payment_py_content = """# Sample Payment Processing File
import logging
logger = logging.getLogger("payment_gateway")

DB_PASSWORD = "SuperSecretDbPassword123!" # Leak: Hardcoded Database Password

def process_transaction(user_email, credit_card_number, amount):
    logger.info(f"Processing transaction for user: {user_email}")
    
    try:
        # Leak: Logging credit card number to files! (PCI-DSS & CCPA violation)
        logger.debug(f"DEBUG: Attempting charge of ${amount} on Card: {credit_card_number}")
        return True
    except Exception as e:
        logger.error(f"Failed transaction for {user_email}: {e}")
        return False
"""

    with open(os.path.join(TARGET_DIR, "auth.js"), "w", encoding="utf-8") as f:
        f.write(auth_js_content)
        
    with open(os.path.join(TARGET_DIR, "payment.py"), "w", encoding="utf-8") as f:
        f.write(payment_py_content)
        
    print(f"[+] Generated mock developer code files inside: '{TARGET_DIR}'")

def scan_file_for_compliance(file_path):
    """
    Reads a file line-by-line and applies the regular expressions
    to flag GDPR/CCPA compliance leaks.
    """
    findings = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                clean_line = line.strip()
                
                for issue_type, pattern in PATTERNS.items():
                    if pattern.search(clean_line):
                        findings.append({
                            "file": os.path.basename(file_path),
                            "line_num": idx,
                            "line_content": clean_line,
                            "issue": issue_type
                        })
    except Exception as e:
        print(f"[!] Error reading file {file_path}: {e}")
        
    return findings

def generate_audit_report(all_findings):
    """
    Generates a professional markdown report summarizing the findings
    and listing compliance recommendations for CCPA/GDPR/HIPAA.
    """
    report_path = os.path.join(REPORT_DIR, "privacy_compliance_report.md")
    
    report_content = f"""# PRIVACY COMPLIANCE AUDIT REPORT (GDPR / CCPA / HIPAA)
============================================================
**Scan Date:** {os.date if hasattr(os, 'date') else '2026-06-06'}
**Audited Directory:** {TARGET_DIR}/

## Summary of Findings
Total Compliance Issues Detected: **{len(all_findings)}**

| Issue Type | File | Line | Severity |
|---|---|---|---|
"""
    
    for f in all_findings:
        severity = "HIGH"
        if "Cookie" in f["issue"]:
            severity = "MEDIUM"
        report_content += f"| {f['issue']} | {f['file']} | {f['line_num']} | **{severity}** |\n"
        
    report_content += "\n## Detailed Findings & Compliance Code Diffs\n"
    
    for f in all_findings:
        report_content += f"""
### [!] {f['issue']} found in `{f['file']}` (Line {f['line_num']})
*   **Violating Code:**
    ```javascript
    {f['line_content']}
    ```
"""
        # Offer customized compliance solutions based on the type of issue
        if "Secret" in f["issue"]:
            report_content += """*   **CCPA/GDPR Mitigation:** Never hardcode API keys or database credentials in source code. Move them to environment variables (`.env` files) and load them using system processes.
"""
        elif "Logging" in f["issue"]:
            report_content += """*   **CCPA/GDPR Mitigation:** Avoid writing personally identifiable information (PII) like passwords or card numbers to system logs. Redact or mask the data (e.g. print `CC: ****-****-****-1234` or use tokenized identifiers).
"""
        elif "Cookie" in f["issue"]:
            report_content += """*   **CCPA/GDPR Mitigation:** Ensure all session and identifier cookies set via code utilize the `Secure` flag (transmits only over HTTPS) and the `HttpOnly` flag (prevents scripts from accessing the session identifiers, protecting against XSS).
"""

    report_content += "\n============================================================\n"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(report_content)
    print(f"[SUCCESS] Compliance audit complete! Saved report to: {report_path}")

def main():
    print("=========================================================")
    print("      ANTIGRAVITY PRIVACY COMPLIANCE CODE AUDITOR        ")
    print("=========================================================\n")
    
    # 1. Create the dummy files
    create_sample_project_files()
    
    # 2. Scan the directory
    all_findings = []
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            # Only scan javascript and python source code files
            if file.endswith((".js", ".py")):
                file_path = os.path.join(root, file)
                findings = scan_file_for_compliance(file_path)
                all_findings.extend(findings)
                
    # 3. Generate Report
    generate_audit_report(all_findings)

if __name__ == "__main__":
    main()

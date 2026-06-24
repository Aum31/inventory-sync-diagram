# PRIVACY COMPLIANCE AUDIT REPORT (GDPR / CCPA / HIPAA)
============================================================
**Scan Date:** 2026-06-06
**Audited Directory:** sample_project/

## Summary of Findings
Total Compliance Issues Detected: **7**

| Issue Type | File | Line | Severity |
|---|---|---|---|
| Hardcoded Secret / API Key | auth.js | 4 | **HIGH** |
| Sensitive Data Logging | auth.js | 11 | **HIGH** |
| Insecure Cookie Configuration | auth.js | 18 | **MEDIUM** |
| Hardcoded Secret / API Key | payment.py | 5 | **HIGH** |
| Sensitive Data Logging | payment.py | 8 | **HIGH** |
| Sensitive Data Logging | payment.py | 12 | **HIGH** |
| Sensitive Data Logging | payment.py | 15 | **HIGH** |

## Detailed Findings & Compliance Code Diffs

### [!] Hardcoded Secret / API Key found in `auth.js` (Line 4)
*   **Violating Code:**
    ```javascript
    const API_KEY = "DUMMY_SECRET_KEY_FOR_TESTING_PURPOSES_ONLY"; // Leak: Hardcoded API Key
    ```
*   **CCPA/GDPR Mitigation:** Never hardcode API keys or database credentials in source code. Move them to environment variables (`.env` files) and load them using system processes.

### [!] Sensitive Data Logging found in `auth.js` (Line 11)
*   **Violating Code:**
    ```javascript
    console.log(`Login successful. User session started with password: ${password}`);
    ```
*   **CCPA/GDPR Mitigation:** Avoid writing personally identifiable information (PII) like passwords or card numbers to system logs. Redact or mask the data (e.g. print `CC: ****-****-****-1234` or use tokenized identifiers).

### [!] Insecure Cookie Configuration found in `auth.js` (Line 18)
*   **Violating Code:**
    ```javascript
    document.cookie = "session_token=xyz123; path=/;";
    ```
*   **CCPA/GDPR Mitigation:** Ensure all session and identifier cookies set via code utilize the `Secure` flag (transmits only over HTTPS) and the `HttpOnly` flag (prevents scripts from accessing the session identifiers, protecting against XSS).

### [!] Hardcoded Secret / API Key found in `payment.py` (Line 5)
*   **Violating Code:**
    ```javascript
    DB_PASSWORD = "SuperSecretDbPassword123!" # Leak: Hardcoded Database Password
    ```
*   **CCPA/GDPR Mitigation:** Never hardcode API keys or database credentials in source code. Move them to environment variables (`.env` files) and load them using system processes.

### [!] Sensitive Data Logging found in `payment.py` (Line 8)
*   **Violating Code:**
    ```javascript
    logger.info(f"Processing transaction for user: {user_email}")
    ```
*   **CCPA/GDPR Mitigation:** Avoid writing personally identifiable information (PII) like passwords or card numbers to system logs. Redact or mask the data (e.g. print `CC: ****-****-****-1234` or use tokenized identifiers).

### [!] Sensitive Data Logging found in `payment.py` (Line 12)
*   **Violating Code:**
    ```javascript
    logger.debug(f"DEBUG: Attempting charge of ${amount} on Card: {credit_card_number}")
    ```
*   **CCPA/GDPR Mitigation:** Avoid writing personally identifiable information (PII) like passwords or card numbers to system logs. Redact or mask the data (e.g. print `CC: ****-****-****-1234` or use tokenized identifiers).

### [!] Sensitive Data Logging found in `payment.py` (Line 15)
*   **Violating Code:**
    ```javascript
    logger.error(f"Failed transaction for {user_email}: {e}")
    ```
*   **CCPA/GDPR Mitigation:** Avoid writing personally identifiable information (PII) like passwords or card numbers to system logs. Redact or mask the data (e.g. print `CC: ****-****-****-1234` or use tokenized identifiers).

============================================================

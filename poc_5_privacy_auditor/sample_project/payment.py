# Sample Payment Processing File
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

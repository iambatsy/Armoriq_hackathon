import hmac
import hashlib

def verify_armor_intent(message: str, token: str, secret: str) -> bool:
    """
    Verifies the HMAC signature. 
    Ensures the data wasn't changed after ArmorIQ signed it.
    """
    if not token or not secret:
        return False

    # Re-calculate the hash using your secret key
    expected_token = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Compare the provided token with the expected one
    return hmac.compare_digest(expected_token, token)
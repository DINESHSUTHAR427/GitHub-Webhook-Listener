import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()


def verify_github_signature(payload: bytes, signature: str) -> bool:
    if not signature or not WEBHOOK_SECRET:
        return False
    
    if not signature.startswith("sha256="):
        return False
    
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET,
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

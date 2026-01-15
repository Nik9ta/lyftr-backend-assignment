import hmac
import hashlib
from app.config import settings

def verify_signature(raw_body: bytes, signature: str) -> bool:
    expected = hmac.new(
        settings.WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

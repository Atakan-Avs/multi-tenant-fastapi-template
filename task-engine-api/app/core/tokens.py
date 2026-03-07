import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import settings


def generate_refresh_token() -> str:
    # URL-safe uzun random token
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """
    Refresh token hash'ini DB'de saklarız.
    Pepper ekleyerek (server-side secret) DB leak durumunda saldırıyı zorlaştırırız.
    """
    pepper = getattr(settings, "refresh_token_pepper", None)
    if not pepper:
        raise RuntimeError("REFRESH_TOKEN_PEPPER is required")

    payload = (pepper + token).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def refresh_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=int(settings.jwt_refresh_token_exp_days))
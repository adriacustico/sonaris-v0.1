"""Authentication and password helper placeholders."""

from datetime import UTC, datetime, timedelta


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """Create a development token string.

    Replace this with signed JWT generation before production use.
    """
    expires_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    return f"dev-token:{subject}:{int(expires_at.timestamp())}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password placeholder for early development."""
    return bool(plain_password) and hashed_password.startswith("dev:")

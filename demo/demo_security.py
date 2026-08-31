"""Authentication boundary for the SecureVault recruiter demonstration."""

from __future__ import annotations

import hashlib
import hmac


DEMO_PASSWORD = "DebugRohit@1995"


def _hash_demo_password(password: str) -> bytes:
    """Create a deterministic SHA-256 digest for demo authentication."""
    return hashlib.sha256(password.encode("utf-8")).digest()


_DEMO_PASSWORD_DIGEST = _hash_demo_password(DEMO_PASSWORD)


def authenticate_demo_user(password: str) -> bool:
    """
    Authenticate the recruiter against the isolated demo account.

    This authentication mechanism is intentionally independent of the
    production SecureVault master-password files.
    """
    if not isinstance(password, str):
        return False

    candidate_digest = _hash_demo_password(password)

    return hmac.compare_digest(
        candidate_digest,
        _DEMO_PASSWORD_DIGEST,
    )
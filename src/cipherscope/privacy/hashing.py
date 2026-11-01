from __future__ import annotations

import hashlib
import hmac
import os
from functools import lru_cache

MIN_SALT_LENGTH = 16
PLACEHOLDER_SALTS = frozenset(
    {
        "local-demo-salt-change-me",
        "replace-with-a-private-random-salt",
        "replace-with-at-least-16-random-characters",
        "change-me",
        "changeme",
        "secret",
        "test",
    }
)


class InsecureSaltError(RuntimeError):
    """Raised when no usable HMAC salt is configured."""


def resolve_salt(salt: str | None = None) -> str:
    """Return a validated HMAC salt, refusing missing, short, or placeholder values."""
    value = salt if salt is not None else os.environ.get("CIPHERSCOPE_HASH_SALT")
    if value is None or not value.strip():
        raise InsecureSaltError(
            "CIPHERSCOPE_HASH_SALT is not set. Set a private random salt of at least "
            f"{MIN_SALT_LENGTH} characters before processing any capture."
        )
    if value.strip().lower() in PLACEHOLDER_SALTS:
        raise InsecureSaltError(
            "CIPHERSCOPE_HASH_SALT still holds a documented placeholder value. "
            "Generate a private random salt first."
        )
    if len(value) < MIN_SALT_LENGTH:
        raise InsecureSaltError(
            f"CIPHERSCOPE_HASH_SALT must be at least {MIN_SALT_LENGTH} characters long."
        )
    return value


@lru_cache(maxsize=16384)
def _hash_identifier(value: str, salt: str) -> str:
    digest = hmac.new(salt.encode("utf-8"), value.encode("utf-8"), hashlib.sha256)
    return "h:" + digest.hexdigest()[:24]


def hash_identifier(value: str, salt: str | None = None) -> str:
    """Return a keyed, truncated pseudonym for an endpoint identifier."""
    return _hash_identifier(value, resolve_salt(salt))


def salt_fingerprint(salt: str | None = None) -> str:
    """Return a short digest that identifies a salt without storing it."""
    resolved = resolve_salt(salt)
    return hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:12]

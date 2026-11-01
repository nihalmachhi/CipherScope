from __future__ import annotations

import hashlib
import hmac
import os


def hash_identifier(value: str, salt: str | None = None) -> str:
    key = (salt or os.getenv("CIPHERSCOPE_HASH_SALT", "local-demo-salt-change-me")).encode()
    return "h:" + hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:24]

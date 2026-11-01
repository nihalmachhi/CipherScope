from __future__ import annotations

import os

# Tests exercise the privacy pipeline, which fails closed without a real salt.
os.environ.setdefault("CIPHERSCOPE_HASH_SALT", "pytest-salt-not-for-production")
os.environ.setdefault("CIPHERSCOPE_ADMIN_TOKEN", "pytest-admin-token-not-for-production")

# Threat model

## In scope

- Offline analysis of captures the operator is authorized to process.
- Accidental exposure of endpoint identifiers in stored data.
- Leakage between train and test splits via host, capture or environment.

## Out of scope

- Live capture, interception or decryption.
- Production deployment and multi-tenant isolation.
- Claims of real-world detection accuracy from synthetic data.

## Controls

- Only headers, sizes, timing and visible metadata are retained.
- Endpoint identifiers are HMAC-hashed before storage; raw IPs, ports and absolute timestamps are never model features.
- `CIPHERSCOPE_HASH_SALT` is required, at least 16 characters and not a known placeholder; the service fails closed without it.
- Reports record the config hash, git SHA, seed list and library versions.
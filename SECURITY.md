# Security policy

## Scope

CipherScope is a local, offline analysis toolkit for **authorized** packet captures.
It reads packet headers and sizes only. It never decrypts traffic, inspects payload
bytes, or captures from a live interface.

Do not use this project on networks or data you do not own or have written
permission to analyze.

## Reporting a vulnerability

Please report security issues privately by opening a
[GitHub security advisory](https://github.com/nihalmachhi/CipherScope/security/advisories/new).
Do not open a public issue for a vulnerability that could expose users.

Include the affected version or commit, a reproduction, and the impact you
observed. We aim to acknowledge reports within seven days.

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Known boundaries

- Endpoint identifiers are HMAC-hashed with `CIPHERSCOPE_HASH_SALT` before storage.
  Rotating the salt changes every pseudonym; old and new identifiers are not linkable.
- The application fails closed when the salt or admin token is missing, shorter than
  16 characters, or still a documented placeholder.
- Absolute timestamps, raw IP addresses and ports are never model features.
- Synthetic datasets are clearly labelled synthetic and never presented as evidence
  of real-world detection.
- The API binds to loopback in the supplied compose file and requires an admin token
  for write endpoints.

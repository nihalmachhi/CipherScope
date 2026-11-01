from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

TRACKED_LIBRARIES = (
    "numpy",
    "scikit-learn",
    "scapy",
    "fastapi",
    "pydantic",
    "PyYAML",
)


def git_sha(directory: str | Path = ".") -> str | None:
    """Return the current commit, or ``None`` when git is unavailable."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def config_hash(config: dict[str, Any]) -> str:
    """Return a stable digest of an experiment configuration."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def library_versions() -> dict[str, str]:
    """Return installed versions for the libraries that affect a report."""
    versions: dict[str, str] = {"python": platform.python_version()}
    for name in TRACKED_LIBRARIES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def build_metadata(
    config: dict[str, Any], seeds: list[int], salt_fingerprint: str | None
) -> dict[str, Any]:
    """Collect the reproducibility metadata stored in every report."""
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "git_sha": git_sha(),
        "config_hash": config_hash(config),
        "seeds": seeds,
        "library_versions": library_versions(),
        "salt_fingerprint": salt_fingerprint,
        "config": config,
    }

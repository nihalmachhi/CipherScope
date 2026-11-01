from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration read from ``CIPHERSCOPE_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="CIPHERSCOPE_", env_file=".env", extra="ignore"
    )

    data_path: str = "data/demo_flows.jsonl"
    report_path: str = "output/reports/synthetic-evaluation.json"
    cors_origin: str = "http://127.0.0.1:5173"
    admin_token: str = "local-demo-admin-token"

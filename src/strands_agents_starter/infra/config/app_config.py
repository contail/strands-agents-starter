from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment/.env."""

    llm_base_url: str
    llm_model: str
    request_timeout_seconds: float = 60.0

    @staticmethod
    def load(dotenv: bool = True) -> "AppConfig":
        if dotenv:
            load_dotenv()
        base_url = os.getenv("LLM_BASE_URL", "")
        model = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
        timeout = float(os.getenv("HTTP_TIMEOUT", "60"))
        return AppConfig(llm_base_url=base_url, llm_model=model, request_timeout_seconds=timeout)



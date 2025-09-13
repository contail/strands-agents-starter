from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Protocol

import httpx

from strands_agents_starter.infra.config.app_config import AppConfig


class LLMClientProtocol(Protocol):
    """Port for LLM client implementations."""

    @property
    def config(self) -> AppConfig: ...

    def list_models(self) -> Dict[str, Any]: ...

    def generate(self, prompt: str, model: str | None = None, **kwargs: Any) -> str: ...

    def get_preferred_model_name(self) -> str: ...


class HttpLLMClient:
    """HTTP-based LLM client (infra adapter)."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        base = (config.llm_base_url or "").strip()
        if base:
            self._client = httpx.Client(
                base_url=base,
                timeout=config.request_timeout_seconds,
            )
        else:
            # No base URL set — client still created, but endpoints will error if used.
            self._client = httpx.Client(
                timeout=config.request_timeout_seconds,
            )

    @property
    def config(self) -> AppConfig:
        return self._config

    def list_models(self) -> Dict[str, Any]:
        base = (self._config.llm_base_url or "").strip()
        if not base:
            raise RuntimeError("LLM_BASE_URL is not configured. Set it via environment or .env.")
        response = self._client.get("/api/tags")
        response.raise_for_status()
        return response.json()

    def _select_latest_model(self) -> str:
        tags = self.list_models()
        models = tags.get("models", [])
        def parse_ts(s: str) -> datetime:
            # Accept ISO8601 with 'Z'
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s)
        latest = None
        latest_ts = None
        for m in models:
            ts_raw = m.get("modified_at") or m.get("modifiedAt")
            try:
                ts = parse_ts(str(ts_raw)) if ts_raw else datetime.min
            except Exception:
                ts = datetime.min
            if latest is None or ts > latest_ts:  # type: ignore[operator]
                latest = m
                latest_ts = ts
        # Prefer 'model' field; fallback to 'name'
        if latest:
            return str(latest.get("model") or latest.get("name"))
        return self._config.llm_model

    def get_preferred_model_name(self) -> str:
        configured = self._config.llm_model
        if str(configured).lower() == "auto":
            return self._select_latest_model()
        return configured

    def generate(self, prompt: str, model: str | None = None, **kwargs: Any) -> str:
        """Generate a completion.

        Tries to force non-streaming first. If the server returns a streaming
        NDJSON/SSE body, falls back to line-wise JSON accumulation.
        """
        base = (self._config.llm_base_url or "").strip()
        if not base:
            raise RuntimeError("LLM_BASE_URL is not configured. Set it via environment or .env.")
        payload: Dict[str, Any] = {
            "model": model or self.get_preferred_model_name(),
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }
        response = self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        try:
            data = response.json()
            return data.get("response") or data.get("text") or ""
        except Exception:
            # Fallback: parse NDJSON / SSE lines
            text = response.text
            parts: list[str] = []
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                try:
                    obj = json.loads(line)
                except Exception:
                    # As a last resort, ignore non-JSON lines
                    continue
                if isinstance(obj, dict):
                    chunk = obj.get("response") or obj.get("text") or ""
                    if chunk:
                        parts.append(str(chunk))
            return "".join(parts)



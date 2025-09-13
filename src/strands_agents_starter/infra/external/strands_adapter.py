from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Optional

from ...application.dto.message import AgentMessage
from .llm_client import LLMClientProtocol


@dataclass(frozen=True)
class StrandsConfig:
    """Configuration for Strands-based agent runner."""

    workflow: Optional[str] = None


# Discover Strands SDK at import time (optional dependency)
StrandsAgent = None
StrandsOllamaModel = None
try:  # pragma: no cover
    _strands = importlib.import_module("strands")
    StrandsAgent = getattr(_strands, "Agent", None)
    try:
        _ollama_mod = importlib.import_module("strands.models.ollama")
        StrandsOllamaModel = getattr(_ollama_mod, "OllamaModel", None)
    except ImportError:  # Specific for missing Ollama model module
        StrandsOllamaModel = None
except ImportError:  # Strands SDK not installed
    StrandsAgent = None
    StrandsOllamaModel = None


class StrandsAgentAdapter:
    """Adapter that runs via Strands SDK when available; falls back to LLM client."""

    def __init__(self, client: LLMClientProtocol, config: Optional[StrandsConfig] = None) -> None:
        self._client = client
        self._config = config or StrandsConfig()
        self._provider_name = os.getenv("STRANDS_PROVIDER", "ollama").lower()

    def available(self) -> bool:
        return StrandsAgent is not None

    def run(self, messages: list[AgentMessage]) -> str:
        # Fallback if SDK missing
        if not self.available():
            prompt = self._messages_to_prompt(messages)
            return self._client.generate(prompt)

        # If user requested Ollama but provider class is missing, fallback to local LLM
        if self._provider_name == "ollama" and StrandsOllamaModel is None:
            prompt = self._messages_to_prompt(messages)
            return self._client.generate(prompt)

        try:  # pragma: no cover
            model_name = os.getenv("LLM_MODEL") or self._client.config.llm_model
            base_url = os.getenv("LLM_BASE_URL") or self._client.config.llm_base_url

            if self._provider_name == "ollama" and StrandsOllamaModel is not None:
                provider = StrandsOllamaModel(host=base_url, model_id=model_name)
                if StrandsAgent is None:
                    raise RuntimeError("Strands SDK not available")
                agent = StrandsAgent(model=provider)
            else:
                # Unknown provider requested; fallback to local LLM
                prompt = self._messages_to_prompt(messages)
                return self._client.generate(prompt)

            prompt = self._messages_to_prompt(messages)
            result = agent(prompt)
            if isinstance(result, str):
                return result
            if hasattr(result, "text"):
                return str(result.text)
            return str(result)
        except (TypeError, ValueError, RuntimeError):
            # Fallback on any SDK errors
            prompt = self._messages_to_prompt(messages)
            return self._client.generate(prompt)

    @staticmethod
    def _messages_to_prompt(messages: list[AgentMessage]) -> str:
        parts: list[str] = []
        for m in messages:
            parts.append(f"[{m.role}] {m.content}")
        parts.append("[assistant] Use tools if needed and keep the answer concise.")
        return "\n".join(parts)



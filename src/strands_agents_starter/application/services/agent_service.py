from __future__ import annotations

from typing import List

from strands_agents_starter.application.dto.message import AgentMessage
from strands_agents_starter.infra.external.llm_client import LLMClientProtocol


class SimpleAgentService:
    """Basic agent orchestration service that converts messages to a prompt.

    This service is intentionally simple and stateless, suitable for demos and
    small use-cases. For multi-step workflows, prefer a more advanced agent.
    """

    def __init__(self, client: LLMClientProtocol) -> None:
        self._client = client

    def run(self, messages: List[AgentMessage]) -> str:
        prompt = self._messages_to_prompt(messages)
        return self._client.generate(prompt)

    @staticmethod
    def _messages_to_prompt(messages: List[AgentMessage]) -> str:
        parts: list[str] = []
        for m in messages:
            parts.append(f"[{m.role}] {m.content}")
        parts.append("[assistant] Provide a concise answer.")
        return "\n".join(parts)



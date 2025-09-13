from __future__ import annotations

from typing import List

from strands_agents_starter.application.dto.message import AgentMessage
from strands_agents_starter.infra.external.llm_client import LLMClientProtocol
from strands_agents_starter.infra.external.strands_adapter import StrandsAgentAdapter, StrandsConfig


class MultiAgentWorkflow:
    """Minimal multi-agent workflow (general-purpose) with safe fallback.

    Orchestrates three roles in sequence: Researcher -> Critic -> Finalizer.
    Uses Strands Agent when available; otherwise falls back to local LLM.
    """

    def __init__(self, client: LLMClientProtocol) -> None:
        self._client = client
        self._runner = StrandsAgentAdapter(client, StrandsConfig())

    def run(self, topic: str) -> str:
        # Phase 1: Researcher produces a brief
        research_messages: List[AgentMessage] = [
            AgentMessage(role="system", content="You are a senior researcher."),
            AgentMessage(
                role="user",
                content=f"Create a concise research brief with 3 bullet points about: {topic}",
            ),
        ]
        brief = self._runner.run(research_messages)

        # Phase 2: Critic reviews the brief
        critic_messages: List[AgentMessage] = [
            AgentMessage(role="system", content="You are a critical reviewer."),
            AgentMessage(
                role="user",
                content=f"Review the brief and list 3 risks or gaps: {brief}",
            ),
        ]
        critique = self._runner.run(critic_messages)

        # Phase 3: Finalizer provides actionable steps
        final_messages: List[AgentMessage] = [
            AgentMessage(role="system", content="You are an expert strategist."),
            AgentMessage(
                role="user",
                content=(
                    "Using the brief and critique, provide 5 concrete, actionable steps.\n"
                    f"Brief: {brief}\nCritique: {critique}"
                ),
            ),
        ]
        final_output = self._runner.run(final_messages)
        return final_output



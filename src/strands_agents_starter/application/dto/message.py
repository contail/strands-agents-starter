from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentMessage:
    """Message DTO used for agent interactions."""

    role: str
    content: str



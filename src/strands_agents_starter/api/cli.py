from __future__ import annotations

import json
from typing import Optional

import typer

from ..application.dto.message import AgentMessage
from ..application.services.agent_service import SimpleAgentService
from ..application.services.workflow_service import MultiAgentWorkflow
from ..domain.entities.twin import TwinState
from ..infra.config.app_config import AppConfig
from ..infra.external.llm_client import HttpLLMClient
from ..infra.external.strands_adapter import StrandsAgentAdapter

app = typer.Typer(add_completion=False, help="Agents CLI (basic, strands, and workflow)")


@app.command()
def models() -> None:
    """List available models from the LLM endpoint as JSON."""
    config = AppConfig.load()
    llm = HttpLLMClient(config)
    data = llm.list_models()
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))


@app.command()
def tick(name: str = "session", question: Optional[str] = None, engine: str = "basic") -> None:
    """Run a single agent step with a simple session context.

    Args:
        name: Session name.
        question: Optional user prompt. If not provided, a summary request is used.
        engine: "basic" for simple LLM orchestration, "strands" for Strands SDK path.
    """
    config = AppConfig.load()
    llm = HttpLLMClient(config)

    if engine == "strands":
        runner = StrandsAgentAdapter(llm)
        run = runner.run
    else:
        agent = SimpleAgentService(llm)
        run = agent.run

    twin = TwinState(name=name)
    messages = [
        AgentMessage(role="system", content="You are a helpful Strands agent."),
        AgentMessage(
            role="user",
            content=question or "Summarize the session context: {}".format(twin.snapshot()),
        ),
    ]
    answer = run(messages)
    typer.echo(answer)


@app.command()
def workflow(topic: str = "modern manufacturing sustainability") -> None:
    """Run a minimal three-phase multi-agent workflow (research → critique → finalize)."""
    config = AppConfig.load()
    llm = HttpLLMClient(config)
    wf = MultiAgentWorkflow(llm)
    out = wf.run(topic)
    typer.echo(out)


if __name__ == "__main__":  # pragma: no cover
    app()



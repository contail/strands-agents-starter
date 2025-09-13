from __future__ import annotations

import json
from typing import Optional

import typer

from ..application.dto.message import AgentMessage
from ..application.services.agent_service import SimpleAgentService
from ..application.services.workflow_service import MultiAgentWorkflow
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

    messages = [
        AgentMessage(role="system", content="You are a helpful Strands agent."),
        AgentMessage(
            role="user",
            content=question or f"Summarize the session context: {{'name': '{name}'}}",
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


@app.command()
def multi_agent(query: str = "What is the capital of France?") -> None:
    """Run the Teacher's Assistant multi-agent system.
    
    This demonstrates a multi-agent architecture where specialized agents work together:
    - Math Assistant: Mathematical calculations and concepts
    - English Assistant: Grammar and language comprehension
    - Language Assistant: Translations between languages
    - Computer Science Assistant: Programming and technical concepts
    - General Assistant: General knowledge queries
    
    Args:
        query: The query to process through the multi-agent system
    """
    try:
        # Import the multi-agent example
        import sys
        from pathlib import Path

        # Add project root to Python path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from examples.multi_agent_example import create_teacher_assistant, run_multi_agent

        # Create and run the multi-agent system
        response = run_multi_agent(query)
        
        typer.echo(f"\nFINAL RESPONSE:\n{response}")
        
    except ImportError as e:
        typer.echo(f"Error: {e}")
        typer.echo("\nThe multi-agent example requires all dependencies to be installed.")
        typer.echo("Please run: poetry install")
    except (RuntimeError, ValueError) as e:
        typer.echo(f"Error running multi-agent system: {e}")


@app.command()
def research(query: str = "What are quantum computers?") -> None:
    """Run the multi-agent research workflow example.
    
    This demonstrates a three-agent workflow:
    1. Researcher Agent: Gathers information from web sources
    2. Analyst Agent: Verifies facts and identifies key insights  
    3. Writer Agent: Creates a final report based on the analysis
    
    Args:
        query: The research query or factual claim to investigate
    """
    try:
        # Try to import from the examples directory
        import sys
        from pathlib import Path

        # Add project root to Python path
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from examples.research_workflow import create_research_workflow, run_research_workflow

        # Create and run the workflow
        report = run_research_workflow(query)
        
        typer.echo(f"\nFINAL REPORT:\n{report}")
        
    except ImportError as e:
        typer.echo(f"Error: {e}")
        typer.echo("\nThe research workflow requires the 'strands-agents' package to be installed.")
        typer.echo("Please run: poetry install")
    except (RuntimeError, ValueError) as e:
        typer.echo(f"Error running research workflow: {e}")


if __name__ == "__main__":  # pragma: no cover
    app()



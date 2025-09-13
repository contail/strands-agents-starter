# Strands Agents Starter

A starter project for building AI agents using the Strands Agents SDK with local LLM support.

## Prerequisites

- Python 3.13
- Poetry (for dependency management)

## Setup

### 1. Python 3.13 + Poetry

```bash
# Set Python 3.13 as the project interpreter
poetry env use $(command -v python3.13)

# Install all dependencies including strands-agents
poetry install
```

### 2. Environment Configuration

Create a `.env` file with the following configuration:

```bash
# Required
LLM_BASE_URL=
LLM_MODEL=auto
HTTP_TIMEOUT=60

# Optional for Strands
STRANDS_PROVIDER=ollama
```

## CLI Commands

### Basic Commands

```bash
# List available models
poetry run strands-agents models

# Run single agent step
poetry run strands-agents tick --name demo --question "요약해줘"

# Run with Strands engine
poetry run strands-agents tick --engine strands --name demo --question "요약해줘"
```

### Workflow Examples

```bash
# Run three-phase workflow (research → critique → finalize)
poetry run strands-agents workflow --topic "factory A thermal stability"

# Run research workflow (Researcher → Analyst → Writer)
poetry run strands-agents research --query "What are quantum computers?"
poetry run strands-agents research --query "Lemon cures cancer"
```

### Multi-Agent System

```bash
# Run Teacher's Assistant multi-agent system
# Routes queries to specialized agents (Math, English, Language, CS, General)
poetry run strands-agents multi-agent --query "Solve x^2 + 5x + 6 = 0"
poetry run strands-agents multi-agent --query "Translate 'Hello' to Spanish"
poetry run strands-agents multi-agent --query "What's the difference between affect and effect?"
```

## Documentation

- **Strands SDK Docs**: https://strandsagents.com/latest/
- **Architecture**: The adapter uses Strands Agent when available (Ollama provider), otherwise falls back to the local LLM client.

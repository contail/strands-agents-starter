Strands Agents (Local LLM ready)

Setup

1. Python 3.13 + Poetry

```
poetry env use $(command -v python3.13)
poetry install
```

2. .env

```
# Copy this to .env and adjust as needed
LLM_BASE_URL=
LLM_MODEL=auto
HTTP_TIMEOUT=60
# Optional for Strands
STRANDS_PROVIDER=ollama
```

CLI

```
poetry run strands-agents models
poetry run strands-agents tick --name demo --question "요약해줘"
poetry run strands-agents tick --engine strands --name demo --question "요약해줘"

Workflow (Strands multi-agent with fallback)
```

poetry run strands-agents workflow --topic "factory A thermal stability"

```

```

Strands SDK

- Docs: https://strandsagents.com/latest/
- The adapter uses Strands Agent when available (Ollama provider), otherwise falls back to the local LLM client.

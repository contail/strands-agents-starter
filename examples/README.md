# Examples

This directory contains example implementations demonstrating various Strands Agents capabilities.

## Research Workflow Example

The `research_workflow.py` example demonstrates a multi-agent workflow for web research, fact-checking, and report generation. This implementation is based on the [Strands Agents documentation](https://strandsagents.com/latest/documentation/docs/examples/python/agents_workflows/).

### Features

- **Multi-Agent Architecture**: Three specialized agents working in sequence
- **Flexible Model Support**: Works with Strands SDK or falls back to local LLM
- **Fact Verification**: Analyzes and verifies information accuracy
- **Report Generation**: Creates structured reports based on research findings

### Agent Roles

1. **Researcher Agent**: Gathers information using available knowledge and resources
2. **Analyst Agent**: Verifies facts and identifies key insights from research findings
3. **Writer Agent**: Creates a final report based on the analysis

### Usage

#### Command Line Interface

```bash
# Run with default query
poetry run strands-agents research

# Run with custom query
poetry run strands-agents research --query "What are the benefits of renewable energy?"

# Run with factual claim verification
poetry run strands-agents research --query "Lemon cures cancer"
```

#### Python Script

```python
from examples.research_workflow import create_research_workflow, run_research_workflow

# Create and run the workflow
report = run_research_workflow("What are quantum computers?")
print(report)

# Or create workflow instance for multiple queries
workflow = create_research_workflow()
report1 = workflow.run("What are quantum computers?")
report2 = workflow.run("Lemon cures cancer")
```

### Sample Outputs

The workflow handles different types of queries:

- **Research Queries**: "What are quantum computers?" → Comprehensive research report
- **Factual Claims**: "Lemon cures cancer" → Fact-check report with verification
- **False Claims**: "Tuesday comes before Monday" → Correction report

### Architecture

The workflow implements output suppression to provide a clean user experience:

- Intermediate agent outputs are suppressed using `callback_handler=None`
- Only the final report from the Writer Agent is displayed
- Progress feedback is provided through simple print statements

### Extending the Example

You can extend this example by:

1. **Adding User Feedback Loop**: Allow users to ask for more detail after receiving the report
2. **Implementing Parallel Research**: Modify the Researcher Agent to gather information from multiple sources simultaneously
3. **Adding Visual Content**: Enhance the Writer Agent to include images or charts in the report
4. **Creating a Web Interface**: Build a web UI for the workflow
5. **Adding Memory**: Implement session memory so the system remembers previous research sessions

## Teacher's Assistant - Multi-Agent Example

The `multi_agent_example.py` demonstrates a multi-agent architecture where specialized agents work together under the coordination of a central orchestrator. This implementation is based on the [Strands Agents documentation](https://strandsagents.com/latest/documentation/docs/examples/python/multi_agent_example/multi_agent_example/).

### Features

- **Central Orchestrator**: Teacher's Assistant routes queries to appropriate specialists
- **Specialized Agents**: Five domain-specific agents for different types of queries
- **Dynamic Query Routing**: Natural language understanding to determine the best agent
- **Tool-Agent Pattern**: Demonstrates how agents can coordinate with each other

### Agent Roles

1. **Teacher's Assistant (Orchestrator)**: Analyzes queries and routes to specialists
2. **Math Assistant**: Handles mathematical calculations, equations, and concepts
3. **English Assistant**: Processes grammar, writing, and language comprehension
4. **Language Assistant**: Manages translations between languages
5. **Computer Science Assistant**: Handles programming and technical concepts
6. **General Assistant**: Processes queries outside specialized domains

### Usage

#### Command Line Interface

```bash
# Run with default query
poetry run strands-agents multi-agent

# Ask a math question
poetry run strands-agents multi-agent --query "Solve x^2 + 5x + 6 = 0"

# Ask for grammar help
poetry run strands-agents multi-agent --query "What's the difference between affect and effect?"

# Request a translation
poetry run strands-agents multi-agent --query "Translate 'Hello' to Spanish"

# Ask a programming question
poetry run strands-agents multi-agent --query "Write a Python function to reverse a string"

# Ask a Genral Question
poetry run strands-agents multi-agent --query "삼겹살과 쏘주는 어울릴까?"


```

#### Python Script

```python
from examples.multi_agent_example import create_teacher_assistant, run_multi_agent

# Create the teacher's assistant
assistant = create_teacher_assistant()

# Process different types of queries
math_response = assistant.process("Calculate the area of a circle with radius 5")
english_response = assistant.process("Is this sentence grammatically correct?")
cs_response = assistant.process("Explain what a hash table is")
```

### Architecture

```
Teacher's Assistant (Orchestrator)
    ├── Query Analysis & Routing
    ├── Math Assistant
    ├── English Assistant
    ├── Language Assistant
    ├── Computer Science Assistant
    └── General Assistant
```

### Sample Interactions

The system automatically routes queries to the most appropriate specialist:

- Mathematical queries → Math Assistant
- Grammar/writing queries → English Assistant
- Translation requests → Language Assistant
- Programming questions → CS Assistant
- Other queries → General Assistant

### Extending the Multi-Agent Example

1. **Add More Specialists**: Create agents for science, history, or other domains
2. **Implement Agent Collaboration**: Enable multiple agents to work together on complex queries
3. **Add Memory and Context**: Maintain conversation history across interactions
4. **Create Complex Workflows**: Chain multiple agents for multi-step problem solving
5. **Add Tool Integration**: Give specialized agents access to specific tools

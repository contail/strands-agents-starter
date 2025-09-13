# Examples

This directory contains example implementations demonstrating various Strands Agents capabilities.

## Research Workflow Example

The `research_workflow.py` example demonstrates a multi-agent workflow for web research, fact-checking, and report generation. This implementation is based on the [Strands Agents documentation](https://strandsagents.com/latest/documentation/docs/examples/python/agents_workflows/).

### Features

- **Multi-Agent Architecture**: Three specialized agents working in sequence
- **Web Research**: Uses `http_request` tool to gather information from web sources
- **Fact Verification**: Analyzes and verifies information accuracy
- **Report Generation**: Creates structured reports based on research findings

### Agent Roles

1. **Researcher Agent**: Gathers information from web sources using HTTP requests
2. **Analyst Agent**: Verifies facts and identifies key insights from research findings
3. **Writer Agent**: Creates a final report based on the analysis

### Usage

#### Command Line Interface

```bash
# Run with default query
strands-agents research

# Run with custom query
strands-agents research "What are the benefits of renewable energy?"

# Run with factual claim verification
strands-agents research "Lemon cures cancer"
```

#### Python Script

```python
from examples.research_workflow import create_research_workflow, run_research_workflow

# Create the workflow agents
researcher_agent, analyst_agent, writer_agent = create_research_workflow()

# Run the workflow
report = run_research_workflow("What are quantum computers?",
                              researcher_agent, analyst_agent, writer_agent)
print(report)
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

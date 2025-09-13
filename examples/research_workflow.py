"""
Multi-Agent Research Workflow Example

This example demonstrates a structured multi-agent workflow for web research, fact-checking, and report generation.
Based on the Strands Agents documentation: https://strandsagents.com/latest/documentation/docs/examples/python/agents_workflows/

The workflow architecture includes:
- Researcher Agent: Gathers information from web sources
- Analyst Agent: Verifies facts and identifies key insights
- Writer Agent: Creates a final report based on the analysis
"""

from typing import List

from strands_agents_starter.application.dto.message import AgentMessage
from strands_agents_starter.infra.config.app_config import AppConfig
from strands_agents_starter.infra.external.llm_client import HttpLLMClient
from strands_agents_starter.infra.external.strands_adapter import StrandsAgentAdapter, StrandsConfig


class ResearchWorkflow:
    """Multi-agent workflow for research, analysis, and report generation."""
    
    def __init__(self):
        config = AppConfig.load()
        self._client = HttpLLMClient(config)
        self._runner = StrandsAgentAdapter(self._client, StrandsConfig())
    
    def run(self, query: str) -> str:
        """Execute the three-phase research workflow."""
        
        print(f"\nProcessing: '{query}'")
        print("\nStep 1: Researcher Agent gathering web information...")
        
        # Phase 1: Researcher Agent gathers web information
        researcher_messages: List[AgentMessage] = [
            AgentMessage(
                role="system",
                content=(
                    "You are a Researcher Agent that gathers information from the web. "
                    "1. Determine if the input is a research query or factual claim "
                    "2. Use your available knowledge to find relevant information "
                    "3. Include source references and keep findings under 500 words"
                )
            ),
            AgentMessage(
                role="user",
                content=f"Research: '{query}'. Gather information from reliable sources."
            )
        ]
        research_findings = self._runner.run(researcher_messages)
        print("Research complete")
        
        print("Passing research findings to Analyst Agent...\n")
        
        # Phase 2: Analyst Agent verifies facts
        analyst_messages: List[AgentMessage] = [
            AgentMessage(
                role="system",
                content=(
            "You are an Analyst Agent that verifies information. "
            "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
            "2. For research queries: Identify 3-5 key insights "
            "3. Evaluate source reliability and keep analysis under 400 words"
                )
            ),
            AgentMessage(
                role="user",
                content=f"Analyze these findings about '{query}':\n\n{research_findings}"
            )
        ]
        analysis = self._runner.run(analyst_messages)
        
        # Phase 3: Writer Agent creates report
        print("Creating final report...")
        writer_messages: List[AgentMessage] = [
            AgentMessage(
                role="system",
                content=(
            "You are a Writer Agent that creates clear reports. "
            "1. For fact-checks: State whether claims are true or false "
            "2. For research: Present key insights in a logical structure "
            "3. Keep reports under 500 words with brief source mentions"
        )
            ),
            AgentMessage(
                role="user",
                content=f"Create a report on '{query}' based on this analysis:\n\n{analysis}"
            )
        ]
        final_report = self._runner.run(writer_messages)
        
        return final_report


def create_research_workflow():
    """
    Create and configure the research workflow.
    
    Returns:
        ResearchWorkflow: Configured workflow instance
    """
    return ResearchWorkflow()


def run_research_workflow(query: str, workflow=None):
    """
    Orchestrate the multi-agent research workflow.
    
    Args:
        query: The research query or factual claim to investigate
        workflow: Optional ResearchWorkflow instance
        
    Returns:
        str: The final report
    """
    if workflow is None:
        workflow = create_research_workflow()
    
    return workflow.run(query)


def main():
    """
    Main function to demonstrate the research workflow with sample queries.
    """
    
    # Create the workflow
    workflow = create_research_workflow()
    
    # Sample queries to demonstrate different types of research
    sample_queries = [
        "What are quantum computers?",
        "Lemon cures cancer",
        "Tuesday comes before Monday in the week"
    ]
    
    print("=== Multi-Agent Research Workflow Demo ===\n")
    
    for i, query in enumerate(sample_queries, 1):
        print(f"--- Example {i} ---")
        try:
            report = run_research_workflow(query, workflow)
            print(f"\nFINAL REPORT:\n{report}")
            print("\n" + "="*80 + "\n")
        except (ImportError, RuntimeError, ValueError) as e:
            print(f"Error processing query '{query}': {e}")
            print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
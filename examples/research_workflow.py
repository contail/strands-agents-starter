"""
Multi-Agent Research Workflow Example

This example demonstrates a structured multi-agent workflow for web research, fact-checking, and report generation.
Based on the Strands Agents documentation: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/

The workflow architecture includes:
- Task management with dependency resolution
- Context passing between agents
- Status tracking and monitoring
- Error handling and recovery

Workflow stages:
1. Researcher Agent: Gathers information from web sources
2. Analyst Agent: Verifies facts and identifies key insights
3. Writer Agent: Creates a final report based on the analysis
"""
# pyright: reportMissingImports=false
# pylint: disable=import-error
# mypy: ignore-errors

import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from strands_agents import Agent
from strands_agents.tools import http_request


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowTask:
    """Represents a task in the workflow"""
    def __init__(self, task_id: str, description: str, agent: Agent, 
                 dependencies: Optional[List[str]] = None, priority: int = 5):
        self.task_id = task_id
        self.description = description
        self.agent = agent
        self.dependencies = dependencies or []
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execution_time(self) -> Optional[float]:
        """Get task execution time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class ResearchWorkflow:
    """Manages the multi-agent research workflow"""
    
    def __init__(self):
        self.tasks: Dict[str, WorkflowTask] = {}
        self.results: Dict[str, Any] = {}
        self.workflow_id = f"research_workflow_{int(time.time())}"
        self.start_time = None
        self.end_time = None
        
    def add_task(self, task: WorkflowTask) -> None:
        """Add a task to the workflow"""
        self.tasks[task.task_id] = task
        
    def get_ready_tasks(self) -> List[str]:
        """Find tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self.tasks[dep].status == TaskStatus.COMPLETED 
                    for dep in task.dependencies
                )
                if deps_satisfied:
                    ready_tasks.append(task_id)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)
        return ready_tasks
    
    def build_task_context(self, task_id: str) -> str:
        """Build context from dependent tasks for a given task"""
        task = self.tasks[task_id]
        context_parts = []
        
        # Add results from dependencies
        for dep_id in task.dependencies:
            if dep_id in self.results:
                context_parts.append(
                    f"Results from {dep_id}:\n{self.results[dep_id]}"
                )
        
        # Construct the prompt with context
        prompt = task.description
        if context_parts:
            context_section = "\n\n".join(context_parts)
            prompt = f"Previous task results:\n{context_section}\n\nTask:\n{prompt}"
            
        return prompt
    
    def execute_task(self, task_id: str) -> None:
        """Execute a single task with error handling"""
        task = self.tasks[task_id]
        
        print(f"\n{'='*60}")
        print(f"Executing task: {task_id}")
        print(f"Description: {task.description}")
        print(f"Priority: {task.priority}")
        print(f"{'='*60}")
        
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        
        try:
            # Build context from dependencies
            prompt = self.build_task_context(task_id)
            
            # Execute the task
            result = task.agent(prompt)
            
            # Store results
            task.result = str(result)
            self.results[task_id] = task.result
            task.status = TaskStatus.COMPLETED
            
            print(f"✓ Task '{task_id}' completed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"✗ Task '{task_id}' failed: {e}")
            raise
            
        finally:
            task.end_time = datetime.now()
            if task.execution_time():
                print(f"Execution time: {task.execution_time():.2f} seconds")
    
    def run(self) -> Dict[str, Any]:
        """Execute the workflow"""
        self.start_time = datetime.now()
        print(f"\nStarting workflow: {self.workflow_id}")
        print(f"Total tasks: {len(self.tasks)}")
        
        completed_count = 0
        
        while completed_count < len(self.tasks):
            # Get tasks ready to execute
            ready_tasks = self.get_ready_tasks()
            
            if not ready_tasks:
                # Check for circular dependencies or all failed
                pending_tasks = [
                    tid for tid, t in self.tasks.items() 
                    if t.status == TaskStatus.PENDING
                ]
                if pending_tasks:
                    raise RuntimeError(
                        f"Workflow stuck! Pending tasks with unmet dependencies: {pending_tasks}"
                    )
                break
            
            # Execute ready tasks (sequential for now, could be parallel)
            for task_id in ready_tasks:
                self.execute_task(task_id)
                completed_count += 1
        
        self.end_time = datetime.now()
        
        # Generate workflow summary
        return self.get_status()
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed workflow status"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        status = {
            "workflow_id": self.workflow_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "progress_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "tasks": {}
        }
        
        # Add individual task status
        for task_id, task in self.tasks.items():
            status["tasks"][task_id] = {
                "status": task.status.value,
                "execution_time": task.execution_time(),
                "dependencies": task.dependencies,
                "error": task.error
            }
        
        # Add workflow execution time
        if self.start_time and self.end_time:
            status["total_execution_time"] = (self.end_time - self.start_time).total_seconds()
        
        return status


def create_research_workflow():
    """
    Create and configure the three-agent research workflow.
    
    Returns:
        tuple: (researcher_agent, analyst_agent, writer_agent)
    """
    
    # Researcher Agent with web capabilities
    researcher_agent = Agent(
        system_prompt=(
            "You are a Researcher Agent that gathers information from the web. "
            "1. Determine if the input is a research query or factual claim "
            "2. Use your research tools (http_request) to find relevant information "
            "3. Include source URLs and keep findings under 500 words"
        ),
        callback_handler=None,  # Suppresses output
        tools=[http_request]
    )

    # Analyst Agent for verification and insight extraction
    analyst_agent = Agent(
        callback_handler=None,  # Suppresses output
        system_prompt=(
            "You are an Analyst Agent that verifies information. "
            "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
            "2. For research queries: Identify 3-5 key insights "
            "3. Evaluate source reliability and keep analysis under 400 words"
        ),
    )

    # Writer Agent for final report creation
    writer_agent = Agent(
        system_prompt=(
            "You are a Writer Agent that creates clear reports. "
            "1. For fact-checks: State whether claims are true or false "
            "2. For research: Present key insights in a logical structure "
            "3. Keep reports under 500 words with brief source mentions"
        )
    )
    
    return researcher_agent, analyst_agent, writer_agent


def run_research_workflow(user_input: str, researcher_agent: Agent, analyst_agent: Agent, writer_agent: Agent):
    """
    Orchestrate the multi-agent research workflow.
    
    Args:
        user_input: The research query or factual claim to investigate
        researcher_agent: Agent responsible for gathering web information
        analyst_agent: Agent responsible for verification and analysis
        writer_agent: Agent responsible for creating the final report
        
    Returns:
        str: The final report generated by the Writer Agent
    """
    
    print(f"\nProcessing: '{user_input}'")
    print("\nStep 1: Researcher Agent gathering web information...")
    
    # Step 1: Researcher Agent gathers web information
    researcher_response = researcher_agent(
        f"Research: '{user_input}'. Use your available tools to gather information from reliable sources.",
    )
    research_findings = str(researcher_response)
    print("Research complete")
    
    print("Passing research findings to Analyst Agent...\n")
    
    # Step 2: Analyst Agent verifies facts
    analyst_response = analyst_agent(
        f"Analyze these findings about '{user_input}':\n\n{research_findings}",
    )
    analysis = str(analyst_response)
    
    # Step 3: Writer Agent creates report
    print("Creating final report...")
    final_report = writer_agent(
        f"Create a report on '{user_input}' based on this analysis:\n\n{analysis}"
    )
    
    return final_report


def main():
    """
    Main function to demonstrate the research workflow with sample queries.
    """
    
    # Create the workflow agents
    researcher_agent, analyst_agent, writer_agent = create_research_workflow()
    
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
            report = run_research_workflow(query, researcher_agent, analyst_agent, writer_agent)
            print(f"\nFINAL REPORT:\n{report}")
            print("\n" + "="*80 + "\n")
        except (ImportError, RuntimeError, ValueError) as e:
            print(f"Error processing query '{query}': {e}")
            print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

"""
Teacher's Assistant - Multi-Agent Architecture Example

This example demonstrates a multi-agent architecture where specialized agents work together
under the coordination of a central orchestrator. Based on the Strands Agents documentation:
https://strandsagents.com/latest/documentation/docs/examples/python/multi_agent_example/multi_agent_example/

Architecture:
- Teacher's Assistant (Orchestrator): Routes queries to appropriate specialists
- Math Assistant: Handles mathematical calculations and concepts
- English Assistant: Processes grammar and language comprehension
- Language Assistant: Manages translations and language-related queries
- Computer Science Assistant: Handles programming and technical concepts
- General Assistant: Processes queries outside specialized domains
"""

import re
from typing import List, Optional

from strands_agents_starter.application.dto.message import AgentMessage
from strands_agents_starter.infra.config.app_config import AppConfig
from strands_agents_starter.infra.external.llm_client import HttpLLMClient
from strands_agents_starter.infra.external.strands_adapter import StrandsAgentAdapter, StrandsConfig

# System prompts for each specialized agent
TEACHER_SYSTEM_PROMPT = """You are a Teacher's Assistant, an intelligent orchestrator that routes queries to specialized assistants.

Your role is to:
1. Analyze incoming queries to understand their subject matter
2. Determine which specialized assistant is best suited to handle the query
3. Route the query to that assistant

Available assistants:
- math_assistant: For mathematical calculations, equations, and concepts
- english_assistant: For grammar, writing, and language comprehension
- language_assistant: For translations between languages
- computer_science_assistant: For programming, algorithms, and technical concepts
- general_assistant: For general knowledge and queries outside specific domains

When routing, be clear about which assistant you're using and why."""

MATH_ASSISTANT_PROMPT = """You are a Math Assistant specializing in mathematical calculations and concepts.
Provide clear, step-by-step solutions and explanations for mathematical problems.
Show your work and explain the concepts involved."""

ENGLISH_ASSISTANT_PROMPT = """You are an English Assistant specializing in grammar, writing, and language comprehension.
Help with grammar questions, writing style, vocabulary, and text analysis.
Provide clear explanations and examples."""

LANGUAGE_ASSISTANT_PROMPT = """You are a Language Assistant specializing in translations between languages.
Provide accurate translations and explain nuances when relevant.
Include cultural context when appropriate."""

CS_ASSISTANT_PROMPT = """You are a Computer Science Assistant specializing in programming and technical concepts.
Help with coding questions, algorithms, data structures, and software development.
Provide clear code examples with explanations."""

GENERAL_ASSISTANT_PROMPT = """You are a General Assistant handling queries outside specialized domains.
Provide helpful, accurate information on a wide range of topics.
Be clear and informative in your responses."""


class SpecializedAgent:
    """Base class for specialized agents."""
    
    def __init__(self, name: str, system_prompt: str, runner: StrandsAgentAdapter):
        self.name = name
        self.system_prompt = system_prompt
        self.runner = runner
    
    def process(self, query: str) -> str:
        """Process a query using this specialized agent."""
        print(f"\nRouted to {self.name}")
        
        messages: List[AgentMessage] = [
            AgentMessage(role="system", content=self.system_prompt),
            AgentMessage(role="user", content=query)
        ]
        
        try:
            response = self.runner.run(messages)
            return response
        except Exception as e:
            return f"Error processing query with {self.name}: {str(e)}"


class TeacherAssistant:
    """Central orchestrator that routes queries to specialized agents."""
    
    def __init__(self):
        config = AppConfig.load()
        self._client = HttpLLMClient(config)
        self._runner = StrandsAgentAdapter(self._client, StrandsConfig())
        
        # Initialize specialized agents
        self.agents = {
            "math": SpecializedAgent("Math Assistant", MATH_ASSISTANT_PROMPT, self._runner),
            "english": SpecializedAgent("English Assistant", ENGLISH_ASSISTANT_PROMPT, self._runner),
            "language": SpecializedAgent("Language Assistant", LANGUAGE_ASSISTANT_PROMPT, self._runner),
            "cs": SpecializedAgent("Computer Science Assistant", CS_ASSISTANT_PROMPT, self._runner),
            "general": SpecializedAgent("General Assistant", GENERAL_ASSISTANT_PROMPT, self._runner)
        }
    
    def route_query(self, query: str) -> str:
        """Analyze query and route to appropriate specialist."""
        
        # First, use the orchestrator to determine routing
        routing_messages: List[AgentMessage] = [
            AgentMessage(role="system", content=TEACHER_SYSTEM_PROMPT),
            AgentMessage(
                role="user",
                content=f"Analyze this query and determine which assistant should handle it: '{query}'"
            )
        ]
        
        routing_response = self._runner.run(routing_messages)
        
        # Extract which assistant was chosen (simple pattern matching)
        routing_lower = routing_response.lower()
        
        if "math" in routing_lower and "assistant" in routing_lower:
            return self.agents["math"].process(query)
        elif "english" in routing_lower and "assistant" in routing_lower:
            return self.agents["english"].process(query)
        elif "language" in routing_lower and "assistant" in routing_lower:
            return self.agents["language"].process(query)
        elif ("computer" in routing_lower or "cs" in routing_lower) and "assistant" in routing_lower:
            return self.agents["cs"].process(query)
        else:
            # Default to general assistant
            return self.agents["general"].process(query)
    
    def process(self, query: str) -> str:
        """Process a query through the multi-agent system."""
        print(f"\nProcessing query: '{query}'")
        print("Analyzing query to determine best assistant...")
        
        response = self.route_query(query)
        return response


def create_teacher_assistant():
    """Create and return a TeacherAssistant instance."""
    return TeacherAssistant()


def run_multi_agent(query: str, assistant: Optional[TeacherAssistant] = None):
    """Run a query through the multi-agent system."""
    if assistant is None:
        assistant = create_teacher_assistant()
    
    return assistant.process(query)


def main():
    """Demonstrate the multi-agent system with example queries."""
    
    # Create the teacher's assistant
    assistant = create_teacher_assistant()
    
    # Example queries demonstrating different domains
    example_queries = [
        "Solve the quadratic equation x^2 + 5x + 6 = 0",
        "What's the difference between 'affect' and 'effect'?",
        "Translate 'Hello, how are you?' to Spanish",
        "Write a Python function to check if a string is a palindrome",
        "What are the main causes of climate change?"
    ]
    
    print("=== Teacher's Assistant Multi-Agent Demo ===\n")
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n--- Example {i} ---")
        try:
            response = run_multi_agent(query, assistant)
            print(f"\nRESPONSE:\n{response}")
            print("\n" + "="*80)
        except Exception as e:
            print(f"Error processing query: {e}")
            print("\n" + "="*80)


if __name__ == "__main__":
    main()

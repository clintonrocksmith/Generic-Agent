"""
Generic-Agent
A generic Agent Python agent that takes in the parameters it needs to run an agent workflow.
"""

__version__ = "0.1.0"
__author__ = "Generic-Agent Team"

# Export main classes and functions
from .agent import GenericAgent, create_agent

__all__ = ["GenericAgent", "create_agent"]

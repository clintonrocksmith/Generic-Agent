"""
Generic Agent implementation that can run different agent workflows
based on provided parameters.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GenericAgent:
    """
    A generic agent that can execute different workflows based on parameters.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Generic Agent.
        
        Args:
            config (Dict[str, Any], optional): Configuration parameters for the agent
        """
        self.config = config or {}
        self.workflow = self.config.get('workflow', 'default')
        logger.info(f"Initialized GenericAgent with workflow: {self.workflow}")
    
    def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent workflow with given parameters.
        
        Args:
            parameters (Dict[str, Any]): Parameters to configure the agent execution
            
        Returns:
            Dict[str, Any]: Results of the agent execution
        """
        logger.info(f"Running agent with parameters: {parameters}")
        
        # Default implementation - can be overridden by specific workflows
        result = {
            'workflow': self.workflow,
            'parameters': parameters,
            'status': 'success',
            'message': 'Agent executed successfully'
        }
        
        return result
    
    def set_workflow(self, workflow_name: str):
        """
        Set the workflow type for this agent.
        
        Args:
            workflow_name (str): Name of the workflow to use
        """
        self.workflow = workflow_name
        logger.info(f"Workflow set to: {workflow_name}")


def create_agent(config: Optional[Dict[str, Any]] = None) -> GenericAgent:
    """
    Factory function to create a GenericAgent instance.
    
    Args:
        config (Dict[str, Any], optional): Configuration for the agent
        
    Returns:
        GenericAgent: New agent instance
    """
    return GenericAgent(config)
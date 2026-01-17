#!/usr/bin/env python3
"""
Generic Agent that processes JSON payloads and interacts with MCP servers using Anthropic SDK.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    command: str = Field(..., description="Command to start the MCP server")
    args: List[str] = Field(default_factory=list, description="Arguments for the MCP server command")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables for the MCP server")


class AgentConfig(BaseModel):
    """Configuration for the agent."""
    api_key: Optional[str] = Field(default=None, description="Anthropic API key (can also use ANTHROPIC_API_KEY env var)")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Model to use for the agent")
    max_tokens: int = Field(default=4096, description="Maximum tokens for responses")
    temperature: float = Field(default=1.0, description="Temperature for sampling")
    mcp_servers: List[MCPServerConfig] = Field(default_factory=list, description="MCP servers to connect to")


class AgentPayload(BaseModel):
    """Payload structure for the agent."""
    config: AgentConfig = Field(..., description="Agent configuration")
    task: str = Field(..., description="Task description or prompt for the agent")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the task")


class GenericAgent:
    """A generic agent that can process tasks using Anthropic's API and MCP servers."""
    
    def __init__(self, payload: AgentPayload):
        """Initialize the agent with a payload.
        
        Args:
            payload: The agent payload containing configuration and task
        """
        self.payload = payload
        self.config = payload.config
        
        # Initialize Anthropic client
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided in config or ANTHROPIC_API_KEY environment variable")
        
        self.client = Anthropic(api_key=api_key)
        self.mcp_sessions = []
    
    async def connect_mcp_servers(self):
        """Connect to all configured MCP servers."""
        for server_config in self.config.mcp_servers:
            try:
                server_params = StdioServerParameters(
                    command=server_config.command,
                    args=server_config.args,
                    env=server_config.env
                )
                
                # Create MCP client session
                stdio_transport = await stdio_client(server_params)
                session = ClientSession(stdio_transport[0], stdio_transport[1])
                await session.initialize()
                
                self.mcp_sessions.append({
                    "config": server_config,
                    "session": session
                })
                
                print(f"Connected to MCP server: {server_config.command}")
            except Exception as e:
                print(f"Failed to connect to MCP server {server_config.command}: {e}", file=sys.stderr)
    
    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from all connected MCP servers.
        
        Returns:
            List of tools in Anthropic API format
        """
        tools = []
        for mcp_session in self.mcp_sessions:
            try:
                session = mcp_session["session"]
                # List available tools from the MCP server
                response = await session.list_tools()
                
                # Convert MCP tools to Anthropic tool format
                for tool in response.tools:
                    tools.append({
                        "name": tool.name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema
                    })
            except Exception as e:
                print(f"Error getting tools from MCP server: {e}", file=sys.stderr)
        
        return tools
    
    async def call_mcp_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Call a tool on the appropriate MCP server.
        
        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
        """
        for mcp_session in self.mcp_sessions:
            session = mcp_session["session"]
            try:
                # Try to call the tool on this server
                result = await session.call_tool(tool_name, tool_input)
                return result
            except Exception as e:
                # Tool might not be on this server, try the next one
                continue
        
        raise ValueError(f"Tool '{tool_name}' not found on any connected MCP server")
    
    async def run(self) -> Dict[str, Any]:
        """Run the agent with the configured task.
        
        Returns:
            Dictionary containing the agent's response and metadata
        """
        # Connect to MCP servers if configured
        if self.config.mcp_servers:
            await self.connect_mcp_servers()
        
        # Get available tools from MCP servers
        tools = await self.get_mcp_tools() if self.mcp_sessions else []
        
        # Build the messages for the API call
        messages = [
            {
                "role": "user",
                "content": self.payload.task
            }
        ]
        
        # Add context if provided
        if self.payload.context:
            context_str = "\n\nAdditional context:\n" + json.dumps(self.payload.context, indent=2)
            messages[0]["content"] += context_str
        
        # Make the API call
        if tools:
            # Use tools if available
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                tools=tools
            )
            
            # Handle tool use if the model wants to use tools
            while response.stop_reason == "tool_use":
                # Extract tool use from response
                tool_use_block = next(
                    (block for block in response.content if block.type == "tool_use"),
                    None
                )
                
                if tool_use_block:
                    # Call the tool via MCP
                    tool_result = await self.call_mcp_tool(
                        tool_use_block.name,
                        tool_use_block.input
                    )
                    
                    # Add the assistant's response and tool result to messages
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Serialize tool result if it's not already a string
                    if isinstance(tool_result, str):
                        result_content = tool_result
                    else:
                        try:
                            result_content = json.dumps(tool_result)
                        except (TypeError, ValueError):
                            # If serialization fails, convert to string
                            result_content = str(tool_result)
                    
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_block.id,
                                "content": result_content
                            }
                        ]
                    })
                    
                    # Continue the conversation
                    response = self.client.messages.create(
                        model=self.config.model,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        messages=messages,
                        tools=tools
                    )
                else:
                    break
        else:
            # No tools available, simple message call
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages
            )
        
        # Extract text content from response
        text_content = ""
        for block in response.content:
            if hasattr(block, "text"):
                text_content += block.text
        
        return {
            "response": text_content,
            "model": self.config.model,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    async def cleanup(self):
        """Clean up resources and close MCP connections."""
        for mcp_session in self.mcp_sessions:
            try:
                await mcp_session["session"].close()
            except Exception as e:
                print(f"Error closing MCP session: {e}", file=sys.stderr)


async def run_agent_from_json(json_payload: str) -> Dict[str, Any]:
    """Run the agent from a JSON payload string.
    
    Args:
        json_payload: JSON string containing the agent payload
        
    Returns:
        Agent execution result
    """
    # Parse the JSON payload
    payload_dict = json.loads(json_payload)
    payload = AgentPayload(**payload_dict)
    
    # Create and run the agent
    agent = GenericAgent(payload)
    try:
        result = await agent.run()
        return result
    finally:
        await agent.cleanup()


async def run_agent_from_file(json_file_path: str) -> Dict[str, Any]:
    """Run the agent from a JSON file.
    
    Args:
        json_file_path: Path to JSON file containing the agent payload
        
    Returns:
        Agent execution result
    """
    with open(json_file_path, 'r') as f:
        json_payload = f.read()
    
    return await run_agent_from_json(json_payload)


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py <json_file_path>")
        print("   or: python agent.py --json '<json_string>'")
        sys.exit(1)
    
    if sys.argv[1] == "--json":
        if len(sys.argv) < 3:
            print("Error: --json requires a JSON string argument")
            sys.exit(1)
        json_input = sys.argv[2]
        result = asyncio.run(run_agent_from_json(json_input))
    else:
        json_file = sys.argv[1]
        if not os.path.exists(json_file):
            print(f"Error: File not found: {json_file}")
            sys.exit(1)
        result = asyncio.run(run_agent_from_file(json_file))
    
    print("\n" + "="*80)
    print("AGENT RESULT")
    print("="*80)
    print(json.dumps(result, indent=2))

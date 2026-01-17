# Generic-Agent
A generic Python agent that takes in JSON payloads and can interact with MCP (Model Context Protocol) servers using the Anthropic SDK.

## Features

- 🤖 **Anthropic SDK Integration**: Uses Claude models for intelligent task processing
- 🔌 **MCP Server Support**: Connect to multiple MCP servers for extended capabilities
- 📝 **JSON-based Configuration**: Easy to configure via JSON payloads
- 🛠️ **Tool Use**: Automatically handles tool calling when MCP servers are connected
- 🔄 **Async Support**: Built with async/await for efficient operations

## Installation

```bash
pip install -r requirements.txt
```

You'll also need to set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Basic Usage (No MCP Servers)

```bash
python agent.py example_simple.json
```

### With MCP Servers

```bash
python agent.py example_with_mcp.json
```

### Using JSON String Directly

```bash
python agent.py --json '{"config": {"model": "claude-3-5-sonnet-20241022", "max_tokens": 1024, "mcp_servers": []}, "task": "Hello, world!"}'
```

## JSON Payload Structure

The agent accepts a JSON payload with the following structure:

```json
{
  "config": {
    "api_key": "optional-api-key",
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "temperature": 1.0,
    "mcp_servers": [
      {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "env": null
      }
    ]
  },
  "task": "Your task description here",
  "context": {
    "key": "value"
  }
}
```

### Configuration Fields

- **api_key** (optional): Anthropic API key. If not provided, uses `ANTHROPIC_API_KEY` environment variable
- **model** (default: "claude-3-5-sonnet-20241022"): The Claude model to use
- **max_tokens** (default: 4096): Maximum tokens for responses
- **temperature** (default: 1.0): Temperature for sampling
- **mcp_servers** (default: []): List of MCP servers to connect to

### MCP Server Configuration

Each MCP server in the `mcp_servers` array has:

- **command**: The command to start the MCP server (e.g., "npx", "python")
- **args**: List of arguments for the command
- **env**: Optional environment variables for the server

### Task and Context

- **task**: The main instruction or prompt for the agent
- **context**: Optional dictionary with additional context information

## Examples

### Example 1: Simple Question

```json
{
  "config": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "mcp_servers": []
  },
  "task": "Explain what a generic agent is and how it can be used in software development."
}
```

### Example 2: With MCP Filesystem Server

```json
{
  "config": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "mcp_servers": [
      {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
      }
    ]
  },
  "task": "List the files in the directory and summarize what you find."
}
```

## Programmatic Usage

You can also use the agent programmatically in your Python code:

```python
import asyncio
from agent import GenericAgent, AgentPayload, AgentConfig

async def main():
    payload = AgentPayload(
        config=AgentConfig(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            mcp_servers=[]
        ),
        task="What is the meaning of life?"
    )
    
    agent = GenericAgent(payload)
    try:
        result = await agent.run()
        print(result["response"])
    finally:
        await agent.cleanup()

asyncio.run(main())
```

## Requirements

- Python 3.8+
- anthropic >= 0.18.0
- mcp >= 0.9.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0

## License

MIT

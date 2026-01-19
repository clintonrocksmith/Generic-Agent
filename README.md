# Generic-Agent

**A schema-driven, protocol-agnostic runtime for autonomous AI agents.**

`Generic-Agent` is a Python execution engine that implements the Model Context Protocol (MCP) for dynamic tool discovery and integrates with LLMs to create powerful autonomous agents.

## Key Features

* **🔌 MCP Native:** Built on the Model Context Protocol, allowing dynamic tool discovery and integration
* **🛡️ Policy Controlled:** Define strict execution limits (timeouts, max cost, max steps) directly in the configuration
* **🏗️ Structured Output:** Enforce JSON schemas on output to guarantee consistent results
* **🧠 Model Agnostic:** Switch between models (Claude, GPT-4, Llama) per-job via configuration

## Installation

```bash
pip install generic-agent
```

## Usage Example

```python
import asyncio
from generic_agent import create_agent

# Create an agent with full configuration
config = {
    "workflow": "data_analysis",
    "llm_config": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "execution_policy": {
        "timeout": 300,
        "max_retries": 3
    },
    "mcp_config": {
        "servers": [
            {
                "id": "database-server",
                "type": "database",
                "connection_string": "postgresql://user:pass@localhost/db"
            },
            {
                "id": "api-server",
                "type": "http",
                "base_url": "https://api.example.com"
            }
        ]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "data_points": {"type": "array"}
        }
    }
}

agent = create_agent(config)

# Run the agent (returns a coroutine)
async def run_agent():
    result = await agent.run()
    print(result)

# Run the async function
asyncio.run(run_agent())
```

## Configuration Structure

The agent accepts a comprehensive configuration dictionary with the following keys:

- `workflow` (string): The type of workflow to execute (defaults to 'default')
- `llm_config` (dict): LLM configuration including model, temperature, max_tokens, etc.
- `execution_policy` (dict): Execution constraints including timeout and retry limits
- `mcp_config` (dict): MCP server configurations with server definitions
- `output_schema` (dict): JSON schema for validating the agent's output

## Development

To install in development mode:

```bash
pip install -e .
```

To run tests:

```bash
pytest
```

To lint code:

```bash
flake8
```

To format code:

```bash
black .
```
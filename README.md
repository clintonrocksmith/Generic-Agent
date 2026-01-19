# Generic-Agent

**A schema-driven, protocol-agnostic runtime for autonomous AI agents.**

`Generic-Agent` is a Python execution engine that decouples agent *logic* from agent *infrastructure*. Instead of writing new Python code for every agent workflow, you define jobs in a standardized JSON payload. The agent parses this payload, dynamically connects to Model Context Protocol (MCP) servers, enforces safety policies, and guarantees structured output.

## Key Features

* **🔌 MCP Native:** Built on top of the **Model Context Protocol** (using `fastmcp`), allowing dynamic tool discovery at runtime.
* **🛡️ Policy Controlled:** Define strict execution limits (timeouts, max cost, max steps) directly in the job payload.
* **🏗️ Structured Output:** Enforce JSON schemas on agent results, making the agent a reliable backend for other APIs.
* **🧠 Model Agnostic:** Switch between models (Claude, GPT-4, Llama) per-job via configuration.

## Installation

```bash
pip install generic-agent

```

*(Note: You will also need `uv` or `npm` installed if you plan to run MCP servers via stdio transport.)*

## Quick Start

1. **Define your job** in a JSON file (e.g., `job.json`).
2. **Run the agent** using the Python SDK.

```python
import json
import asyncio
from generic_agent import GenericAgent

# 1. Load the Job Configuration
with open("job.json", "r") as f:
    job_payload = json.load(f)

# 2. Initialize the Runtime
agent = GenericAgent(job_payload)

# 3. Execute
# The agent will connect to MCP servers, run the loop, and validate output.
async def main():
    result = await agent.run()
    print(f"Agent Status: {result['status']}")
    print(f"Result Data: {result['data']}")

if __name__ == "__main__":
    asyncio.run(main())

```

## The Payload Specification

The core of `Generic-Agent` is the JSON payload. It acts as a manifest for the agent's capabilities for a single run.

### Complete Example

```json
{
  "task_type": "autonomous_agent",
  "action": "solve_goal",
  "payload": {
    "goal": "Check the 'users.db' database for inactive users and remove them.",
    "context": "Inactive means no login in 30 days. Return the list of deleted IDs."
  },
  "output_schema": {
    "type": "json_schema",
    "schema": {
      "type": "object",
      "properties": {
        "status": { "type": "string", "enum": ["success", "failed"] },
        "deleted_user_ids": { "type": "array", "items": { "type": "integer" } },
        "reasoning": { "type": "string" }
      },
      "required": ["status", "deleted_user_ids"]
    }
  },
  "mcp_config": {
    "servers": [
      {
        "id": "sqlite",
        "transport": "stdio",
        "command": "uvx", 
        "args": ["mcp-server-sqlite", "--db-path", "./users.db"]
      }
    ],
    "security": {
      "auto_approve_tools": true,
      "max_tool_calls": 10
    }
  },
  "llm_config": {
    "model": "claude-3-5-sonnet",
    "temperature": 0.0
  },
  "execution_policy": {
    "timeout_seconds": 120,
    "max_cost_usd": 0.50
  },
  "metadata": {
    "trace_id": "trace-8899-0011",
    "requester_id": "admin-panel"
  }
}

```

### Configuration Breakdown

| Section | Description |
| --- | --- |
| **`payload`** | **The Mission.** Contains the natural language `goal` and specific `context` data needed for the prompt. |
| **`output_schema`** | **The Contract.** A JSON Schema definition. The agent will self-correct until its final answer matches this structure. |
| **`mcp_config`** | **The Tools.** Defines which MCP servers to connect to. Supports `stdio` (local commands) and `sse` (remote URLs). |
| **`llm_config`** | **The Brain.** Specifies which model to use and its parameters (temperature, max_tokens). |
| **`execution_policy`** | **The Safety Rails.** Hard limits on time and budget to prevent runaway agent loops. |

## Tool Integration (MCP)

This agent uses the [Model Context Protocol](https://modelcontextprotocol.io/). You do not write Python tools inside this repo. Instead, you point the agent to MCP servers.

**Supported Transports:**

* **stdio:** Runs a local command (e.g., `uvx mcp-server-sqlite`). Good for local file/db access.
* **sse:** Connects to a remote HTTP endpoint. Good for production microservices.

## Roadmap

* [ ] Support for OAuth-based MCP servers
* [ ] Add "Human-in-the-loop" interruption in `execution_policy`
* [ ] Dockerized runtime for sandboxed execution
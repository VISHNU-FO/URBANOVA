"""PRISM-instrumented Google ADK tracing adapter.

This module initializes the PRISMtraceADKAdapter once and exposes it
as a singleton so every agent in the project shares one adapter instance,
one session lifecycle, and one HTTP connection pool.

Usage in any agent file:

    from tracing import prism_adapter

    agent = LlmAgent(
        name="my_agent",
        model="gemini-2.0-flash",
        instruction="...",
        before_model_callback=prism_adapter.before_model,
        after_model_callback=prism_adapter.after_model,
        before_tool_callback=prism_adapter.before_tool,
        after_tool_callback=prism_adapter.after_tool,
        before_agent_callback=prism_adapter.before_agent,
        after_agent_callback=prism_adapter.after_agent,
    )
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Load .env file if present (development / staging).
# In production, set env vars via your secret manager.
load_dotenv()

from prismtrace import PRISMtraceADKAdapter  # noqa: E402

_api_key = os.environ.get("PRISMTRACE_API_KEY", "")
_project_id = os.environ.get(
    "PRISMTRACE_PROJECT_ID", "c3687725-bb84-48ac-b633-86402bbe6321"
)
_host = os.environ.get(
    "PRISMTRACE_HOST", "https://prism-api-prod.up.railway.app"
)

if not _api_key:
    raise RuntimeError(
        "PRISMTRACE_API_KEY is not set. "
        "Copy .env.example to .env and fill in the key, "
        "or export it in your shell."
    )

# Singleton adapter — shared across all agents in this process.
prism_adapter = PRISMtraceADKAdapter(
    api_key=_api_key,
    project_id=_project_id,
    agent_name="something-else",  # top-level display name in PRISM
    endpoint=_host,
)


def wire_agent_callbacks() -> dict:
    """Return the dict of ADK callback kwargs to spread into any LlmAgent.

    Example:
        agent = LlmAgent(
            name="my_agent",
            model="gemini-2.0-flash",
            instruction="...",
            **wire_agent_callbacks(),
        )
    """
    return {
        "before_model_callback": prism_adapter.before_model,
        "after_model_callback": prism_adapter.after_model,
        "before_tool_callback": prism_adapter.before_tool,
        "after_tool_callback": prism_adapter.after_tool,
        "before_agent_callback": prism_adapter.before_agent,
        "after_agent_callback": prism_adapter.after_agent,
    }

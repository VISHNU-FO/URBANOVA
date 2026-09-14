"""Example Google ADK agent with PRISM tracing wired in.

This is a scaffold. Replace the agent instruction and tools with your
actual application logic. The tracing callbacks are already connected —
every model call, tool invocation, error, and sub-agent handoff will
appear in the PRISM dashboard automatically.

To run (requires GOOGLE_API_KEY in .env):
    python agent.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import LlmAgent  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402

from tracing import prism_adapter, wire_agent_callbacks  # noqa: E402


# ── Tools ──────────────────────────────────────────────────────────────
# Add your tools here. Each tool is a plain Python function.

def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}! Welcome to Something Else."


def get_decision_options(topic: str) -> str:
    """Return decision options for a given topic (placeholder)."""
    return (
        f"For '{topic}', here are your options:\n"
        "1. Option A — conservative approach\n"
        "2. Option B — balanced approach\n"
        "3. Option C — aggressive approach"
    )


# ── Agent ──────────────────────────────────────────────────────────────
# PRISM callbacks are wired via wire_agent_callbacks(). Every model call,
# tool use, and error is traced automatically.

root_agent = LlmAgent(
    name="decision_assistant",
    model="gemini-2.0-flash",
    instruction=(
        "You are a decision-making assistant for Something Else. "
        "Help users evaluate options and make informed decisions. "
        "Use the available tools to gather information."
    ),
    tools=[greet, get_decision_options],
    **wire_agent_callbacks(),
)


# ── Runner (for local development) ────────────────────────────────────

async def main():
    """Run one turn for local testing."""
    import asyncio

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="something-else",
        user_id="dev-user",
    )

    # Bind the PRISM adapter's session to the ADK session id so all
    # traces in this conversation share one trajectory.
    prism_adapter.session_id = session.id

    runner = Runner(
        agent=root_agent,
        app_name="something-else",
        session_service=session_service,
    )

    from google.genai import types  # noqa: E402

    user_msg = types.Content(
        role="user",
        parts=[types.Part(text="Help me decide on a project management tool.")],
    )

    print("Running agent...")
    try:
        async for event in runner.run_async(
            user_id="dev-user",
            session_id=session.id,
            new_message=user_msg,
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"Agent: {part.text}")
    except Exception as exc:
        prism_adapter.record_runner_error(exc)
        raise
    finally:
        prism_adapter.flush() if hasattr(prism_adapter, "flush") else None

    print("\nDone. Check the PRISM dashboard for traces.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

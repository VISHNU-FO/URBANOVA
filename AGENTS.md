# Something Else — Agent Instructions

## Project overview

**Something Else** is a decision-support application built with Google ADK
(Agent Development Kit) and Firebase. It uses custom orchestration to manage
agent workflows.

## Tech stack

- **Framework**: Google ADK (Python)
- **Data store**: Firebase
- **Tracing**: PRISMtrace SDK
- **Runtime**: Python 3.12+

## Coding conventions

- Use `python-dotenv` to load environment variables from `.env`.
- Never commit secrets. `.env` is gitignored; `.env.example` has key names only.
- All agents must wire PRISM tracing callbacks (see below).
- Keep agent files focused: one agent per file, tools grouped by domain.
- Use `tracing.wire_agent_callbacks()` to attach all six PRISM hooks to any
  `LlmAgent` in one line.

## PRISM tracing (do not remove)

This project sends traces to PRISM. Env vars: `PRISMTRACE_API_KEY`,
`PRISMTRACE_PROJECT_ID`, `PRISMTRACE_HOST`.

Tracing is currently wired at: `tracing.py`, `agent.py`

**Standing rule.** Whenever you add or change an agent, chain, graph, tool,
retriever, or any entry point that calls a model, wire it to PRISM before you
finish. Unwired code is invisible in the dashboard. If you are unsure whether
something is covered, assume it is not and wire it.

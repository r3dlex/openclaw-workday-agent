# 0002. Elixir/OTP for Orchestration

Date: 2026-03-18

## Status

Accepted

## Context

The system needs to coordinate multiple concerns:

- Browser backend management (headless Playwright, CDP relay)
- Pipeline step sequencing with retries and timeouts
- LLM calls for task analysis and compliance checking
- Strategy switching (fall from headless to relay on auth failure)
- Graceful handling of crashes in any component

A simple script runner is insufficient: browser processes crash, network requests time
out, and the system must recover without losing pipeline state. We need fault-tolerant
coordination with supervised processes.

## Decision

Use **Elixir/OTP** as the orchestration layer.

- **GenServer: PipelineRunner** -- Manages pipeline state, sequences steps, handles retries
- **GenServer: BrowserManager** -- Manages browser backend lifecycle, strategy switching
- **Erlang Ports** -- Supervised IPC with the Python pipeline runner process
- **Supervision trees** -- Automatic restart of crashed components with backoff

The Elixir orchestrator owns all decision logic: what to do, when to retry, when to
fall back. The Python layer (see [ADR-0003](0003-python-pipeline-runner.md)) handles
only DOM manipulation.

## Consequences

- **Strong fault tolerance**: OTP supervision trees handle crashes, restarts, and backoff automatically
- **Erlang Ports provide supervised IPC**: If the Python process crashes, the Port detects it and the supervisor can restart
- **Clear separation of concerns**: Orchestration logic lives in Elixir; browser automation in Python
- **Team needs Elixir knowledge**: Elixir/OTP is less common than Node.js or Python; onboarding requires learning the ecosystem
- **Well-suited for long-running processes**: The BEAM VM is designed for systems that run indefinitely

# 0003. Python + Playwright as Pipeline Runner

Date: 2026-03-18

## Status

Accepted

## Context

Headless browser automation (see [ADR-0001](0001-headless-browser-primary.md)) requires
a reliable browser automation library. Playwright offers the best cross-browser support
and has mature Python bindings with async support.

The system needs a clean separation between:

- **Orchestration** (what to do): Pipeline sequencing, retries, fallback strategy
- **Execution** (how to do it): DOM queries, clicks, form fills, screenshot capture

Mixing these concerns in a single process makes fault isolation difficult and couples
business logic to browser implementation details.

## Decision

Use **Python + Playwright** as the browser automation layer (pipeline runner).

Communication with the Elixir orchestrator uses a **JSON-lines protocol** over
stdin/stdout (via Erlang Ports):

- Elixir sends a JSON command (one line) to the Python process's stdin
- Python executes the DOM action and writes a JSON response (one line) to stdout
- Each message is a self-contained JSON object terminated by a newline

The Python layer contains **no decision logic**. It only:

- Receives action commands (navigate, click, fill, query, screenshot)
- Executes them against the browser via Playwright
- Returns results (success/failure, extracted data, error details)

All orchestration, retry logic, and strategy decisions remain in Elixir
(see [ADR-0002](0002-elixir-orchestration.md)).

## Consequences

- **Clean separation of concerns**: Python handles only DOM manipulation; all orchestration stays in Elixir
- **JSON-lines protocol is simple and debuggable**: Messages can be logged, replayed, and inspected with standard tools
- **Playwright ecosystem**: Access to Playwright's selector engine, auto-waiting, and trace viewer for debugging
- **Process isolation**: A crash in the Python runner does not bring down the Elixir orchestrator
- **Serialization overhead**: Every action crosses a process boundary via JSON; acceptable for UI automation latency

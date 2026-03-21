# System Architecture

## Overview

The OpenClaw Workday Agent uses a three-layer architecture that separates concerns
between agent intelligence, process orchestration, and browser automation.

```
+----------------------------------------------------------+
|                    OpenClaw Agent                         |
|  (LLM reasoning, user interaction, compliance checks)    |
+------------------------------+---------------------------+
                               |
                          HTTPS / CLI
                               |
+------------------------------v---------------------------+
|                  Elixir Orchestrator                      |
|  PipelineRunner (GenServer)  |  BrowserManager (GenServer)|
|  - Step sequencing           |  - Backend lifecycle       |
|  - Retry logic               |  - Strategy switching      |
|  - Fallback decisions        |  - Health monitoring       |
+----------+-------------------+-----------+---------------+
           |                               |
     Erlang Port                     CDP WebSocket
     (JSON-lines)                    (DevTools Protocol)
           |                               |
+----------v-----------+    +-------------v--------------+
|   Python Runner      |    |      CDP Relay             |
|   (Playwright)       |    |      (Node.js)             |
|   - DOM manipulation |    |   - User's Chrome          |
|   - Headless browser |    |   - SSO/MFA fallback       |
|   - Screenshots      |    |   - Session reuse          |
+----------------------+    +----------------------------+
```

## Components

### OpenClaw Agent

The LLM-powered agent that interprets user requests, applies compliance rules
(see [PROTOCOL.md](../PROTOCOL.md)), and decides which pipeline to execute.
Communicates with the orchestrator to trigger operations.

### Elixir Orchestrator

The coordination layer built on OTP (see [ADR-0002](adr/0002-elixir-orchestration.md)).

- **PipelineRunner**: A GenServer that manages pipeline state. Receives a pipeline
  definition, executes steps in sequence, handles retries, and reports results.
- **BrowserManager**: A GenServer that manages browser backend lifecycle. Starts/stops
  headless browsers, monitors health, and switches strategies on failure.

### Python Pipeline Runner

The browser automation layer (see [ADR-0003](adr/0003-python-pipeline-runner.md)).
A Python process running Playwright that receives action commands from the Elixir
orchestrator via JSON-lines on stdin/stdout. Contains no decision logic -- only
DOM manipulation.

### CDP Relay (Node.js)

The fallback browser backend for SSO flows requiring a visible browser
(see [ADR-0001](adr/0001-headless-browser-primary.md)). Connects to the user's
open Chrome via Chrome DevTools Protocol. Used when headless authentication fails
(e.g., MFA prompts requiring user interaction).

## Data Flow: Task Approval

A typical task approval flows through the system as follows:

1. **User** asks the OpenClaw agent to check pending tasks
2. **Agent** triggers the Task Approval pipeline via the orchestrator
3. **Orchestrator** starts the pipeline:
   a. Checks auth status (runs `ensure_auth` step)
   b. Navigates to the tasks page
   c. Queries the DOM for pending tasks
   d. Returns task list to the agent
4. **Agent** presents tasks to the user with compliance analysis
5. **User** approves a specific task
6. **Orchestrator** executes the approval step
7. **Runner** clicks the approve button, confirms the dialog
8. **Orchestrator** verifies success, returns result to agent
9. **Agent** confirms completion to user

## Browser Strategy

The `BrowserManager` supports three strategies, configured via environment variable:

| Strategy | Behavior |
|----------|----------|
| `headless_first` (default) | Try headless Playwright; fall back to CDP relay on auth failure |
| `headless_only` | Headless only; fail if auth cannot be completed without user interaction |
| `relay_only` | CDP relay only; requires user's Chrome to be open and authenticated |

## IPC: JSON-Lines Protocol

The Elixir orchestrator communicates with the Python runner via a JSON-lines protocol
over stdin/stdout (Erlang Ports). See [PIPELINES.md](PIPELINES.md) for the full
protocol specification.

Each message is a single JSON object on one line:

```
-> {"action": "navigate", "url": "https://your_tenant.workday.com/tasks"}
<- {"status": "ok", "data": {"title": "My Tasks"}}
```

## Logging

Runtime logs go to the `logs/` directory (gitignored, `.gitkeep` tracked):

- `logs/pipeline.log` — pipeline execution events (Python runner)
- `logs/agent.log` — general agent activity

## Further Reading

- [ADR index](adr/README.md) for architectural decisions
- [PIPELINES.md](PIPELINES.md) for pipeline definitions and protocol spec
- [TESTING.md](TESTING.md) for test strategy

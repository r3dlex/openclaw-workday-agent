# API — openclaw-workday-agent

## Overview

The Workday agent does not expose a public HTTP server. All cross-agent
communication uses IAMQ. The Elixir orchestrator exposes a local HTTP API
on port 4001 for internal use between the orchestrator and the Python/Playwright
automation layer. This internal API is not intended for external agents.

---

## IAMQ Message Interface

### Incoming messages accepted by `workday_agent`

| Subject | Purpose | Body fields |
|---------|---------|-------------|
| `workday.sync_timesheet` | Trigger a timesheet sync for the current period | `date?: "YYYY-MM-DD"` |
| `workday.approve_requests` | Process pending approval requests | — |
| `workday.task_summary` | Return a summary of open tasks and approvals | — |
| `workday.check_absence` | Check upcoming approved absences | `days?: number` |
| `workday.status` | Return agent health and last sync timestamp | — |
| `status` | Return agent process health | — |

#### Example: trigger a timesheet sync

```json
{
  "from": "agent_claude",
  "to": "workday_agent",
  "type": "request",
  "priority": "NORMAL",
  "subject": "workday.sync_timesheet",
  "body": {}
}
```

#### Example response

```json
{
  "from": "workday_agent",
  "to": "agent_claude",
  "type": "response",
  "priority": "NORMAL",
  "subject": "workday.sync_timesheet.result",
  "body": {
    "status": "synced",
    "period": "2026-03-30 to 2026-04-05",
    "hours_logged": 40.0,
    "entries_updated": 5,
    "timestamp": "2026-04-02T17:31:00Z"
  }
}
```

#### Example: task summary

```json
{
  "from": "workday_agent",
  "to": "agent_claude",
  "type": "response",
  "subject": "workday.task_summary.result",
  "body": {
    "open_approvals": 2,
    "pending_timesheets": 0,
    "upcoming_absences": 1,
    "action_required": true
  }
}
```

---

## Internal Orchestrator API (Port 4001)

The Elixir orchestrator exposes a local REST API consumed only by the Python
automation layer running on the same host. External agents must NOT call this
directly — use IAMQ instead.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/internal/run` | POST | Start a Playwright automation job |
| `/internal/status` | GET | Return current job status |
| `/internal/result` | GET | Fetch the result of the last completed job |

---

## Company Norms

Certain behaviours are restricted by company policy documents in `company-norms/`
(gitignored, mounted at runtime). The agent reads these to determine which
Workday actions it may take autonomously vs. which require user confirmation.
See `spec/safety-boundaries.md` for the full constraint set.

---

**Related:** `spec/COMMUNICATION.md`, `spec/ARCHITECTURE.md`, `spec/safety-boundaries.md`

# Communication

IAMQ messaging patterns for the OpenClaw Workday Agent.

## Registration

The agent registers with the Inter-Agent Message Queue on startup:

```json
{
  "agent_id": "workday_agent",
  "capabilities": [
    "workday_approvals",
    "time_tracking",
    "hr_automation",
    "browser_automation",
    "task_management"
  ]
}
```

Environment variables: `IAMQ_HTTP_URL`, `IAMQ_WS_URL`, `IAMQ_AGENT_ID`.
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for registration failure diagnostics.

## Inbound Message Routing

Incoming IAMQ messages are routed by subject keyword matching:

| Subject contains | Route to | Pipeline |
|------------------|----------|----------|
| `approve`, `approval` | Task Approval handler | Task Approval (see [PIPELINES.md](PIPELINES.md)) |
| `time`, `timesheet` | Time Tracking handler | Time Tracking |
| `status` | Status reporter | Returns current pipeline state |

Messages that match no route are logged and acknowledged without action.

### Request Format

```json
{
  "from": "main",
  "to": "workday_agent",
  "subject": "approve pending tasks",
  "body": { "filter": "urgent" },
  "reply_to": "main"
}
```

### Response Format

```json
{
  "from": "workday_agent",
  "to": "main",
  "subject": "approval_result",
  "body": {
    "status": "completed",
    "tasks_approved": 2,
    "tasks_skipped": 1
  }
}
```

## Peer Agents

| Agent | Interaction | Direction |
|-------|-------------|-----------|
| `main` | Status reports, task results, escalations | Outbound |
| `main` | Task requests, approval instructions | Inbound |
| `broadcast` | Completion announcements, compliance warnings | Outbound |

### Status Reports

On pipeline completion, the agent sends a summary to `main`:

```json
{
  "from": "workday_agent",
  "to": "main",
  "subject": "status",
  "body": {
    "pipeline": "task_approval",
    "result": "completed",
    "summary": "Approved 3 tasks, 1 requires manual review"
  }
}
```

### Broadcast Announcements

Significant events are broadcast to all agents:

- Pipeline completion (approval batches, timesheet submissions)
- Compliance warnings (overtime threshold, flex frame violations)
- Agent health changes (session expired, reconnecting)

```json
{
  "from": "workday_agent",
  "to": "broadcast",
  "subject": "completion",
  "body": {
    "event": "weekly_timesheet_validated",
    "details": "39h logged, all entries within flex frame"
  }
}
```

## Group Chat Behavior

When operating in Telegram or other group contexts, the agent follows
[group-chat-protocol.md](group-chat-protocol.md):

- Respond only when directly mentioned or when adding genuine value
- Use `HEARTBEAT_OK` for silent acknowledgment
- Never share private Workday data in group channels
- Keep messages concise; link to detailed results rather than inlining them

## Heartbeat Integration

The agent participates in the IAMQ heartbeat system
(see [heartbeat-strategy.md](heartbeat-strategy.md)):

- Sends periodic heartbeats to confirm liveness
- On heartbeat poll, checks for pending Workday tasks if the last check was >30 min ago
- Escalates urgent items (overdue approvals) via direct message to `main`

## Error Escalation

When the agent cannot complete a request:

1. Retry once (handled by the orchestrator -- see [ARCHITECTURE.md](ARCHITECTURE.md))
2. If retry fails, send error report to `main` with failure reason
3. If the error is auth-related, include instructions for the user to re-authenticate

```json
{
  "from": "workday_agent",
  "to": "main",
  "subject": "error",
  "body": {
    "pipeline": "task_approval",
    "error": "AUTH_REQUIRED",
    "message": "Workday session expired. Please re-authenticate in Chrome."
  }
}
```

---

*Owner: dev team. Last updated: 2026-03-23.*

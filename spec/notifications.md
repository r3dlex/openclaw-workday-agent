# Notifications

## Overview

The agent sends important operational events to the user via Telegram.
Notifications are a complement to the interactive chat, not a replacement.
They ensure the user is aware of events that require attention even when not
actively in conversation.

## Channel: Telegram

Configuration (`.env`):

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Target chat (user or group) |

If either variable is empty, notifications are silently skipped and a warning
is logged to `logs/notifications.log`.

## What Gets Notified

| Event | Priority | Example |
|-------|----------|---------|
| Task approval completed | High | "Approved PTO request for Max Mustermann (3 days)" |
| Task denied or sent back | High | "Denied overtime request: exceeds 10h/day limit" |
| Compliance warning | High | "Time entry implies 11h workday (legal violation)" |
| Time tracking reminder | Medium | "Daily time entry reminder: no entry for today yet" |
| Pipeline failure | Medium | "Task approval pipeline failed: AUTH_REQUIRED" |
| Heartbeat anomaly | Low | "Heartbeat detected 3 overdue tasks" |
| Session started | Low | "Agent session started" |

## Message Format

Messages use Telegram's MarkdownV2 formatting:

```
*[PRIORITY] Event Title*

Details of the event in 1-2 sentences.

_Timestamp: 2024-03-19 14:30 CET_
```

## When NOT to Notify

- Routine `HEARTBEAT_OK` responses (nothing to report)
- Intermediate pipeline steps (only final results)
- Late night (23:00-08:00) unless priority is High
- Duplicate events within 5 minutes (debounce)

## Logging

All notification attempts (sent, skipped, failed) are logged to
`logs/notifications.log` with timestamps. This allows debugging delivery
issues without exposing message content in git.

## Implementation

### Elixir Orchestrator

`Orchestrator.Notifications.Telegram` module sends messages via the
Telegram Bot API (`POST /bot<token>/sendMessage`). Used by pipeline
steps to report outcomes.

### Python Runner

`pipeline_runner.notifications` module provides a `notify()` helper
for sending messages from within pipeline actions. Used sparingly,
since most notifications originate from the orchestrator layer.

### OpenClaw Agent

The agent can send notifications directly using the Telegram Bot API
via HTTP. It should do so for compliance warnings and user-facing
decisions that happen outside of pipelines.

## Further Reading

- [heartbeat-strategy.md](heartbeat-strategy.md) for periodic check scheduling
- [PIPELINES.md](PIPELINES.md) for pipeline event lifecycle
- [safety-boundaries.md](safety-boundaries.md) for data handling rules

# Cron Schedules — openclaw-workday-agent

## Overview

The Workday agent runs a weekday afternoon timesheet sync. This is the primary
scheduled task; all other Workday interactions (approvals, task checks) are
triggered on-demand via IAMQ. All crons are registered with IAMQ on startup.

## Schedules

### timesheet_sync
- **Expression**: `30 17 * * 1-5` (17:30 UTC Mon-Fri)
- **Purpose**: Log into Workday via Playwright headless browser, compare locally
  tracked hours against Workday entries for the current pay period, fill in any
  gaps, and submit. Reads time entries from `$WORKDAY_DATA_DIR/timesheet.json`.
  The Elixir orchestrator coordinates with the Python automation layer via the
  internal port-4001 API.
- **Trigger**: Delivered via IAMQ message `cron::timesheet_sync`
- **Handler**: `Orchestrator.Pipeline.run(:timesheet_sync)` (Elixir) →
  `pipeline_runner.timesheet.sync()` (Python/Playwright)
- **Expected duration**: 3–8 minutes (Workday UI can be slow; Playwright retries
  on transient failures up to 3 times)
- **On failure**: Log error to `logs/`; send IAMQ alert to `agent_claude` and
  user via Telegram; do NOT retry automatically (risk of duplicate submissions)

### approval_check
- **Expression**: `0 9 * * 1-5` (09:00 UTC Mon-Fri)
- **Purpose**: Check the Workday inbox for pending approval requests (absence
  requests, expense reports, task reassignments). Log findings. Deliver a
  summary to `agent_claude` if any action is required. Does not auto-approve
  anything without explicit permission.
- **Trigger**: Delivered via IAMQ message `cron::approval_check`
- **Handler**: `Orchestrator.Pipeline.run(:approval_check)`
- **Expected duration**: 1–3 minutes
- **On failure**: Log error; skip; operator can trigger `workday.approve_requests`
  via IAMQ manually

## Cron Registration

Registered with IAMQ on startup via `POST /crons`:

```json
[
  {"subject": "cron::approval_check",  "expression": "0 9 * * 1-5"},
  {"subject": "cron::timesheet_sync",  "expression": "30 17 * * 1-5"}
]
```

## Safety Constraints on Cron Actions

The agent will not submit a timesheet if:
- Hours for the period differ by more than 2 hours from the expected schedule
- A pay period has already been submitted and locked
- The Playwright session cannot authenticate (login error)

In any of these cases, the cron fails gracefully and raises an IAMQ alert
for human review. See `spec/safety-boundaries.md` for the full rule set.

## Manual Trigger

```bash
# Trigger timesheet sync via Makefile
make timesheet-sync

# Or via IAMQ
curl -X POST http://127.0.0.1:18790/send \
  -H "Content-Type: application/json" \
  -d '{"from":"developer","to":"workday_agent","type":"request","priority":"HIGH","subject":"workday.sync_timesheet","body":{}}'
```

---

**Related:** `spec/API.md`, `spec/COMMUNICATION.md`, `spec/safety-boundaries.md`

## References

- [IAMQ Cron Subsystem](https://github.com/r3dlex/openclaw-inter-agent-message-queue/blob/main/spec/CRON.md) — how cron schedules are stored and fired
- [IAMQ API — Cron endpoints](https://github.com/r3dlex/openclaw-inter-agent-message-queue/blob/main/spec/API.md#cron-scheduling)
- [IamqSidecar.MqClient.register_cron/3](https://github.com/r3dlex/openclaw-inter-agent-message-queue/tree/main/sidecar) — Elixir sidecar helper
- [openclaw-main-agent](https://github.com/r3dlex/openclaw-main-agent) — orchestrates cron-triggered pipelines

# Heartbeat & Scheduling Strategy

> Extracted from AGENTS.md — when and how to use heartbeats vs cron tasks.

## Heartbeat Overview

On receiving a heartbeat poll, the agent checks `HEARTBEAT.md` for pending tasks. If nothing needs attention, reply `HEARTBEAT_OK`.

The agent may edit `HEARTBEAT.md` to add short checklists or reminders. Keep it small to limit token usage.

## Heartbeat vs Cron

| Use Heartbeat when... | Use Cron when... |
|----------------------|------------------|
| Multiple checks can batch together | Exact timing matters ("9:00 AM sharp") |
| You need recent conversational context | Task needs isolation from main session |
| Timing can drift (~30 min is fine) | Different model/thinking level needed |
| Reducing API calls by combining checks | One-shot reminders |

**Tip:** Batch similar periodic checks into `HEARTBEAT.md`. Use cron for precise schedules and standalone tasks.

## Periodic Checks (rotate 2-4 times/day)

- **Emails** — urgent unread messages?
- **Calendar** — events in next 24-48h?
- **Mentions** — social notifications?
- **Weather** — relevant if human might go out?

Track check timestamps in `memory/heartbeat-state.json`.

## When to Reach Out

- Important email arrived
- Calendar event approaching (<2h)
- Something interesting discovered
- Been >8h since last message

When reaching out, also send a Telegram notification for high-priority items
(overdue tasks, compliance warnings). See `spec/notifications.md`.

## When to Stay Quiet (HEARTBEAT_OK)

- Late night (23:00-08:00) unless urgent
- Human is clearly busy
- Nothing new since last check
- Checked <30 minutes ago

## Proactive Work (no permission needed)

- Read and organize memory files
- Check project status (git status, etc.)
- Update documentation
- Commit and push own changes
- Review and update MEMORY.md

# AGENT.md — Workday Entry Points

## Navigation

All Workday URLs are constructed from environment variables:

| Page | Environment Variable | Description |
|------|---------------------|-------------|
| Time Entries | `WORKDAY_BASE_URL` + `WORKDAY_TIME_TRACKING_PATH` | Personal time entry page |
| Tasks / Inbox | `WORKDAY_BASE_URL` + `WORKDAY_TASKS_PATH` | Pending HR items |
| Home | `WORKDAY_BASE_URL` + `WORKDAY_HOME_PATH` | Dashboard with "My Tasks" |

## Quick Reference

- Use the OpenClaw browser profile for Workday automation
- Check "Enter My Time" for time entry overview
- Flex time accumulates when working >8h/day
- See `PROTOCOL.md` for the full task processing workflow

# HEARTBEAT.md

## On every poll

1. **IAMQ heartbeat** — Send a heartbeat to stay visible to other agents:
   `POST $IAMQ_HTTP_URL/heartbeat` with `{"agent_id": "$IAMQ_AGENT_ID"}`
   If the service is unreachable, log a warning and continue.

2. **Check inbox** — Fetch unread messages:
   `GET $IAMQ_HTTP_URL/inbox/$IAMQ_AGENT_ID?status=unread`
   - For each message, decide whether to act, respond, or acknowledge.
   - Mark handled messages as `read` or `acted` via `PATCH /messages/:id`.
   - If a message requires user confirmation (e.g., a task approval request from another agent), present it to the user before acting.

3. **Workday tasks** — If no pending messages need attention, check for Workday tasks per `SOUL.md` and `PROTOCOL.md`.

## Notes

- All env vars (`IAMQ_HTTP_URL`, `IAMQ_AGENT_ID`) are in `.env`.
- See `TOOLS.md` for the full IAMQ API reference and sibling agent list.
- If `IAMQ_HTTP_URL` is empty, skip steps 1-2 silently.

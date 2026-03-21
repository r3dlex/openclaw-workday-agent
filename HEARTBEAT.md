# HEARTBEAT.md

## On session start

1. **Register with full metadata** — Not just `agent_id`. Include name, emoji, description, capabilities, and workspace:
   ```
   POST $IAMQ_HTTP_URL/register
   {
     "agent_id": "workday_agent",
     "name": "HROps",
     "emoji": "🏢",
     "description": "HR operations automation — Workday task approvals, time tracking, compliance checks",
     "capabilities": ["workday_approvals", "time_tracking", "compliance_checks", "hr_notifications"],
     "workspace": "<absolute path to this workspace>"
   }
   ```

2. **Send initial heartbeat:**
   `POST $IAMQ_HTTP_URL/heartbeat` with `{"agent_id": "workday_agent"}`

3. **Check inbox** and process unread messages (see below).

4. **Discover sibling agents:**
   `GET $IAMQ_HTTP_URL/agents`

## On every poll

1. **IAMQ heartbeat** — Send a heartbeat to stay visible to other agents:
   `POST $IAMQ_HTTP_URL/heartbeat` with `{"agent_id": "workday_agent"}`
   If the service is unreachable, log a warning and continue.

2. **Check inbox** — Fetch unread messages:
   `GET $IAMQ_HTTP_URL/inbox/workday_agent?status=unread`
   - For each message, decide whether to act, respond, or acknowledge.
   - Mark handled messages as `read` or `acted` via `PATCH /messages/:id`.
   - Reply to agents via `POST /send` with `replyTo` set to the original message ID.
   - If a message requires user confirmation (e.g., a task approval request from another agent), present it to the user before acting.

3. **Workday tasks** — If no pending messages need attention, check for Workday tasks per `SOUL.md` and `PROTOCOL.md`.

## Notes

- All env vars (`IAMQ_HTTP_URL`, `IAMQ_AGENT_ID`) are in `.env`.
- See `TOOLS.md` for the full IAMQ API reference and sibling agent list.
- For the full IAMQ protocol, read `spec/PROTOCOL.md` in the MQ workspace.
- Telegram is the user-facing log. The MQ is the inter-agent backbone.
- If `IAMQ_HTTP_URL` is empty, skip IAMQ steps silently.

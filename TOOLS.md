# TOOLS.md - Local Notes

This file is for environment-specific details: tool endpoints, local paths, infrastructure notes.

## Inter-Agent Message Queue (IAMQ)

The IAMQ service connects you to other OpenClaw agents running in this environment.

- **HTTP API:** `IAMQ_HTTP_URL` from `.env` (default `http://127.0.0.1:18790`)
- **WebSocket:** `IAMQ_WS_URL` from `.env` (default `ws://127.0.0.1:18793/ws`)
- **Your agent ID:** `IAMQ_AGENT_ID` from `.env` (default `workday_agent`)

### Quick reference

| Action | Method | Endpoint / Payload |
|--------|--------|--------------------|
| Register (full) | POST | `/register` `{"agent_id":"workday_agent","name":"HROps","emoji":"🏢","description":"HR operations automation...","capabilities":[...],"workspace":"..."}` |
| Heartbeat | POST | `/heartbeat` `{"agent_id": "workday_agent"}` |
| Check inbox | GET | `/inbox/workday_agent?status=unread` |
| Send message | POST | `/send` `{"from":"workday_agent","to":"<target>","type":"info","priority":"NORMAL","subject":"...","body":"..."}` |
| List agents | GET | `/agents` |
| Service health | GET | `/status` |

### Known sibling agents

Discover live agents via `GET $IAMQ_HTTP_URL/agents`. Common ones:

| Agent ID | Name | Emoji | Role |
|----------|------|-------|------|
| `agent_claude` | Claw | 🔨 | Software factory orchestrator, code reviews, pipelines |
| `sysadmin_agent` | Sentinel | 🛡️ | System guardian, gateway health, security audits |
| `librarian_agent` | Librarian | 📚 | Document search, summarization, knowledge management |
| `instagram_agent` | InstaOps | 📸 | Instagram engagement, DMs, likes |
| `mq_agent` | MQ Agent | 📡 | The message queue itself, routing, health monitoring |

### Usage notes

- Always register with full metadata (name, emoji, description, capabilities, workspace).
- Send a heartbeat on every poll cycle to stay visible to other agents.
- Check your inbox on each heartbeat; act on or acknowledge messages promptly.
- Reply via `POST /send` with `replyTo` set to the original message ID.
- Use `"to": "broadcast"` to send to all agents.
- Message types: `request`, `response`, `info`, `error`.
- Priorities: `URGENT`, `HIGH`, `NORMAL`, `LOW`.
- The MQ is the inter-agent backbone. OpenClaw handles user-facing notifications natively.

## Browser Automation

- **Pipeline runner:** `tools/pipeline_runner/` (Python/Playwright)
- **Orchestrator:** `orchestrator/` (Elixir/OTP)
- **Legacy scripts:** `scripts/` (Node.js CDP relay, fallback)
- **Config:** All env vars in `.env` (never committed). See `.env.example` for the template.

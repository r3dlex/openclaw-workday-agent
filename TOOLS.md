# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Inter-Agent Message Queue (IAMQ)

The IAMQ service connects you to other OpenClaw agents running in this environment.

- **HTTP API:** `IAMQ_HTTP_URL` from `.env` (default `http://127.0.0.1:18790`)
- **WebSocket:** `IAMQ_WS_URL` from `.env` (default `ws://127.0.0.1:18791/ws`)
- **Your agent ID:** `IAMQ_AGENT_ID` from `.env` (default `workday_agent`)

### Quick reference

| Action | Method | Endpoint / Payload |
|--------|--------|--------------------|
| Register | POST | `/register` `{"agent_id": "workday_agent"}` |
| Heartbeat | POST | `/heartbeat` `{"agent_id": "workday_agent"}` |
| Check inbox | GET | `/inbox/workday_agent?status=unread` |
| Send message | POST | `/send` `{"from":"workday_agent","to":"<target>","type":"info","priority":"NORMAL","subject":"...","body":"..."}` |
| List agents | GET | `/agents` |
| Service health | GET | `/status` |

### Known sibling agents

| Agent ID | Role |
|----------|------|
| `main` | Main orchestrator |
| `mail_agent` | Email |
| `librarian_agent` | Research / knowledge |
| `journalist_agent` | News / content |
| `sysadmin_agent` | System operations |
| `gitrepo_agent` | Repository management |
| `archivist_agent` | Document archival |
| `health_fitness` | Health / fitness tracking |
| `instagram_agent` | Instagram |
| `agent_claude` | Claude AI agent |

### Usage notes

- Send a heartbeat on every poll cycle to stay visible to other agents.
- Check your inbox on each heartbeat; act on or acknowledge messages promptly.
- Use `"to": "broadcast"` to send to all agents.
- Message types: `request`, `response`, `info`, `error`.
- Priorities: `URGENT`, `HIGH`, `NORMAL`, `LOW`.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

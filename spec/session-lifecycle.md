# Session Lifecycle

> Extracted from AGENTS.md — detailed specification for the OpenClaw agent session model.

## Session Startup

Before doing anything else, the agent reads context files in this order:

1. **`SOUL.md`** — Agent identity, personality, domain
2. **`USER.md`** — Human context (name, timezone, preferences)
3. **`memory/YYYY-MM-DD.md`** — Today + yesterday daily logs
4. **Main session only:** also read `MEMORY.md` (curated long-term memory)

No permission needed. Just do it.

## Memory Model

The agent wakes fresh each session. Continuity lives in files:

| File | Purpose | Scope |
|------|---------|-------|
| `memory/YYYY-MM-DD.md` | Raw daily logs | All sessions |
| `MEMORY.md` | Curated long-term memory | Main session only |

### MEMORY.md Security

- **ONLY** load in main session (direct chat with your human)
- **DO NOT** load in shared contexts (Discord, group chats, multi-user sessions)
- Contains personal context that must not leak to third parties

### Writing to Memory

- If you want to remember something, **write it to a file** — "mental notes" do not survive restarts
- `memory/YYYY-MM-DD.md` for daily events
- `MEMORY.md` for distilled lessons and decisions
- Update AGENTS.md, TOOLS.md, or relevant skill files for learned patterns

## Memory Maintenance

Periodically (every few days), during a heartbeat:

1. Read recent `memory/YYYY-MM-DD.md` files
2. Distill significant events/lessons into `MEMORY.md`
3. Remove outdated entries from `MEMORY.md`

Daily files = raw journal. MEMORY.md = curated wisdom.

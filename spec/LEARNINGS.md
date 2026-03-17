# Operational Learnings

What works, what breaks, and what we learned the hard way.

> This file is maintained by developers and agents working on this repo.
> Add new entries at the top of each section. Date your entries.

---

## SSO & Authentication

| # | Learning | Detail |
|---|----------|--------|
| 1 | **SSO button click is fragile** | The Workday SSO landing page renders provider buttons dynamically. The agent sometimes cannot find or click `SSO_PROVIDER_NAME`. Always have the `ORG_TENANT_DIRECT_LINK` fallback ready; it bypasses the selector entirely. |
| 2 | **After SSO redirect, re-navigate** | The redirect does not always land on the originally requested page. After authentication completes, navigate back to the target `WORKDAY_TASKS_PATH` or `WORKDAY_TIME_TRACKING_PATH` explicitly. |
| 3 | **Session cookies expire silently** | A tab that was logged in hours ago may have an expired session. Check for login prompts before assuming the page is ready. |

## Chrome DevTools Protocol (CDP)

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Append token to WebSocket URL** | The CDP discovery endpoint returns `webSocketDebuggerUrl` without the auth token. Scripts must append `?token=CHROME_CDP_TOKEN` if not already present (see `approve-workday.js` line ~87). |
| 2 | **Tab discovery needs dual matching** | Find the Workday tab by URL (`.includes("workday.com")`) *or* title (`.includes("Workday")`). Either can be absent depending on page state. |
| 3 | **Button selectors must be broad** | Workday uses both native `<button>` and `<div role="button">`. Use `querySelectorAll('button, div[role="button"]')` to catch both. |
| 4 | **Docker to host connectivity** | Containers reach Chrome on the host via `host.docker.internal`. Set `CDP_HOST=host.docker.internal` in docker-compose and add the `extra_hosts` entry. Without this, CDP WebSocket connections fail silently. |

## Time Tracking & Compliance

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Flex time frame is 07:00 to 19:00** | Building access outside this window requires management approval. The agent should warn users attempting to log hours outside this range. |
| 2 | **Core hours are 09:00 to 16:00** | Minus lunch break. Mandatory presence window. Meetings should be scheduled within this band. |
| 3 | **Plus/minus balance has a 2-month cycle** | Max 10 hours carry over. The agent should track cumulative balance when reviewing time entries and flag when approaching the limit. |
| 4 | **Comp days cannot adjoin annual leave** | Up to 6 per year from plus hours, but they must not be taken next to vacation or as a continuous block. Workday does not enforce this; the agent must. |
| 5 | **On departure, minus hours are deducted from pay** | Plus hours are forfeited if not taken before notice period ends. Worth flagging to the user during offboarding tasks. |
| 6 | **Public holidays are state-specific** | Baden-Wuerttemberg holidays differ from other German states. Check BW calendar before prompting for time entry. |

## Compliance Lookup Chain

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Three-tier lookup works well** | `PROTOCOL.md` summary → `company-norms/INDEX.md` decision framework → full agreement text. The first tier handles ~90% of decisions. Only escalate to full text when quoting specific clauses. |
| 2 | **Never assume approval** | The five-step workflow (analyze → summarize → compliance check → likelihood → ask user) exists because auto-approving is legally indefensible. Always ask. |

## Agent Memory & Session Management

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Agent wakes stateless** | No context survives between sessions except what is written to files. Mental notes, partial thoughts, and mid-task state are lost on restart. Write important state to `memory/` immediately. |
| 2 | **Two-tier memory prevents bloat** | `memory/YYYY-MM-DD.md` for raw daily logs; `MEMORY.md` for curated long-term knowledge. Daily files can grow large; the curated file should stay lean. |
| 3 | **MEMORY.md must not leak to group chats** | It contains personal user context. In shared/Discord sessions, only `memory/YYYY-MM-DD.md` is safe to reference. |

## Heartbeat vs Cron

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Heartbeat for batched, drift-tolerant checks** | Multiple checks in one pass; saves API calls. ~30 min timing drift is acceptable. |
| 2 | **Cron for exact-time, isolated tasks** | Morning reminders, end-of-day summaries. Runs in its own session, no conversational context needed. |
| 3 | **Duplicate check prevention** | Store last-check timestamps in `memory/heartbeat-state.json`. Skip if checked < 30 minutes ago. |
| 4 | **Late-night silence window: 23:00 to 08:00** | Unless something is genuinely urgent, return `HEARTBEAT_OK` and let the human sleep. |

## Group Chat Behavior

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Less is more** | Humans do not respond to every message. Neither should the agent. One thoughtful response beats three fragments. |
| 2 | **Never proxy the user** | The agent has access to the human's data; it must not share it in group contexts unless explicitly asked. |
| 3 | **Avoid the triple-tap** | Do not respond multiple times to the same message. |

## Documentation & Repo Hygiene

| # | Learning | Detail |
|---|----------|--------|
| 1 | **Hardcoded secrets are painful to remove** | Git history rewriting is expensive. Always use `.env` from the start. The refactor to environment variables (commit `1b233f7`) taught this lesson. |
| 2 | **Progressive disclosure scales** | Flat docs get long and ignored. Layered docs (summary → detail) keep both quick-glancers and deep-divers happy. |
| 3 | **Two audiences, two file sets** | Agent runtime files (AGENTS.md, SOUL.md, etc.) and dev files (CLAUDE.md, scripts/) serve different readers. Mixing them causes confusion about "who reads what." |
| 4 | **No dashes in agent output** | The `--` and em-dash `—` constraint in SOUL.md is real. Likely a downstream parsing issue. Weird rules exist for a reason; honor them. |
| 5 | **Docker zero-install removes setup bugs** | `docker compose run --rm` isolates execution. No "works on my machine" issues. Alpine + Node.js 18 is minimal and sufficient. |

---

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It Fails |
|--------------|-------------|
| Auto-approving Workday tasks | Legally indefensible. Always require explicit user decision. |
| Storing secrets in Markdown | Gets committed, pushed, and shared. Use `.env` exclusively. |
| Sleeping in retry loops | Blocks the session. Use proper error handling and fallbacks. |
| Sending `rm` without asking | Prefer `trash`; recoverable > gone forever. |
| Responding to every group message | Noise. Follow the "would a human respond?" test. |
| Amending commits after hook failure | The commit never happened; `--amend` modifies the *previous* commit, destroying work. Create a new commit instead. |
| Using `-uall` with git status | Can cause memory issues on large repos. Use plain `git status`. |

---

*Last updated: 2026-03-17*

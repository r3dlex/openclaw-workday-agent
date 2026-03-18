# CLAUDE.md — Developer Guide

This file is for **you** (Claude Code, Cursor, or any dev agent working on this repo).
It is not read by the OpenClaw agent at runtime.

## What This Repo Is

An [OpenClaw](https://docs.openclaw.ai/) agent that automates Workday HR operations
(task approvals, time tracking) via browser automation over Chrome DevTools Protocol.

## Repository Layout

```
.
├── CLAUDE.md              ← You are here (dev guide)
├── README.md              ← Public-facing documentation
├── AGENTS.md              ← OpenClaw agent operating manual
├── SOUL.md                ← Agent identity & personality
├── PROTOCOL.md            ← HR operational protocol & compliance rules
├── AGENT.md               ← Workday navigation entry points
├── IDENTITY.md            ← Agent self-description template (OpenClaw)
├── USER.md                ← Human context template (OpenClaw)
├── TOOLS.md               ← Local environment notes (OpenClaw)
├── HEARTBEAT.md           ← Periodic task checklist (OpenClaw)
├── spec/                  ← Detailed specifications (referenced by AGENTS.md)
│   ├── ARCHITECTURE.md    ← System architecture (three-layer design)
│   ├── PIPELINES.md       ← Pipeline definitions & lifecycle
│   ├── TESTING.md         ← Test strategy & conventions
│   ├── LEARNINGS.md       ← Operational knowledge base (maintained by agents)
│   ├── adr/               ← Architecture Decision Records (archgate/cli)
│   ├── session-lifecycle.md
│   ├── safety-boundaries.md
│   ├── group-chat-protocol.md
│   ├── heartbeat-strategy.md
│   └── company-norms.md   ← Committed stub for company-norms setup
├── orchestrator/          ← Elixir/OTP orchestration layer
│   ├── lib/orchestrator/  ← Pipeline runner, browser manager, workday steps
│   ├── test/              ← ExUnit tests
│   └── mix.exs
├── tools/
│   └── pipeline_runner/   ← Python/Playwright headless browser automation
│       ├── pipeline_runner/ ← Actions, selectors, protocol, browser
│       ├── tests/         ← Pytest tests
│       └── pyproject.toml ← Poetry project
├── company-norms/         ← Work council agreements (GITIGNORED, not committed)
│   └── README.md          ← Explains what goes here
├── scripts/               ← Legacy Node.js CDP scripts (relay fallback)
│   ├── approve-workday.js
│   └── get-token.js
├── Makefile               ← Developer commands (make test, make build)
├── Dockerfile             ← Zero-install container (Node.js legacy)
├── docker-compose.yml     ← Multi-service orchestration
├── docker-compose.test.yml ← Test overrides
├── package.json
├── .env.example           ← Template for environment variables
└── .env                   ← Actual secrets (GITIGNORED)
```

### Two audiences, two file sets

| Audience | Files |
|----------|-------|
| **OpenClaw agent** (runtime) | AGENTS.md, SOUL.md, PROTOCOL.md, AGENT.md, IDENTITY.md, USER.md, TOOLS.md, HEARTBEAT.md, `company-norms/`, `spec/` |
| **Dev agents** (you) | CLAUDE.md, README.md, `scripts/`, `orchestrator/`, `tools/`, Makefile, Dockerfile(s), docker-compose.yml, `.env.example`, `spec/adr/`, `spec/ARCHITECTURE.md`, `spec/PIPELINES.md`, `spec/TESTING.md` |

## Key Principles

1. **No secrets in git.** All credentials go in `.env`. The `.gitignore` blocks `.env`, `company-norms/`, `.openclaw/`, `memory/`, `logs/`, `artifacts/`.
2. **Progressive disclosure.** AGENTS.md is a concise entry point; details live in `spec/` files. PROTOCOL.md summarizes compliance rules; full agreements live in `company-norms/`.
3. **Zero-install via Docker.** Scripts run in containers: `docker compose run --rm agent node scripts/approve-workday.js`
4. **Agent autonomy.** The OpenClaw agent is designed to make its own decisions within the safety boundaries defined in `spec/safety-boundaries.md`. It asks the user before taking external actions.

## Environment Variables

See `.env.example` for the full list. Key variables:

- `ORG_NAME` / `SSO_PROVIDER_NAME` — Organization name and SSO identity provider label
- `ORG_TENANT_ID` / `ORG_TENANT_DIRECT_LINK` — Azure AD tenant and direct SSO fallback URL
- `CHROME_CDP_TOKEN` / `CHROME_CDP_PORT` — Chrome DevTools Protocol auth
- `WORKDAY_BASE_URL` — Workday tenant root
- `WORKDAY_TIME_TRACKING_PATH` / `WORKDAY_TASKS_PATH` / `WORKDAY_HOME_PATH` — page paths

## Components

| Component | Language | Purpose |
|-----------|----------|---------|
| `orchestrator/` | Elixir/OTP | Pipeline coordination, browser strategy, fault tolerance |
| `tools/pipeline_runner/` | Python | Playwright headless browser automation |
| `scripts/` | Node.js | Legacy CDP relay scripts (fallback) |

### Running

```bash
make test            # Run all tests (Python + Elixir)
make test-docker     # Run tests in Docker (zero-install)
make build           # Build all Docker images
docker compose up -d # Start orchestrator + pipeline runner
```

> Architecture: `spec/ARCHITECTURE.md` | Pipelines: `spec/PIPELINES.md` | Testing: `spec/TESTING.md`

## Making Changes

- **Agent behavior:** Edit AGENTS.md, SOUL.md, PROTOCOL.md, or files in `spec/`
- **Compliance rules:** Update PROTOCOL.md summary AND the full docs in `company-norms/`
- **Pipelines:** Edit `tools/pipeline_runner/` (Python) or `orchestrator/` (Elixir), run `make test`
- **Legacy scripts:** Edit files in `scripts/`, rebuild Docker image
- **Architecture decisions:** Add ADRs in `spec/adr/` following the template
- **New env vars:** Add to both `.env` and `.env.example` (with dummy values in example)

## Conventions

- No hardcoded URLs, tokens, or local paths in committed files
- Scripts read all config from environment variables
- Markdown files use progressive disclosure: summary first, link to details
- The OpenClaw agent files (AGENTS.md, SOUL.md, etc.) follow [OpenClaw template conventions](https://docs.openclaw.ai/reference/templates/)

<p align="center">
  <img src="assets/logo.svg" alt="Workday Agent logo" width="96" height="96">
</p>

# OpenClaw Workday Agent

An [OpenClaw](https://docs.openclaw.ai/) agent that automates Workday HR operations
through browser interactions — not API calls.

## What It Does

- **Task approvals** — Reviews pending HR tasks, checks compliance against work council
  agreements (Betriebsvereinbarungen), and executes approvals with user confirmation
- **Time tracking** — Validates and assists with daily time entry per German labor regulations

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) (recommended, zero-install) **or** local runtimes:
  - Python 3.11+ with [Poetry](https://python-poetry.org/)
  - [Elixir](https://elixir-lang.org/) 1.17+
  - [Node.js](https://nodejs.org/) 18+
- An [OpenClaw](https://docs.openclaw.ai/) workspace

### Setup

```bash
# Clone the repository
git clone https://github.com/r3dlex/openclaw-workday-agent.git
cd openclaw-workday-agent

# Configure environment
cp .env.example .env
# Edit .env with your actual values

# Install dependencies (skip if using Docker)
npm install
```

### Run

```bash
# Docker (zero-install, recommended)
docker compose up -d

# Run tests
make test          # Local (requires Python + Elixir)
make test-docker   # Docker (zero-install)

# Legacy CDP relay (requires Chrome with DevTools Protocol)
docker compose run --rm agent node scripts/approve-workday.js
```

## Project Structure

```
AGENTS.md              # OpenClaw agent operating manual
SOUL.md                # Agent identity & personality
PROTOCOL.md            # HR operational protocol & compliance
AGENT.md               # Workday navigation entry points
spec/                  # Detailed specifications
  ├── ARCHITECTURE.md    # System architecture (three-layer design)
  ├── PIPELINES.md       # Pipeline definitions & lifecycle
  ├── TESTING.md         # Test strategy & conventions
  ├── LEARNINGS.md       # Operational knowledge base
  ├── adr/               # Architecture Decision Records
  └── ...                # Safety, session, heartbeat, group chat specs
orchestrator/          # Elixir/OTP orchestration layer
tools/pipeline_runner/ # Python/Playwright headless browser automation
scripts/               # Legacy Node.js CDP relay (fallback)
company-norms/         # Work council agreements (gitignored)
.env.example           # Environment variable template
Makefile               # Developer commands (make test, make build, etc.)
```

For developer documentation, see [CLAUDE.md](CLAUDE.md).

## Configuration

All configuration is via environment variables. See [.env.example](.env.example)
for the full list with descriptions.

### Company Norms

Place your work council agreements (Betriebsvereinbarungen) in `company-norms/` as
Markdown or PDF files. This directory is gitignored and never committed.

The agent reads these for compliance decisions when approving Workday tasks. If absent,
it falls back to the summary in [PROTOCOL.md](PROTOCOL.md).

See [`spec/company-norms.md`](spec/company-norms.md) for the full setup guide. Expected files:

- `company-norms/INDEX.md` — Agent entry point and decision framework
- `company-norms/betriebsvereinbarung-arbeitszeit-de.md` — Working time agreement (German)
- `company-norms/working-hours-agreement-en.md` — Working time agreement (English)
- `company-norms/betriebsvereinbarung-mobile-arbeit-de.md` — Mobile working agreement (German)
- `company-norms/mobile-working-agreement-en.md` — Mobile working agreement (English)

## How It Works

The system uses a three-layer architecture:

1. **OpenClaw Agent** (conversational layer) — Decides what to do, asks for user confirmation
2. **Elixir Orchestrator** (control plane) — Coordinates pipeline steps, browser strategy, and LLM calls
3. **Browser Backends** (execution layer):
   - **Primary:** Python/Playwright headless browser (unattended operation)
   - **Fallback:** Node.js CDP relay (connects to user's visible Chrome for MFA flows)

Since Workday has no public API, all interactions use browser automation. The headless
browser handles most operations; the CDP relay covers edge cases requiring a visible browser.

> Architecture details: [`spec/ARCHITECTURE.md`](spec/ARCHITECTURE.md)
> Pipeline definitions: [`spec/PIPELINES.md`](spec/PIPELINES.md)
> Architecture decisions: [`spec/adr/`](spec/adr/)

## Inter-Agent Message Queue (IAMQ)

The workday agent participates in the OpenClaw agent swarm via the Inter-Agent
Message Queue (IAMQ), using HTTP polling and WebSocket dual-mode transport
(`Orchestrator.MqClient` for HTTP, `Orchestrator.MqWsClient` for WebSocket).

| Property | Value |
|----------|-------|
| **Agent ID** | `workday_agent` |
| **Transport** | HTTP + WebSocket |

### Capabilities

The agent advertises the following capabilities on the queue:

- `workday_approvals` — HR task review and approval workflow
- `time_tracking` — Daily time entry validation and submission
- `hr_automation` — General Workday HR process automation
- `browser_automation` — Headless browser operations (Playwright / CDP)
- `task_management` — Workday inbox task coordination

### Environment Variables

| Variable | Description |
|----------|-------------|
| `IAMQ_HTTP_URL` | HTTP endpoint for the message queue (e.g. `http://localhost:4000/api/mq`) |
| `IAMQ_WS_URL` | WebSocket endpoint for real-time messages (e.g. `ws://localhost:4000/ws/mq`) |
| `IAMQ_AGENT_ID` | Agent identifier on the queue (default: `workday_agent`) |

## License

MIT

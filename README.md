# OpenClaw Workday Agent

An [OpenClaw](https://docs.openclaw.ai/) agent that automates Workday HR operations
through browser interactions — not API calls.

## What It Does

- **Task approvals** — Reviews pending HR tasks, checks compliance against work council
  agreements (Betriebsvereinbarungen), and executes approvals with user confirmation
- **Time tracking** — Validates and assists with daily time entry per German labor regulations

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) 18+ **or** [Docker](https://www.docker.com/)
- Chrome with DevTools Protocol enabled
- An [OpenClaw](https://docs.openclaw.ai/) workspace

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/openclaw-workday-agent.git
cd openclaw-workday-agent

# Configure environment
cp .env.example .env
# Edit .env with your actual values

# Install dependencies (skip if using Docker)
npm install
```

### Run

```bash
# Local
npm run approve

# Docker (zero-install)
docker compose run --rm agent node scripts/approve-workday.js
```

## Project Structure

```
AGENTS.md              # OpenClaw agent operating manual
SOUL.md                # Agent identity & personality
PROTOCOL.md            # HR operational protocol & compliance
spec/                  # Detailed behavioral specifications
company-norms/         # Work council agreements (gitignored)
scripts/               # Automation scripts
Dockerfile             # Zero-install container
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

Expected files:
- `company-norms/betriebsvereinbarung-arbeitszeit.md` — Working time agreement
- `company-norms/betriebsvereinbarung-mobile-arbeit.md` — Mobile working agreement

## How It Works

The agent operates through Chrome DevTools Protocol (CDP) to interact with Workday's
web interface. It connects to a running Chrome instance, finds the Workday tab, and
performs actions via JavaScript evaluation.

The OpenClaw agent framework provides the conversational layer — reading pending tasks,
checking compliance, asking for confirmation, and executing approvals.

## License

MIT

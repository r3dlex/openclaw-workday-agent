# 0004. Zero-Install via Docker Compose

Date: 2026-03-18

## Status

Accepted

## Context

The system spans multiple runtimes:

- **Node.js** for existing CDP relay scripts
- **Python** for Playwright browser automation
- **Elixir/OTP** for orchestration

Each runtime has its own dependency management (npm, pip/poetry, mix). Ensuring
consistent versions across developer machines, CI, and production is error-prone.
"Works on my machine" issues are inevitable without containerization.

## Decision

Use **Docker Compose** for multi-service orchestration.

- Each component has its own Dockerfile with pinned base images
- A single `docker compose up` starts all services
- Environment variables are passed via `.env` file (not committed; see `.env.example`)
- Development can still use local runtimes for faster iteration

Services:

- `orchestrator` -- Elixir/OTP application
- `runner` -- Python + Playwright with bundled browsers
- `relay` -- Node.js CDP relay (optional, for SSO fallback)

## Consequences

- **Zero-install for users**: Only Docker and Docker Compose are required
- **Reproducible builds**: Pinned base images and lockfiles ensure consistency
- **Larger total image size**: Three runtime images plus Playwright browsers (~1.5 GB total)
- **Docker Compose required**: Adds a dependency, but is widely available
- **Development flexibility**: Developers can run individual components locally or in containers
- **CI-friendly**: Same `docker compose` commands work in CI environments

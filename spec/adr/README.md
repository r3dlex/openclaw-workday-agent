# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the OpenClaw Workday Agent.

ADRs document significant architectural decisions, their context, and consequences.
We follow the format conventions from [archgate/cli](https://github.com/archgate/cli):
each ADR is a short Markdown file with a numbered title, status, context, decision, and consequences.

## ADR Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-headless-browser-primary.md) | Headless Browser as Primary Automation Strategy | Accepted |
| [0002](0002-elixir-orchestration.md) | Elixir/OTP for Orchestration | Accepted |
| [0003](0003-python-pipeline-runner.md) | Python + Playwright as Pipeline Runner | Accepted |
| [0004](0004-zero-install-containers.md) | Zero-Install via Docker Compose | Accepted |

## Creating a New ADR

1. Copy `template.md` to a new file: `NNNN-short-title.md`
2. Fill in the sections
3. Add an entry to the index table above
4. Submit for review

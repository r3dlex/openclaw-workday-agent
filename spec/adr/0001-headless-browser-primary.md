# 0001. Headless Browser as Primary Automation Strategy

Date: 2026-03-18

## Status

Accepted

## Context

Workday does not expose a public API for task approvals or time tracking operations.
The current approach uses a Chrome DevTools Protocol (CDP) relay that connects to the
user's open Chrome browser. This works but requires:

- The user to have Chrome open and logged in
- A visible browser session at all times
- Manual intervention if the browser closes or the session expires

For unattended operation (scheduled approvals, CI pipelines, overnight runs), we need
a browser automation strategy that does not depend on a user's desktop session.

## Decision

Use **Playwright in headless mode** as the primary browser automation strategy.
The existing CDP relay scripts remain as a fallback for SSO flows that require a
visible browser (e.g., MFA prompts that need user interaction).

The browser strategy is configurable:

- `headless_first` (default) -- Try headless Playwright; fall back to CDP relay on auth failure
- `headless_only` -- Headless only; fail if auth cannot be completed
- `relay_only` -- CDP relay only; requires user's Chrome to be open

## Consequences

- **Enables CI/unattended execution**: Headless browser runs without a desktop session
- **Larger Docker image**: Playwright bundles Chromium (~400 MB), increasing image size
- **Relay fallback covers edge cases**: SSO providers requiring visible MFA still work via CDP relay
- **Two code paths to maintain**: Headless Playwright actions and CDP relay scripts must stay in sync for core operations

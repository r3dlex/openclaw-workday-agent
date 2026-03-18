# Pipeline Definitions

## What Is a Pipeline?

A pipeline is a sequence of named steps that execute a Workday operation end-to-end.
Each step maps to one or more browser actions sent to the Python runner via the
JSON-lines protocol.

Pipelines are defined in the Elixir orchestrator and executed by the PipelineRunner
GenServer. The Python runner knows nothing about pipelines -- it only executes
individual actions.

## Pipeline: SSO Login

Authenticates the user via the organization's SSO provider.

| Step | Action | Fallback |
|------|--------|----------|
| `navigate` | Open the Workday login page | -- |
| `detect_login` | Check if already authenticated | Skip remaining steps if authenticated |
| `click_provider` | Click the SSO provider button (e.g., "Sign in with YourCompany") | `fallback_direct_link` |
| `fallback_direct_link` | Navigate directly to SSO provider URL | Fall to relay strategy |
| `verify_auth` | Confirm authentication succeeded (check for home page elements) | Fail pipeline |

**Notes:**
- If headless login fails (MFA prompt, CAPTCHA), the pipeline falls back to relay strategy
- The relay strategy assumes the user is already authenticated in their Chrome browser

## Pipeline: Task Approval

Reviews and acts on pending Workday tasks (approvals, acknowledgments).

| Step | Action | Fallback |
|------|--------|----------|
| `ensure_auth` | Run SSO Login pipeline if not authenticated | -- |
| `navigate_tasks` | Open the Workday tasks/inbox page | -- |
| `list_tasks` | Query DOM for all pending task items | Return empty list |
| `get_details` | Click into a specific task, extract details | Skip task |
| `analyze_compliance` | Return task data to agent for compliance check | -- |
| `present_to_user` | Agent presents task with recommendation | -- |
| `execute_action` | Click Approve/Deny/Acknowledge based on user decision | Retry once |

**Notes:**
- The `analyze_compliance` step exits the runner and returns to the agent layer
- The agent applies rules from PROTOCOL.md before proceeding
- User confirmation is always required before `execute_action`

## Pipeline: Time Tracking

Retrieves and validates time tracking entries.

| Step | Action | Fallback |
|------|--------|----------|
| `ensure_auth` | Run SSO Login pipeline if not authenticated | -- |
| `navigate_time` | Open the Workday time tracking page | -- |
| `get_entries` | Query DOM for time entries in the current period | Return empty list |
| `validate` | Check entries against expected hours and rules | -- |
| `return_results` | Return structured time data to the agent | -- |

## Fallback Strategy

Each pipeline can fall from headless to relay if authentication fails:

```
headless_first strategy:
  1. Start headless Playwright browser
  2. Run pipeline steps
  3. If auth step fails -> stop headless browser
  4. Connect to user's Chrome via CDP relay
  5. Re-run pipeline from the failed step
  6. If relay also fails -> report error to user
```

## JSON-Lines Protocol Specification

### Request Format

Sent from Elixir orchestrator to Python runner (one JSON object per line on stdin):

```json
{"id": "req_001", "action": "navigate", "params": {"url": "https://your_tenant.workday.com/home"}}
{"id": "req_002", "action": "click", "params": {"selector": "button[data-automation-id='approve']"}}
{"id": "req_003", "action": "query", "params": {"selector": ".task-item", "extract": ["text", "href"]}}
{"id": "req_004", "action": "fill", "params": {"selector": "input[name='hours']", "value": "8"}}
{"id": "req_005", "action": "screenshot", "params": {"path": "/tmp/screenshot.png"}}
```

### Response Format

Sent from Python runner to Elixir orchestrator (one JSON object per line on stdout):

```json
{"id": "req_001", "status": "ok", "data": {"title": "Home - Workday", "url": "..."}}
{"id": "req_002", "status": "ok", "data": {}}
{"id": "req_003", "status": "ok", "data": {"items": [{"text": "Approve PTO", "href": "/task/123"}]}}
{"id": "req_004", "status": "ok", "data": {}}
{"id": "req_005", "status": "error", "error": {"code": "TIMEOUT", "message": "Page did not stabilize within 30s"}}
```

### Supported Actions

| Action | Description | Key Params |
|--------|-------------|------------|
| `navigate` | Go to a URL | `url` |
| `click` | Click an element | `selector` |
| `fill` | Type into an input | `selector`, `value` |
| `query` | Extract data from elements | `selector`, `extract` |
| `screenshot` | Capture page screenshot | `path` (optional) |
| `wait` | Wait for an element | `selector`, `timeout_ms` |
| `evaluate` | Run JavaScript in page context | `expression` |

### Error Codes

| Code | Meaning |
|------|---------|
| `TIMEOUT` | Action did not complete within timeout |
| `NOT_FOUND` | Selector matched no elements |
| `NAVIGATION_ERROR` | Page failed to load |
| `AUTH_REQUIRED` | Detected login page (not authenticated) |
| `INTERNAL_ERROR` | Unexpected error in the runner |

## Adding a New Pipeline

1. Define the pipeline steps in the Elixir orchestrator (`lib/pipelines/`)
2. Implement any new actions needed in the Python runner (`runner/actions/`)
3. Add tests for both the pipeline logic and the new actions (see [TESTING.md](TESTING.md))
4. Document the pipeline in this file
5. If the pipeline introduces new architectural decisions, create an ADR (see [adr/](adr/README.md))

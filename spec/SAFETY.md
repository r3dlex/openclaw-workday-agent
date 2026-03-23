# Safety

Standardized safety rules for the OpenClaw Workday Agent.
For the foundational red lines and data handling policy, see
[safety-boundaries.md](safety-boundaries.md).

## Approval Safety

- **Never** approve a Workday task without explicit user confirmation
- **Never** deny a task without explicit user confirmation
- Present the task details, compliance analysis, and recommendation **before** asking
- Log every approval/denial action with timestamp and user confirmation reference

The Task Approval pipeline enforces this by exiting to the agent layer at the
`analyze_compliance` step (see [PIPELINES.md](PIPELINES.md)).

## Timesheet Safety

- **Never** submit a timesheet without user review
- Validate all entries against company norms before presenting
  (see [company-norms.md](company-norms.md))
- Flag entries that violate flex frame, daily max, or weekly target rules
- Show the full timesheet summary and wait for explicit "submit" confirmation

## Browser Session Isolation

Each pipeline execution gets a fresh browser context:

| Rule | Rationale |
|------|-----------|
| New context per pipeline run | Prevents state leakage between tasks |
| Cookies cleared after pipeline completes | No stale auth tokens persist |
| Screenshots stored in `artifacts/` (gitignored) | Sensitive data stays local |
| No cross-pipeline session reuse | One task failure cannot corrupt another |

The BrowserManager GenServer enforces context lifecycle
(see [ARCHITECTURE.md](ARCHITECTURE.md)).

## Credential Handling

- Workday credentials come from environment variables **only** (`WORKDAY_BASE_URL`, SSO config)
- **Never** store credentials in committed files -- use `.env` (gitignored)
- **Never** echo tokens, passwords, or session cookies in logs or chat
- CDP tokens (`CHROME_CDP_TOKEN`) are treated as secrets
- IAMQ credentials follow the same `.env`-only rule

See [safety-boundaries.md](safety-boundaries.md) for the full data handling policy.

## Rate Limits

| Operation | Limit | Rationale |
|-----------|-------|-----------|
| Task list refresh | Max 1 per 5 min | Avoid excessive Workday load |
| Approval actions | Max 10 per batch | Prevent runaway approvals |
| Timesheet page loads | Max 1 per 5 min | Workday rate limiting |
| Screenshot captures | Max 20 per pipeline run | Disk and memory constraints |

If a rate limit is hit, the orchestrator queues the request and retries after the
cooldown window.

## Session Timeout Handling

Workday sessions expire after inactivity. The agent handles this at two levels:

1. **Detection:** The Python runner returns `AUTH_REQUIRED` when it detects a login page
   (see [PIPELINES.md](PIPELINES.md) error codes)
2. **Recovery:** The orchestrator triggers the SSO Login pipeline before retrying the
   failed step. If headless re-auth fails, it falls back to the CDP relay strategy
   (see [ARCHITECTURE.md](ARCHITECTURE.md))

The agent **never** stores or caches Workday session tokens between pipeline runs.

## Audit Trail

All safety-relevant events are logged to `logs/agent.log`:

- User confirmation requests and responses
- Approval/denial actions with task identifiers
- Session creation and teardown events
- Rate limit triggers
- Auth failures and recovery attempts

## Further Reading

- [safety-boundaries.md](safety-boundaries.md) -- Red lines, external vs internal actions, data handling
- [session-lifecycle.md](session-lifecycle.md) -- Memory model and session startup
- [company-norms.md](company-norms.md) -- Compliance decision framework
- [PIPELINES.md](PIPELINES.md) -- Pipeline steps with confirmation gates

---

*Owner: dev team. Last updated: 2026-03-23.*

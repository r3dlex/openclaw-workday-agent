# Troubleshooting

Common issues and resolutions for the OpenClaw Workday Agent.

## Browser Automation

### CDP connection failed

```
Error: WebSocket connection to ws://127.0.0.1:9222/devtools/browser/... failed
```

| Cause | Fix |
|-------|-----|
| Chrome not running with `--remote-debugging-port` | Restart Chrome: `chrome --remote-debugging-port=9222` |
| Wrong port in `.env` | Verify `CHROME_CDP_PORT` matches Chrome's actual port |
| Container can't reach host Chrome | Use `host.docker.internal` instead of `localhost` in Docker |
| Another process occupies the port | `lsof -i :9222` to find and kill the conflict |

### Stale selectors

Workday updates its DOM structure periodically. Symptoms:

- `NOT_FOUND` errors on previously working selectors
- Pipeline steps timing out on element waits

**Fix:** Check `tools/pipeline_runner/pipeline_runner/selectors/` for the failing selector.
Compare against the live DOM using Chrome DevTools. Update the selector and add a test
fixture (see [TESTING.md](TESTING.md)).

### Session expired mid-pipeline

```json
{"status": "error", "error": {"code": "AUTH_REQUIRED", "message": "..."}}
```

The `headless_first` strategy (see [ARCHITECTURE.md](ARCHITECTURE.md)) should auto-recover
by falling back to the CDP relay. If it doesn't:

1. Check that the user's Chrome is authenticated to Workday
2. Verify `WORKDAY_BASE_URL` matches the tenant URL in Chrome
3. Look at `logs/pipeline.log` for the specific auth detection failure

## Workday-Specific

### Task list not loading

- **Workday is slow:** Increase the `wait` step timeout in the Task Approval pipeline.
  Default is 30s; try 60s for tenants with many inbox items.
- **Wrong path:** Verify `WORKDAY_TASKS_PATH` in `.env` matches your tenant's inbox URL.
- **Role mismatch:** The authenticated user may not have inbox permissions. Check Workday
  security role assignments.

### Approval timeout

The `execute_action` step in the Task Approval pipeline (see [PIPELINES.md](PIPELINES.md))
clicks approve and waits for a confirmation dialog. If Workday shows an intermediate
review screen:

1. Check if the task type requires additional fields before approval
2. Look for a "Submit" button after the initial "Approve" click
3. Update the pipeline step to handle multi-step approval flows

### Timesheet validation failures

The Time Tracking pipeline cross-references entries against company norms
(see [company-norms.md](company-norms.md)). Common validation issues:

| Validation | Rule | Resolution |
|------------|------|------------|
| Exceeds daily max | >10h triggers ArbZG warning | Split across days or get management authorization |
| Outside flex frame | Entry before 07:00 or after 19:00 | Adjust entry times to flex window |
| Weekly target mismatch | Entries don't sum to 39h | Check for missing days or partial entries |

## Orchestrator

### OTP crash / GenServer restart

The PipelineRunner and BrowserManager are supervised (see [ARCHITECTURE.md](ARCHITECTURE.md)).
A crash triggers automatic restart with a clean state.

**If restarts loop:**

```bash
# Check orchestrator logs
docker compose logs orchestrator | grep "** (EXIT)"

# Common causes:
# - Python runner binary not found: verify PATH in Docker image
# - Port conflict on Erlang distribution: check RELEASE_DISTRIBUTION env
# - Bad pipeline definition: look for MatchError in the stack trace
```

### Pipeline runner failure

The Python runner communicates via JSON-lines over stdin/stdout (Erlang Ports).

| Symptom | Cause | Fix |
|---------|-------|-----|
| Runner exits immediately | Missing Python dependency | `cd tools/pipeline_runner && poetry install` |
| No response from runner | stdout buffering | Ensure Python uses `flush=True` or `-u` flag |
| Garbled JSON | stderr leaking to stdout | Runner must use stderr for logs, stdout only for protocol |

## IAMQ Integration

### Registration fails

```
Error: Failed to register workday_agent with IAMQ
```

1. Verify `IAMQ_HTTP_URL` and `IAMQ_WS_URL` in `.env` are reachable
2. Check that `IAMQ_AGENT_ID` is set to `workday_agent`
3. Confirm the IAMQ server is running: `curl $IAMQ_HTTP_URL/health`
4. If behind a firewall, ensure WebSocket upgrade is allowed

### Heartbeat timeout

The agent sends periodic heartbeats to IAMQ (see [heartbeat-strategy.md](heartbeat-strategy.md)).
If heartbeats stop:

- Check WebSocket connection: look for `WS_CLOSED` in agent logs
- IAMQ server may have restarted: the agent should auto-reconnect
- Network interruption: verify container DNS resolution

## Docker / Container

### Build failures

```bash
# Rebuild from scratch (no cache)
docker compose build --no-cache

# Common issues:
# - Playwright browsers not installed: Dockerfile must run `playwright install chromium`
# - Mix deps timeout: check network access from Docker build context
# - Python version mismatch: pyproject.toml requires Python 3.11+
```

### Container can't reach Workday

| Environment | Fix |
|-------------|-----|
| Docker Desktop (macOS) | Use `host.docker.internal` for host URLs |
| Linux Docker | Add `--network host` or configure bridge network |
| Corporate proxy | Set `HTTP_PROXY` / `HTTPS_PROXY` in `docker-compose.yml` |

### Volume permission issues

```bash
# logs/ and artifacts/ directories need write access
chmod -R 777 logs/ artifacts/

# Or run container with matching UID
docker compose run --user $(id -u):$(id -g) orchestrator
```

---

*Owner: dev team. Last updated: 2026-03-23.*

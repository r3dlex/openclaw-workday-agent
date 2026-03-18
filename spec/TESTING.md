# Test Strategy

## Overview

All tests run against mocks and fixtures. No live Workday instance is used in CI or
local test runs. The test strategy mirrors the three-layer architecture
(see [ARCHITECTURE.md](ARCHITECTURE.md)).

## Test Layers

### Python Unit Tests (pytest)

Test the browser automation layer in isolation.

- **Mock Playwright Page objects**: Each test creates a mock `Page` with predefined
  DOM responses. No real browser is launched.
- **Test each action in isolation**: `navigate`, `click`, `fill`, `query`, `screenshot`,
  `wait`, `evaluate` each have their own test module.
- **Test selectors**: Verify that Workday-specific selectors match expected elements
  using HTML fixtures.

```
runner/
  tests/
    test_actions/
      test_navigate.py
      test_click.py
      test_fill.py
      test_query.py
      test_screenshot.py
    test_protocol.py        # JSON-lines parsing and serialization
    test_selectors.py       # Workday DOM selector validation
    fixtures/
      task_list.html        # Sample Workday task list page
      time_tracking.html    # Sample time tracking page
      login_page.html       # Sample SSO login page
```

### Elixir Unit Tests (ExUnit)

Test the orchestration layer.

- **Mock Port/System.cmd**: Replace Erlang Ports with in-memory mock that responds
  to JSON-lines messages with predefined responses.
- **Test pipeline sequencing**: Verify that steps execute in order, that state
  propagates between steps, and that pipelines complete correctly.
- **Test fallback logic**: Simulate auth failures and verify that the BrowserManager
  switches from headless to relay strategy.
- **Test retry behavior**: Simulate transient failures and verify retry with backoff.

```
orchestrator/
  test/
    pipeline_runner_test.exs
    browser_manager_test.exs
    pipelines/
      sso_login_test.exs
      task_approval_test.exs
      time_tracking_test.exs
    support/
      mock_port.ex           # Mock Erlang Port for testing
      fixtures.ex            # Predefined JSON-lines responses
```

### Integration Tests (Docker Compose)

Test the full system with all components running in containers.

- **Docker Compose test profile**: `docker compose --profile test up`
- **End-to-end pipeline execution**: Send a pipeline request to the orchestrator,
  verify it flows through the Python runner (using mock HTML pages), and returns
  the expected result.
- **IPC verification**: Confirm JSON-lines messages are correctly serialized and
  deserialized across the Erlang Port boundary.

### Pipeline Tests

Test complete pipeline definitions against recorded Workday page snapshots.

- **Recorded snapshots**: HTML snapshots of Workday pages stored in test fixtures.
  These are sanitized to remove any company-specific data.
- **Replay mode**: The Python runner serves fixture HTML instead of navigating to
  live URLs. The Elixir orchestrator runs the full pipeline against these fixtures.

## Running Tests

```bash
# Run all tests
make test

# Run Python tests only
make test-python
# Equivalent to: cd runner && pytest -v

# Run Elixir tests only
make test-elixir
# Equivalent to: cd orchestrator && mix test

# Run integration tests (requires Docker)
make test-integration
# Equivalent to: docker compose --profile test up --abort-on-container-exit

# Run with coverage
make test-coverage
```

## Test Naming Conventions

- **Python**: `test_<action>_<scenario>` (e.g., `test_click_element_not_found`)
- **Elixir**: `test <description>` (e.g., `test "pipeline retries on transient failure"`)
- **Integration**: `test_<pipeline>_<scenario>` (e.g., `test_task_approval_happy_path`)

## CI Considerations

- **No live Workday in CI**: All tests use mocks and fixtures. No network access
  to Workday is required.
- **Docker-in-Docker**: Integration tests run in Docker Compose. CI must support
  Docker-in-Docker or use a VM-based runner.
- **Parallelism**: Python and Elixir unit tests can run in parallel. Integration
  tests run sequentially.
- **Artifacts**: Test failures save screenshots and JSON-lines logs as CI artifacts.

## Coverage Targets

| Component | Target | Tool |
|-----------|--------|------|
| Python runner | 90% line coverage | `pytest-cov` |
| Elixir orchestrator | 85% line coverage | `excoveralls` |
| Integration | All pipelines exercised | Manual checklist |

Coverage is enforced in CI. PRs that decrease coverage below the target are flagged.

## Further Reading

- [ARCHITECTURE.md](ARCHITECTURE.md) for system context and component descriptions
- [PIPELINES.md](PIPELINES.md) for pipeline definitions and protocol spec

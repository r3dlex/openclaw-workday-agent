"""Tests for pipeline_runner.main (dispatch, run_stdio, run_single, CLI)."""

from __future__ import annotations

import json
import sys
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from playwright.async_api import TimeoutError as PlaywrightTimeout

from pipeline_runner.config import PipelineConfig
from pipeline_runner.main import dispatch, run_single, run_stdio, setup_logging
from pipeline_runner.protocol import Response


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**env) -> PipelineConfig:
    defaults = {
        "WORKDAY_BASE_URL": "https://workday.example.com",
        "SSO_PROVIDER_NAME": "TestSSO",
        "ORG_TENANT_DIRECT_LINK": "https://sso.example.com",
        "BROWSER_STRATEGY": "headless_first",
        "PLAYWRIGHT_HEADLESS": "true",
        "PLAYWRIGHT_TIMEOUT": "5000",
    }
    return PipelineConfig(**{**defaults, **env})  # type: ignore[call-arg]


def _mock_bm_and_page():
    """Return (mock_bm, mock_page) with get_page wired up."""
    mock_page = AsyncMock()
    mock_page.url = "https://workday.example.com/home"
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.is_closed = MagicMock(return_value=False)

    default_locator = AsyncMock()
    default_locator.wait_for = AsyncMock()
    default_locator.click = AsyncMock()
    default_locator.is_visible = AsyncMock(return_value=True)
    default_locator.text_content = AsyncMock(return_value="text")
    default_locator.count = AsyncMock(return_value=0)
    default_locator.first = default_locator
    default_locator.nth = MagicMock(return_value=default_locator)
    mock_page.locator = MagicMock(return_value=default_locator)

    mock_bm = AsyncMock()
    mock_bm.get_page = AsyncMock(return_value=mock_page)
    mock_bm.__aenter__ = AsyncMock(return_value=mock_bm)
    mock_bm.__aexit__ = AsyncMock(return_value=False)

    return mock_bm, mock_page


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


class TestSetupLogging:
    def test_setup_logging_does_not_raise(self):
        setup_logging()


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------


class TestDispatch:
    @pytest.mark.asyncio
    async def test_ping(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()
        result = await dispatch("ping", {}, mock_bm, config)
        assert result == {"status": "ok", "message": "pong"}

    @pytest.mark.asyncio
    async def test_unknown_action_raises(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()
        with pytest.raises(ValueError, match="Unknown action"):
            await dispatch("nonexistent_action", {}, mock_bm, config)

    @pytest.mark.asyncio
    async def test_validate_entry_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()
        entry = {"hours": 8, "start_time": "09:00", "end_time": "17:00"}
        result = await dispatch("validate_entry", {"entry": entry}, mock_bm, config)
        assert "valid" in result
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_list_tasks_action(self, dummy_env):
        config = _make_config()
        mock_bm, mock_page = _mock_bm_and_page()

        # locator returns empty task list (timeout triggers empty return)
        empty_locator = AsyncMock()
        empty_locator.wait_for = AsyncMock(
            side_effect=PlaywrightTimeout("timeout")
        )
        empty_locator.first = empty_locator
        mock_page.locator = MagicMock(return_value=empty_locator)

        result = await dispatch("list_tasks", {}, mock_bm, config)
        assert "tasks" in result

    @pytest.mark.asyncio
    async def test_get_time_entries_action(self, dummy_env):
        config = _make_config()
        mock_bm, mock_page = _mock_bm_and_page()

        empty_locator = AsyncMock()
        empty_locator.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        empty_locator.first = empty_locator
        mock_page.locator = MagicMock(return_value=empty_locator)

        result = await dispatch("get_time_entries", {}, mock_bm, config)
        assert "entries" in result

    @pytest.mark.asyncio
    async def test_login_action_succeeds(self, dummy_env):
        config = _make_config()
        mock_bm, mock_page = _mock_bm_and_page()

        result = await dispatch("login", {}, mock_bm, config)
        # Provider name is set so we attempt provider login; it may succeed
        assert "status" in result

    @pytest.mark.asyncio
    async def test_login_provider_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        result = await dispatch(
            "login_provider",
            {"provider_name": "TestSSO", "base_url": "https://workday.example.com"},
            mock_bm,
            config,
        )
        assert "status" in result

    @pytest.mark.asyncio
    async def test_login_direct_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        result = await dispatch(
            "login_direct",
            {"direct_link": "https://sso.example.com/tenant"},
            mock_bm,
            config,
        )
        assert "status" in result

    @pytest.mark.asyncio
    async def test_approve_task_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        result = await dispatch("approve_task", {}, mock_bm, config)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_deny_task_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        result = await dispatch("deny_task", {}, mock_bm, config)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_send_back_task_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        result = await dispatch("send_back_task", {}, mock_bm, config)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_submit_time_entry_no_row(self, dummy_env):
        config = _make_config()
        mock_bm, mock_page = _mock_bm_and_page()

        rows_locator = AsyncMock()
        rows_locator.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=rows_locator)

        result = await dispatch(
            "submit_time_entry", {"hours": 8, "date": "2026-01-15"}, mock_bm, config
        )
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# run_single
# ---------------------------------------------------------------------------


class TestRunSingle:
    @pytest.mark.asyncio
    async def test_run_single_ping(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        captured = StringIO()
        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdout", captured):
                await run_single("ping", {}, config)

        output = captured.getvalue()
        data = json.loads(output.strip())
        assert data["status"] == "ok"
        assert data["result"]["message"] == "pong"

    @pytest.mark.asyncio
    async def test_run_single_unknown_action(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        captured = StringIO()
        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdout", captured):
                await run_single("bad_action", {}, config)

        output = captured.getvalue()
        data = json.loads(output.strip())
        assert data["status"] == "error"


# ---------------------------------------------------------------------------
# run_stdio
# ---------------------------------------------------------------------------


class TestRunStdio:
    @pytest.mark.asyncio
    async def test_run_stdio_handles_valid_request(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        line = json.dumps({"action": "ping", "request_id": "req-1"})
        stdin_mock = StringIO(line + "\n")
        stdout_mock = StringIO()

        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdin", stdin_mock):
                with patch("sys.stdout", stdout_mock):
                    await run_stdio(config)

        output = stdout_mock.getvalue()
        data = json.loads(output.strip())
        assert data["status"] == "ok"
        assert data["request_id"] == "req-1"

    @pytest.mark.asyncio
    async def test_run_stdio_handles_invalid_json(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        stdin_mock = StringIO("not json\n")
        stdout_mock = StringIO()

        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdin", stdin_mock):
                with patch("sys.stdout", stdout_mock):
                    await run_stdio(config)

        output = stdout_mock.getvalue()
        data = json.loads(output.strip())
        assert data["status"] == "error"
        assert "Invalid JSON" in data["error"]

    @pytest.mark.asyncio
    async def test_run_stdio_skips_blank_lines(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        # Two blank lines followed by a valid request
        stdin_mock = StringIO("\n\n" + json.dumps({"action": "ping"}) + "\n")
        stdout_mock = StringIO()

        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdin", stdin_mock):
                with patch("sys.stdout", stdout_mock):
                    await run_stdio(config)

        # Only one response should be written
        lines = [l for l in stdout_mock.getvalue().strip().splitlines() if l]
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_run_stdio_handles_dispatch_exception(self, dummy_env):
        config = _make_config()
        mock_bm, _ = _mock_bm_and_page()

        stdin_mock = StringIO(json.dumps({"action": "bad_action"}) + "\n")
        stdout_mock = StringIO()

        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdin", stdin_mock):
                with patch("sys.stdout", stdout_mock):
                    await run_stdio(config)

        output = stdout_mock.getvalue()
        data = json.loads(output.strip())
        assert data["status"] == "error"
        assert "Unknown action" in data["error"]


# ---------------------------------------------------------------------------
# main() CLI entry point
# ---------------------------------------------------------------------------


class TestMainCLI:
    def test_main_stdio_mode(self, dummy_env):
        """main() with --stdio calls asyncio.run(run_stdio(...))."""
        import asyncio

        mock_bm, _ = _mock_bm_and_page()
        stdin_mock = StringIO("")  # empty stdin so stdio loop exits immediately

        with patch("pipeline_runner.main.BrowserManager", return_value=mock_bm):
            with patch("sys.stdin", stdin_mock):
                with patch("sys.argv", ["pipeline-runner", "--stdio"]):
                    with patch("asyncio.run") as mock_run:
                        mock_run.return_value = None
                        from pipeline_runner.main import main
                        main()
                        mock_run.assert_called_once()

    def test_main_action_mode(self, dummy_env):
        """main() with --action calls asyncio.run(run_single(...))."""
        with patch("sys.argv", ["pipeline-runner", "--action", "ping", "--params", "{}"]):
            with patch("asyncio.run") as mock_run:
                mock_run.return_value = None
                from pipeline_runner.main import main
                main()
                mock_run.assert_called_once()

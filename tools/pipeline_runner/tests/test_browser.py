"""Tests for pipeline_runner.browser (BrowserManager)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline_runner.browser import BrowserManager
from pipeline_runner.config import PipelineConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides) -> PipelineConfig:
    env = {
        "WORKDAY_BASE_URL": "https://workday.example.com",
        "BROWSER_STRATEGY": "headless_first",
        "PLAYWRIGHT_HEADLESS": "true",
        "PLAYWRIGHT_TIMEOUT": "5000",
        **overrides,
    }
    return PipelineConfig(**env)  # type: ignore[call-arg]


def _make_playwright_mock(browser=None, context=None, page=None):
    """Build a nested Playwright mock: playwright -> chromium -> browser -> context -> page."""
    mock_page = page or AsyncMock()
    mock_page.is_closed = MagicMock(return_value=False)

    mock_context = context or AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.set_default_timeout = MagicMock()
    mock_context.close = AsyncMock()

    mock_browser = browser or AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_chromium = AsyncMock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)
    mock_chromium.connect_over_cdp = AsyncMock(return_value=mock_browser)

    mock_playwright = AsyncMock()
    mock_playwright.chromium = mock_chromium
    mock_playwright.stop = AsyncMock()

    return mock_playwright, mock_browser, mock_context, mock_page


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBrowserManagerLaunch:
    @pytest.mark.asyncio
    async def test_launch_headless(self, dummy_env):
        """Headless launch (non-cdp_only strategy) calls chromium.launch."""
        config = _make_config(BROWSER_STRATEGY="headless_first")
        mock_pw, mock_browser, _, _ = _make_playwright_mock()

        with patch(
            "pipeline_runner.browser.async_playwright"
        ) as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()

            mock_pw.chromium.launch.assert_called_once_with(headless=True)
            assert bm._browser is mock_browser
            assert bm._playwright is mock_pw

    @pytest.mark.asyncio
    async def test_launch_cdp_strategy_with_token(self, dummy_env):
        """CDP-only strategy with a token calls connect_over_cdp."""
        config = _make_config(
            BROWSER_STRATEGY="cdp_only",
            CHROME_CDP_TOKEN="my-token",
            CHROME_CDP_PORT="9222",
        )
        mock_pw, mock_browser, _, _ = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()

            mock_pw.chromium.connect_over_cdp.assert_called_once()
            call_args = mock_pw.chromium.connect_over_cdp.call_args[0][0]
            assert "my-token" in call_args

    @pytest.mark.asyncio
    async def test_launch_cdp_strategy_without_token_falls_back(self, dummy_env):
        """CDP-only without a token still uses chromium.launch."""
        config = _make_config(BROWSER_STRATEGY="cdp_only", CHROME_CDP_TOKEN="")
        mock_pw, _, _, _ = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()

            mock_pw.chromium.launch.assert_called_once()
            mock_pw.chromium.connect_over_cdp.assert_not_called()


class TestBrowserManagerContext:
    @pytest.mark.asyncio
    async def test_new_context_creates_context(self, dummy_env):
        """new_context() creates a browser context with correct viewport."""
        config = _make_config()
        mock_pw, mock_browser, mock_context, _ = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()
            ctx = await bm.new_context()

            mock_browser.new_context.assert_called_once()
            call_kwargs = mock_browser.new_context.call_args[1]
            assert call_kwargs["viewport"] == {"width": 1280, "height": 720}
            assert ctx is mock_context

    @pytest.mark.asyncio
    async def test_new_context_raises_if_not_launched(self):
        """new_context() raises RuntimeError if browser has not been launched."""
        config = _make_config()
        bm = BrowserManager(config)

        with pytest.raises(RuntimeError, match="not launched"):
            await bm.new_context()


class TestBrowserManagerGetPage:
    @pytest.mark.asyncio
    async def test_get_page_returns_page(self, dummy_env):
        """get_page() returns the mock page after launch."""
        config = _make_config()
        mock_pw, _, _, mock_page = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()
            page = await bm.get_page()

            assert page is mock_page

    @pytest.mark.asyncio
    async def test_get_page_reuses_open_page(self, dummy_env):
        """get_page() reuses an existing open page."""
        config = _make_config()
        mock_pw, _, mock_context, mock_page = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()

            page1 = await bm.get_page()
            page2 = await bm.get_page()

            assert page1 is page2
            # new_page called only once
            assert mock_context.new_page.call_count == 1

    @pytest.mark.asyncio
    async def test_get_page_recreates_closed_page(self, dummy_env):
        """get_page() creates a new page when the existing one is closed."""
        config = _make_config()
        bm = BrowserManager(config)

        closed_page = AsyncMock()
        closed_page.is_closed = MagicMock(return_value=True)

        fresh_page = AsyncMock()
        fresh_page.is_closed = MagicMock(return_value=False)

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=fresh_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.close = AsyncMock()

        # Directly inject state — skip launch() to avoid mock chain complexity
        bm._browser = AsyncMock()
        bm._context = mock_context
        bm._page = closed_page  # will be detected as closed

        page = await bm.get_page()
        assert page is fresh_page


class TestBrowserManagerClose:
    @pytest.mark.asyncio
    async def test_close_cleans_up_all_resources(self, dummy_env):
        """close() calls close on context, browser, and stop on playwright."""
        config = _make_config()
        mock_pw, mock_browser, mock_context, _ = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()
            await bm.new_context()
            await bm.close()

            mock_context.close.assert_called_once()
            mock_browser.close.assert_called_once()
            mock_pw.stop.assert_called_once()
            assert bm._browser is None
            assert bm._context is None
            assert bm._playwright is None
            assert bm._page is None

    @pytest.mark.asyncio
    async def test_close_handles_exceptions_gracefully(self, dummy_env):
        """close() doesn't raise even if close/stop calls fail."""
        config = _make_config()
        mock_pw, mock_browser, mock_context, _ = _make_playwright_mock()
        mock_context.close = AsyncMock(side_effect=Exception("boom"))
        mock_browser.close = AsyncMock(side_effect=Exception("boom"))
        mock_pw.stop = AsyncMock(side_effect=Exception("boom"))

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            bm = BrowserManager(config)
            await bm.launch()
            bm._context = mock_context

            # Should not raise
            await bm.close()

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self, dummy_env):
        """Calling close() multiple times does not raise."""
        config = _make_config()
        bm = BrowserManager(config)
        # No launch — all fields are None
        await bm.close()
        await bm.close()


class TestBrowserManagerContextManager:
    @pytest.mark.asyncio
    async def test_async_context_manager(self, dummy_env):
        """BrowserManager can be used as an async context manager."""
        config = _make_config()
        mock_pw, _, _, _ = _make_playwright_mock()

        with patch("pipeline_runner.browser.async_playwright") as mock_ap:
            cm = AsyncMock()
            cm.start = AsyncMock(return_value=mock_pw)
            mock_ap.return_value = cm

            async with BrowserManager(config) as bm:
                assert bm._playwright is mock_pw

            mock_pw.stop.assert_called_once()

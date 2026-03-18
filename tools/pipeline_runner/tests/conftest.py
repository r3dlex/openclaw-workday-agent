"""Shared test fixtures. All values are dummy — no real secrets."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline_runner.config import PipelineConfig


# ---------------------------------------------------------------------------
# Environment / config
# ---------------------------------------------------------------------------

DUMMY_ENV = {
    "WORKDAY_BASE_URL": "https://workday.example.com",
    "WORKDAY_TASKS_PATH": "/tasks",
    "WORKDAY_TIME_TRACKING_PATH": "/time-tracking",
    "WORKDAY_HOME_PATH": "/home",
    "SSO_PROVIDER_NAME": "TestSSO",
    "ORG_TENANT_DIRECT_LINK": "https://sso.example.com/tenant",
    "CHROME_CDP_TOKEN": "dummy-token",
    "CHROME_CDP_PORT": "9222",
    "PLAYWRIGHT_HEADLESS": "true",
    "PLAYWRIGHT_TIMEOUT": "5000",
    "BROWSER_STRATEGY": "headless_first",
}


@pytest.fixture()
def dummy_env(monkeypatch):
    """Populate environment with dummy config values."""
    for key, value in DUMMY_ENV.items():
        monkeypatch.setenv(key, value)
    return DUMMY_ENV


@pytest.fixture()
def config(dummy_env) -> PipelineConfig:
    """Return a PipelineConfig loaded from dummy env vars."""
    return PipelineConfig()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Mock Playwright objects
# ---------------------------------------------------------------------------


def _make_mock_locator(text: str = "", count: int = 1, visible: bool = True):
    """Create a mock Playwright Locator."""
    locator = AsyncMock()
    locator.text_content = AsyncMock(return_value=text)
    locator.is_visible = AsyncMock(return_value=visible)
    locator.click = AsyncMock()
    locator.fill = AsyncMock()
    locator.wait_for = AsyncMock()
    locator.count = AsyncMock(return_value=count)
    locator.first = locator
    locator.nth = MagicMock(return_value=locator)
    return locator


@pytest.fixture()
def mock_page():
    """A mock Playwright Page with common methods stubbed."""
    page = AsyncMock()
    page.url = "https://workday.example.com/home"
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.is_closed = MagicMock(return_value=False)

    default_locator = _make_mock_locator()
    page.locator = MagicMock(return_value=default_locator)

    return page


@pytest.fixture()
def mock_browser_manager(mock_page):
    """A mock BrowserManager that returns the mock page."""
    bm = AsyncMock()
    bm.get_page = AsyncMock(return_value=mock_page)
    bm.launch = AsyncMock()
    bm.close = AsyncMock()
    bm.__aenter__ = AsyncMock(return_value=bm)
    bm.__aexit__ = AsyncMock(return_value=False)
    return bm

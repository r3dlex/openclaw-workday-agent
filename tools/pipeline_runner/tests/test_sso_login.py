"""Tests for pipeline_runner.actions.sso_login."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from pipeline_runner.actions.sso_login import (
    ensure_authenticated,
    login_with_direct_link,
    login_with_provider,
)


@pytest.fixture()
def sso_page():
    """Page mock tailored for SSO tests."""
    page = AsyncMock()
    page.url = "https://workday.example.com/home"
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()

    locator = AsyncMock()
    locator.wait_for = AsyncMock()
    locator.click = AsyncMock()
    locator.first = locator

    page.locator = MagicMock(return_value=locator)
    return page


class TestLoginWithProvider:
    @pytest.mark.asyncio
    async def test_success(self, sso_page):
        result = await login_with_provider(
            sso_page, "TestSSO", "https://workday.example.com"
        )
        assert result["status"] == "ok"
        sso_page.goto.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_not_found(self, sso_page):
        locator = AsyncMock()
        locator.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        locator.first = locator
        sso_page.locator = MagicMock(return_value=locator)

        result = await login_with_provider(
            sso_page, "NonExistent", "https://workday.example.com"
        )
        assert result["status"] == "provider_not_found"


class TestLoginWithDirectLink:
    @pytest.mark.asyncio
    async def test_success(self, sso_page):
        result = await login_with_direct_link(
            sso_page, "https://sso.example.com/tenant"
        )
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_timeout(self, sso_page):
        sso_page.goto = AsyncMock(side_effect=PlaywrightTimeout("timeout"))

        result = await login_with_direct_link(
            sso_page, "https://sso.example.com/tenant"
        )
        assert result["status"] == "timeout"


class TestEnsureAuthenticated:
    @pytest.mark.asyncio
    async def test_provider_success(self, sso_page, config):
        result = await ensure_authenticated(sso_page, config)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_fallback_to_direct_link(self, sso_page, config):
        # Make provider login fail
        locator = AsyncMock()
        locator.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        locator.first = locator
        sso_page.locator = MagicMock(return_value=locator)

        result = await ensure_authenticated(sso_page, config)
        # Direct link should succeed
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_all_methods_fail(self, sso_page, monkeypatch):
        monkeypatch.setenv("WORKDAY_BASE_URL", "https://workday.example.com")
        monkeypatch.setenv("SSO_PROVIDER_NAME", "")
        monkeypatch.setenv("ORG_TENANT_DIRECT_LINK", "")

        from pipeline_runner.config import PipelineConfig
        cfg = PipelineConfig()  # type: ignore[call-arg]

        result = await ensure_authenticated(sso_page, cfg)
        assert result["status"] == "error"

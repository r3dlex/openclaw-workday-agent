"""SSO authentication actions for Workday."""

from __future__ import annotations

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from pipeline_runner.config import PipelineConfig
from pipeline_runner.selectors.workday import SSO_PROVIDER_BUTTON


async def login_with_provider(page: Page, provider_name: str, base_url: str) -> dict:
    """Navigate to Workday and click the SSO provider button.

    Returns a result dict with ``status`` and ``url`` after redirect.
    """
    await page.goto(base_url, wait_until="domcontentloaded")

    selector = SSO_PROVIDER_BUTTON.format(name=provider_name)

    try:
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=10_000)
        await locator.click()
    except PlaywrightTimeout:
        return {
            "status": "provider_not_found",
            "message": f"SSO provider button '{provider_name}' not found on page",
        }

    # Wait for SSO redirect to complete
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=30_000)
    except PlaywrightTimeout:
        return {"status": "timeout", "message": "SSO redirect timed out"}

    return {"status": "ok", "url": page.url}


async def login_with_direct_link(page: Page, direct_link: str) -> dict:
    """Navigate directly to the tenant SSO link.

    Returns a result dict with ``status`` and ``url`` after redirect.
    """
    try:
        await page.goto(direct_link, wait_until="domcontentloaded", timeout=30_000)
    except PlaywrightTimeout:
        return {"status": "timeout", "message": "Direct link navigation timed out"}

    return {"status": "ok", "url": page.url}


async def ensure_authenticated(page: Page, config: PipelineConfig) -> dict:
    """Authenticate against Workday, trying provider login first, then direct link.

    Returns a result dict describing the outcome.
    """
    # Try provider-based SSO first
    if config.SSO_PROVIDER_NAME:
        result = await login_with_provider(
            page, config.SSO_PROVIDER_NAME, config.WORKDAY_BASE_URL
        )
        if result.get("status") == "ok":
            return result

    # Fallback to direct tenant link
    if config.ORG_TENANT_DIRECT_LINK:
        result = await login_with_direct_link(page, config.ORG_TENANT_DIRECT_LINK)
        if result.get("status") == "ok":
            return result

    return {
        "status": "error",
        "message": "All authentication methods failed. "
        "Set SSO_PROVIDER_NAME or ORG_TENANT_DIRECT_LINK in the environment.",
    }

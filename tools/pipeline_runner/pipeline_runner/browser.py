"""Playwright browser lifecycle management."""

from __future__ import annotations

from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from pipeline_runner.config import PipelineConfig


class BrowserManager:
    """Manages the Playwright browser lifecycle as an async context manager."""

    def __init__(self, config: PipelineConfig) -> None:
        self._config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def __aenter__(self) -> "BrowserManager":
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def launch(self) -> None:
        """Start Playwright and launch a Chromium browser."""
        self._playwright = await async_playwright().start()

        if self._config.BROWSER_STRATEGY == "cdp_only" and self._config.CHROME_CDP_TOKEN:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"ws://127.0.0.1:{self._config.CHROME_CDP_PORT}/?token={self._config.CHROME_CDP_TOKEN}"
            )
        else:
            self._browser = await self._playwright.chromium.launch(
                headless=self._config.PLAYWRIGHT_HEADLESS,
            )

    async def new_context(self) -> BrowserContext:
        """Create a new browser context with sensible defaults."""
        if self._browser is None:
            raise RuntimeError("Browser not launched. Call launch() first.")

        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            java_script_enabled=True,
        )
        self._context.set_default_timeout(self._config.PLAYWRIGHT_TIMEOUT)
        return self._context

    async def get_page(self) -> Page:
        """Return the active page, creating a context and page if needed."""
        if self._page is None or self._page.is_closed():
            if self._context is None:
                await self.new_context()
            assert self._context is not None
            self._page = await self._context.new_page()
        return self._page

    async def close(self) -> None:
        """Clean up all Playwright resources."""
        if self._context is not None:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None

        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        self._page = None

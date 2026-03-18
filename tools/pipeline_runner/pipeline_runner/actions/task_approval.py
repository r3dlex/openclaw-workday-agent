"""Task listing and approval actions for Workday."""

from __future__ import annotations

from playwright.async_api import Locator, Page, TimeoutError as PlaywrightTimeout

from pipeline_runner.selectors.workday import (
    APPROVE_BUTTON,
    CONFIRMATION_DIALOG,
    DENY_BUTTON,
    DONE_BUTTON,
    SEND_BACK_BUTTON,
    TASK_DATE,
    TASK_DESCRIPTION,
    TASK_LIST_ITEMS,
    TASK_TITLE,
    TASK_TYPE,
)


async def list_tasks(page: Page, tasks_url: str) -> list[dict]:
    """Navigate to the tasks page and extract a structured task list."""
    await page.goto(tasks_url, wait_until="domcontentloaded")

    try:
        await page.locator(TASK_LIST_ITEMS).first.wait_for(
            state="visible", timeout=15_000
        )
    except PlaywrightTimeout:
        return []

    items = page.locator(TASK_LIST_ITEMS)
    count = await items.count()

    tasks = []
    for i in range(count):
        item = items.nth(i)
        title = await _safe_text(item.locator(TASK_TITLE).first)
        task_type = await _safe_text(item.locator(TASK_TYPE).first)
        date = await _safe_text(item.locator(TASK_DATE).first)

        tasks.append(
            {
                "index": i,
                "title": title,
                "type": task_type,
                "date": date,
            }
        )

    return tasks


async def get_task_details(page: Page, task_element: Locator) -> dict:
    """Click into a task and extract its detail fields."""
    await task_element.click()
    await page.wait_for_load_state("domcontentloaded")

    title = await _safe_text(page.locator(TASK_TITLE).first)
    task_type = await _safe_text(page.locator(TASK_TYPE).first)
    date = await _safe_text(page.locator(TASK_DATE).first)
    description = await _safe_text(page.locator(TASK_DESCRIPTION).first)

    return {
        "title": title,
        "type": task_type,
        "date": date,
        "description": description,
    }


async def approve_task(page: Page) -> dict:
    """Click the Approve button on the currently open task."""
    return await _click_action_button(page, APPROVE_BUTTON, "approve")


async def deny_task(page: Page) -> dict:
    """Click the Deny button on the currently open task."""
    return await _click_action_button(page, DENY_BUTTON, "deny")


async def send_back_task(page: Page) -> dict:
    """Click the Send Back button on the currently open task."""
    return await _click_action_button(page, SEND_BACK_BUTTON, "send_back")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _click_action_button(page: Page, selector: str, action_name: str) -> dict:
    """Click an action button and wait for confirmation."""
    try:
        button = page.locator(selector).first
        await button.wait_for(state="visible", timeout=10_000)
        await button.click()
    except PlaywrightTimeout:
        return {
            "status": "error",
            "message": f"'{action_name}' button not found or not visible",
        }

    # Wait for confirmation dialog or page transition
    try:
        done = page.locator(f"{CONFIRMATION_DIALOG}, {DONE_BUTTON}")
        await done.first.wait_for(state="visible", timeout=10_000)

        done_btn = page.locator(DONE_BUTTON).first
        if await done_btn.is_visible():
            await done_btn.click()
    except PlaywrightTimeout:
        pass  # Some actions complete without a confirmation dialog

    return {"status": "ok", "action": action_name}


async def _safe_text(locator: Locator) -> str:
    """Extract text content from a locator, returning empty string on failure."""
    try:
        text = await locator.text_content(timeout=3_000)
        return (text or "").strip()
    except Exception:
        return ""

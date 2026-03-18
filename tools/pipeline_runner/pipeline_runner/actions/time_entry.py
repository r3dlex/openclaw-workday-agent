"""Time tracking actions for Workday."""

from __future__ import annotations

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from pipeline_runner.selectors.workday import (
    SUBMIT_BUTTON,
    TIME_ENTRY_DATE,
    TIME_ENTRY_HOURS,
    TIME_ENTRY_ROW,
)

# Compliance boundaries (configurable via rules dict)
DEFAULT_RULES = {
    "flex_start": "07:00",
    "flex_end": "19:00",
    "core_start": "09:00",
    "core_end": "16:00",
    "max_daily_hours": 10.0,
}


async def get_time_entries(page: Page, time_tracking_url: str) -> list[dict]:
    """Navigate to the time tracking page and extract existing entries."""
    await page.goto(time_tracking_url, wait_until="domcontentloaded")

    try:
        await page.locator(TIME_ENTRY_ROW).first.wait_for(
            state="visible", timeout=15_000
        )
    except PlaywrightTimeout:
        return []

    rows = page.locator(TIME_ENTRY_ROW)
    count = await rows.count()

    entries = []
    for i in range(count):
        row = rows.nth(i)
        hours_text = await _safe_text(row.locator(TIME_ENTRY_HOURS).first)
        date_text = await _safe_text(row.locator(TIME_ENTRY_DATE).first)

        entries.append(
            {
                "index": i,
                "hours": hours_text,
                "date": date_text,
            }
        )

    return entries


def validate_entry(entry: dict, rules: dict | None = None) -> dict:
    """Validate a time entry against compliance rules.

    Returns a dict with ``valid`` (bool), ``warnings`` (list), and ``errors`` (list).
    """
    rules = {**DEFAULT_RULES, **(rules or {})}
    warnings: list[str] = []
    errors: list[str] = []

    hours = _parse_hours(entry.get("hours"))
    start_time = entry.get("start_time", "")
    end_time = entry.get("end_time", "")

    # Check daily hour cap
    if hours is not None and hours > rules["max_daily_hours"]:
        warnings.append(
            f"Daily hours ({hours}h) exceed maximum ({rules['max_daily_hours']}h)"
        )

    if hours is not None and hours < 0:
        errors.append("Hours cannot be negative")

    # Check flex frame
    if start_time and start_time < rules["flex_start"]:
        errors.append(
            f"Start time {start_time} is before flex frame ({rules['flex_start']})"
        )

    if end_time and end_time > rules["flex_end"]:
        errors.append(
            f"End time {end_time} is after flex frame ({rules['flex_end']})"
        )

    # Check core hours coverage
    if start_time and start_time > rules["core_start"]:
        warnings.append(
            f"Start time {start_time} is after core hours start ({rules['core_start']})"
        )

    if end_time and end_time < rules["core_end"]:
        warnings.append(
            f"End time {end_time} is before core hours end ({rules['core_end']})"
        )

    return {
        "valid": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
    }


async def submit_time_entry(page: Page, hours: float, date: str) -> dict:
    """Fill in and submit a time entry for the given date."""
    # Locate the entry row for the target date
    rows = page.locator(TIME_ENTRY_ROW)
    count = await rows.count()

    target_row = None
    for i in range(count):
        row = rows.nth(i)
        date_text = await _safe_text(row.locator(TIME_ENTRY_DATE).first)
        if date in date_text:
            target_row = row
            break

    if target_row is None:
        return {"status": "error", "message": f"No entry row found for date {date}"}

    # Fill hours
    hours_input = target_row.locator(TIME_ENTRY_HOURS).first
    try:
        await hours_input.click()
        await hours_input.fill(str(hours))
    except PlaywrightTimeout:
        return {"status": "error", "message": "Could not fill hours input"}

    # Submit
    try:
        submit = page.locator(SUBMIT_BUTTON).first
        await submit.wait_for(state="visible", timeout=10_000)
        await submit.click()
    except PlaywrightTimeout:
        return {"status": "error", "message": "Submit button not found"}

    return {"status": "ok", "hours": hours, "date": date}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_hours(value) -> float | None:
    """Best-effort parse of an hours value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


async def _safe_text(locator) -> str:
    """Extract text content, returning empty string on failure."""
    try:
        text = await locator.text_content(timeout=3_000)
        return (text or "").strip()
    except Exception:
        return ""

"""Extended tests for pipeline_runner.actions.time_entry."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from pipeline_runner.actions.time_entry import (
    _parse_hours,
    _safe_text,
    get_time_entries,
    submit_time_entry,
    validate_entry,
)
from pipeline_runner.selectors.workday import TIME_ENTRY_ROW


# ---------------------------------------------------------------------------
# _parse_hours
# ---------------------------------------------------------------------------


class TestParseHours:
    def test_parses_float_string(self):
        assert _parse_hours("8.5") == 8.5

    def test_parses_int_string(self):
        assert _parse_hours("8") == 8.0

    def test_parses_float(self):
        assert _parse_hours(8.0) == 8.0

    def test_parses_int(self):
        assert _parse_hours(7) == 7.0

    def test_returns_none_for_none(self):
        assert _parse_hours(None) is None

    def test_returns_none_for_non_numeric(self):
        assert _parse_hours("not-a-number") is None

    def test_returns_none_for_empty_string(self):
        assert _parse_hours("") is None


# ---------------------------------------------------------------------------
# _safe_text
# ---------------------------------------------------------------------------


class TestSafeTextTimeEntry:
    @pytest.mark.asyncio
    async def test_returns_stripped_text(self):
        loc = AsyncMock()
        loc.text_content = AsyncMock(return_value="  8.00  ")
        result = await _safe_text(loc)
        assert result == "8.00"

    @pytest.mark.asyncio
    async def test_returns_empty_on_exception(self):
        loc = AsyncMock()
        loc.text_content = AsyncMock(side_effect=Exception("fail"))
        result = await _safe_text(loc)
        assert result == ""

    @pytest.mark.asyncio
    async def test_returns_empty_for_none(self):
        loc = AsyncMock()
        loc.text_content = AsyncMock(return_value=None)
        result = await _safe_text(loc)
        assert result == ""


# ---------------------------------------------------------------------------
# validate_entry (additional cases)
# ---------------------------------------------------------------------------


class TestValidateEntryAdditional:
    def test_non_parseable_hours_is_valid(self):
        entry = {"hours": "not-a-number", "start_time": "09:00", "end_time": "17:00"}
        result = validate_entry(entry)
        # hours can't be checked, no error from hours validation
        assert isinstance(result["valid"], bool)

    def test_empty_entry(self):
        result = validate_entry({})
        assert result["valid"] is True
        assert result["warnings"] == []
        assert result["errors"] == []

    def test_exactly_at_max_hours_no_warning(self):
        entry = {"hours": 10.0}
        result = validate_entry(entry)
        assert not any("exceed maximum" in w for w in result["warnings"])

    def test_exactly_at_flex_boundaries(self):
        entry = {"hours": 8, "start_time": "07:00", "end_time": "19:00"}
        result = validate_entry(entry)
        assert result["valid"] is True

    def test_custom_rules_override_max_hours(self):
        entry = {"hours": 3, "start_time": "09:00", "end_time": "12:00"}
        rules = {
            "max_daily_hours": 2.0,
            "flex_start": "07:00",
            "flex_end": "19:00",
            "core_start": "09:00",
            "core_end": "16:00",
        }
        result = validate_entry(entry, rules)
        assert any("exceed maximum" in w for w in result["warnings"])

    def test_both_warnings_and_no_errors(self):
        entry = {"hours": 11, "start_time": "10:00", "end_time": "14:00"}
        result = validate_entry(entry)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert result["errors"] == []


# ---------------------------------------------------------------------------
# get_time_entries
# ---------------------------------------------------------------------------


def _make_time_page(row_count=0, hours_text="8.00", date_text="2026-01-15"):
    """Build a mock page with time entry rows."""
    page = AsyncMock()
    page.goto = AsyncMock()

    leaf_loc = AsyncMock()
    leaf_loc.text_content = AsyncMock(side_effect=[hours_text, date_text] * (row_count + 1))
    leaf_loc.first = leaf_loc
    leaf_loc.nth = MagicMock(return_value=leaf_loc)
    leaf_loc.wait_for = AsyncMock()

    row_item = MagicMock()
    row_item.locator = MagicMock(return_value=leaf_loc)

    rows_locator = AsyncMock()
    rows_locator.count = AsyncMock(return_value=row_count)
    rows_locator.first = rows_locator
    rows_locator.wait_for = AsyncMock()
    rows_locator.nth = MagicMock(return_value=row_item)

    page.locator = MagicMock(return_value=rows_locator)
    return page, rows_locator, leaf_loc


class TestGetTimeEntries:
    @pytest.mark.asyncio
    async def test_returns_empty_on_no_rows(self):
        page = AsyncMock()
        page.goto = AsyncMock()

        loc = AsyncMock()
        loc.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        loc.first = loc
        page.locator = MagicMock(return_value=loc)

        entries = await get_time_entries(page, "https://workday.example.com/time-tracking")
        assert entries == []

    @pytest.mark.asyncio
    async def test_returns_entries_when_rows_present(self):
        page, _, _ = _make_time_page(row_count=2, hours_text="8.00", date_text="2026-01-15")

        entries = await get_time_entries(page, "https://workday.example.com/time-tracking")
        assert isinstance(entries, list)
        assert len(entries) == 2
        for entry in entries:
            assert "index" in entry
            assert "hours" in entry
            assert "date" in entry

    @pytest.mark.asyncio
    async def test_navigates_to_url(self):
        page, _, _ = _make_time_page(row_count=0)
        # Patch wait_for to raise to short-circuit
        url = "https://workday.example.com/time-tracking"

        loc = AsyncMock()
        loc.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        loc.first = loc
        page.locator = MagicMock(return_value=loc)

        await get_time_entries(page, url)
        page.goto.assert_called_once_with(url, wait_until="domcontentloaded")


# ---------------------------------------------------------------------------
# submit_time_entry
# ---------------------------------------------------------------------------


class TestSubmitTimeEntry:
    @pytest.mark.asyncio
    async def test_returns_error_when_no_rows(self):
        page = AsyncMock()

        rows = AsyncMock()
        rows.count = AsyncMock(return_value=0)
        page.locator = MagicMock(return_value=rows)

        result = await submit_time_entry(page, 8.0, "2026-01-15")
        assert result["status"] == "error"
        assert "No entry row" in result["message"]

    @pytest.mark.asyncio
    async def test_returns_error_when_date_not_found(self):
        page = AsyncMock()

        date_leaf = AsyncMock()
        date_leaf.text_content = AsyncMock(return_value="2026-01-20")
        date_leaf.first = date_leaf

        row = MagicMock()
        row.locator = MagicMock(return_value=date_leaf)

        rows = AsyncMock()
        rows.count = AsyncMock(return_value=1)
        rows.nth = MagicMock(return_value=row)
        page.locator = MagicMock(return_value=rows)

        result = await submit_time_entry(page, 8.0, "2026-01-15")
        assert result["status"] == "error"
        assert "No entry row" in result["message"]

    @pytest.mark.asyncio
    async def test_success_when_date_matches(self):
        page = AsyncMock()

        hours_input = AsyncMock()
        hours_input.click = AsyncMock()
        hours_input.fill = AsyncMock()
        hours_input.first = hours_input

        date_leaf = AsyncMock()
        date_leaf.text_content = AsyncMock(return_value="2026-01-15")
        date_leaf.first = date_leaf

        def _row_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_HOURS, TIME_ENTRY_DATE
            if selector == TIME_ENTRY_HOURS:
                return hours_input
            return date_leaf

        row = MagicMock()
        row.locator = MagicMock(side_effect=_row_locator)

        submit_btn = AsyncMock()
        submit_btn.wait_for = AsyncMock()
        submit_btn.click = AsyncMock()
        submit_btn.first = submit_btn

        rows = AsyncMock()
        rows.count = AsyncMock(return_value=1)
        rows.nth = MagicMock(return_value=row)

        def _page_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_ROW
            if selector == TIME_ENTRY_ROW:
                return rows
            return submit_btn

        page.locator = MagicMock(side_effect=_page_locator)

        result = await submit_time_entry(page, 8.0, "2026-01-15")
        assert result["status"] == "ok"
        assert result["hours"] == 8.0
        assert result["date"] == "2026-01-15"
        hours_input.fill.assert_called_once_with("8.0")

    @pytest.mark.asyncio
    async def test_error_when_fill_fails(self):
        page = AsyncMock()

        hours_input = AsyncMock()
        hours_input.click = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        hours_input.first = hours_input

        date_leaf = AsyncMock()
        date_leaf.text_content = AsyncMock(return_value="2026-01-15")
        date_leaf.first = date_leaf

        def _row_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_HOURS, TIME_ENTRY_DATE
            if selector == TIME_ENTRY_HOURS:
                return hours_input
            return date_leaf

        row = MagicMock()
        row.locator = MagicMock(side_effect=_row_locator)

        rows = AsyncMock()
        rows.count = AsyncMock(return_value=1)
        rows.nth = MagicMock(return_value=row)

        def _page_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_ROW
            if selector == TIME_ENTRY_ROW:
                return rows
            return AsyncMock()

        page.locator = MagicMock(side_effect=_page_locator)

        result = await submit_time_entry(page, 8.0, "2026-01-15")
        assert result["status"] == "error"
        assert "Could not fill" in result["message"]

    @pytest.mark.asyncio
    async def test_error_when_submit_button_not_found(self):
        page = AsyncMock()

        hours_input = AsyncMock()
        hours_input.click = AsyncMock()
        hours_input.fill = AsyncMock()
        hours_input.first = hours_input

        date_leaf = AsyncMock()
        date_leaf.text_content = AsyncMock(return_value="2026-01-15")
        date_leaf.first = date_leaf

        def _row_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_HOURS
            if selector == TIME_ENTRY_HOURS:
                return hours_input
            return date_leaf

        row = MagicMock()
        row.locator = MagicMock(side_effect=_row_locator)

        missing_submit = AsyncMock()
        missing_submit.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        missing_submit.first = missing_submit

        rows = AsyncMock()
        rows.count = AsyncMock(return_value=1)
        rows.nth = MagicMock(return_value=row)

        def _page_locator(selector):
            from pipeline_runner.selectors.workday import TIME_ENTRY_ROW
            if selector == TIME_ENTRY_ROW:
                return rows
            return missing_submit

        page.locator = MagicMock(side_effect=_page_locator)

        result = await submit_time_entry(page, 8.0, "2026-01-15")
        assert result["status"] == "error"
        assert "Submit button" in result["message"]

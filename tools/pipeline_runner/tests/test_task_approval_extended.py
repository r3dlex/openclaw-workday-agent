"""Extended tests for pipeline_runner.actions.task_approval."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from pipeline_runner.actions.task_approval import (
    _click_action_button,
    _safe_text,
    approve_task,
    deny_task,
    get_task_details,
    list_tasks,
    send_back_task,
)
from pipeline_runner.selectors.workday import (
    APPROVE_BUTTON,
    DONE_BUTTON,
    TASK_LIST_ITEMS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_leaf_locator(text="Task Text", visible=True):
    loc = AsyncMock()
    loc.text_content = AsyncMock(return_value=text)
    loc.wait_for = AsyncMock()
    loc.click = AsyncMock()
    loc.is_visible = AsyncMock(return_value=visible)
    loc.fill = AsyncMock()
    loc.first = loc
    loc.nth = MagicMock(return_value=loc)
    loc.count = AsyncMock(return_value=1)
    return loc


def _make_task_page(task_count=1, task_text="My Task"):
    """Build a mock page for task tests with configurable task count."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()

    leaf = _make_leaf_locator(task_text)

    item = MagicMock()
    item.locator = MagicMock(return_value=leaf)

    list_locator = AsyncMock()
    list_locator.count = AsyncMock(return_value=task_count)
    list_locator.wait_for = AsyncMock()
    list_locator.first = list_locator
    list_locator.nth = MagicMock(return_value=item)

    action_locator = AsyncMock()
    action_locator.wait_for = AsyncMock()
    action_locator.click = AsyncMock()
    action_locator.is_visible = AsyncMock(return_value=True)
    action_locator.first = action_locator

    def _route(selector):
        if selector == TASK_LIST_ITEMS:
            return list_locator
        return action_locator

    page.locator = MagicMock(side_effect=_route)
    return page, leaf, action_locator


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


class TestListTasksExtended:
    @pytest.mark.asyncio
    async def test_multiple_tasks(self):
        page, leaf, _ = _make_task_page(task_count=3, task_text="Multi Task")
        tasks = await list_tasks(page, "https://workday.example.com/tasks")
        assert len(tasks) == 3
        for task in tasks:
            assert "index" in task
            assert "title" in task

    @pytest.mark.asyncio
    async def test_task_has_all_fields(self):
        page, _, _ = _make_task_page(task_count=1)
        tasks = await list_tasks(page, "https://workday.example.com/tasks")
        task = tasks[0]
        assert set(task.keys()) == {"index", "title", "type", "date"}


# ---------------------------------------------------------------------------
# get_task_details
# ---------------------------------------------------------------------------


class TestGetTaskDetails:
    @pytest.mark.asyncio
    async def test_returns_task_details(self):
        page = AsyncMock()
        page.wait_for_load_state = AsyncMock()

        leaf = _make_leaf_locator("Detail Value")
        page.locator = MagicMock(return_value=leaf)

        task_element = AsyncMock()
        task_element.click = AsyncMock()

        details = await get_task_details(page, task_element)

        task_element.click.assert_called_once()
        assert "title" in details
        assert "type" in details
        assert "date" in details
        assert "description" in details


# ---------------------------------------------------------------------------
# _safe_text
# ---------------------------------------------------------------------------


class TestSafeText:
    @pytest.mark.asyncio
    async def test_returns_stripped_text(self):
        locator = AsyncMock()
        locator.text_content = AsyncMock(return_value="  hello world  ")
        result = await _safe_text(locator)
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_returns_empty_string_on_exception(self):
        locator = AsyncMock()
        locator.text_content = AsyncMock(side_effect=Exception("DOM error"))
        result = await _safe_text(locator)
        assert result == ""

    @pytest.mark.asyncio
    async def test_returns_empty_string_on_none(self):
        locator = AsyncMock()
        locator.text_content = AsyncMock(return_value=None)
        result = await _safe_text(locator)
        assert result == ""


# ---------------------------------------------------------------------------
# _click_action_button
# ---------------------------------------------------------------------------


class TestClickActionButton:
    @pytest.mark.asyncio
    async def test_success_with_done_button_visible(self):
        page = AsyncMock()

        approve_loc = AsyncMock()
        approve_loc.wait_for = AsyncMock()
        approve_loc.click = AsyncMock()
        approve_loc.first = approve_loc

        done_loc = AsyncMock()
        done_loc.wait_for = AsyncMock()
        done_loc.is_visible = AsyncMock(return_value=True)
        done_loc.click = AsyncMock()
        done_loc.first = done_loc

        def _route(selector):
            if APPROVE_BUTTON in selector:
                return approve_loc
            if DONE_BUTTON in selector:
                return done_loc
            # Combined selector for confirmation/done
            return done_loc

        page.locator = MagicMock(side_effect=_route)

        result = await _click_action_button(page, APPROVE_BUTTON, "approve")
        assert result["status"] == "ok"
        assert result["action"] == "approve"

    @pytest.mark.asyncio
    async def test_success_with_no_confirmation(self):
        page = AsyncMock()

        button_loc = AsyncMock()
        button_loc.wait_for = AsyncMock()
        button_loc.click = AsyncMock()
        button_loc.first = button_loc
        button_loc.is_visible = AsyncMock(return_value=False)

        # Confirmation times out
        confirm_loc = AsyncMock()
        confirm_loc.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        confirm_loc.first = confirm_loc

        call_count = [0]

        def _route(selector):
            call_count[0] += 1
            if call_count[0] <= 1:
                return button_loc
            return confirm_loc

        page.locator = MagicMock(side_effect=_route)

        result = await _click_action_button(page, APPROVE_BUTTON, "approve")
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_error_when_button_not_found(self):
        page = AsyncMock()

        loc = AsyncMock()
        loc.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        loc.first = loc
        page.locator = MagicMock(return_value=loc)

        result = await _click_action_button(page, APPROVE_BUTTON, "approve")
        assert result["status"] == "error"
        assert "approve" in result["message"]


# ---------------------------------------------------------------------------
# send_back_task
# ---------------------------------------------------------------------------


class TestSendBackTask:
    @pytest.mark.asyncio
    async def test_send_back_success(self):
        page = AsyncMock()
        loc = AsyncMock()
        loc.wait_for = AsyncMock()
        loc.click = AsyncMock()
        loc.is_visible = AsyncMock(return_value=False)
        loc.first = loc
        page.locator = MagicMock(return_value=loc)

        result = await send_back_task(page)
        assert result["status"] == "ok"
        assert result["action"] == "send_back"

    @pytest.mark.asyncio
    async def test_send_back_error(self):
        page = AsyncMock()
        loc = AsyncMock()
        loc.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        loc.first = loc
        page.locator = MagicMock(return_value=loc)

        result = await send_back_task(page)
        assert result["status"] == "error"

"""Tests for pipeline_runner.actions.task_approval."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeout

from pipeline_runner.actions.task_approval import (
    approve_task,
    deny_task,
    list_tasks,
)


def _make_leaf_locator(text="Test Task"):
    """A locator that supports .first and .text_content."""
    loc = AsyncMock()
    loc.text_content = AsyncMock(return_value=text)
    loc.wait_for = AsyncMock()
    loc.click = AsyncMock()
    loc.is_visible = AsyncMock(return_value=True)
    loc.first = loc
    return loc


@pytest.fixture()
def task_page():
    """Page mock for task approval tests."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()

    # Item locator returned by nth() — supports chained .locator() calls
    item_locator = MagicMock()
    item_locator.locator = MagicMock(return_value=_make_leaf_locator("Test Task"))

    # List locator — supports count/nth/first
    list_locator = AsyncMock()
    list_locator.count = AsyncMock(return_value=1)
    list_locator.wait_for = AsyncMock()
    list_locator.first = list_locator
    list_locator.nth = MagicMock(return_value=item_locator)

    # Action-button locator (approve/deny/done/confirmation)
    action_locator = AsyncMock()
    action_locator.wait_for = AsyncMock()
    action_locator.click = AsyncMock()
    action_locator.is_visible = AsyncMock(return_value=True)
    action_locator.first = action_locator

    def _route_locator(selector):
        from pipeline_runner.selectors.workday import TASK_LIST_ITEMS
        if selector == TASK_LIST_ITEMS:
            return list_locator
        return action_locator

    page.locator = MagicMock(side_effect=_route_locator)
    return page


class TestListTasks:
    @pytest.mark.asyncio
    async def test_returns_structured_data(self, task_page):
        tasks = await list_tasks(task_page, "https://workday.example.com/tasks")
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert "title" in tasks[0]
        assert "index" in tasks[0]

    @pytest.mark.asyncio
    async def test_empty_when_no_tasks(self, task_page):
        locator = AsyncMock()
        locator.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        locator.first = locator
        task_page.locator = MagicMock(return_value=locator)

        tasks = await list_tasks(task_page, "https://workday.example.com/tasks")
        assert tasks == []


class TestApproveTask:
    @pytest.mark.asyncio
    async def test_clicks_approve_button(self, task_page):
        result = await approve_task(task_page)
        assert result["status"] == "ok"
        assert result["action"] == "approve"

    @pytest.mark.asyncio
    async def test_error_when_button_missing(self, task_page):
        locator = AsyncMock()
        locator.wait_for = AsyncMock(side_effect=PlaywrightTimeout("timeout"))
        locator.first = locator
        task_page.locator = MagicMock(return_value=locator)

        result = await approve_task(task_page)
        assert result["status"] == "error"


class TestDenyTask:
    @pytest.mark.asyncio
    async def test_clicks_deny_button(self, task_page):
        result = await deny_task(task_page)
        assert result["status"] == "ok"
        assert result["action"] == "deny"

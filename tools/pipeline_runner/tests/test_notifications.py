"""Tests for pipeline_runner.notifications module."""

import os

import pytest

from pipeline_runner.notifications import Priority, notify, send_message


class TestSendMessage:
    """Tests for send_message()."""

    def test_skipped_when_not_configured(self, monkeypatch):
        """Should return False when Telegram credentials are missing."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        result = send_message("test message")
        assert result is False

    def test_skipped_when_token_empty(self, monkeypatch):
        """Should return False when token is empty string."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")

        result = send_message("test message")
        assert result is False

    def test_skipped_when_chat_id_empty(self, monkeypatch):
        """Should return False when chat_id is empty string."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "")

        result = send_message("test message")
        assert result is False


class TestNotify:
    """Tests for notify()."""

    def test_high_priority_skipped_when_not_configured(self, monkeypatch):
        """Should format and skip high priority messages."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        result = notify(Priority.HIGH, "Test alert")
        assert result is False

    def test_medium_priority_skipped_when_not_configured(self, monkeypatch):
        """Should format and skip medium priority messages."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        result = notify(Priority.MEDIUM, "Test info")
        assert result is False

    def test_low_priority_skipped_when_not_configured(self, monkeypatch):
        """Should format and skip low priority messages."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        result = notify(Priority.LOW, "Test debug")
        assert result is False

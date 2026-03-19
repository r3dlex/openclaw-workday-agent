"""Telegram notification helper for the pipeline runner.

Sends important pipeline events to the user via Telegram Bot API.
Configuration is read from environment variables:
- TELEGRAM_BOT_TOKEN: Bot token from @BotFather
- TELEGRAM_CHAT_ID: Target chat ID

If either is missing, notifications are silently skipped and logged.
"""

import logging
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def _get_config() -> tuple[str, str] | None:
    """Return (token, chat_id) or None if not configured."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if token and chat_id:
        return token, chat_id
    return None


def _log_notification(status: str, text: str, detail: str) -> None:
    """Append notification event to logs/notifications.log."""
    log_dir = os.environ.get("LOG_DIR", "logs")
    log_path = Path(log_dir) / "notifications.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        preview = text[:100]
        line = f"[{timestamp}] {status} | {detail} | {preview}\n"
        with open(log_path, "a") as f:
            f.write(line)
    except OSError as e:
        logger.warning("Failed to write notification log: %s", e)


def _priority_prefix(priority: Priority) -> str:
    if priority == Priority.HIGH:
        return "*\\[HIGH\\]*"
    if priority == Priority.MEDIUM:
        return "*\\[MEDIUM\\]*"
    return "\\[LOW\\]"


def send_message(text: str) -> bool:
    """Send a raw text message to Telegram.

    Returns True on success, False on failure or if not configured.
    """
    config = _get_config()
    if config is None:
        logger.warning(
            "Telegram not configured: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"
        )
        _log_notification("skipped", text, "not configured")
        return False

    token, chat_id = config
    url = f"{TELEGRAM_API}/bot{token}/sendMessage"

    try:
        resp = httpx.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "MarkdownV2",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            logger.info("Telegram notification sent")
            _log_notification("sent", text, "ok")
            return True
        else:
            logger.error("Telegram API error: %d - %s", resp.status_code, resp.text)
            _log_notification("failed", text, f"HTTP {resp.status_code}")
            return False
    except httpx.HTTPError as e:
        logger.error("Telegram request failed: %s", e)
        _log_notification("failed", text, str(e))
        return False


def notify(priority: Priority, message: str) -> bool:
    """Send a formatted notification with priority and timestamp."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    prefix = _priority_prefix(priority)
    formatted = f"{prefix} {message}\n\n_{timestamp}_"
    return send_message(formatted)

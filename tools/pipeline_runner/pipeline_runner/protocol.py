"""JSON-lines protocol for Elixir <-> Python communication over stdin/stdout."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Request:
    """Inbound command from the Elixir orchestrator."""

    action: str
    params: dict = field(default_factory=dict)
    request_id: str = ""


@dataclass
class Response:
    """Outbound result sent back to the Elixir orchestrator."""

    status: str  # "ok" | "error"
    result: Optional[dict] = None
    error: Optional[str] = None
    request_id: str = ""


def parse_request(line: str) -> Request:
    """Parse a single JSON line into a Request.

    Raises ValueError on malformed input.
    """
    line = line.strip()
    if not line:
        raise ValueError("Empty input line")

    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")

    action = data.get("action")
    if not action or not isinstance(action, str):
        raise ValueError("Missing or invalid 'action' field")

    return Request(
        action=action,
        params=data.get("params", {}),
        request_id=data.get("request_id", ""),
    )


def format_response(response: Response) -> str:
    """Serialize a Response to a single JSON line (no trailing newline)."""
    payload = {
        "status": response.status,
        "request_id": response.request_id,
    }
    if response.result is not None:
        payload["result"] = response.result
    if response.error is not None:
        payload["error"] = response.error
    return json.dumps(payload, separators=(",", ":"))

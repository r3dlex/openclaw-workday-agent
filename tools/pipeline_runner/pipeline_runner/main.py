"""CLI entry point for the pipeline runner.

Usage:
    # JSON-lines mode (Elixir orchestrator)
    pipeline-runner --stdio

    # Single action mode
    pipeline-runner --action login --params '{"provider_name": "MySSO"}'
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

from pipeline_runner.browser import BrowserManager
from pipeline_runner.config import PipelineConfig
from pipeline_runner.protocol import Request, Response, format_response, parse_request


def setup_logging() -> None:
    """Configure logging to stderr."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


async def dispatch(
    action: str, params: dict, browser_manager: BrowserManager, config: PipelineConfig
) -> dict:
    """Route an action name to the correct handler function."""
    # Import actions lazily so the module loads fast for --help
    from pipeline_runner.actions.sso_login import (
        ensure_authenticated,
        login_with_direct_link,
        login_with_provider,
    )
    from pipeline_runner.actions.task_approval import (
        approve_task,
        deny_task,
        list_tasks,
        send_back_task,
    )
    from pipeline_runner.actions.time_entry import (
        get_time_entries,
        submit_time_entry,
        validate_entry,
    )

    page = await browser_manager.get_page()

    if action == "login":
        return await ensure_authenticated(page, config)
    elif action == "login_provider":
        return await login_with_provider(
            page,
            params.get("provider_name", config.SSO_PROVIDER_NAME),
            params.get("base_url", config.WORKDAY_BASE_URL),
        )
    elif action == "login_direct":
        return await login_with_direct_link(
            page,
            params.get("direct_link", config.ORG_TENANT_DIRECT_LINK),
        )
    elif action == "list_tasks":
        tasks = await list_tasks(page, params.get("url", config.tasks_url))
        return {"tasks": tasks}
    elif action == "approve_task":
        return await approve_task(page)
    elif action == "deny_task":
        return await deny_task(page)
    elif action == "send_back_task":
        return await send_back_task(page)
    elif action == "get_time_entries":
        entries = await get_time_entries(
            page, params.get("url", config.time_tracking_url)
        )
        return {"entries": entries}
    elif action == "validate_entry":
        return validate_entry(params.get("entry", {}), params.get("rules"))
    elif action == "submit_time_entry":
        return await submit_time_entry(
            page, params.get("hours", 0), params.get("date", "")
        )
    elif action == "ping":
        return {"status": "ok", "message": "pong"}
    else:
        raise ValueError(f"Unknown action: {action}")


async def run_stdio(config: PipelineConfig) -> None:
    """Run the JSON-lines protocol loop, reading from stdin, writing to stdout."""
    async with BrowserManager(config) as bm:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = parse_request(line)
            except ValueError as exc:
                resp = Response(
                    status="error", error=str(exc), request_id=""
                )
                sys.stdout.write(format_response(resp) + "\n")
                sys.stdout.flush()
                continue

            try:
                result = await dispatch(request.action, request.params, bm, config)
                resp = Response(
                    status="ok", result=result, request_id=request.request_id
                )
            except Exception as exc:
                resp = Response(
                    status="error",
                    error=f"{type(exc).__name__}: {exc}",
                    request_id=request.request_id,
                )

            sys.stdout.write(format_response(resp) + "\n")
            sys.stdout.flush()


async def run_single(action: str, params: dict, config: PipelineConfig) -> None:
    """Run a single action and print the result."""
    async with BrowserManager(config) as bm:
        try:
            result = await dispatch(action, params, bm, config)
            resp = Response(status="ok", result=result)
        except Exception as exc:
            resp = Response(status="error", error=f"{type(exc).__name__}: {exc}")

    print(format_response(resp))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Pipeline Runner for Workday automation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stdio",
        action="store_true",
        help="Run in JSON-lines mode (stdin/stdout)",
    )
    group.add_argument(
        "--action",
        type=str,
        help="Run a single action by name",
    )
    parser.add_argument(
        "--params",
        type=str,
        default="{}",
        help="JSON string of action parameters",
    )

    args = parser.parse_args()
    config = PipelineConfig()  # type: ignore[call-arg]
    setup_logging()

    if args.stdio:
        asyncio.run(run_stdio(config))
    else:
        params = json.loads(args.params)
        asyncio.run(run_single(args.action, params, config))


if __name__ == "__main__":
    main()

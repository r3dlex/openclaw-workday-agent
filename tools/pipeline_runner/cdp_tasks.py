#!/usr/bin/env python3
"""Direct CDP relay — connects to Chrome on port 18792 and extracts Workday tasks."""

import json
import time
import asyncio

try:
    import websockets
except ImportError:
    print(json.dumps({"status": "error", "message": "websockets not installed"}))
    exit(1)

async def run():
    tasks_url = "https://wd3.myworkday.com/aveva/d/task/2998$44084.htmld"
    ws_url = "ws://127.0.0.1:18792/devtools/page/224B395CB4D7C6ECBF7957F679AF9942"

    cmd_id = [1]

    def next_id():
        cmd_id[0] += 1
        return cmd_id[0]

    async with websockets.connect(ws_url, open_timeout=10, close_timeout=5) as ws:
        # Navigate
        await ws.send(json.dumps({"id": next_id(), "method": "Page.navigate", "params": {"url": tasks_url}}))

        # Wait for load event
        await asyncio.sleep(5)

        # Query selector for task list items
        selector = '[data-automation-id="taskListItem"], [role="listitem"][class*="task"]'
        script = f"""
        (function() {{
            var items = document.querySelectorAll('{selector}');
            var result = [];
            items.forEach(function(item) {{
                var title = item.querySelector('[data-automation-id="taskTitle"]') ||
                            item.querySelector('[class*="task-title"]');
                var type = item.querySelector('[data-automation-id="taskType"]') ||
                           item.querySelector('[class*="task-type"]');
                var date = item.querySelector('[data-automation-id="taskDate"]') ||
                           item.querySelector('[class*="task-date"]');
                result.push({{
                    title: title ? title.innerText.trim() : '',
                    type: type ? type.innerText.trim() : '',
                    date: date ? date.innerText.trim() : '',
                    html: item.innerHTML.substring(0, 200)
                }});
            }});
            return JSON.stringify(result);
        }})()
        """

        await ws.send(json.dumps({
            "id": next_id(),
            "method": "Runtime.evaluate",
            "params": {"expression": script, "returnByValue": True}
        }))

        # Collect response
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=15)
            data = json.loads(msg)
            result_str = data.get("result", {}).get("result", {}).get("value", "[]")
            tasks = json.loads(result_str)
            print(json.dumps({"status": "ok", "tasks": tasks}, indent=2))
        except asyncio.TimeoutError:
            print(json.dumps({"status": "error", "message": "timeout waiting for task list"}))

if __name__ == "__main__":
    asyncio.run(run())
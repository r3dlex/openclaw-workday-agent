#!/usr/bin/env python3
"""Debug what's on the Workday tasks page."""

import json
import asyncio
try:
    import websockets
except ImportError:
    print(json.dumps({"status": "error", "message": "websockets not installed"}))
    exit(1)

async def run():
    # Try direct Microsoft SSO link first to get authenticated
    sso_url = "https://myapps.microsoft.com/signin/workday-sso/0e1fd44f-7ffa-4d85-b82e-c6524f8568f8?tenantId=c5738e01-9cd8-4e57-8437-2da092e4f858"

    ws_url = "ws://127.0.0.1:18792/devtools/page/224B395CB4D7C6ECBF7957F679AF9942"
    cmd_id = [1]
    def nid():
        cmd_id[0] += 1
        return cmd_id[0]

    async with websockets.connect(ws_url, open_timeout=10, close_timeout=5) as ws:
        # Navigate to SSO
        await ws.send(json.dumps({"id": nid(), "method": "Page.navigate", "params": {"url": sso_url}}))
        await asyncio.sleep(8)

        # Get page info
        await ws.send(json.dumps({
            "id": nid(),
            "method": "Runtime.evaluate",
            "params": {"expression": "JSON.stringify({url: window.location.href, title: document.title})", "returnByValue": True}
        }))
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        page_info = json.loads(msg)
        print("Page info:", json.dumps(page_info.get("result", {}).get("result", {}), indent=2))

        # Body text
        await ws.send(json.dumps({
            "id": nid(),
            "method": "Runtime.evaluate",
            "params": {"expression": "document.body ? document.body.innerText.substring(0, 800) : 'NO BODY'", "returnByValue": True}
        }))
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        body_text = json.loads(msg)
        print("Body:", json.dumps(body_text.get("result", {}).get("result", {}), indent=2))

        # Check if we're on Workday now
        await ws.send(json.dumps({
            "id": nid(),
            "method": "Runtime.evaluate",
            "params": {"expression": "window.location.href", "returnByValue": True}
        }))
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        result = json.loads(msg)
        final_url = result.get("result", {}).get("result", {}).get("value", "")
        print("Final URL:", final_url)

if __name__ == "__main__":
    asyncio.run(run())